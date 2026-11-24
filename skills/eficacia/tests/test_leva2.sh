#!/usr/bin/env bash
# Testes da segunda leva da eficacia: permissao, desvios da noite, bandeira automatica,
# tokens e entregas, acordar agrupado, e sanitizacao de controle (escape de terminal).
# Tudo num HOME temporario; loginctl e git sao stubs/locais ao sandbox.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PERM="$DIR/bin/hook_permissao.sh"
STOP="$DIR/bin/hook_fim_turno.sh"
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
export XDG_CONFIG_HOME="$SANDBOX/conf"
export USER=tester
unset XDG_SESSION_ID
ST="$XDG_STATE_HOME/bigtech-eficacia"
SESS="$HOME/.claude/sessions"
PROJ="$HOME/.claude/projects"
mkdir -p "$SESS" "$PROJ" "$SANDBOX/work/alfa" "$SANDBOX/bin"
NOW_MS=$(( EPOCHSECONDS * 1000 ))

# Notificacao stubada: grava em avisos.txt.
cat > "$SANDBOX/notify.sh" <<STUB
#!/usr/bin/env bash
printf '%s\n' "\$1" >> "$SANDBOX/avisos.txt"
STUB
chmod +x "$SANDBOX/notify.sh"
export EFICACIA_NOTIFY_CMD="$SANDBOX/notify.sh"

# loginctl stub: LOCKED (yes|no) vem do ambiente.
cat > "$SANDBOX/bin/loginctl" <<'STUB'
#!/usr/bin/env bash
case "$1" in
  list-sessions) echo "c1 1000 tester seat0" ;;
  show-session) echo "LockedHint=${LOCKED:-no}"; echo "IdleHint=no" ;;
esac
STUB
chmod +x "$SANDBOX/bin/loginctl"

# Sessao viva "alfa" (pid do teste), cwd do sandbox, waiting antigo (vira desvio ESPERANDO).
printf '{"pid":%s,"sessionId":"sid-alfa","name":"alfa","cwd":"%s","status":"waiting","statusUpdatedAt":%s,"updatedAt":%s}\n' \
  "$$" "$SANDBOX/work/alfa" $(( NOW_MS - 20*60*1000 )) "$NOW_MS" > "$SESS/alfa.json"

echo "== 1. PermissionRequest: com bandeira nega, grava na fila, sem bandeira fica calado"
EVT_P='{"hook_event_name":"PermissionRequest","session_id":"sid-alfa","cwd":"'"$SANDBOX/work/alfa"'","tool_name":"Bash","tool_input":{"command":"rm -rf pasta_x"}}'
out="$(printf '%s' "$EVT_P" | bash "$PERM")"; rc=$?
assert_eq "$rc" "0" "sem bandeira: exit 0"
assert_eq "$out" "" "sem bandeira: silencio (fluxo normal)"
bash "$VIGIA" dormir >/dev/null
out="$(printf '%s' "$EVT_P" | bash "$PERM")"; rc=$?
assert_eq "$rc" "0" "com bandeira: exit 0"
assert_has "$out" '"hookEventName":"PermissionRequest"' "com bandeira: evento PermissionRequest"
assert_has "$out" '"behavior":"deny"' "com bandeira: nega"
assert_has "$out" "troque de trabalho" "com bandeira: manda trocar de trabalho"
assert_has "$(cat "$ST/fila.md" 2>/dev/null)" "PERMISSAO: Bash rm -rf pasta_x" "fila recebe 'permissao: ferramenta resumo'"

echo "== 2. check com bandeira: nao avisa o celular, grava desvios da noite"
rm -f "$SANDBOX/avisos.txt"
bash "$VIGIA" check >/dev/null 2>&1
if [ ! -e "$SANDBOX/avisos.txt" ]; then pass "check com bandeira nao avisa o celular"; else fail "check com bandeira avisou o celular"; fi
assert_has "$(cat "$ST/desvios_noite.md" 2>/dev/null)" "ESPERANDO" "desvio gravado em desvios_noite.md"

echo "== 3. Stop com bandeira: motivo pede o proximo item do TODO.md"
out="$(printf '{"hook_event_name":"Stop","stop_hook_active":false}' | bash "$STOP")"
assert_has "$out" "item sem dependencia no TODO.md" "Stop: motivo cita o TODO.md"

echo "== 4. bandeira automatica por tela bloqueada"
rm -f "$ST/lider_dormindo"
mkdir -p "$ST"; printf '%s\n' $(( EPOCHSECONDS - 40*60 )) > "$ST/lock_desde"
PATH="$SANDBOX/bin:$PATH" LOCKED=yes bash "$VIGIA" check >/dev/null 2>&1
if [ -e "$ST/lider_dormindo" ]; then pass "tela bloqueada ha 40 min cria a bandeira"; else fail "tela bloqueada 40 min nao criou bandeira"; fi
assert_eq "$(cat "$ST/lider_dormindo" 2>/dev/null)" "automatica" "bandeira automatica e marcada"
PATH="$SANDBOX/bin:$PATH" LOCKED=no bash "$VIGIA" check >/dev/null 2>&1
if [ ! -e "$ST/lider_dormindo" ]; then pass "desbloqueio apaga a bandeira automatica"; else fail "desbloqueio nao apagou a automatica"; fi
echo "== 4b. bandeira manual nunca e apagada sozinha"
bash "$VIGIA" dormir >/dev/null
printf '%s\n' $(( EPOCHSECONDS - 40*60 )) > "$ST/lock_desde"
PATH="$SANDBOX/bin:$PATH" LOCKED=no bash "$VIGIA" check >/dev/null 2>&1
if [ -e "$ST/lider_dormindo" ]; then pass "bandeira manual sobrevive ao desbloqueio"; else fail "bandeira manual foi apagada sozinha"; fi
bash "$VIGIA" acordar >/dev/null 2>&1
echo "== 4c. bandeira_auto_min 0 desliga"
mkdir -p "$XDG_CONFIG_HOME/bigtech"; printf '{"bandeira_auto_min":0}\n' > "$XDG_CONFIG_HOME/bigtech/eficacia.json"
printf '%s\n' $(( EPOCHSECONDS - 40*60 )) > "$ST/lock_desde"
PATH="$SANDBOX/bin:$PATH" LOCKED=yes bash "$VIGIA" check >/dev/null 2>&1
if [ ! -e "$ST/lider_dormindo" ]; then pass "com 0 a bandeira automatica fica desligada"; else fail "com 0 a bandeira foi criada"; fi
rm -f "$XDG_CONFIG_HOME/bigtech/eficacia.json"

