#!/usr/bin/env bash
# Controlador da skill watchcode.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

UNIT="watchcode-daemon"

wc_daemon_active() { systemctl --user is-active --quiet "$UNIT.service"; }

wc_daemon_start() {
  wc_daemon_active && return 0
  systemd-run --user --unit="$UNIT" --collect \
    --setenv=WATCHCODE_STATE_DIR="$(wc_state_dir)" \
    --setenv=WATCHCODE_BASELINE_FILE="$(wc_baseline_path)" \
    --setenv=WATCHCODE_INTERVAL="${WATCHCODE_INTERVAL:-120}" \
    "$DIR/watchcode_daemon.sh"
}

wc_daemon_stop() {
  wc_daemon_active && systemctl --user stop "$UNIT.service" >/dev/null 2>&1 || true
  rm -f "$(wc_state_dir)/daemon.armed"
}

_sid() { printf '%s\n' "${CLAUDE_CODE_SESSION_ID:-desconhecida}"; }
_scope() { printf '%s\n' "${WATCHCODE_SCOPE:-$PWD}"; }

cmd_on() {
  wc_init_state; wc_reap
  local adotou=nao
  wc_daemon_active && [ "$(wc_count)" = "0" ] && ! wc_is_pinned && adotou=sim
  wc_register_session "$(_sid)" "$(_scope)"
  wc_daemon_start
  if [ "$adotou" = "sim" ]; then
    printf 'vigiando (ADOTOU daemon orfao; scope=%s; sessoes: %s)\n' "$(_scope)" "$(wc_count)"
  else
    printf 'vigiando (scope=%s; sessoes: %s)\n' "$(_scope)" "$(wc_count)"
  fi
}

cmd_off() {
  wc_unregister_session "$(_sid)"; wc_reap
  if wc_should_stop_daemon "$(wc_count)"; then
    wc_daemon_stop
    printf 'encerrado (daemon derrubado)\n'
  elif [ "$(wc_count)" = "0" ]; then
    printf 'saiu; daemon PINADO segue vigiando\n'
  else
    printf 'saiu; ainda vigiando por %s sessao(oes)\n' "$(wc_count)"
  fi
}

cmd_pin() {
  wc_init_state; wc_daemon_start
  : > "$(wc_pin_file)"
  printf 'PINADO (daemon segue vivo mesmo sem sessoes; /bigtech:watchcode unpin para liberar)\n'
}

cmd_unpin() {
  rm -f "$(wc_pin_file)"; wc_reap
  if [ "$(wc_count)" = "0" ]; then
    wc_daemon_stop
    printf 'liberado (unpin); daemon derrubado (ninguem usando)\n'
  else
    printf 'liberado (unpin); ainda vigiando por %s sessao(oes)\n' "$(wc_count)"
  fi
}

cmd_status() {
  wc_reap
  local nf=0; [ -f "$(wc_findings_file)" ] && nf="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
  local pin=""; wc_is_pinned && pin=" [PINADO]"
  if wc_daemon_active; then
    printf 'VIGIANDO por %s sessao(oes); %s achado(s) acumulado(s)%s\n' "$(wc_count)" "$nf" "$pin"
  else
    printf 'parado%s\n' "$pin"
  fi
}

case "${1:-status}" in
  on) cmd_on ;; off) cmd_off ;; status) cmd_status ;;
  pin) cmd_pin ;; unpin) cmd_unpin ;;
  *) printf 'uso: watchcode.sh {on|off|status|pin|unpin}\n' >&2; exit 2 ;;
esac
