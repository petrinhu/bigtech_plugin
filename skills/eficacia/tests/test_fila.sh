#!/usr/bin/env bash
# Testes da fila das perguntas barradas, do registrar, do acordar que move, e do hook Stop.
# Tudo num HOME temporario: nunca toca o HOME real.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$DIR/bin/hook_lider_dormindo.sh"
STOP="$DIR/bin/hook_fim_turno.sh"
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
ST="$XDG_STATE_HOME/bigtech-eficacia"
SESS="$HOME/.claude/sessions"
mkdir -p "$SESS" "$SANDBOX/work/alfa"

# Sessao viva de exemplo (pid do proprio teste), para casar por sessionId e por cwd.
printf '{"pid":%s,"sessionId":"sid-alfa","name":"alfa","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$SANDBOX/work/alfa" > "$SESS/alfa.json"

EVT='{"hook_event_name":"PreToolUse","session_id":"sid-alfa","cwd":"'"$SANDBOX/work/alfa"'","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"Trocar o banco agora?","header":"Banco","options":[{"label":"Sim","description":"migra hoje"},{"label":"Nao","description":"segue"}],"multiSelect":false}]}}'
FLAG="$ST/lider_dormindo"
FILA="$ST/fila.md"

echo "== hook com bandeira: nega, grava na fila com nome da sessao"
bash "$VIGIA" dormir >/dev/null
out="$(printf '%s' "$EVT" | bash "$HOOK")"; rc=$?
assert_eq "$rc" "0" "hook com bandeira: exit 0"
assert_has "$out" '"permissionDecision":"deny"' "hook com bandeira: nega"
assert_has "$out" "vigia.sh registrar" "motivo cita registrar"
assert_has "$out" "ja esta na fila" "motivo diz que decisao do lider ja esta na fila"
if [ -f "$FILA" ]; then pass "fila.md criada"; else fail "fila.md nao criada"; fi
fila="$(cat "$FILA" 2>/dev/null)"
assert_has "$fila" "Trocar o banco agora?" "fila tem a pergunta"
assert_has "$fila" "Sim" "fila tem a opcao Sim"
assert_has "$fila" "migra hoje" "fila tem a descricao da opcao"
assert_has "$fila" "alfa" "fila tem o nome da sessao (casado pelo session_id)"

echo "== concorrencia: dois escritores ao mesmo tempo"
EVT2='{"hook_event_name":"PreToolUse","session_id":"sid-zeta","cwd":"/x","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"PERGUNTA-ZETA","options":[{"label":"A"}]}]}}'
EVT3='{"hook_event_name":"PreToolUse","session_id":"sid-beta","cwd":"/y","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"PERGUNTA-BETA","options":[{"label":"B"}]}]}}'
for _ in 1 2 3 4 5 6; do
  printf '%s' "$EVT2" | bash "$HOOK" >/dev/null &
  printf '%s' "$EVT3" | bash "$HOOK" >/dev/null &
done
wait
assert_eq "$(grep -c 'PERGUNTA-ZETA' "$FILA")" "6" "6 perguntas zeta gravadas sem perda"
assert_eq "$(grep -c 'PERGUNTA-BETA' "$FILA")" "6" "6 perguntas beta gravadas sem perda"
assert_eq "$(grep -c '^## ' "$FILA")" "13" "13 blocos (1 + 12), nenhum intercalado"

echo "== registrar: decisao do C-level com hora e sessao (cwd)"
( cd "$SANDBOX/work/alfa" && bash "$VIGIA" registrar "Escolhi o indice B, ratificar" >/dev/null )
DEC="$ST/decisoes_clevel.md"
if [ -f "$DEC" ]; then pass "decisoes_clevel.md criado"; else fail "decisoes_clevel.md nao criado"; fi
assert_has "$(cat "$DEC" 2>/dev/null)" "Escolhi o indice B, ratificar" "registrar grava o texto"
assert_has "$(cat "$DEC" 2>/dev/null)" "alfa" "registrar grava a sessao casada pelo cwd"

echo "== acordar: imprime e move (nao apaga)"
out="$(bash "$VIGIA" acordar 2>&1)"
if [ ! -e "$FLAG" ]; then pass "acordar apaga a bandeira"; else fail "acordar nao apagou a bandeira"; fi
assert_has "$out" "Trocar o banco agora?" "acordar imprime a fila"
assert_has "$out" "Escolhi o indice B" "acordar imprime as decisoes"
if [ ! -e "$FILA" ]; then pass "fila saiu da raiz"; else fail "fila ficou na raiz"; fi
arq="$(find "$ST/arquivo" -name fila.md 2>/dev/null | head -n1)"
if [ -n "$arq" ]; then pass "fila movida para arquivo/<data-hora>/"; else fail "fila nao foi movida para arquivo/"; fi
assert_has "$(cat "$arq" 2>/dev/null)" "Trocar o banco agora?" "conteudo movido integro"
assert_has "$(cat "$(dirname "$arq")/decisoes_clevel.md" 2>/dev/null)" "Escolhi o indice B" "decisoes movidas junto"

echo "== hook Stop: silencio sem bandeira"
out="$(printf '{"hook_event_name":"Stop","stop_hook_active":false}' | bash "$STOP")"; rc=$?
assert_eq "$rc" "0" "Stop sem bandeira: exit 0"
assert_eq "$out" "" "Stop sem bandeira: silencio"

echo "== hook Stop: bloqueia uma vez com a bandeira"
bash "$VIGIA" dormir >/dev/null
out="$(printf '{"hook_event_name":"Stop","stop_hook_active":false}' | bash "$STOP")"; rc=$?
assert_eq "$rc" "0" "Stop com bandeira: exit 0"
assert_has "$out" '"decision":"block"' "Stop com bandeira e active false: bloqueia"
assert_has "$out" "nao pare esperando o lider" "Stop: motivo presente"
if printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["decision"]=="block" and d["reason"]' 2>/dev/null; then
  pass "Stop: saida e JSON valido com decision e reason"
else
  fail "Stop: saida nao e JSON valido"
fi
echo "== hook Stop: libera com stop_hook_active verdadeiro (sem laco)"
out="$(printf '{"hook_event_name":"Stop","stop_hook_active":true}' | bash "$STOP")"; rc=$?
assert_eq "$rc" "0" "Stop com active true: exit 0"
assert_eq "$out" "" "Stop com active true: silencio, deixa parar"

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
