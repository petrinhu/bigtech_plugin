#!/usr/bin/env bash
# Funcoes da skill watchcode. Sourced pelo controlador, daemon e testes.

# Estado PRIVADO (CONS-09S): nunca /tmp, que e compartilhado entre usuarios.
# Padrao: $XDG_RUNTIME_DIR (tmpfs do usuario) ou $HOME/.cache.
wc_state_dir() {
  if [ -n "${WATCHCODE_STATE_DIR:-}" ]; then printf '%s\n' "$WATCHCODE_STATE_DIR"; return; fi
  printf '%s\n' "${XDG_RUNTIME_DIR:-$HOME/.cache}/watchcode"
}
wc_sessions_dir() { printf '%s\n' "$(wc_state_dir)/sessions"; }

# _wc_secure_dir <dir>: cria com umask 077 (modo 700) e recusa o que nao for
# diretorio real do usuario atual (symlink ou dono diferente). Fail-secure: rc!=0.
_wc_secure_dir() {
  local p="$1"
  if [ -L "$p" ]; then printf 'watchcode: estado recusado: %s e symlink\n' "$p" >&2; return 1; fi
  if [ -e "$p" ]; then
    if [ ! -d "$p" ] || [ ! -O "$p" ]; then
      printf 'watchcode: estado recusado: %s nao e diretorio do usuario atual\n' "$p" >&2
      return 1
    fi
    return 0
  fi
  ( umask 077; mkdir -p "$p" ) || return 1
  chmod 700 "$p" || return 1
}

wc_init_state() {
  _wc_secure_dir "$(wc_state_dir)" || return 1
  _wc_secure_dir "$(wc_sessions_dir)"
}

wc_register_session() {
  # <sid> <scope>
  wc_init_state
  printf '%s\n' "$2" > "$(wc_sessions_dir)/$1"
}

wc_unregister_session() { rm -f "$(wc_sessions_dir)/$1"; }

wc_count() {
  local d; d="$(wc_sessions_dir)"
  [ -d "$d" ] || { printf '0\n'; return; }
  find "$d" -maxdepth 1 -type f | wc -l | tr -d ' '
}

