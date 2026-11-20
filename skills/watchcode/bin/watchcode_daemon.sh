#!/usr/bin/env bash
# Daemon "burro" do watchcode: detecta crashes reais, filtra baseline, anexa achados crus.
#
# Transporte (redesenho 01/09/2026, SPEC-transporte-watchcode.md): um UNICO
# processo filho de vida longa (`journalctl -f -o json`, coproc WCJ) entrega
# cada entrada do journal como uma linha. O laco le com `read -t` (builtin) e
# roteia/extrai/grava tudo com regex/case/printf builtins -- em regime
# permanente o custo e ZERO processos criados (so residem daemon+journalctl).
# O antigo "acordar a cada 120s e reprocessar a janela inteira" (69 forks por
# ciclo ocioso, ~2070/h medidos) morreu; a INTELIGENCIA de deteccao dos 5
# sensores migrou intacta para os wc_parse_* em lib.sh. O sensor pids
# continua fora do fluxo (nao e de journal) e nao muda uma linha do seu
# caminho quente.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

wc_init_state
# Resolve UMA VEZ, no arranque, os caminhos que o caminho quente (uma
# chamada por linha do journal: wc_append_*/wc_cursor_flush) usa -- mesmo
# padrao que wc_pids_init ja aplica a WC_PIDS_FILE/WC_PIDS_FINDINGS.
# Achado da revisao adversarial (strace -f -c, 50 achados): SEM isto, cada
# wc_append_* recomputava "$(wc_findings_file)" (um $(), que forka um
# subshell so pra capturar a saida de uma funcao 100% builtin) a cada
# achado -- media ~4 clone/execve por achado, violando o orcamento de 0
# processos da secao 5 da spec. Com a variavel cacheada aqui, esse custo
# vira ZERO no caminho quente (medido: ver evidencia da onda).
WC_FINDINGS_FILE="$(wc_findings_file)"
WC_STREAM_CURSOR_FILE="$(wc_state_dir)/stream_cursor"
WC_LAST_SCAN_FILE="$(wc_state_dir)/last_scan"
FLAG="$(wc_state_dir)/daemon.armed"
SLEEP_FIFO="$(wc_state_dir)/sleep.fifo"
: > "$FLAG"
trap 'wc_stream_close; wc_cursor_flush; rm -f "$FLAG" "$SLEEP_FIFO"' EXIT

wc_pids_init
wc_daemon_sleep_init
wc_spin_guard_init

WATCHCODE_INTERVAL="${WATCHCODE_INTERVAL:-120}"

# Espia a ocupacao ANTES do laco (puro, builtin) so para registrar o modo no
# estado -- diferente do redesenho antigo, a ocupacao no arranque NAO impede
# a abertura do fluxo: abrir 1 processo de vida longa e um custo FIXO (nao
# escala com o numero de achados), e a detecao de journal passa a CONTINUAR
# durante o crit (secao 7 da spec: "some" o pulo dos sensores; a unica coisa
# que fica adiada sob crit e o *reinicio* do fluxo morto, ver wc_stream_restart).
# wc_pids_sense (nao so read/level_calc) porque e a MESMA funcao chamada a
# cada tick -- fonte unica de verdade (secao 0 da spec). Chamar so a versao
# pura aqui deixava WC_PIDS_SKIP_FORKS no valor inicial (0) ate o 1o tick,
# o que abria uma janela real: um fluxo que morre ANTES do 1o tick (ex.
# journalctl crashando nos primeiros segundos) via wc_stream_restart lia
# SKIP_FORKS desatualizado e reiniciava mesmo com a ocupacao ja critica.
DAEMON_MODE_FILE="$(wc_state_dir)/daemon_mode"
wc_pids_sense
if [ "${WC_PIDS_SKIP_FORKS:-0}" = "1" ]; then
  printf 'stream aberto (fluxo unico, custo fixo); ocupacao ja critica no arranque (cur=%s max=%s) -- so o REINICIO do fluxo fica adiado enquanto durar o crit\n' \
    "${WC_PIDS_CUR:-NA}" "${WC_PIDS_LIMIT:-NA}" > "$DAEMON_MODE_FILE"
elif [ "${WC_PIDS_ENABLED:-0}" = "1" ]; then
  printf 'normal (cur=%s max=%s no arranque)\n' "${WC_PIDS_CUR:-NA}" "${WC_PIDS_LIMIT:-NA}" > "$DAEMON_MODE_FILE"
