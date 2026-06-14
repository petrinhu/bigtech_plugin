#!/usr/bin/env python3
"""
tab_pendencias_reminder.py

Hook SessionStart do plugin bigtech. Lembrete leve, anti-ruído, para gerar a
TABELA DE PENDÊNCIAS (TODO.md) via /tab_pendencias num projeto que já foi
classificado pelo /bigtech mas ainda não tem a tabela.

Gatilho SEQUENCIAL (evita empilhar com bigtech_porte_reminder.py):
- Só dispara se EXISTE o marcador `.bigtech-porte` na raiz (projeto já
  classificado pelo Cósimo) E NÃO existe `TODO.md` na raiz.
- Quando falta o porte, quem lembra é o bigtech_porte_reminder (-> /bigtech,
  cujo Cósimo já exige a tabela). Quando o TODO.md é criado, o lembrete para.

A skill só é iniciada pela THREAD PRINCIPAL (nenhum agent tem a ferramenta
Skill; subagent não dispara subagent). Este hook apenas lembra.

Saída: JSON com hookSpecificOutput.additionalContext quando dispara; nada caso
contrário. Sempre exit 0 (lembrete, nunca bloqueia).
"""
import json
import os
import sys

PORTE_MARKER = ".bigtech-porte"
TODO_FILE = "TODO.md"


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = (data.get("cwd") or os.getcwd() or "").strip()
    if not cwd or not os.path.isdir(cwd):
        return 0

    # Gatilho sequencial: projeto classificado (.bigtech-porte) sem TODO.md.
    if not os.path.isfile(os.path.join(cwd, PORTE_MARKER)):
        return 0
    if os.path.isfile(os.path.join(cwd, TODO_FILE)):
        return 0

    msg = (
        "[tab_pendencias] Projeto já classificado (.bigtech-porte presente) mas "
        "SEM TODO.md (tabela de pendências). Considere rodar /tab_pendencias "
        "--create: gera a tabela ordenada por execução (topological + WSJF + "
        "ondas, anti-retrabalho) e já garante, com dupla-confirmação, os testes "
        "não-unitários e as auditorias aplicáveis ao stack como itens de "
        "fechamento (cria ./TESTES.md e ./AUDITORIAS.md se faltarem). Quem inicia "
        "a skill é a thread principal (agents não têm a ferramenta Skill). Após "
        "criar o TODO.md, este lembrete para."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg,
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
