#!/usr/bin/env bash
# Testes do hook lider_dormindo e de dormir/acordar do vigia. HOME temporario.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$DIR/bin/hook_lider_dormindo.sh"
VIGIA="$DIR/bin/vigia.sh"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi; }
assert_has() { if printf '%s' "$1" | grep -qF -- "$2"; then pass "$3"; else fail "$3 (sem '$2')"; fi; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
export XDG_STATE_HOME="$SANDBOX/state"
FLAG="$XDG_STATE_HOME/bigtech-eficacia/lider_dormindo"

# Entrada de exemplo no formato de evento PreToolUse.
EVT='{"hook_event_name":"PreToolUse","tool_name":"AskUserQuestion","tool_input":{"questions":[]}}'

echo "== hook sem bandeira: silencio e saida 0"
out="$(printf '%s' "$EVT" | bash "$HOOK")"; rc=$?
assert_eq "$rc" "0" "sem bandeira: exit 0"
assert_eq "$out" "" "sem bandeira: nenhuma saida"

echo "== dormir cria a bandeira; hook nega"
bash "$VIGIA" dormir >/dev/null
if [ -e "$FLAG" ]; then pass "dormir cria a bandeira"; else fail "dormir nao criou a bandeira"; fi
out="$(printf '%s' "$EVT" | bash "$HOOK")"; rc=$?
assert_eq "$rc" "0" "com bandeira: exit 0 (a negacao vai no JSON)"
assert_has "$out" '"permissionDecision":"deny"' "com bandeira: nega"
assert_has "$out" '"hookEventName":"PreToolUse"' "com bandeira: evento PreToolUse"
assert_has "$out" "lider dormindo" "com bandeira: motivo presente"
if printf '%s' "$out" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
  pass "saida com bandeira e JSON valido"
else
  fail "saida com bandeira nao e JSON valido"
fi

echo "== acordar apaga a bandeira; hook volta ao silencio"
bash "$VIGIA" acordar >/dev/null
if [ ! -e "$FLAG" ]; then pass "acordar apaga a bandeira"; else fail "acordar nao apagou a bandeira"; fi
out="$(printf '%s' "$EVT" | bash "$HOOK")"; rc=$?
assert_eq "$rc" "0" "sem bandeira de novo: exit 0"
assert_eq "$out" "" "sem bandeira de novo: silencio"

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
