#!/usr/bin/env bash
# Fixture generica de WATCHCODE_STREAM_CMD (secao 9.1 da SPEC-transporte-
# watchcode.md), usada pelos testes de fluxo de test_watchcode.sh. Cada
# invocacao (o daemon reabre o coproc uma vez por wc_stream_open/restart)
# consome UMA linha do arquivo de plano ($WC_TEST_STREAM_PLAN_FILE) e grava
# um registro em $WC_TEST_STREAM_LOG com a posicao recebida (--after-cursor=
# ou --since=) -- sentinela que os testes de reinicio (5, 6, 7, 8) leem para
# provar QUAL posicao cada reinicio de verdade usou, sem confiar so no
# comportamento observado.
#
# Cada linha do plano e um destes tokens:
#   <caminho-de-arquivo.jsonl>  -> `exec cat <arquivo>` (serve o fluxo e sai)
#   DIE                         -> sai com status 1 imediatamente (fluxo morto rapido)
#   REJECT_CURSOR               -> sai com status 1 SO se a posicao recebida for --after-cursor=...; senao serve vazio e sai 0
#   (linha vazia ou faltando)   -> sai 0 sem imprimir nada (fluxo vazio)
set -u
pos="${1:-}"
plan_file="${WC_TEST_STREAM_PLAN_FILE:?WC_TEST_STREAM_PLAN_FILE nao setado}"
log="${WC_TEST_STREAM_LOG:-/dev/null}"
count_file="${WC_TEST_STREAM_COUNT_FILE:?WC_TEST_STREAM_COUNT_FILE nao setado}"

n=0
[ -f "$count_file" ] && read -r n < "$count_file"
n=$((n + 1))
printf '%s\n' "$n" > "$count_file"
printf 'invocacao=%s pos=%s\n' "$n" "$pos" >> "$log"

entry="$(sed -n "${n}p" "$plan_file" 2>/dev/null || true)"
case "$entry" in
  DIE) exit 1 ;;
  REJECT_CURSOR)
    case "$pos" in
      --after-cursor=*) exit 1 ;;
      *) exit 0 ;;
    esac
    ;;
  "") exit 0 ;;
  *) exec cat "$entry" ;;
esac
