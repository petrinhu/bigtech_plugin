#!/usr/bin/env bash
# Funções da skill manter_ligado. Sourced pelo controlador, guardião e testes.

# Guarda de plataforma: a skill so existe em Linux com systemd --user
# (systemd-run e systemd-inhibit). Fora disso, sai com 3 e uma mensagem clara.
ml_require_linux_systemd() {
  case "${OSTYPE:-}" in
    linux*) ;;
    *) printf 'manter_ligado: so roda em Linux com systemd --user (OSTYPE=%s)\n' "${OSTYPE:-vazio}" >&2; return 3 ;;
  esac
  if ! command -v systemd-run >/dev/null 2>&1 || ! command -v systemd-inhibit >/dev/null 2>&1; then
    printf 'manter_ligado: faltam systemd-run e/ou systemd-inhibit (exige Linux com systemd)\n' >&2
    return 3
  fi
  return 0
}

# Estado PRIVADO (CONS-09S): nunca /tmp, compartilhado entre usuarios.
ml_state_dir() {
  if [ -n "${MANTER_STATE_DIR:-}" ]; then printf '%s\n' "$MANTER_STATE_DIR"; return; fi
  printf '%s\n' "${XDG_RUNTIME_DIR:-$HOME/.cache}/manter_ligado"
}
ml_sessions_dir() { printf '%s\n' "$(ml_state_dir)/sessions"; }

# _ml_secure_dir <dir>: cria com umask 077 (modo 700); recusa symlink ou dono diferente.
_ml_secure_dir() {
  local p="$1"
  if [ -L "$p" ]; then printf 'manter_ligado: estado recusado: %s e symlink\n' "$p" >&2; return 1; fi
  if [ -e "$p" ]; then
    if [ ! -d "$p" ] || [ ! -O "$p" ]; then
      printf 'manter_ligado: estado recusado: %s nao e diretorio do usuario atual\n' "$p" >&2
      return 1
    fi
    return 0
  fi
  ( umask 077; mkdir -p "$p" ) || return 1
  chmod 700 "$p" || return 1
}
ml_init_state() { _ml_secure_dir "$(ml_state_dir)" && _ml_secure_dir "$(ml_sessions_dir)"; }

# $sid so passa se casar o padrao (CONS-09S): vai para nome de arquivo e para claude -p.
ml_valid_sid() { [[ "$1" =~ ^[A-Za-z0-9-]+$ ]]; }

ml_register_session() {
  # <sid> <slug> <transcript>
  ml_init_state
  ml_valid_sid "$1" || return 1
  { printf '%s\n' "$1"; printf '%s\n' "$2"; printf '%s\n' "$3"; } > "$(ml_sessions_dir)/$1"
}

ml_unregister_session() { rm -f "$(ml_sessions_dir)/$1"; }

ml_count() {
  local d; d="$(ml_sessions_dir)"
  [ -d "$d" ] || { printf '0\n'; return; }
  find "$d" -maxdepth 1 -type f | wc -l | tr -d ' '
}

ml_live_sids() {
  # Override para testes; senão varre /proc por CLAUDE_CODE_SESSION_ID.
  if [ -n "${MANTER_LIVE_SIDS:-}" ]; then
    # shellcheck disable=SC2086  # word-splitting intencional: sids separados por espaco
    printf '%s\n' $MANTER_LIVE_SIDS
    return
  fi
  local pid env_sid
  for pid in $(pgrep -u "$(id -u)" -f claude 2>/dev/null); do
    [ -r "/proc/$pid/environ" ] || continue
    env_sid="$( { tr '\0' '\n' < "/proc/$pid/environ"; } 2>/dev/null \
      | sed -n 's/^CLAUDE_CODE_SESSION_ID=//p' | head -n1)"
    [ -n "$env_sid" ] && printf '%s\n' "$env_sid"
  done
}

ml_reap() {
  local d sid; d="$(ml_sessions_dir)"
  [ -d "$d" ] || return 0
  local live; live="$(ml_live_sids)"
  local f
  for f in "$d"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    printf '%s\n' "$live" | grep -qx "$sid" || rm -f "$f"
  done
}

ml_battery_capacity() {
  local f="${MANTER_BAT_CAPACITY_FILE:-/sys/class/power_supply/BAT1/capacity}"
  local v=""
  [ -r "$f" ] && v="$(tr -dc '0-9' < "$f")"
  printf '%s\n' "${v:-100}"
}

ml_on_ac() {
  local f="${MANTER_AC_ONLINE_FILE:-/sys/class/power_supply/ACAD/online}"
  local v=""
  [ -r "$f" ] && v="$(tr -dc '0-9' < "$f")"
  printf '%s\n' "${v:-0}"
}

# ml_transcript_ok <caminho>: transcript so vale se for arquivo regular sob o diretorio
# de projetos do Claude do usuario, sem '..' e sem symlink (CONS-09S).
ml_transcript_ok() {
  local t="$1" base
  base="${MANTER_PROJECTS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects}"
  case "$t" in "$base"/*) ;; *) return 1 ;; esac
  case "$t" in *"/../"*|*/..) return 1 ;; esac
  [ -f "$t" ] && [ ! -L "$t" ]
}

