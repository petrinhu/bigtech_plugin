#!/usr/bin/env bash
# Testes dos campos do JSON de sessao: nome com tab, quebra de linha e injecao de
# aritmetica nunca executam comando nem injetam linha. HOME temporario.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
VIGIA="$DIR/bin/vigia.sh"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
export XDG_STATE_HOME="$SANDBOX/state"
export XDG_CONFIG_HOME="$SANDBOX/conf"
ST="$XDG_STATE_HOME/bigtech-eficacia"
SESS="$HOME/.claude/sessions"
mkdir -p "$SESS" "$SANDBOX/work/tab" "$SANDBOX/work/nl" "$SANDBOX/work/inj"
PWN="$SANDBOX/pwn_$$"

# s1: nome com TAB; s2: nome com injecao de aritmetica (sem tab); s3: nome com quebra de linha.
printf '{"pid":%s,"sessionId":"sid-tab","name":"x\\ty","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$SANDBOX/work/tab" > "$SESS/tab.json"
# shellcheck disable=SC2016  # $( e literal na fixture, de proposito
printf '{"pid":%s,"sessionId":"sid-inj","name":"a[$(touch %s)]","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$PWN" "$SANDBOX/work/inj" > "$SESS/inj.json"
printf '{"pid":%s,"sessionId":"sid-nl","name":"x\\nFAKE","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$SANDBOX/work/nl" > "$SESS/nl.json"
# Injecao pelo campo de tab: dois tabs empurram o valor para a coluna tin (aritmetica).
# HOME e variavel definida: o bash avalia a subscrito e executa o comando (set -u nao impede).
# shellcheck disable=SC2016  # $( e literal na fixture, de proposito
printf '{"pid":%s,"sessionId":"sid-tinj","name":"w\\tb\\tHOME[$(touch %s)]","cwd":"%s","status":"busy","statusUpdatedAt":0,"updatedAt":0}\n' \
  "$$" "$PWN.tab" "$SANDBOX/work/inj" > "$SESS/a_tinj.json"

echo "== 1. status: nome com tab e injecao nao executam comando"
bash "$VIGIA" status >/dev/null 2>&1
if [ -e "$PWN" ] || [ -e "$PWN.tab" ]; then fail "status executou comando injetado"; else pass "status nao executa comando injetado"; fi

echo "== 2. registrar: nome com quebra de linha nao injeta linha"
bash "$VIGIA" registrar "decisao unica" >/dev/null 2>&1
( cd "$SANDBOX/work/nl" && bash "$VIGIA" registrar "decisao nl" >/dev/null 2>&1 )
linhas="$(grep -c . "$ST/decisoes_clevel.md" 2>/dev/null || echo 0)"
if grep -q '^FAKE' "$ST/decisoes_clevel.md" 2>/dev/null; then fail "nome com \\n injetou linha FAKE"; else pass "nome com \\n nao injeta linha"; fi
if [ "$linhas" = 2 ]; then pass "duas decisoes, duas linhas (uma por registrar)"; else fail "esperadas 2 linhas, obtidas $linhas"; fi

echo "== 3. check: nomes malucos nao quebram a passada"
bash "$VIGIA" check --dry-run >/dev/null 2>&1; rc=$?
if [ "$rc" = 0 ]; then pass "check com nomes malucos sai 0"; else fail "check saiu $rc"; fi
if [ -e "$PWN" ]; then fail "check executou comando injetado"; else pass "check nao executa comando"; fi

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
