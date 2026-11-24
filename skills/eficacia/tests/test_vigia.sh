#!/usr/bin/env bash
# Testes do vigia.sh (skill eficacia). Tudo num HOME temporario: nunca toca o HOME real.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
VIGIA="$DIR/bin/vigia.sh"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi; }
assert_has() { if printf '%s' "$1" | grep -qF -- "$2"; then pass "$3"; else fail "$3 (sem '$2')"; fi; }
assert_not() { if printf '%s' "$1" | grep -qF -- "$2"; then fail "$3 (nao devia ter '$2')"; else pass "$3"; fi; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
export XDG_STATE_HOME="$SANDBOX/state"
export XDG_CONFIG_HOME="$SANDBOX/conf"
ST="$XDG_STATE_HOME/bigtech-eficacia"
SESS="$HOME/.claude/sessions"
PROJ="$HOME/.claude/projects"
mkdir -p "$SESS" "$PROJ"

# Stub do aviso: grava a mensagem num arquivo em vez de tocar o celular.
cat > "$SANDBOX/notify.sh" <<STUB
#!/usr/bin/env bash
printf '%s\n' "\$1" >> "$SANDBOX/avisos.txt"
STUB
chmod +x "$SANDBOX/notify.sh"
export EFICACIA_NOTIFY_CMD="$SANDBOX/notify.sh"

NOW_MS=$(( EPOCHSECONDS * 1000 ))
# mk_sess <arquivo> <pid> <nome> <status> <statusUpdatedAt_ms> <cwd>
mk_sess() {
  printf '{"pid":%s,"name":"%s","cwd":"%s","status":"%s","statusUpdatedAt":%s,"updatedAt":%s}\n' \
    "$2" "$3" "$6" "$4" "$5" "$NOW_MS" > "$SESS/$1.json"
}

PID_VIVO=$$          # o proprio teste: existe durante toda a rodada
PID_MORTO=99999999   # acima do pid_max (4194304): nunca existe

# Fixtures:
#  alfa : waiting ha 20 min (ESPERANDO), updatedAt fresco (nao pode contar como batimento)
#  beta : busy agora, sem transcript (OCUPADA)
#  gama : esperada, pid morto (MORTA, so com config)
#  delta: busy, arquivo de parada (PARADA, nunca desvio)
#  eps  : busy, transcript velho de 40 min (TRAVADA)
mk_sess alfa  "$PID_VIVO" alfa  waiting $(( NOW_MS - 20*60*1000 )) "$SANDBOX/work/alfa"
mk_sess beta  "$PID_VIVO" beta  busy    "$NOW_MS" "$SANDBOX/work/beta"
mk_sess gama  "$PID_MORTO" gama busy    "$NOW_MS" "$SANDBOX/work/gama"
mk_sess delta "$PID_VIVO" delta busy    "$NOW_MS" "$SANDBOX/work/delta"
mk_sess eps   "$PID_VIVO" eps   busy    "$NOW_MS" "$SANDBOX/work/eps"

mkdir -p "$ST/parada"; : > "$ST/parada/delta"
slug_eps="$(printf '%s' "$SANDBOX/work/eps" | sed 's/[^A-Za-z0-9]/-/g')"
mkdir -p "$PROJ/$slug_eps"; : > "$PROJ/$slug_eps/eps-antigo.jsonl"
touch -d '40 minutes ago' "$PROJ/$slug_eps/eps-antigo.jsonl"

echo "== dry-run sem config (gama nao e esperada)"
out="$(bash "$VIGIA" check --dry-run 2>&1)"; rc=$?
assert_eq "$rc" "0" "dry-run sai 0"
assert_has "$out" "ESPERANDO" "a: detecta ESPERANDO"
assert_has "$out" "TRAVADA" "d: detecta TRAVADA"
assert_not "$out" "MORTA" "b: sem config, gama nao vira MORTA"
assert_not "$(printf "%s" "$out" | grep "^desvio")" "delta" "c: parada nao vira desvio"
if [ ! -e "$ST/log.tsv" ] && [ ! -e "$ST/desvios.txt" ]; then pass "dry-run nao grava estado"; else fail "dry-run gravou estado"; fi
if [ ! -e "$SANDBOX/avisos.txt" ]; then pass "dry-run nao avisa"; else fail "dry-run avisou"; fi

echo "== config com esperada gama"
mkdir -p "$XDG_CONFIG_HOME/bigtech"
printf '{"esperadas":["gama"]}\n' > "$XDG_CONFIG_HOME/bigtech/eficacia.json"
out="$(bash "$VIGIA" check --dry-run 2>&1)"
assert_has "$out" "MORTA" "b: com config, gama vira MORTA"

echo "== passada real: so avisa desvio novo"
bash "$VIGIA" check >/dev/null 2>&1
assert_eq "$(wc -l < "$SANDBOX/avisos.txt" | tr -d ' ')" "3" "primeira passada avisa 3 desvios"
assert_not "$(cat "$SANDBOX/avisos.txt")" "delta" "parada nunca avisa"
bash "$VIGIA" check >/dev/null 2>&1
assert_eq "$(wc -l < "$SANDBOX/avisos.txt" | tr -d ' ')" "3" "segunda passada igual nao avisa de novo"

echo "== log.tsv"
st_de() { awk -F'\t' -v s="$1" '$2==s{v=$3} END{print v}' "$ST/log.tsv"; }
assert_eq "$(st_de alfa)" "esperando" "log: alfa esperando"
assert_eq "$(st_de beta)" "ocupada" "log: beta ocupada"
assert_eq "$(st_de gama)" "morta" "log: gama morta"
assert_eq "$(st_de delta)" "parada" "log: delta parada"
assert_eq "$(st_de eps)" "travada" "log: eps travada"

echo "== desvio some e volta"
mk_sess alfa "$PID_VIVO" alfa busy "$NOW_MS" "$SANDBOX/work/alfa"
bash "$VIGIA" check >/dev/null 2>&1
assert_eq "$(wc -l < "$SANDBOX/avisos.txt" | tr -d ' ')" "3" "desvio que some nao avisa"
mk_sess alfa "$PID_VIVO" alfa waiting $(( NOW_MS - 20*60*1000 )) "$SANDBOX/work/alfa"
bash "$VIGIA" check >/dev/null 2>&1
assert_eq "$(wc -l < "$SANDBOX/avisos.txt" | tr -d ' ')" "4" "desvio que volta e novo: avisa de novo"

echo "== status"
out="$(bash "$VIGIA" status 2>&1)"; rc=$?
assert_eq "$rc" "0" "status sai 0"
assert_has "$out" "TOTAL" "status imprime total"
assert_has "$out" "beta" "status lista sessao"

echo "== instalar e remover (systemctl stub, nunca o real)"
mkdir -p "$SANDBOX/bin"
printf '#!/usr/bin/env bash\necho "$*" >> "%s/systemctl.log"\n' "$SANDBOX" > "$SANDBOX/bin/systemctl"
chmod +x "$SANDBOX/bin/systemctl"
PATH="$SANDBOX/bin:$PATH" bash "$VIGIA" instalar --intervalo 7 >/dev/null 2>&1
U="$XDG_CONFIG_HOME/systemd/user"
assert_has "$(cat "$U/bigtech-eficacia.timer" 2>/dev/null)" "OnUnitActiveSec=7min" "instalar grava timer com intervalo"
assert_has "$(cat "$U/bigtech-eficacia.service" 2>/dev/null)" "check" "instalar grava service que roda check"
PATH="$SANDBOX/bin:$PATH" bash "$VIGIA" remover >/dev/null 2>&1
if [ ! -e "$U/bigtech-eficacia.timer" ]; then pass "remover apaga o timer"; else fail "remover nao apagou o timer"; fi

echo "== config invalida sai 2"
printf 'nao e json' > "$XDG_CONFIG_HOME/bigtech/eficacia.json"
bash "$VIGIA" check --dry-run >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "config invalida: exit 2"

echo
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; exit 0; fi
echo "FALHAS: $FAILS"; exit 1
