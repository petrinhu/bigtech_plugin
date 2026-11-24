#!/usr/bin/env bash
# hook_fim_turno.sh - Stop: com a bandeira lider_dormindo, a sessao nao para esperando o
# lider. Bloqueia UMA vez (stop_hook_active falso); com stop_hook_active verdadeiro sai 0
# para nao entrar em laco. Sem a bandeira: silencio, saida 0.
# Doc oficial (Stop): stop_hook_active e campo de entrada; saida {"decision":"block","reason":...}.
set -euo pipefail

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia"
IN="$(cat || true)"

if [ ! -e "$STATE_DIR/lider_dormindo" ]; then
  exit 0
fi

ATIVO="$(printf '%s' "$IN" | python3 -I -c '
import json, sys
try:
    print("1" if json.load(sys.stdin).get("stop_hook_active") is True else "0")
except (ValueError, AttributeError):
    print("0")
' 2>/dev/null || echo 0)"

if [ "$ATIVO" = "1" ]; then
  exit 0
fi

printf '%s\n' '{"decision":"block","reason":"lider dormindo: nao pare esperando o lider. Duvida tecnica vai ao C-level pela ferramenta Agent; decisao so do lider vai a fila com vigia.sh registrar ou ja esta la. Troque de trabalho: item sem dependencia no TODO.md; se depende da resposta e e reversivel, siga a recomendacao num ramo sem merge; se nada sobrar, pode parar."}'
exit 0
