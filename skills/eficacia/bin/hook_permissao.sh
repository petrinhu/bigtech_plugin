#!/usr/bin/env bash
# hook_permissao.sh - PermissionRequest (doc oficial: decision.behavior "deny" + message).
# Com a bandeira lider_dormindo: nega o pedido, grava "PERMISSAO: <ferramenta> <resumo>"
# em <estado>/fila.md (flock) e manda trocar de trabalho. Sem a bandeira: silencio, saida 0.
set -euo pipefail

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia"
SESS_DIR="$HOME/.claude/sessions"
IN="$(cat || true)"
LIMPA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/limpa_texto.py"

if [ ! -e "$STATE_DIR/lider_dormindo" ]; then
  exit 0
fi

PY_PERM='
import glob, json, os, sys, time
def lim(v):
    return " ".join(str(v).split())
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
achou = None
if sid:
    achou = next((d for d in sessoes if str(d.get("sessionId") or "") == sid), None)
if achou is None and cwd:
    achou = next((d for d in sessoes if str(d.get("cwd") or "") == cwd), None)
nome = lim(achou.get("name") or "desconhecida") if achou is not None else "desconhecida"
ferr = lim(data.get("tool_name") or "?")
ti = data.get("tool_input") or {}
if isinstance(ti, dict) and ti.get("command"):
    resumo = lim(ti.get("command"))
elif isinstance(ti, dict) and ti.get("file_path"):
    resumo = lim(ti.get("file_path"))
else:
    resumo = lim(json.dumps(ti, ensure_ascii=False))[:200]
print("## %s - sessao: %s" % (time.strftime("%Y-%m-%d %H:%M"), nome))
print("- PERMISSAO: %s %s" % (ferr, resumo))
'

BLOCO="$(printf '%s' "$IN" | python3 -I -c "$PY_PERM" "$SESS_DIR" 2>/dev/null | python3 -I "$LIMPA" || true)"
if [ -n "$BLOCO" ]; then
  ( umask 077; mkdir -p "$STATE_DIR" )
  (
    flock 9
    printf '%s\n\n' "$BLOCO" >> "$STATE_DIR/fila.md"
  ) 9>"$STATE_DIR/.fila.lock"
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny","message":"lider dormindo: o pedido de permissao ja esta na fila: troque de trabalho"}}}'
exit 0
