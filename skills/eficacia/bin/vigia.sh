#!/usr/bin/env bash
# vigia.sh - vigia de sessoes do Claude Code, SEM modelo de IA (skill /bigtech:eficacia).
# Mecanico e offline (L-56): le $HOME/.claude/sessions e os transcripts, aplica os
# detectores e avisa so o desvio NOVO. Um python3 por passada (L-11), sem fork por item.
#
# Subcomandos:
#   check [--dry-run]          uma passada; --dry-run imprime e nao grava nem avisa
#   status                     disponibilidade e tempo em "esperando" (log das ultimas 24 h)
#   instalar [--intervalo MIN] timer systemd --user bigtech-eficacia.timer (padrao 5 min)
#   remover                    apaga o timer e o service
#   dormir | acordar           cria/apaga a bandeira lider_dormindo (o hook PreToolUse le)
set -euo pipefail

SESS_DIR="$HOME/.claude/sessions"
PROJ_DIR="$HOME/.claude/projects"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia"
CONF_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/bigtech/eficacia.json"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT="bigtech-eficacia"
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

die() { printf 'vigia: %s\n' "$1" >&2; exit "${2:-1}"; }

# Aviso ao celular: copia minima do lib.sh do manter_ligado (sem source entre skills).
# EFICACIA_NOTIFY_CMD existe so para teste (stub). Falha de aviso nunca derruba a passada.
vigia_notify() {
  local msg="$1" dev=""
  if [ -n "${EFICACIA_NOTIFY_CMD:-}" ]; then $EFICACIA_NOTIFY_CMD "$msg" 2>/dev/null || true; return 0; fi
  dev="$(kdeconnect-cli -a --id-only 2>/dev/null | head -n1 || true)"
  if [ -n "$dev" ]; then
    kdeconnect-cli --ping-msg "$msg" -d "$dev" >/dev/null 2>&1 && return 0
  fi
  notify-send "bigtech-eficacia" "$msg" >/dev/null 2>&1 || true
  return 0
}

# Leitura unica: python3 -I le config e sessoes e devolve TSV. Nunca abre os .key.
# Linhas: C<esp><trav> | E<nome> (esperada) | S<pid><nome><status><statusUpdatedAt_s><mtime_transcript_s><vivo>
# updatedAt NAO e usado como batimento (nao confiavel).
PY_READ='
import glob, json, os, re, sys
cfg_path, sess_dir, proj_dir = sys.argv[1], sys.argv[2], sys.argv[3]

def clean(v):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(v))