ml_resolve_transcript() {
  local sid="$1" base m
  base="${MANTER_PROJECTS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects}"
  for m in "$base"/*/"$sid".jsonl; do
    [ -e "$m" ] && { printf '%s\n' "$m"; return 0; }
  done
  return 1
}

# ml_decide_into <cap> <on_ac> <warned20> <saved5> -> ML_ACAO = none|warn|save (sem fork)
ml_decide_into() {
  local cap="$1" ac="$2" warned="$3" saved="$4"
  local warn_pct="${MANTER_WARN_PCT:-20}" save_pct="${MANTER_SAVE_PCT:-5}"
  ML_ACAO=none
  [ "$ac" = "1" ] && return 0
  if [ "$cap" -le "$save_pct" ]; then
    [ "$saved" = "1" ] || ML_ACAO=save
    return 0
  fi
  if [ "$cap" -le "$warn_pct" ]; then
    [ "$warned" = "1" ] || ML_ACAO=warn
    return 0
  fi
  return 0
}

ml_decide() {
  # <cap> <on_ac> <warned20> <saved5> -> none|warn|save
  ml_decide_into "$@"
  printf '%s\n' "$ML_ACAO"
}

# ml_current_ppid -> ML_PPID: PPID ATUAL, lido de /proc/self/stat por builtin.
# ($PPID do bash e fixado no arranque: nao acompanha o reparenting quando o pai morre.)
ml_current_ppid() {
  local st=""
  ML_PPID=""
  read -r st < /proc/self/stat 2>/dev/null || return 1
  st="${st##*) }"
  set -- $st
  ML_PPID="${2:-}"
}

# ml_read_num <arquivo> <padrao> -> ML_NUM (builtin, sem fork): so digitos do arquivo.
ml_read_num() {
  local v=""
  ML_NUM="$2"
  [ -r "$1" ] && read -r v < "$1" 2>/dev/null
  v="${v//[!0-9]/}"
  [ -n "$v" ] && ML_NUM="$v"
  return 0
}

# ml_pids_crit: 0 = em degrau critico (>= 80% do teto de processos do usuario);
# 1 = abaixo, ou indeterminado. Leitura so por builtin (a leitura e por builtin).
ml_pids_crit() {
  local lim="" cur="" l
  if [ -n "${MANTER_PIDS_LIMIT:-}" ]; then
    lim="$MANTER_PIDS_LIMIT"
  else
    while IFS= read -r l; do
      case "$l" in "Max processes"*) set -- $l; lim="$3"; break ;; esac
    done < /proc/self/limits
  fi
  ml_read_num "${MANTER_PIDS_CURRENT_FILE:-/sys/fs/cgroup/user.slice/user-${UID}.slice/pids.current}" ""
  cur="$ML_NUM"
  [[ "$lim" =~ ^[0-9]+$ && "$cur" =~ ^[0-9]+$ ]] || return 1
  (( lim > 0 && cur * 10 >= lim * 8 ))
}

ml_snap_dir() { printf '%s\n' "${MANTER_SNAP_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/manter_ligado_snapshots}"; }

ml_push() {
  local msg="$1"
  if [ -n "${MANTER_NOTIFY_CMD:-}" ]; then
    $MANTER_NOTIFY_CMD "$msg" 2>/dev/null || true
    return 0
  fi
  local dev
  dev="$(kdeconnect-cli -a --id-only 2>/dev/null | head -n1)"
  if [ -n "$dev" ]; then
    kdeconnect-cli --ping-msg "$msg" -d "$dev" >/dev/null 2>&1 && return 0
  fi
  notify-send "manter_ligado" "$msg" >/dev/null 2>&1 || true
  return 0
}

ml_prune_snaps() {
  local base; base="$(ml_snap_dir)"
  [ -d "$base" ] || return 0
  local d
  ls -1dt "$base"/*/ 2>/dev/null | tail -n +2 | while IFS= read -r d; do
    rm -rf "$d"
  done
}

ml_save() {
  local stamp="$1" out; out="$(ml_snap_dir)/$stamp"
  mkdir -p "$out"
  ml_push "Bateria ${MANTER_SAVE_PCT:-5}% - salvando estado das sessoes."
  local f sid tr
  for f in "$(ml_sessions_dir)"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    ml_valid_sid "$sid" || continue   # $sid fora do padrao nunca vai a arquivo nem a claude -p
    tr="$(sed -n '3p' "$f")"
    [ -z "$tr" ] && tr="$(ml_resolve_transcript "$sid" || true)"
    if [ -n "$tr" ] && ml_transcript_ok "$tr"; then
      cp -f "$tr" "$out/$sid.jsonl"
      { printf 'sid=%s\n' "$sid"; printf 'slug=%s\n' "$(sed -n '2p' "$f")";
        printf 'transcript=%s\n' "$tr"; printf 'stamp=%s\n' "$stamp"; } > "$out/$sid.meta"
    fi
    if [ "${MEMO_HEADLESS:-0}" = "1" ] && command -v claude >/dev/null 2>&1; then
      timeout 90 claude -p "/memo_persistente snapshot de emergencia (bateria baixa) da sessao $sid" \
        >/dev/null 2>&1 || true
    fi
  done
  ml_prune_snaps
}
