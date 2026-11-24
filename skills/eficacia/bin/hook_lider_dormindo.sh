#!/usr/bin/env bash
# hook_lider_dormindo.sh - PreToolUse para AskUserQuestion enquanto o lider dorme.
# Com a bandeira lider_dormindo (criada por `vigia.sh dormir`), nega a pergunta e manda
# gravar nas pendencias com recomendacao e trocar de trabalho. Sem a bandeira: silencio, saida 0.
# NAO declarado em hooks.json: a doc oficial nao nomeia AskUserQuestion no PreToolUse (ver relatorio).
set -euo pipefail

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia"

# Le e descarta o stdin (JSON do evento): a decisao depende so da bandeira.
cat >/dev/null || true

if [ ! -e "$STATE_DIR/lider_dormindo" ]; then
  exit 0
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"lider dormindo: grave a pergunta nas pendencias com recomendacao e troque de trabalho"}}'
exit 0
