#!/usr/bin/env bash
# Fixture de consumo REAL de processos para o sensor pids. Roda DENTRO de um
# scope systemd isolado (TasksMax=64), lancado por test_watchcode.sh apos o
# guarda-corpo de folga. NUNCA chamar direto na sessao viva do
# usuário: sobe processos de verdade, mesmo que o teto do scope os confine a
# no maximo 64 tasks (1,6% do teto real de 4000 desta maquina).
set -u
FAILS=0
ENCONTRADOS=0
ANALISADOS=0
pass() { printf '  ok  - %s\n' "$1"; ANALISADOS=$((ANALISADOS+1)); }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); ANALISADOS=$((ANALISADOS+1)); }
assert_eq() {
  ENCONTRADOS=$((ENCONTRADOS+1))
  if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi
}

DIR="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
. "$DIR/bin/lib.sh"

# 1. Descobre o proprio cgroup (path real dentro do scope isolado).
read -r cgline < /proc/self/cgroup
cgpath="${cgline#0::}"
export WATCHCODE_PIDS_CURRENT_FILE="/sys/fs/cgroup${cgpath}/pids.current"
export WATCHCODE_PIDS_LIMIT="64"
FIXSANDBOX="$(mktemp -d)"
export WATCHCODE_STATE_DIR="$FIXSANDBOX/state"
wc_init_state
wc_pids_init

# fifo local para poll sem sleep externo (builtin read -t, mesmo mecanismo
# do wc_daemon_sleep de producao).
mkfifo "$FIXSANDBOX/poll.fifo"
exec 8<>"$FIXSANDBOX/poll.fifo"
poll_wait() { read -t "$1" -u 8 _ 2>/dev/null; return 0; }

wait_for_pids_ge() {
  # <alvo> -> espera pids.current >= alvo, teto 5s (25 x 0.2s);
  # estourou o teto -> FALHA, nunca skip silencioso.
  local alvo="$1" elapsed=0
  while :; do
    wc_pids_read
    if [ "${WC_PIDS_CUR:-0}" -ge "$alvo" ]; then return 0; fi
    poll_wait 0.2
    elapsed=$((elapsed+1))
    [ "$elapsed" -ge 25 ] && return 1
  done
}

JOBS=()
teardown() {
  local p
  for p in "${JOBS[@]:-}"; do
    [ -n "$p" ] && kill "$p" 2>/dev/null
  done
  JOBS=()
}
trap teardown EXIT

# 2. Fase baixa (controle positivo real): 20 sleeps (~31% de 64).
for _ in $(seq 1 20); do
  sleep 30 &
  JOBS+=("$!")
done
if wait_for_pids_ge 21; then
  : > "$(wc_findings_file)"
  wc_pids_sense
  n="$(grep -c '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null || true)"
  assert_eq "${n:-0}" "0" "fixture real: fase baixa (20 sleeps, ~31% de 64) fica ok, zero achados"
else
  fail "fixture real: fase baixa nao atingiu 21 tasks em 5s (pids.current=${WC_PIDS_CUR:-?})"
fi

# 3. Fase warn (controle negativo real): sobe ate 45 sleeps (~70% de 64).
for _ in $(seq 1 25); do
  sleep 30 &
  JOBS+=("$!")
done
if wait_for_pids_ge 46; then
  : > "$(wc_findings_file)"
  wc_pids_sense
  n="$(grep -c '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null || true)"
  assert_eq "${n:-0}" "1" "fixture real: fase warn (45 sleeps, ~70% de 64) gera 1 achado"
  maxv="$(grep '"kind":"pids"' "$(wc_findings_file)" | tail -n1 | sed -n 's/.*"max":\([0-9]*\).*/\1/p')"
  assert_eq "$maxv" "64" "fixture real: achado warn carrega max=64 (teto do scope isolado)"
else
  fail "fixture real: fase warn nao atingiu 46 tasks em 5s (pids.current=${WC_PIDS_CUR:-?})"
fi

# 4. Fase crit: sobe ate 56 sleeps (~87,5% de 64).
for _ in $(seq 1 11); do
  sleep 30 &
  JOBS+=("$!")
done
if wait_for_pids_ge 57; then
  : > "$(wc_findings_file)"
  wc_pids_sense
  n="$(grep -c '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null || true)"
  assert_eq "${n:-0}" "1" "fixture real: fase crit (56 sleeps, ~87,5% de 64) gera 1 achado"
  lvl="$(grep '"kind":"pids"' "$(wc_findings_file)" | tail -n1 | sed -n 's/.*"level":"\([a-z]*\)".*/\1/p')"
  assert_eq "$lvl" "crit" "fixture real: fase crit classifica como crit"
else
  fail "fixture real: fase crit nao atingiu 57 tasks em 5s (pids.current=${WC_PIDS_CUR:-?})"
fi

# 5. teardown explicito (o trap EXIT cobre o caso de saida antecipada).
teardown

# 6. laco item a item: imprime encontrados/analisados sempre, mesmo zero.
printf 'encontrados=%d analisados=%d\n' "$ENCONTRADOS" "$ANALISADOS"
rm -rf "$FIXSANDBOX"

if [ "$FAILS" -eq 0 ] && [ "$ENCONTRADOS" -eq "$ANALISADOS" ] && [ "$ENCONTRADOS" -gt 0 ]; then
  echo "FIXTURE OK"
else
  echo "FIXTURE $FAILS FALHA(S) (encontrados=$ENCONTRADOS analisados=$ANALISADOS)"
  exit 1
fi
