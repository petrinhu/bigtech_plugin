#!/usr/bin/env bash
# Controlador fino da skill manter_ligado.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"
ml_require_linux_systemd || exit $?

UNIT="manter-ligado-guardian"

ml_guardian_active() { systemctl --user is-active --quiet "$UNIT.service"; }

ml_guardian_start() {
  ml_guardian_active && return 0
  systemd-run --user --unit="$UNIT" --collect \
    --setenv=MANTER_WARN_PCT="${MANTER_WARN_PCT:-20}" \
    --setenv=MANTER_SAVE_PCT="${MANTER_SAVE_PCT:-5}" \
    --setenv=MANTER_INTERVAL="${MANTER_INTERVAL:-60}" \
    --setenv=MEMO_HEADLESS="${MEMO_HEADLESS:-0}" \
    systemd-inhibit --what=sleep:handle-lid-switch \
      --who="manter_ligado" --why="transito com tampa fechada" --mode=block \
      "$DIR/guardiao.sh"
}

ml_guardian_stop() {
  ml_guardian_active && systemctl --user stop "$UNIT.service" >/dev/null 2>&1 || true
  rm -f "$(ml_state_dir)/guardian.armed"
}

_sid() { printf '%s\n' "${CLAUDE_CODE_SESSION_ID:-desconhecida}"; }
_slug() { printf '%s\n' "$PWD" | sed 's#/#-#g; s#_#-#g'; }

cmd_on() {
  ml_init_state; ml_reap
  local sid; sid="$(_sid)"
  ml_register_session "$sid" "$(_slug)" "$(ml_resolve_transcript "$sid" || true)"
  ml_guardian_start
  printf 'armado (sessoes: %s)\n' "$(ml_count)"
}

cmd_off() {
  ml_unregister_session "$(_sid)"; ml_reap
  if [ "$(ml_count)" = "0" ]; then ml_guardian_stop; printf 'desarmado (guardiao derrubado)\n';
  else printf 'saiu; ainda armado por %s sessao(oes)\n' "$(ml_count)"; fi
}

cmd_status() {
  ml_reap
  if ml_guardian_active; then printf 'ARMADO por %s sessao(oes)\n' "$(ml_count)";
  else printf 'desarmado\n'; fi
}

cmd_limpar() {
  ml_guardian_stop
  rm -rf "$(ml_snap_dir)" "$(ml_sessions_dir)"
  printf 'faxina concluida: snapshots e registro zerados\n'
}

case "${1:-status}" in
  on) cmd_on ;; off) cmd_off ;; status) cmd_status ;; limpar) cmd_limpar ;;
  *) printf 'uso: manter_ligado.sh {on|off|status|limpar}\n' >&2; exit 2 ;;
esac