wc_live_sids() {
  if [ -n "${WATCHCODE_LIVE_SIDS:-}" ]; then
    printf '%s\n' $WATCHCODE_LIVE_SIDS
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

wc_reap() {
  local d sid live f; d="$(wc_sessions_dir)"
  [ -d "$d" ] || return 0
  live="$(wc_live_sids)"
  for f in "$d"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    printf '%s\n' "$live" | grep -qx "$sid" || rm -f "$f"
  done
}

# --- Transporte: fluxo continuo do journal (redesenho 01/09/2026) ---
# journalctl -f -o json vira UM processo filho de vida longa; o resto do
# roteamento/extracao/gravacao e 100% builtin do bash (regex/case/printf).
# Ver SPEC-transporte-watchcode.md secao 0-9. As 5 funcoes wc_detect_* que
# existiam aqui morreram com o transporte de janela ($(comando)|grep|sed);
# a INTELIGENCIA delas (os padroes) migrou intacta para os wc_parse_* abaixo.

WC_COREDUMP_MSGID="fc2e22bc6ee647b6b90729ab34a250b1"

# wc_json_str <line> <campo>: extrai de UMA linha do `journalctl -o json` o
# valor do campo <campo>, na forma JA-ESCAPADA que o journalctl emitiu (NUNCA
# des-escapa -- contrato da secao 5 da spec: quem des-escapa e o consumidor
# humano, nunca este parser). So builtin (BASH_REMATCH). Regex ERE de string
# JSON com escape: um valor e zero ou mais (qualquer-coisa-que-nao-seja-aspa-
# ou-barra OU barra-seguida-de-um-caractere) -- e o que impede truncar no
# primeiro \" escapado dentro do valor (achado C2 da revisao, nao coberto
# pela spec original).
#
# Contrato de retorno (as formas do man journalctl NUNCA somem em
# silencio -- achado C1 da revisao):
#   0 = achou como string; WC_JSON_VALUE tem o valor
#   1 = campo ausente na linha
#   2 = campo presente mas em forma de ARRAY: valor nao-UTF8 vira array de
#       bytes, OU campo repetido na mesma entrada vira array com todos os
#       valores (man journalctl, -o json). WC_JSON_VALUE fica vazio; o
#       CHAMADOR decide como tornar isso visivel (nunca descarta a entrada).
wc_json_str() {
  local line="$1" campo="$2"
  WC_JSON_VALUE=""
  if [[ $line =~ \"$campo\":\"(([^\"\\]|\\.)*)\" ]]; then
    WC_JSON_VALUE="${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ $line =~ \"$campo\":\[ ]]; then
    return 2
  fi
  return 1
}

# wc_stream_matches: imprime, um argumento por linha, os termos de match do
# journalctl que definem O QUE o fluxo cobre (disjuncao dos 3 sensores de
# journal com formato de entrada distinto). Sensor de journal novo soma um
# termo aqui, nao no laco do daemon.
wc_stream_matches() {
  printf '%s\n' \
    '_TRANSPORT=kernel' \
    '+' \
    '_SYSTEMD_UNIT=systemd-oomd.service' \
    '+' \
    "MESSAGE_ID=$WC_COREDUMP_MSGID"
}

# wc_cursor_load: le cursor+ts persistidos do estado para WC_STREAM_CURSOR/
# WC_STREAM_TS (vazios se nao houver). So builtin. 0=achou, 1=nao achou.
# So chamada em open/restart (nao no caminho quente); usa a variavel
# cacheada quando o daemon ja resolveu (evita $() mesmo aqui).
wc_cursor_load() {
  local f="${WC_STREAM_CURSOR_FILE:-$(wc_state_dir)/stream_cursor}"
  WC_STREAM_CURSOR=""
  WC_STREAM_TS=""
  [ -r "$f" ] || return 1
  read -r WC_STREAM_CURSOR WC_STREAM_TS < "$f" 2>/dev/null || true
  [ -n "$WC_STREAM_CURSOR" ]
}

# wc_cursor_flush: grava a posicao vigente (cursor+ts) do fluxo em disco. So
# builtin (printf). Chamado a cada tick, a cada linha processada (que cobre
# "a cada achado"), antes de reiniciar o stream, e no trap de saida --
# CAMINHO QUENTE de verdade (uma vez por linha do journal). Usa
# WC_STREAM_CURSOR_FILE cacheada pelo daemon no arranque (sem $()); so cai
# no fallback (forka) se chamada fora do daemon.
wc_cursor_flush() {
  [ -n "${WC_STREAM_CURSOR:-}" ] || return 0
  printf '%s %s\n' "$WC_STREAM_CURSOR" "${WC_STREAM_TS:-0}" > "${WC_STREAM_CURSOR_FILE:-$(wc_state_dir)/stream_cursor}"
}

# wc_stream_position: decide a POSICAO de arranque/reinicio do fluxo, na
# ordem cursor > last_scan (ponte de migracao do daemon velho) > janela de
# 130s (secao 2.2 da spec). Imprime o argumento --after-cursor=.../--since=...
# em stdout. So builtin (le arquivos de estado); chamada so em open/restart.
wc_stream_position() {
  local last_scan_file last_scan
  if wc_cursor_load; then
    printf -- '--after-cursor=%s\n' "$WC_STREAM_CURSOR"
    return 0
  fi
  last_scan_file="${WC_LAST_SCAN_FILE:-$(wc_state_dir)/last_scan}"
  if [ -r "$last_scan_file" ]; then
    read -r last_scan < "$last_scan_file" 2>/dev/null || last_scan=""
    if [[ "$last_scan" =~ ^[0-9]+$ ]]; then
      printf -- '--since=@%s\n' "$((last_scan - 130))"
      return 0
    fi
  fi
  printf -- '--since=-130s\n'
}

# wc_stream_open [posarg]: abre o coproc do fluxo (journalctl -f -o json, ou
# $WATCHCODE_STREAM_CMD em teste, mesmo padrao dos WATCHCODE_*_CMD antigos)
# na posicao dada, ou a calculada por wc_stream_position se nenhuma vier.
# `exec` dentro do coproc faz $WCJ_PID ser o proprio processo do fluxo (kill
# builtin direto, sem subshell intermediario -- secao 2.2). E o UNICO ponto
# do regime permanente que forka (1 processo).
#
# Achado da revisao adversarial (nao coberto pela spec, medido nesta
# maquina, bash 5.3.9): `coproc` fecha os PROPRIOS fds (WCJ[0]/WCJ[1]) assim
# que o bash percebe que o processo filho morreu (reap por SIGCHLD), mesmo
# que ainda haja bytes bufferizados e nao lidos no pipe -- perde linhas em
# corrida, medido repetidas vezes com um filho de vida curta (`cat` de 3
# linhas: 1 ou 2 das 3 chegavam, nunca as 3, nao deterministico). Contra
# journalctl -f (vida longa) isso nunca aparece em operacao normal, mas
# reaparece exatamente no cenario que a spec pede para cobrir (issue
# systemd/systemd#36247, filho que morre) e em QUALQUER teste com fixture
# curta. Correcao: mover o fd de leitura para fora do rastreamento interno
# do coproc logo apos abrir (`exec {WC_STREAM_FD}<&${WCJ[0]}-` -- aloca um
# fd novo, copia e FECHA o original), o que o desanexa do coproc e elimina a
# corrida (reproduzido 100/100 sem a correcao, 0/100 com ela nesta maquina).
# O laco do daemon le de $WC_STREAM_FD, nunca de ${WCJ[0]} diretamente.
wc_stream_open() {
  local pos="${1:-}"
  [ -n "$pos" ] || pos="$(wc_stream_position)"
  WC_STREAM_LAST_POS="$pos"
  if [ -n "${WATCHCODE_STREAM_CMD:-}" ]; then
    # shellcheck disable=SC2086,SC2086
    coproc WCJ { exec $WATCHCODE_STREAM_CMD "$pos"; }
  else
    # shellcheck disable=SC2046
    coproc WCJ { exec journalctl -f --lines=0 -o json \
      --output-fields=MESSAGE,_TRANSPORT,_SYSTEMD_UNIT,MESSAGE_ID,COREDUMP_EXE,COREDUMP_SIGNAL,COREDUMP_TIMESTAMP \
      --no-pager \
      $(wc_stream_matches) \
      "$pos"; }
  fi
  WC_STREAM_PID="$WCJ_PID"
  exec {WC_STREAM_FD}<&${WCJ[0]}-
  WC_STREAM_OPENED_AT=$EPOCHSECONDS
}

# wc_stream_close: mata e colhe o filho do fluxo (kill builtin + wait), e
# fecha o fd de leitura desanexado (WC_STREAM_FD, ver nota acima). So forka
# se o filho ainda estiver vivo (kill/wait/exec de fechamento sao builtins;
# nao ha fork aqui, so sinal + espera + fechar fd).
wc_stream_close() {
  local pid="${WC_STREAM_PID:-}"
  if [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
  fi
  if [ -n "${WC_STREAM_FD:-}" ]; then
    eval "exec ${WC_STREAM_FD}<&-" 2>/dev/null
  fi
  WC_STREAM_PID=""
  WC_STREAM_FD=""
}

# wc_stream_restart: chamado quando o read do fluxo devolve EOF/erro (o
# filho morreu). Fecha o que sobrou; sob crit (WC_PIDS_SKIP_FORKS=1) ADIA o
# reinicio sem forkar (WC_STREAM_DEFERRED=1, retorna 0 sem abrir nada -- a
# unica acao que forka no regime fica pausada, igual ao D2 do sensor pids);
# senao aplica a guarda de rotacao reusada (wc_spin_guard_tick) e reabre.
# Se o filho morreu RAPIDO (< intervalo/2) por cima de uma abertura que
# usava cursor, o cursor e descartado e o proximo open cai para --since
# (cobre E6: cursor rejeitado pelo journalctl). Retorna 1 se a guarda
# mandou parar (chamador encerra o daemon).
wc_stream_restart() {
  local uptime interval pos=""
  interval="${WATCHCODE_INTERVAL:-120}"
  (( uptime = EPOCHSECONDS - ${WC_STREAM_OPENED_AT:-EPOCHSECONDS} ))
  wc_stream_close
  wc_cursor_flush

  if [ "${WC_PIDS_SKIP_FORKS:-0}" = "1" ]; then
    WC_STREAM_DEFERRED=1
    return 0
  fi
  WC_STREAM_DEFERRED=0

  wc_spin_guard_tick "$uptime" "$interval" || return 1

  if [ "$uptime" -lt "$((interval / 2))" ] \
     && [ "${WC_STREAM_LAST_KIND:-}" = "cursor" ] \
     && [ -n "${WC_STREAM_CURSOR:-}" ]; then
    pos="--since=@$((${WC_STREAM_TS:-0} / 1000000))"
    rm -f "${WC_STREAM_CURSOR_FILE:-$(wc_state_dir)/stream_cursor}"
    WC_STREAM_CURSOR=""
  fi

  wc_stream_open "$pos"
  case "$WC_STREAM_LAST_POS" in
    --after-cursor=*) WC_STREAM_LAST_KIND=cursor ;;
    *) WC_STREAM_LAST_KIND=since ;;
  esac
  return 0
}

# wc_stream_dispatch <line>: roteia UMA linha JSON do fluxo ao parser do
# sensor dono dela, por conteudo (coredump > oomd > kernel generico -- nesta
# ordem porque MESSAGE_ID/_SYSTEMD_UNIT sao mais especificos que
# _TRANSPORT=kernel puro). Sensor novo soma um ramo do case. C1 (achado da
# revisao): quando o MESSAGE de uma linha kernel generica (nao-coredump,
# nao-oomd) vem em forma de array, NENHUM dos 3 parsers (oom/vram/disk) sabe
# a qual pertenceria -- em vez de chama-los as cegas (o que duplicaria o
# achado 3x, tao ruim quanto sumir) ou de descartar em silencio, a entrada
# vira um achado "unparseable" explicito, unico, visivel.
wc_stream_dispatch() {
  local line="$1" rc_msg
  case "$line" in
    *'"MESSAGE_ID":"'"$WC_COREDUMP_MSGID"'"'*)
      wc_parse_coredump "$line" ;;
    *'"_SYSTEMD_UNIT":"systemd-oomd.service"'*)
      wc_parse_oomd "$line" ;;
    *'"_TRANSPORT":"kernel"'*)
      wc_json_str "$line" MESSAGE; rc_msg=$?
      if [ "$rc_msg" -eq 0 ]; then
        wc_parse_oom "$line"
        wc_parse_vram "$line"
        wc_parse_disk "$line"
      elif [ "$rc_msg" -eq 2 ]; then
        wc_append_unparseable 'linha kernel com MESSAGE em array (nao-UTF8 ou campo repetido, journalctl -o json); nao foi possivel identificar o sensor'
      fi
      ;;
  esac
}

