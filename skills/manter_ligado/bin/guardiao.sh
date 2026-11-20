#!/usr/bin/env bash
# Guardião singleton: segura o inhibitor (via systemd-inhibit, no controlador) e roda o loop de bateria.
#
# Guardas do laço (o mecanismo de proteção não pode ser a causa do dano):
#  (a) guarda de rotação: o sleep que volta antes do tempo 3 vezes seguidas encerra o guardião
#      (tempo medido com $EPOCHSECONDS, builtin);
#  (b) recusa de arranque sob escassez: com processos em >= 80% do teto, não arma (sai com 5);
#      em operação, ciclo nessa faixa não lê bateria, só dorme;
#  (c) teto declarado: 1 processo externo por ciclo (o sleep); as leituras são builtins
#      (medido com strace em CONS-09S, teste 4d);
#  + sinais TERM/INT/HUP encerram; pai morto (reparentado) encerra no ciclo seguinte.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

ML_INTERVAL="${MANTER_INTERVAL:-60}"
if ! [[ "$ML_INTERVAL" =~ ^[0-9]+$ ]] || [ "$ML_INTERVAL" -lt 1 ]; then ML_INTERVAL=60; fi
ml_current_ppid; ML_PARENT="$ML_PPID"

if ml_pids_crit; then
  printf 'manter_ligado: guardiao recusou o arranque: processos em degrau critico (>= 80%% do teto); nada foi armado\n' >&2
  exit 5
fi

ml_init_state
FLAG="$(ml_state_dir)/guardian.armed"
: > "$FLAG"
trap 'rm -f "$FLAG"' EXIT
trap 'exit 0' TERM INT HUP

warned=0; saved=0; spins=0
while :; do
  # pai morto: o processo foi reparentado (PPID mudou) -> encerra
  ml_current_ppid
  [ "$ML_PPID" = "$ML_PARENT" ] || exit 0

  if ! ml_pids_crit; then
    ml_read_num "${MANTER_BAT_CAPACITY_FILE:-/sys/class/power_supply/BAT1/capacity}" 100; cap="$ML_NUM"
    ml_read_num "${MANTER_AC_ONLINE_FILE:-/sys/class/power_supply/ACAD/online}" 0; ac="$ML_NUM"
    ml_decide_into "$cap" "$ac" "$warned" "$saved"
    case "$ML_ACAO" in
      warn) ml_push "Bateria ${MANTER_WARN_PCT:-20}% - rode /memo nas sessoes via /rc se quiser."; warned=1 ;;
      save) ml_save "$(date +%Y%m%d-%H%M%S)"; saved=1 ;;
    esac
  fi
  [ "${MANTER_ONESHOT:-0}" = "1" ] && break

  t0=$EPOCHSECONDS
  sleep "$ML_INTERVAL"
  t1=$EPOCHSECONDS
  if (( t1 - t0 < ML_INTERVAL )); then
    spins=$((spins+1))
    if [ "$spins" -ge 3 ]; then
      printf 'manter_ligado: guarda de rotacao: sleep voltou antes do tempo 3 vezes seguidas; guardiao encerra\n' >&2
      exit 4
    fi
  else
    spins=0
  fi
done
