#!/usr/bin/env bash
# Testes de seguranca da skill eficacia: sanitizador unico (controles C1 e bidi)
# e git endurecido nas leituras de repo de terceiro. HOME temporario.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
VIGIA="$DIR/bin/vigia.sh"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
# has_bytes <rotulo> <texto-com-bytes> <padrao-bytes>: falha se o padrao aparecer.
nao_tem() { if printf '%s' "$2" | LC_ALL=C grep -q -- "$3"; then fail "$1"; else pass "$1"; fi; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
export XDG_STATE_HOME="$SANDBOX/state"
export XDG_CONFIG_HOME="$SANDBOX/conf"
ST="$XDG_STATE_HOME/bigtech-eficacia"
SESS="$HOME/.claude/sessions"
mkdir -p "$SESS" "$SANDBOX/work/alfa"
REALGIT="$(command -v git)"

# Sessao "alfa" com cwd num repo com um commit.
printf '{"pid":%s,"sessionId":"sid-alfa","name":"alfa","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$SANDBOX/work/alfa" > "$SESS/alfa.json"
( cd "$SANDBOX/work/alfa" && "$REALGIT" init -q && "$REALGIT" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "feat: x" )

# Stub do git: registra os argumentos e repassa ao git real.
mkdir -p "$SANDBOX/bin"
cat > "$SANDBOX/bin/git" <<STUB
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "$SANDBOX/git_args.log"
exec "$REALGIT" "\$@"
STUB
chmod +x "$SANDBOX/bin/git"

C1=$'\xc2\x9b'        # U+009B, CSI de 8 bits (categoria Cc)
BIDI=$'\xe2\x80\xae'  # U+202E, override bidi (categoria Cf)
ESC=$'\e'
BEL=$'\a'

echo "== 1. registrar: controle C1 e bidi nao entram no arquivo"
bash "$VIGIA" registrar "ok${C1}x${BIDI}y${ESC}[2J" >/dev/null 2>&1
dec="$(cat "$ST/decisoes_clevel.md" 2>/dev/null)"
nao_tem "registrar: sem C1 (U+009B)" "$dec" "$C1"
nao_tem "registrar: sem bidi (U+202E)" "$dec" "$BIDI"
nao_tem "registrar: sem ESC" "$dec" "$ESC"

echo "== 2. acordar: nada de controle sai na tela"
bash "$VIGIA" dormir >/dev/null
printf '%s' '{"hook_event_name":"PreToolUse","session_id":"sid-alfa","cwd":"x","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"a\u009b2J‮b\u001b]0;x\u0007","options":[{"label":"Sim"}]}]}}' | bash "$DIR/bin/hook_lider_dormindo.sh" >/dev/null
out="$(bash "$VIGIA" acordar 2>&1)"
nao_tem "acordar: sem C1 (U+009B)" "$out" "$C1"
nao_tem "acordar: sem bidi (U+202E)" "$out" "$BIDI"
nao_tem "acordar: sem ESC" "$out" "$ESC"
nao_tem "acordar: sem BEL" "$out" "$BEL"

echo "== 3. status: git endurecido (flags e checagem de dono)"
PATH="$SANDBOX/bin:$PATH" bash "$VIGIA" status >/dev/null 2>&1
args="$(cat "$SANDBOX/git_args.log" 2>/dev/null)"
case "$args" in *core.fsmonitor=*) pass "git: core.fsmonitor desligado";; *) fail "git: sem core.fsmonitor= (args: $args)";; esac
case "$args" in *core.hooksPath=/dev/null*) pass "git: hooksPath em /dev/null";; *) fail "git: sem core.hooksPath";; esac
case "$args" in *gpg.program=true*) pass "git: gpg.program neutralizado";; *) fail "git: sem gpg.program";; esac
case "$args" in *--no-show-signature*) pass "git: sem verificacao de assinatura";; *) fail "git: sem --no-show-signature";; esac

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