try:
    cfg = {}
    if os.path.isfile(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
    if not isinstance(cfg, dict):
        raise ValueError("raiz deve ser objeto")
    esp = int(cfg.get("limiar_espera_min", 10))
    trav = int(cfg.get("limiar_travada_min", 15))
    nomes = cfg.get("esperadas", [])
    if not isinstance(nomes, list):
        raise ValueError("esperadas deve ser lista")
except (OSError, ValueError, TypeError) as e:
    sys.stderr.write("vigia: config invalida em %s (%s)\n" % (cfg_path, e))
    sys.exit(2)

print("C\t%d\t%d" % (esp, trav))
for n in nomes:
    print("E\t%s" % clean(n))

for p in sorted(glob.glob(os.path.join(sess_dir, "*.json"))):
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        pid = int(d["pid"])
    except (OSError, ValueError, KeyError, TypeError):
        continue
    name = clean(d.get("name") or "pid-%d" % pid)
    status = clean(d.get("status") or "")
    try:
        sua = int(float(d.get("statusUpdatedAt") or 0)) // 1000
    except (ValueError, TypeError):
        sua = 0
    cwd = str(d.get("cwd") or "")
    tm = 0
    if cwd:
        slug = re.sub(r"[^A-Za-z0-9]", "-", cwd)
        try:
            cands = glob.glob(os.path.join(proj_dir, slug, "*.jsonl"))
            if cands:
                tm = int(max(os.path.getmtime(c) for c in cands))
        except OSError:
            tm = 0
    vivo = 1 if os.path.exists("/proc/%d" % pid) else 0
    print("S\t%d\t%s\t%s\t%d\t%d\t%d" % (pid, name, status, sua, tm, vivo))
'

vigia_read() {
  PYOUT="$(python3 -I -c "$PY_READ" "$CONF_FILE" "$SESS_DIR" "$PROJ_DIR")" \
    || die "falha ao ler config ou sessoes" 2
}

cmd_check() {
  local dry=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --dry-run) dry=1 ;;
      *) die "argumento desconhecido: $1" 2 ;;
    esac
    shift
  done

  vigia_read
  local now=$EPOCHSECONDS esp=10 trav=15 kind a b c d e f
  local -a E_NAMES=() S_PID=() S_NAME=() S_STATUS=() S_SUA=() S_TM=() S_VIVO=()
  local -a R_NAME=() R_STATE=() R_DET=() D_KEY=() D_MSG=()
  declare -A alive=()

  while IFS=$'\t' read -r kind a b c d e f; do
    case "$kind" in
      C) esp="$a"; trav="$b" ;;
      E) E_NAMES+=("$a") ;;
      S)
        S_PID+=("$a"); S_NAME+=("$b"); S_STATUS+=("$c")
        S_SUA+=("$d"); S_TM+=("$e"); S_VIVO+=("$f")
        ;;
    esac
  done <<< "$PYOUT"

  add_row() { R_NAME+=("$1"); R_STATE+=("$2"); R_DET+=("$3"); }
  add_des() { D_KEY+=("$1"); D_MSG+=("$2"); }

  local i n p st sua tm key age
  for ((i = 0; i < ${#S_NAME[@]}; i++)); do
    [ "${S_VIVO[i]}" = 1 ] || continue
    n="${S_NAME[i]}"; p="${S_PID[i]}"; st="${S_STATUS[i]}"
    sua="${S_SUA[i]}"; tm="${S_TM[i]}"; key="$n@$p"
    alive["$n"]=1
    if [ -e "$STATE_DIR/parada/$n" ]; then
      add_row "$n" parada "pid $p, parada ordenada"; continue
    fi
    if [ "$st" = waiting ]; then
      age=$(( sua > 0 ? now - sua : 0 ))
      if [ "$sua" -gt 0 ] && [ "$age" -gt $(( esp * 60 )) ]; then
        add_row "$n" esperando "pid $p, aguarda ha $(( age / 60 )) min"
        add_des "ESPERANDO $key" "ESPERANDO: $n (pid $p) aguarda resposta ha $(( age / 60 )) min"
      else
        add_row "$n" esperando "pid $p, waiting recente"
      fi
      continue
    fi
    # A VERIFICAR (fora desta fatia): falta de delta de CPU da arvore do pid; por ora so o transcript.
    # Nota: status "idle" conta aqui (regra da letra: status != waiting). Confirmar com dados reais.
    if [ "$tm" -gt 0 ] && [ $(( now - tm )) -gt $(( trav * 60 )) ]; then
      add_row "$n" travada "pid $p, transcript parado ha $(( (now - tm) / 60 )) min"
      add_des "TRAVADA $key" "TRAVADA: $n (pid $p) transcript parado ha $(( (now - tm) / 60 )) min"
      continue
    fi
    add_row "$n" ocupada "pid $p"
  done

  # Morta: esperada sem nenhum processo vivo (precedencia: parada > morta).
  local m
  for m in "${E_NAMES[@]}"; do
    [ -n "${alive[$m]:-}" ] && continue
    if [ -e "$STATE_DIR/parada/$m" ]; then
      add_row "$m" parada "parada ordenada"
    else
      add_row "$m" morta "esperada, sem processo vivo"
      add_des "MORTA morta:$m" "MORTA: $m esperada e sem processo vivo"
    fi
  done

  # Desvio novo = chave que nao estava na passada anterior.
  declare -A prev=()
  local k
  if [ -f "$STATE_DIR/desvios.txt" ]; then
    while IFS= read -r k; do prev["$k"]=1; done < "$STATE_DIR/desvios.txt"
  fi

  local j marca
  local -a NOVOS=()
  for ((j = 0; j < ${#D_KEY[@]}; j++)); do
    if [ -n "${prev[${D_KEY[j]}]:-}" ]; then marca="ja avisado"; else marca="NOVO"; NOVOS+=("$j"); fi
    if [ "$dry" = 1 ]; then printf 'desvio\t%s\t%s\n' "$marca" "${D_MSG[j]}"; fi
  done

  for ((i = 0; i < ${#R_NAME[@]}; i++)); do
    [ "$dry" = 1 ] && printf '%s\t%s\t%s\n' "${R_STATE[i]}" "${R_NAME[i]}" "${R_DET[i]}"
  done

  if [ "$dry" = 1 ]; then
    printf '(dry-run: nada gravado, nada avisado)\n'
    return 0
  fi

  ( umask 077; mkdir -p "$STATE_DIR" )
  : > "$STATE_DIR/desvios.txt.tmp"
  for ((j = 0; j < ${#D_KEY[@]}; j++)); do printf '%s\n' "${D_KEY[j]}" >> "$STATE_DIR/desvios.txt.tmp"; done
  mv -f "$STATE_DIR/desvios.txt.tmp" "$STATE_DIR/desvios.txt"

  for ((i = 0; i < ${#R_NAME[@]}; i++)); do
    printf '%s\t%s\t%s\n' "$now" "${R_NAME[i]}" "${R_STATE[i]}" >> "$STATE_DIR/log.tsv"
  done

  for j in "${NOVOS[@]}"; do
    vigia_notify "${D_MSG[j]}"
  done
  return 0
}

cmd_status() {
  local log="$STATE_DIR/log.tsv"
  if [ ! -f "$log" ]; then printf 'sem dados: nenhum log em %s\n' "$STATE_DIR"; return 0; fi
  printf '%-24s %14s %14s\n' "sessao" "disponibilidade" "esperando_min"
  awk -F'\t' -v lim=$(( EPOCHSECONDS - 86400 )) '
    $1 < lim { next }
    {
      s = $2; e = $3
      if (e != "parada") { tot[s]++; if (e == "ocupada") oc[s]++ }
      # Tempo em esperando = soma dos intervalos entre passadas consecutivas da mesma sessao
      # cuja passada anterior estava em "esperando" (o log nao guarda o intervalo).
      if ((s in pe) && pe[s] == "esperando") esp[s] += $1 - pt[s]
      pe[s] = e; pt[s] = $1
    }
    END {
      T_tot = 0; T_oc = 0; T_esp = 0
      for (s in pe) {
        t = (s in tot) ? tot[s] : 0; o = (s in oc) ? oc[s] : 0; w = (s in esp) ? esp[s] : 0
        pct = t > 0 ? sprintf("%.1f%%", o * 100 / t) : "-"
        printf "D\t%s\t%s\t%.1f\n", s, pct, w / 60
        T_tot += t; T_oc += o; T_esp += w
      }
      printf "T\tTOTAL\t%s\t%.1f\n", (T_tot > 0 ? sprintf("%.1f%%", T_oc * 100 / T_tot) : "-"), T_esp / 60
    }' "$log" | sort | while IFS=$'\t' read -r kind s pct w; do
      if [ "$kind" = "T" ]; then printf '%-24s %14s %14s\n' "TOTAL" "$pct" "$w"
      else printf '%-24s %14s %14s\n' "$s" "$pct" "$w"; fi
    done
}

cmd_instalar() {
  local min=5
  while [ $# -gt 0 ]; do
    case "$1" in
      --intervalo)
        [ $# -ge 2 ] || die "--intervalo exige MIN" 2
        min="$2"; shift ;;
      *) die "argumento desconhecido: $1" 2 ;;
    esac
    shift
  done
  case "$min" in ''|*[!0-9]*) die "intervalo deve ser inteiro em minutos" 2 ;; esac
  [ "$min" -ge 1 ] || die "intervalo minimo e 1 minuto" 2
  command -v systemctl >/dev/null 2>&1 || die "systemctl ausente (exige systemd --user)" 3

  mkdir -p "$UNIT_DIR"
  cat > "$UNIT_DIR/$UNIT.service" <<EOF
[Unit]
Description=bigtech eficacia: vigia de sessoes (sem modelo)

[Service]
Type=oneshot
Nice=19
ExecStart=/bin/bash "$SELF" check
EOF
  cat > "$UNIT_DIR/$UNIT.timer" <<EOF
[Unit]
Description=bigtech eficacia: timer do vigia

[Timer]
OnBootSec=2min
OnUnitActiveSec=${min}min

[Install]
WantedBy=timers.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now "$UNIT.timer"
  printf 'instalado: %s.timer a cada %s min\n' "$UNIT" "$min"
}

cmd_remover() {
  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user disable --now "$UNIT.timer" >/dev/null 2>&1 || true
  fi
  rm -f "$UNIT_DIR/$UNIT.timer" "$UNIT_DIR/$UNIT.service"
  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload >/dev/null 2>&1 || true
  fi
  printf 'removido: %s\n' "$UNIT"
}

cmd_dormir() {
  ( umask 077; mkdir -p "$STATE_DIR" )
  : > "$STATE_DIR/lider_dormindo"
  printf 'bandeira lider_dormindo criada\n'
}

cmd_acordar() {
  rm -f "$STATE_DIR/lider_dormindo"
  printf 'bandeira lider_dormindo apagada\n'
}

usage() {
  cat <<'EOF'
uso: vigia.sh {check [--dry-run] | status | instalar [--intervalo MIN] | remover | dormir | acordar}
EOF
}

case "${1:-help}" in
  check) shift; cmd_check "$@" ;;
  status) cmd_status ;;
  instalar) shift; cmd_instalar "$@" ;;
  remover) cmd_remover ;;
  dormir) cmd_dormir ;;
  acordar) cmd_acordar ;;
  -h|--help|help) usage ;;
  *) usage >&2; die "subcomando desconhecido: $1" 2 ;;
esac
