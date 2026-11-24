#!/usr/bin/env bash
# hook_lider_dormindo.sh - PreToolUse para AskUserQuestion enquanto o lider dorme.
# Com a bandeira lider_dormindo (criada por `vigia.sh dormir`): nega a pergunta, grava
# a pergunta barrada em <estado>/fila.md (flock, varias sessoes ao mesmo tempo) e manda
# o agente seguir sem o lider. Sem a bandeira: silencio, saida 0.
set -euo pipefail

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia"
SESS_DIR="$HOME/.claude/sessions"

# Le o JSON do evento uma vez (stdin).
IN="$(cat || true)"

if [ ! -e "$STATE_DIR/lider_dormindo" ]; then
  exit 0
fi

# Bloco de texto da fila, montado por python3 -I (uma chamada). Nome da sessao:
# casa pelo session_id e, se nao achar, pelo cwd do JSON de entrada.
PY_FILA='
import glob, json, os, sys, time, unicodedata
def clean(v):
    return "".join(c for c in str(v) if c == "\n" or not unicodedata.category(c).startswith("C"))
sess_dir = sys.argv[1]
try:
    data = json.loads(sys.stdin.read() or "{}")
except ValueError:
    data = {}
sid = str(data.get("session_id") or "")
cwd = str(data.get("cwd") or "")
sessoes = []
for p in sorted(glob.glob(os.path.join(sess_dir, "*.json"))):
    try:
        with open(p, encoding="utf-8") as f:
            sessoes.append(json.load(f))
    except (OSError, ValueError):
        continue
nome = "desconhecida"
achou = None
if sid:
    achou = next((d for d in sessoes if str(d.get("sessionId") or "") == sid), None)
if achou is None and cwd:
    achou = next((d for d in sessoes if str(d.get("cwd") or "") == cwd), None)
if achou is not None:
    nome = str(achou.get("name") or "desconhecida")
def lim(v):
    return " ".join(clean(v).split())
ti = data.get("tool_input") or {}
perguntas = ti.get("questions") or []
out = ["## %s - sessao: %s" % (time.strftime("%Y-%m-%d %H:%M"), lim(nome))]
for q in perguntas:
    if not isinstance(q, dict):
        continue
    out.append("- PERGUNTA: " + lim(q.get("question") or "(sem texto)"))
    for op in q.get("options") or []:
        if isinstance(op, dict):
            linha = "  - opcao: " + lim(op.get("label") or "")
            if op.get("description"):
                linha += " - " + lim(op.get("description"))
            out.append(linha)
if not perguntas:
    out.append("- PERGUNTA: (tool_input sem perguntas)")
print("\n".join(out))
'

BLOCO="$(printf '%s' "$IN" | python3 -I -c "$PY_FILA" "$SESS_DIR" 2>/dev/null || true)"
if [ -n "$BLOCO" ]; then
  ( umask 077; mkdir -p "$STATE_DIR" )
  (
    flock 9
    printf '%s\n\n' "$BLOCO" >> "$STATE_DIR/fila.md"
  ) 9>"$STATE_DIR/.fila.lock"
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"lider dormindo: se e duvida tecnica, chame o C-level do dominio pela ferramenta Agent e registre a decisao com vigia.sh registrar; se e decisao so do lider (commit barrado, permissao, lei, gasto, irreversivel, merge, tag, deploy), ela ja esta na fila: troque de trabalho"}}'
exit 0