echo "== 5. status: tokens, entregas e tokens por entrega"
mkdir -p "$PROJ/$(printf '%s' "$SANDBOX/work/alfa" | sed 's/[^A-Za-z0-9]/-/g')"
printf '%s\n' '{"message":{"usage":{"input_tokens":100,"output_tokens":50,"cache_creation_input_tokens":10,"cache_read_input_tokens":40}}}' \
  > "$PROJ/$(printf '%s' "$SANDBOX/work/alfa" | sed 's/[^A-Za-z0-9]/-/g')/t.jsonl"
( cd "$SANDBOX/work/alfa" && git init -q && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m "feat: x" )
out="$(bash "$VIGIA" status 2>&1)"
assert_has "$out" "tokens" "status tem coluna de tokens"
assert_has "$out" "alfa" "status lista alfa"
assert_has "$out" "200" "status soma input+output+cache (100+50+10+40)"

echo "== 6. acordar: agrupa por sessao, imprime desvios e arquiva"
# Os passos 4 desligaram a bandeira e arquivaram a fila; recria fila e um desvio novo.
bash "$VIGIA" dormir >/dev/null
printf '%s' "$EVT_P" | bash "$PERM" >/dev/null
rm -f "$ST/desvios.txt"
bash "$VIGIA" check >/dev/null 2>&1
bash "$VIGIA" registrar "Escolhi o indice B" >/dev/null 2>&1 || true
out="$(bash "$VIGIA" acordar 2>&1)"
assert_has "$out" "== sessao: alfa ==" "acordar agrupa por sessao"
assert_has "$out" "PERMISSAO: Bash rm -rf pasta_x" "acordar imprime a permissao barrada"
assert_has "$out" "ESPERANDO" "acordar imprime os desvios da noite"
arq="$(find "$ST/arquivo" -name desvios_noite.md 2>/dev/null | head -n1)"
if [ -n "$arq" ]; then pass "desvios_noite.md arquivado junto com a fila"; else fail "desvios_noite.md nao arquivado"; fi

echo "== 7. escape de terminal nao sai no acordar"
ESC=$'\e]0;x\a'
CLR=$'\e[2J'
bash "$VIGIA" dormir >/dev/null
EVT_Q='{"hook_event_name":"PreToolUse","session_id":"sid-alfa","cwd":"'"$SANDBOX/work/alfa"'","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"oi\u001b]0;x\u0007\u001b[2J","options":[{"label":"Sim"}]}]}}'
printf '%s' "$EVT_Q" | bash "$HOOK" >/dev/null
bash "$VIGIA" registrar "$ESC$CLR decisao" >/dev/null 2>&1 || true
out_raw="$(bash "$VIGIA" acordar 2>&1)"
if printf '%s' "$out_raw" | LC_ALL=C grep -q "$(printf '\033')"; then fail "acordar imprimiu ESC"; else pass "acordar nao imprime ESC (\\e)"; fi
if printf '%s' "$out_raw" | LC_ALL=C grep -q "$(printf '\007')"; then fail "acordar imprimiu BEL"; else pass "acordar nao imprime BEL (\\a)"; fi
if LC_ALL=C grep -rq "$(printf '\033')" "$ST/arquivo" 2>/dev/null; then fail "arquivo guardou ESC"; else pass "arquivo nao guarda ESC"; fi

echo "== 8. docs e declaracao"
assert_has "$(cat "$DIR/../../hooks/hooks.json")" "PermissionRequest" "hooks.json declara PermissionRequest"
assert_has "$(cat "$DIR/../../hooks/hooks.json")" "hook_permissao.sh" "hooks.json aponta hook_permissao.sh"
assert_has "$(cat "$DIR/SKILL.md")" "desempate barato" "SKILL classe 1 tem desempate barato"
assert_has "$(cat "$DIR/SKILL.md")" "SendMessage" "SKILL gerente manda resposta por SendMessage"
assert_has "$(cat "$DIR/SKILL.md")" "itens do TODO.md" "SKILL projeto: pre-voo marca os proximos itens"
assert_has "$(cat "$DIR/../olhe_agentes/SKILL.md")" "bigtech-eficacia.timer" "olhe_agentes checa o timer"
assert_has "$(cat "$DIR/../olhe_agentes/SKILL.md")" "/bigtech:eficacia gerente" "olhe_agentes sugere eficacia gerente"

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