# wc_parse_coredump <line>: extrai coredump de uma linha do fluxo e grava o
# achado (baseline antes). C1 (revisao, nao coberto pela spec original):
# COREDUMP_EXE as vezes chega em forma de ARRAY de bytes (path com byte
# nao-UTF8) em vez de string -- a entrada NUNCA e descartada em silencio
# nesse caso: vira achado coredump normal (ts/sig continuam legiveis) com
# exe marcado como texto ilegivel, visivel, que o baseline (so casa string
# legivel) nunca filtra por engano.
wc_parse_coredump() {
  local line="$1" ts sig exe rc_ts rc_sig rc_exe
  wc_json_str "$line" COREDUMP_TIMESTAMP; rc_ts=$?; ts="$WC_JSON_VALUE"
  wc_json_str "$line" COREDUMP_SIGNAL;   rc_sig=$?; sig="$WC_JSON_VALUE"
  wc_json_str "$line" COREDUMP_EXE;      rc_exe=$?; exe="$WC_JSON_VALUE"

  [ "$rc_ts"  -eq 0 ] && [[ $ts  =~ ^[0-9]+$ ]] || return 0
  [ "$rc_sig" -eq 0 ] && [[ $sig =~ ^[0-9]+$ ]] || return 0

  if [ "$rc_exe" -eq 2 ]; then
    exe='<COREDUMP_EXE em array: nao-UTF8 ou campo repetido, journalctl entregou bytes brutos>'
  elif [ "$rc_exe" -ne 0 ]; then
    return 0
  fi

  wc_baseline_match "$exe" && return 0
  wc_append_coredump "$((ts / 1000000))" "$sig" "$exe"
}

# wc_parse_oom <line>: extrai "Killed process N (comm)" do MESSAGE de uma
# linha de kernel (o dispatch ja confirmou MESSAGE legivel, rc=0).
wc_parse_oom() {
  local line="$1" msg pid comm re='Killed[[:space:]]process[[:space:]]([0-9]+)[[:space:]]\(([^)]*)\)'
  wc_json_str "$line" MESSAGE || return 0
  msg="$WC_JSON_VALUE"
  [[ $msg =~ $re ]] || return 0
  pid="${BASH_REMATCH[1]}"; comm="${BASH_REMATCH[2]}"
  wc_baseline_match "$comm" && return 0
  wc_append_oom "$pid" "$comm"
}