else
  printf 'normal (sensor pids inativo ou fonte ilegivel no arranque)\n' > "$DAEMON_MODE_FILE"
fi

WC_STREAM_STATE=streaming
wc_stream_open
case "$WC_STREAM_LAST_POS" in
  --after-cursor=*) WC_STREAM_LAST_KIND=cursor ;;
  *) WC_STREAM_LAST_KIND=since ;;
esac

next_tick=$((EPOCHSECONDS + WATCHCODE_INTERVAL))

while :; do
  if (( EPOCHSECONDS >= next_tick )); then
    wc_pids_sense
    if [ "$WC_STREAM_STATE" = deferred ] && [ "${WC_PIDS_SKIP_FORKS:-0}" != "1" ]; then
      wc_stream_open
      case "$WC_STREAM_LAST_POS" in
        --after-cursor=*) WC_STREAM_LAST_KIND=cursor ;;
        *) WC_STREAM_LAST_KIND=since ;;
      esac
      WC_STREAM_STATE=streaming
    fi
    wc_cursor_flush
    next_tick=$((EPOCHSECONDS + WATCHCODE_INTERVAL))
  fi

  if [ "$WC_STREAM_STATE" = deferred ]; then
    # D0-a/D2 (fail-closed, regra de produto): o fluxo esta fechado de proposito
    # (crit); nao ha fd pra ler. Dorme ate o proximo tick reavaliar o rearme.
    timeout=$((next_tick - EPOCHSECONDS)); (( timeout < 1 )) && timeout=1
    wc_daemon_sleep "$timeout"
    [ "${WATCHCODE_ONESHOT:-0}" = "1" ] && break
    continue
  fi

  timeout=$((next_tick - EPOCHSECONDS)); (( timeout < 1 )) && timeout=1
  if IFS= read -r -t "$timeout" line <&"$WC_STREAM_FD"; then
    # Fato do manual do bash: read -t que estoura sai com status > 128; EOF
    # sai com 1. Aqui o read teve sucesso (linha chegou), entao processa.
    wc_json_str "$line" __CURSOR && WC_STREAM_CURSOR="$WC_JSON_VALUE"
    wc_json_str "$line" __REALTIME_TIMESTAMP && WC_STREAM_TS="$WC_JSON_VALUE"
    wc_stream_dispatch "$line"
    wc_cursor_flush
    continue
  fi
  rc=$?
  if (( rc > 128 )); then
    continue    # timeout do read: so volta e faz o tick
  fi

  # rc=1 (nao timeout): fim de fluxo. Fato do manual do bash (medido nesta
  # maquina): o `read` builtin POPULA a variavel mesmo retornando falha
  # quando o produtor fecha o fluxo logo apos escrever um JSON completo,
  # ANTES do byte de nova linha -- essa e a 3a forma de descarte silencioso
  # do parser (as outras duas, campo nulo e campo em array de bytes, estao
  # documentadas no dispatch/parsers e na SKILL.md). Despacha essa ultima
  # linha (se houver conteudo) ANTES de tratar como fim de fluxo; um fluxo
  # que fecha sem escrever nada deixa $line vazia e nada e despachado.
  if [ -n "$line" ]; then
    wc_json_str "$line" __CURSOR && WC_STREAM_CURSOR="$WC_JSON_VALUE"
    wc_json_str "$line" __REALTIME_TIMESTAMP && WC_STREAM_TS="$WC_JSON_VALUE"
    wc_stream_dispatch "$line"
    wc_cursor_flush
  fi

  # EOF/erro: o filho do fluxo morreu.
  if [ "${WATCHCODE_ONESHOT:-0}" = "1" ]; then
    wc_stream_close
    wc_pids_sense
    wc_cursor_flush
    break
  fi
  # D0-a: guarda de rotacao, so builtins ($EPOCHSECONDS, aritmetica) -- ver a
  # nota longa em cima de wc_spin_guard_tick em lib.sh. wc_stream_restart
  # reusa a mesma guarda para o novo cenario (fluxo que nao volta / tempestade
  # de reinicio, issue systemd/systemd#36247).
  if wc_stream_restart; then
    [ "${WC_STREAM_DEFERRED:-0}" = "1" ] && WC_STREAM_STATE=deferred || WC_STREAM_STATE=streaming
  else
    break
  fi
done
