#!/usr/bin/env bash
# Testes do timer em pasta fixa: instalar copia o vigia para ${XDG_DATA_HOME}/bigtech-eficacia,
# grava VERSAO, aponta o service para a copia; status/check avisam copia velha; remover mostra
# e apaga. HOME falso e systemctl stubado: o timer real nunca e tocado.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
VIGIA="$DIR/bin/vigia.sh"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
assert_has() { if printf '%s' "$1" | grep -qF -- "$2"; then pass "$3"; else fail "$3 (sem '$2')"; fi; }
assert_not() { if printf '%s' "$1" | grep -qF -- "$2"; then fail "$3 (nao devia ter '$2')"; else pass "$3"; fi; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
export XDG_DATA_HOME="$SANDBOX/data"
export XDG_CONFIG_HOME="$SANDBOX/conf"
export XDG_STATE_HOME="$SANDBOX/state"
mkdir -p "$HOME" "$SANDBOX/bin"
DATA="$XDG_DATA_HOME/bigtech-eficacia"
UNIT="$XDG_CONFIG_HOME/systemd/user"
VER="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["version"])' "$DIR/../../.claude-plugin/plugin.json")"

# systemctl stub: registra os argumentos, nunca toca o timer real.
printf '#!/usr/bin/env bash\necho "$*" >> "%s/systemctl.log"\n' "$SANDBOX" > "$SANDBOX/bin/systemctl"
chmod +x "$SANDBOX/bin/systemctl"
export PATH="$SANDBOX/bin:$PATH"

echo "== 1. instalar copia para a pasta fixa"
bash "$VIGIA" instalar --intervalo 5 >/dev/null 2>&1
if [ -x "$DATA/vigia.sh" ]; then pass "copia do vigia.sh na pasta fixa"; else fail "vigia.sh nao copiado para $DATA"; fi
if [ -f "$DATA/limpa_texto.py" ]; then pass "copia do limpa_texto.py na pasta fixa"; else fail "limpa_texto.py nao copiado"; fi
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi; }
assert_eq "$(stat -c %a "$DATA" 2>/dev/null)" "700" "pasta fixa com modo 700"
assert_eq "$(cat "$DATA/VERSAO" 2>/dev/null)" "$VER" "VERSAO grava a versao do plugin.json"

echo "== 2. o service aponta para a copia, nao para o plugin"
svc="$(cat "$UNIT/bigtech-eficacia.service" 2>/dev/null)"
assert_has "$svc" "$DATA/vigia.sh" "ExecStart aponta para a copia fixa"
assert_not "$svc" "/skills/eficacia/bin/vigia.sh" "ExecStart nao aponta para a pasta do plugin"

echo "== 3. a copia roda sozinha"
out="$(bash "$DATA/vigia.sh" check --dry-run 2>&1)"; rc=$?
assert_eq "$rc" "0" "copia: check --dry-run sai 0"

echo "== 4. status avisa copia velha (rodado do plugin)"
printf '0.0.1\n' > "$DATA/VERSAO"
out="$(bash "$VIGIA" status 2>&1)"
assert_has "$out" "timer com copia da versao 0.0.1; rode vigia.sh instalar para atualizar" "status avisa a copia velha"
echo "== 5. a copia no timer nao avisa (nao sabe a versao do plugin)"
out="$(bash "$DATA/vigia.sh" check --dry-run 2>&1)"
assert_not "$out" "timer com copia" "copia nao avisa"

echo "== 6. remover mostra e apaga"
printf '%s\n' "$VER" > "$DATA/VERSAO"
out="$(bash "$VIGIA" remover 2>&1)"
assert_has "$out" "$DATA/vigia.sh" "remover mostra a copia que apaga"
if [ ! -e "$DATA/vigia.sh" ]; then pass "remover apaga a copia"; else fail "remover nao apagou a copia"; fi
if [ ! -e "$UNIT/bigtech-eficacia.service" ]; then pass "remover apaga o service"; else fail "service ficou"; fi
if [ ! -e "$UNIT/bigtech-eficacia.timer" ]; then pass "remover apaga o timer"; else fail "timer ficou"; fi

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