# Deriva um "comm" plausivel a partir do path de cgroup que o oomd reporta.
# Best-effort: so reconhece o padrao comum unit/scope do systemd
# (app-<nome>.scope, run-<nome>.service); sem isso, devolve o ultimo
# segmento do path como esta. Preservada intacta (transporte novo, mesma
# funcao).
_wc_comm_from_cgroup() {
  local cg="$1" base
  base="${cg##*/}"
  base="${base%.scope}"; base="${base%.service}"; base="${base%.slice}"
  case "$base" in
    app-*) base="${base#app-}" ;;
    run-*) base="${base#run-}" ;;
  esac
  printf '%s\n' "$base"
}

# wc_parse_oomd <line>: extrai "Killed /caminho/cgroup" do MESSAGE de uma
# linha do systemd-oomd.service. Formato distinto do OOM de kernel, sensor
# dedicado (comentario original, preservado). C1: MESSAGE em array vira
# achado oomd marcado, nunca descartado em silencio.
wc_parse_oomd() {
  local line="$1" msg rc cgroup comm key re='Killed[[:space:]](/[^[:space:]]+)'
  wc_json_str "$line" MESSAGE; rc=$?
  if [ "$rc" -eq 2 ]; then
    wc_append_oomd '<MESSAGE em array: nao-UTF8 ou campo repetido, journalctl entregou bytes brutos>' ''
    return 0
  fi
  [ "$rc" -eq 0 ] || return 0
  msg="$WC_JSON_VALUE"
  [[ $msg =~ $re ]] || return 0
  cgroup="${BASH_REMATCH[1]}"
  comm="$(_wc_comm_from_cgroup "$cgroup")"
  key="$comm"; [ -z "$key" ] && key="$cgroup"
  wc_baseline_match "$key" && return 0
  wc_append_oomd "$cgroup" "$comm"
}

# wc_parse_vram <line>: Xid da NVIDIA associados a falha de app/MMU (nao
# ruido generico de driver) -- 13 (graphics engine exception), 31 (MMU fault
# / GPU memory access invalido), 43 (GPU stopped processing), 69 (VM_L2
# fault, canal invalido) -- e os 3 padroes AMD. Mesmo parser de hoje (nao
# confunde o codigo do Xid com os digitos do endereco PCI dentro do
# parenteses), agora em `[[ =~ ]]` sobre uma linha por vez em vez de
# `sed -nE` sobre um bloco de texto.
wc_parse_vram() {
  local line="$1" msg code="" xid pid="" comm="" \
        re_xid='Xid[^()]*\([^)]*\)[[:space:]]*:[[:space:]]*([0-9]+)' \
        re_pid='pid=([0-9]+)' re_name='name=([^,[:space:]]+)'
  wc_json_str "$line" MESSAGE || return 0
  msg="$WC_JSON_VALUE"
  case "$msg" in
    *NV_ERR_NO_MEMORY*) code="NV_ERR_NO_MEMORY" ;;
    *Xid*)
      if [[ $msg =~ $re_xid ]]; then
        xid="${BASH_REMATCH[1]}"
        case "$xid" in
          13|31|43|69) code="Xid:$xid" ;;
        esac
      fi
      ;;
  esac
  if [ -z "$code" ]; then
    case "$msg" in
      *amdgpu*"GPU reset"*) code="amdgpu:GPU reset" ;;
      *"ring "*"timeout"*) code="amdgpu:ring timeout" ;;
      *VM_L2_PROTECTION_FAULT*) code="amdgpu:VM_L2_PROTECTION_FAULT" ;;
    esac
  fi
  [ -z "$code" ] && return 0
  [[ $msg =~ $re_pid ]] && pid="${BASH_REMATCH[1]}"
  [[ $msg =~ $re_name ]] && comm="${BASH_REMATCH[1]}"
  local key="$comm"; [ -z "$key" ] && key="$msg"
  wc_baseline_match "$key" && return 0
  wc_append_vram "$code" "$pid" "$comm" "$msg"
}

# wc_parse_disk <line>: falhas de disco/IO que chegam ao journal do kernel.
# Limitacao conhecida (preservada): o caso mais comum de disco cheio
# quebrando build (ld morrendo com "No space left on device") sai em stderr
# do proprio linker, nao no kernel log -- este sensor NAO cobre esse caso,
# so o que o kernel reporta.
wc_parse_disk() {
  local line="$1" msg re='(no space left on device|btrfs.*(enospc|no space left)|csum failed|buffer i/o error|ext4-fs error|remounting filesystem read-only)'
  wc_json_str "$line" MESSAGE || return 0
  msg="$WC_JSON_VALUE"
  shopt -s nocasematch
  if [[ $msg =~ $re ]]; then
    shopt -u nocasematch
  else
    shopt -u nocasematch
    return 0
  fi
  wc_baseline_match "$msg" && return 0
  wc_append_disk "$msg"
}

# Resolvedor unico da baseline: WATCHCODE_BASELINE_FILE (env); senao a baseline
# LOCAL nao versionada do usuario; senao o exemplo generico desta skill.
wc_baseline_path() {
  if [ -n "${WATCHCODE_BASELINE_FILE:-}" ]; then printf '%s\n' "$WATCHCODE_BASELINE_FILE"; return 0; fi
  local local_f="$HOME/.config/bigtech/watchcode_baseline.txt"
  if [ -r "$local_f" ]; then printf '%s\n' "$local_f"; return 0; fi
  printf '%s\n' "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/baseline.txt"
}

wc_baseline_match() {
  local s="$1" f pat
  f="$(wc_baseline_path)"
  [ -r "$f" ] || return 1
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$pat" in \#*) continue ;; esac
    # shellcheck disable=SC2254  # glob intencional vindo do baseline
    case "$s" in $pat) return 0 ;; esac
  done < "$f"
  return 1
}

wc_classify_exe() {
  local exe="$1" scope="$2" proot="$3" rest proj
  case "$exe" in
    "$scope"/*) printf 'this\n'; return ;;
  esac
  case "$exe" in
    "$proot"/*)
      rest="${exe#"$proot"/}"; proj="${rest%%/*}"
      printf 'other:%s\n' "$proj"; return ;;
  esac
  printf 'system\n'
}

# Processos de toolchain de build (compilador/linker/build system/bundler JS)
# cujo comm NUNCA aparece na arvore do projeto -- ver wc_classify_oom.
# Compiladores versionados (gcc-13, clang-17, g++-14, clang++-15) usam padrao
# de sufixo numerico em vez de lista nome-a-nome (senao vira manutencao
# infinita); o padrao exige "-" seguido de digito, entao NAO casa nomes como
# "clang-tidy-14" (letra logo apos o "-") nem strings soltas como "systemd",
# "world" ou "gold" (substring "ld" sozinha nunca casa, so o comm exato).
_wc_is_build_toolchain() {
  case "$1" in
    cc1plus|cc1|cc1obj|gcc|g++|cc|c++|ld|ld.lld|lld|ld.gold|mold|collect2|\
rustc|cargo|ninja|make|cmake|moc|uic|rcc|tsc|node|javac|go|link|lto1|\
webpack|webpack-cli|vite|esbuild|rollup|babel|swc|parcel|turbo|\
npm|yarn|pnpm|bun|deno|next-server|\
gcc-[0-9]*|g++-[0-9]*|clang-[0-9]*|clang++-[0-9]*)
      return 0 ;;
    *) return 1 ;;
  esac
}

wc_classify_oom() {
  local comm="$1" scope="$2"
  if find "$scope" -maxdepth 8 -type f -name "$comm" 2>/dev/null | head -n1 | grep -q .; then
    printf 'this\n'; return
  fi
  if _wc_is_build_toolchain "$comm"; then
    printf 'build\n'; return
  fi
  printf 'system\n'
}

wc_findings_file() { printf '%s\n' "$(wc_state_dir)/findings.jsonl"; }

# Os wc_append_* trocam jq (1 fork por achado) por printf builtin (secao 5
# da spec: custo 0 processos em qualquer volume). Contrato: todo campo de
# TEXTO chega no argumento JA em forma JSON-escapada (quem escapou foi o
# journalctl, na fonte -- RFC 8259 exige escapar '"', '\' e U+0000..U+001F,
# e -o json ja entrega nessa forma); quem chama e sempre um wc_parse_* (via
# wc_json_str) ou um literal fixo do proprio codigo. NUNCA des-escapar aqui:
# reemitir o texto verbatim entre aspas produz string JSON valida por
# construcao. Campos numericos via printf %d (nunca texto livre).
#
# Achado da revisao adversarial (medido com strace -f -c, nao coberto pela
# spec original): NEM `wc_init_state` NEM `"$(wc_findings_file)"` sao de
# graca -- `wc_init_state` chama `mkdir` (externo, fork+exec) e QUALQUER
# `$(...)` forka um subshell so para capturar a saida, mesmo quando a funcao
# chamada dentro e 100% builtin. Chamar as duas coisas a cada achado
# (padrao herdado do jq antigo, que ja forkava mesmo) violava o orcamento
# de "0 processos por achado" no transporte novo: medido, 10 achados
# custavam ~40 clone/execve so nessas duas linhas. Correcao: NENHUM
# wc_append_* chama wc_init_state (quem cria o diretorio de estado e o
# ARRANQUE do daemon/teste, uma vez so -- mesmo padrao que wc_pids_init ja
# usa para WC_PIDS_FILE/WC_PIDS_FINDINGS); e todos escrevem em
# "${WC_FINDINGS_FILE:-$(wc_findings_file)}" -- o daemon resolve
# WC_FINDINGS_FILE UMA VEZ no arranque (variavel simples, sem $()), e so o
# fallback (chamada direta fora do daemon, ex. em teste) ainda forka.
# CONS-09S: exe, comm, cgroup e linhas vindos do journal sao DADO NAO CONFIAVEL.
# _wc_safe: charset estrito [A-Za-z0-9._/+-]; cada caractere fora dele vira '_'
# (fail-closed). Resultado em WC_SAFE (sem fork). Nunca chega cru ao finding.
_wc_safe() {
  local LC_ALL=C v="$1"
  v="${v//[^A-Za-z0-9._+\/-]/_}"
  WC_SAFE="${v:0:255}"
}

# _wc_safe_text: linha de texto livre do kernel. O parser (wc_json_str) ja entrega
# o valor com os escapes JSON do journal (passthrough, teste 2); aqui so se limita
# o tamanho. Resultado em WC_SAFE. Nunca vai para comando.
_wc_safe_text() { WC_SAFE="${1:0:300}"; }

wc_append_coredump() {
  _wc_safe "$3"
  printf '{"kind":"coredump","ts":%d,"sig":%d,"exe":"%s"}\n' "$1" "$2" "$WC_SAFE" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
}

wc_append_oom() {
  _wc_safe "$2"
  printf '{"kind":"oom","src":"kernel","pid":"%s","comm":"%s"}\n' "$1" "$WC_SAFE" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
}

wc_append_oomd() {
  # <cgroup> <comm>
  local cg comm
  _wc_safe "$1"; cg="$WC_SAFE"
  _wc_safe "$2"; comm="$WC_SAFE"
  if [ -n "$2" ]; then
    printf '{"kind":"oom","src":"oomd","cgroup":"%s","comm":"%s"}\n' "$cg" "$comm" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
  else
    printf '{"kind":"oom","src":"oomd","cgroup":"%s"}\n' "$cg" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
  fi
}

wc_append_vram() {
  # <code> <pid> <comm> <line>
  local extra="" pid comm line
  _wc_safe "$2"; pid="$WC_SAFE"
  _wc_safe "$3"; comm="$WC_SAFE"
  _wc_safe_text "$4"; line="$WC_SAFE"
  [ -n "$2" ] && extra="$extra,\"pid\":\"$pid\""
  [ -n "$3" ] && extra="$extra,\"comm\":\"$comm\""
  [ -n "$4" ] && extra="$extra,\"line\":\"$line\""
  printf '{"kind":"vram","code":"%s"%s}\n' "$1" "$extra" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
}

wc_append_disk() {
  # <line>
  _wc_safe_text "$1"
  printf '{"kind":"disk","line":"%s"}\n' "$WC_SAFE" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
}

wc_append_unparseable() {
  # <marca> -- entrada cujo campo relevante veio em forma nao-texto (array
  # de bytes/campo repetido) e nao pode ser atribuida a um sensor especifico.
  printf '{"kind":"unparseable","line":"%s"}\n' "$1" >> "${WC_FINDINGS_FILE:-$(wc_findings_file)}"
}

wc_read_new() {
  local sid="$1" cur cf ff total
  ff="$(wc_findings_file)"; cf="$(wc_state_dir)/cursor/$sid"
  [ -f "$ff" ] || return 0
  cur=0; [ -f "$cf" ] && cur="$(cat "$cf")"
  total="$(wc -l < "$ff" | tr -d ' ')"
  if [ "$total" -gt "$cur" ]; then
    sed -n "$((cur+1)),${total}p" "$ff"
    mkdir -p "$(dirname "$cf")"; printf '%s\n' "$total" > "$cf"
  fi
}

wc_sig_name() {
  case "$1" in
    4) printf 'SIGILL\n' ;; 6) printf 'SIGABRT\n' ;; 7) printf 'SIGBUS\n' ;;
    8) printf 'SIGFPE\n' ;; 11) printf 'SIGSEGV\n' ;; *) printf 'SIG%s\n' "$1" ;;
  esac
}

wc_report_other() {
  # <proj> <corpo>
  printf 'De: WatchCode\nPara: sessão de %s\n\n%s\n' "$1" "$2"
}

wc_report_user() {
  # <corpo>
  printf 'De: WatchCode\nPara: Usuário\n\n%s\n' "$1"
}

# --- Sensor pids (preventivo, fork-free) ---
# Mede a ocupacao de tasks (processos+threads) do usuario contra o teto de
# RLIMIT_NPROC e emite achado ANTES do estouro, sem forkar.
# Portao que forka por item varrido e exatamente o que
# derrubou a area de trabalho do usuario num incidente de 01/09/2026.
# Nao "readonly": D4 (revisao adversarial) -- readonly aqui era o unico uso
# no arquivo inteiro e quebra sourcing duplo (". lib.sh; . lib.sh" emite
# "variavel permite somente leitura" 4x). Simples atribuicao e idempotente
# por natureza, como o resto da lib.
WC_PIDS_WARN_ON=60
WC_PIDS_WARN_OFF=55
WC_PIDS_CRIT_ON=80
WC_PIDS_CRIT_OFF=75

# wc_pids_init: roda 1 vez no arranque do daemon; PODE forkar (ainda ha
# folga). Resolve e cacheia fonte, limite e paths de estado/findings nos
# globais WC_PIDS_*; decide ativo/inativo; escreve o arquivo de estado.
wc_pids_init() {
  WC_PIDS_FILE="${WATCHCODE_PIDS_CURRENT_FILE:-/sys/fs/cgroup/user.slice/user-${UID}.slice/pids.current}"
  local state ulim_file max_file lim max invalid_override=0
  state="$(wc_state_dir)"
  wc_init_state
  WC_PIDS_STATE_FILE="$state/pids_sensor"
  WC_PIDS_FINDINGS="$state/findings.jsonl"
  WC_PIDS_LEVEL=0
  WC_PIDS_PRE_ERR_LEVEL=0
  WC_PIDS_SKIP_FORKS=0
  # D5: limite tem de ser inteiro MAIOR QUE ZERO nas tres origens (override,
  # ulimit, pids.max) -- "^[0-9]+$" antigo aceitava "0", que com cur>0
  # classificava tudo como crit permanente (cur*100 >= 0*80 e sempre
  # verdade) sem o sensor nunca se declarar disabled/error: silencio
  # disfarcado de alerta.
  if [ -n "${WATCHCODE_PIDS_LIMIT:-}" ]; then
    if [[ "${WATCHCODE_PIDS_LIMIT}" =~ ^[1-9][0-9]*$ ]]; then
      WC_PIDS_LIMIT="$WATCHCODE_PIDS_LIMIT"
    else
      WC_PIDS_LIMIT=""
      invalid_override=1
    fi
  else
    ulim_file="$state/pids_ulimit"
    ulimit -u > "$ulim_file"
    read -r lim < "$ulim_file"
    max_file="${WC_PIDS_FILE%/*}/pids.max"
    max=""
    if [ -r "$max_file" ]; then
      read -r max < "$max_file" 2>/dev/null || max=""
    fi
    if [[ "$lim" =~ ^[1-9][0-9]*$ ]] && [[ "$max" =~ ^[1-9][0-9]*$ ]]; then
      if [ "$lim" -le "$max" ]; then WC_PIDS_LIMIT="$lim"; else WC_PIDS_LIMIT="$max"; fi
    elif [[ "$lim" =~ ^[1-9][0-9]*$ ]]; then
      WC_PIDS_LIMIT="$lim"
    elif [[ "$max" =~ ^[1-9][0-9]*$ ]]; then
      WC_PIDS_LIMIT="$max"
    else
      WC_PIDS_LIMIT=""
    fi
  fi
  if [ -r "$WC_PIDS_FILE" ] && [ -n "${WC_PIDS_LIMIT:-}" ]; then
    WC_PIDS_ENABLED=1
    printf 'active file=%s limit=%s\n' "$WC_PIDS_FILE" "$WC_PIDS_LIMIT" > "$WC_PIDS_STATE_FILE"
  else
    WC_PIDS_ENABLED=0
    if [ ! -r "$WC_PIDS_FILE" ]; then
      printf 'disabled fonte ausente ou ilegivel: %s\n' "$WC_PIDS_FILE" > "$WC_PIDS_STATE_FILE"
    elif [ "$invalid_override" = "1" ]; then
      printf 'disabled limite invalido (WATCHCODE_PIDS_LIMIT=%s precisa ser inteiro > 0)\n' "$WATCHCODE_PIDS_LIMIT" > "$WC_PIDS_STATE_FILE"
    else
      printf 'disabled limite indeterminavel (ulimit e pids.max nao numericos ou <= 0)\n' > "$WC_PIDS_STATE_FILE"
    fi
  fi
}

# wc_pids_read: caminho quente, SO builtins. Le a ocupacao atual para
# WC_PIDS_CUR. 0=ok; 2=fonte ilegivel ou valor nao numerico.
wc_pids_read() {
  [[ -r $WC_PIDS_FILE ]] || return 2
  read -r WC_PIDS_CUR < "$WC_PIDS_FILE" || return 2
  [[ $WC_PIDS_CUR =~ ^[0-9]+$ ]] || return 2
}

# wc_pids_level_calc: PURA, sem I/O, SO aritmetica builtin. A partir de
# WC_PIDS_CUR/WC_PIDS_LIMIT/WC_PIDS_LEVEL (nivel vigente) calcula
# WC_PIDS_NEWLEVEL aplicando degraus + histerese (secao 4 da spec).
wc_pids_level_calc() {
  local cur="$WC_PIDS_CUR" lim="$WC_PIDS_LIMIT" cand="$WC_PIDS_LEVEL" vigente="$WC_PIDS_LEVEL" off
  if (( cur*100 >= lim*WC_PIDS_CRIT_ON )); then
    cand=2
  elif (( cur*100 >= lim*WC_PIDS_WARN_ON )); then
    cand=1
  else
    cand=0
  fi
  if (( cand >= vigente )); then
    WC_PIDS_NEWLEVEL=$cand
    return
  fi
  case "$vigente" in
    2) off=$WC_PIDS_CRIT_OFF ;;
    1) off=$WC_PIDS_WARN_OFF ;;
    *) off=0 ;;
  esac
  if (( cur*100 < lim*off )); then
    WC_PIDS_NEWLEVEL=$cand
  else
    WC_PIDS_NEWLEVEL=$vigente
  fi
}

# wc_pids_append <cur> <max> <level_str>: caminho quente, SO builtins.
# Serializa UMA linha JSONL do achado. Nao decide nada, recebe valores ja
# validados. level_str=err grava a forma curta (sem cur/max) -- prova de
# escape na secao 2 da spec: todo campo vem de printf %d ou de um literal
# fixo, nenhum campo de texto livre, jq desnecessario neste caminho.
wc_pids_append() {
  case "$3" in
    err)
      printf '{"kind":"pids","ts":%d,"level":"err"}\n' "${EPOCHSECONDS:-0}" >> "$WC_PIDS_FINDINGS"
      ;;
    *)
      printf '{"kind":"pids","ts":%d,"cur":%d,"max":%d,"level":"%s"}\n' \
        "${EPOCHSECONDS:-0}" "$1" "$2" "$3" >> "$WC_PIDS_FINDINGS"
      ;;
  esac
}

# wc_pids_sense: caminho quente, SO builtins, chamada unica no ciclo.
# Protocolo do tick: read -> em falha, transicao para err (uma linha, uma
# vez) -> senao level_calc -> achado SO em transicao de subida -> atualiza
# o nivel vigente (subida E descida) -> seta SKIP_FORKS sse crit.
wc_pids_sense() {
  [ "${WC_PIDS_ENABLED:-0}" = "1" ] || return 0
  if ! wc_pids_read; then
    if [ "$WC_PIDS_LEVEL" != "3" ]; then
      WC_PIDS_PRE_ERR_LEVEL=$WC_PIDS_LEVEL
      wc_pids_append 0 0 err
      printf 'error nao foi possivel ler %s\n' "$WC_PIDS_FILE" > "$WC_PIDS_STATE_FILE"
      WC_PIDS_LEVEL=3
    fi
    # D2 (fail-closed, decisao de produto): NAO zera WC_PIDS_SKIP_FORKS aqui.
    # Sem saber quanta folga existe, o daemon PRESERVA o valor vigente --
    # se estava pausando os sensores que forkam (crit), continua pausando;
    # nao assume folga so porque parou de medir.
    return 0
  fi
  if [ "$WC_PIDS_LEVEL" = "3" ]; then
    # D6: recupera para o nivel que estava vigente ANTES do erro, nao para 0
    # -- forcar 0 faz o proximo calculo comparar contra "ok" e reanunciar o
    # mesmo degrau que ja tinha sido avisado antes da fonte sumir.
    WC_PIDS_LEVEL=$WC_PIDS_PRE_ERR_LEVEL
    printf 'active file=%s limit=%s\n' "$WC_PIDS_FILE" "$WC_PIDS_LIMIT" > "$WC_PIDS_STATE_FILE"
  fi
  wc_pids_level_calc
  if [ "$WC_PIDS_NEWLEVEL" -gt "$WC_PIDS_LEVEL" ]; then
    case "$WC_PIDS_NEWLEVEL" in
      1) wc_pids_append "$WC_PIDS_CUR" "$WC_PIDS_LIMIT" warn ;;
      2) wc_pids_append "$WC_PIDS_CUR" "$WC_PIDS_LIMIT" crit ;;
    esac
  fi
  WC_PIDS_LEVEL=$WC_PIDS_NEWLEVEL
  if [ "$WC_PIDS_LEVEL" = "2" ]; then WC_PIDS_SKIP_FORKS=1; else WC_PIDS_SKIP_FORKS=0; fi
}

# wc_daemon_sleep_init (arranque; pode forkar uma vez: mkfifo) e
# wc_daemon_sleep <segundos> (caminho quente; SO builtin `read -t`) --
# dormem sem fork, substituindo o `sleep` externo do laco do daemon (que
# no incidente teria matado o proprio daemon no degrau em que ele mais e
# preciso).
wc_daemon_sleep_init() {
  local state fifo
  state="$(wc_state_dir)"
  wc_init_state
  fifo="$state/sleep.fifo"
  WC_SLEEP_FIFO_OK=1
  WC_SLEEP_STATE_FILE="$state/sleep_sensor"
  # D1 (CRITICO): mkfifo/exec sem checar erro faziam o read -u 9 seguinte
  # falhar toda vez sem abrir fd nenhum -- "return 0" escondia o erro e o
  # laco girava livre (1039 voltas em ~2s medidas pelo revisor, reproduzindo
  # a tempestade de forks que o sensor existe para prevenir). Agora: se o
  # fifo nao existir/nao puder ser criado, ou o exec falhar, cai para
  # sleep externo (1 fork por ciclo, seguro) em vez de rotacao livre.
  if [ ! -p "$fifo" ] && ! mkfifo "$fifo" 2>/dev/null; then
    WC_SLEEP_FIFO_OK=0
  fi
  if [ "$WC_SLEEP_FIFO_OK" = "1" ] && ! exec 9<>"$fifo" 2>/dev/null; then
    WC_SLEEP_FIFO_OK=0
  fi
  if [ "$WC_SLEEP_FIFO_OK" = "1" ]; then
    printf 'fifo ok file=%s\n' "$fifo" > "$WC_SLEEP_STATE_FILE"
  else
    printf 'fallback sleep externo (fifo indisponivel: %s)\n' "$fifo" > "$WC_SLEEP_STATE_FILE"
  fi
}

wc_daemon_sleep() {
  if [ "${WC_SLEEP_FIFO_OK:-0}" = "1" ]; then
    read -t "$1" -u 9 _ 2>/dev/null
  else
    sleep "$1"
  fi
  return 0
}

# --- Guarda de rotacao (D0-a): a propria skill nao pode matar a maquina. O fallback de wc_daemon_sleep (sleep externo,
# D1) resolve o caso "fifo indisponivel por permissao", mas se a maquina ja
# estiver SEM fork nenhum sobrando, o `sleep` externo TAMBEM falha ao forkar
# e o laco volta a girar livre pelo MESMO caminho -- e exatamente o defeito
# que o fallback deveria consertar, um degrau adiante. Este guarda mede o
# tempo decorrido de cada volta com $EPOCHSECONDS (builtin, sem `date`) e,
# se voltas sucessivas terminarem bem mais rapido que o intervalo pedido,
# encerra o daemon: parar de vigiar (o `off` ja e um custo aceito) e seguro;
# continuar girando sem dormir derruba a maquina do usuario, que e o cenario
# que este sensor inteiro existe para evitar.
WC_SPIN_THRESHOLD=3

# wc_spin_guard_init: roda 1 vez no arranque do daemon.
wc_spin_guard_init() {
  WC_SPIN_COUNT=0
  WC_SPIN_STATE_FILE="$(wc_state_dir)/spin_guard"
}

# wc_spin_guard_tick <elapsed> <expected>: caminho quente, SO builtins
# (nenhuma parte deste guarda pode forkar -- e o guarda que roda quando a
# maquina pode ja estar sem fork nenhum sobrando). Atualiza o contador de
# voltas rapidas consecutivas; retorna 1 (e grava o motivo no estado) quando
# o limiar e alcancado -- o chamador (o laco do daemon) tem de parar nesse
# caso. Limiar de 3 voltas consecutivas, nao 1: absorve jitter legitimo
# (ajuste de relogio, EINTR pontual em `read -t`) sem falso positivo, e
# ainda assim para quase instantaneamente quando o problema e sistematico
# (uma rotacao livre de verdade produz voltas de poucos milissegundos, 3
# delas se acumulam bem abaixo de 1 segundo).
wc_spin_guard_tick() {
  local elapsed="$1" expected="$2" min_ok
  (( min_ok = expected / 2 ))
  if (( elapsed < min_ok )); then
    (( WC_SPIN_COUNT += 1 ))
  else
    WC_SPIN_COUNT=0
  fi
  if (( WC_SPIN_COUNT >= WC_SPIN_THRESHOLD )); then
    printf 'stopped rotacao livre detectada: %d voltas consecutivas com intervalo decorrido menor que %ds (pedido %ds) -- daemon encerrado (parar de vigiar e seguro, girar sem dormir nao e)\n' \
      "$WC_SPIN_COUNT" "$min_ok" "$expected" > "$WC_SPIN_STATE_FILE"
    return 1
  fi
  return 0
}

wc_pin_file() { printf '%s\n' "$(wc_state_dir)/pinned"; }
wc_is_pinned() { [ -f "$(wc_pin_file)" ]; }
wc_should_stop_daemon() {
  # <count> -> exit 0 se deve parar (ninguem usando E nao pinado)
  [ "$1" = "0" ] && ! wc_is_pinned
}
