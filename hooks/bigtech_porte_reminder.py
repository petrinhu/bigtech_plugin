#!/usr/bin/env python3
"""
bigtech_porte_reminder.py

Hook SessionStart. Lembrete leve, anti-ruido, para classificar o PORTE de um
projeto de codigo via /bigtech (que invoca o Cosimo / Chief of Staff) e
dimensionar a constelacao de agents.

Logica:
- So dispara em diretorio que parece PROJETO DE CODIGO (tem marcador de build
  ou manifesto: CMakeLists.txt, package.json, pyproject.toml, go.mod,
  Cargo.toml, composer.json, build.gradle, *.csproj, *.pro). CLAUDE.md ou .git
  sozinhos NAO contam (amplo demais, pegaria pastas de doc).
- So dispara se NAO existe o marcador `.bigtech-porte` na raiz do projeto.
  O marcador e relativo ao PROJETO do usuario (cwd), nao ao plugin.
- Quando /bigtech classifica o porte, grava `.bigtech-porte` e o lembrete para.

Saida: JSON com hookSpecificOutput.additionalContext quando dispara; nada caso
contrario. Sempre exit 0 (lembrete, nunca bloqueia).
"""
import json
import os
import re
import sys
import glob

MARKER = ".bigtech-porte"
MAX_MARKER_BYTES = 4096

# Manifestos/marcadores que caracterizam projeto de codigo (basenames exatos).
CODE_MARKERS = (
    "CMakeLists.txt",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "composer.json",
    "build.gradle",
    "build.gradle.kts",
    "Makefile",
    "setup.py",
)

# Marcadores por glob (extensoes de projeto).
CODE_GLOBS = ("*.csproj", "*.pro", "*.sln", "*.xcodeproj")


def is_code_project(d: str) -> bool:
    for m in CODE_MARKERS:
        if os.path.isfile(os.path.join(d, m)):
            return True
    for g in CODE_GLOBS:
        if glob.glob(os.path.join(d, g)):
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = (data.get("cwd") or os.getcwd() or "").strip()
    if not cwd or not os.path.isdir(cwd):
        return 0

    marker_path = os.path.join(cwd, MARKER)

    # Ja classificado: em vez de silencio, ANCORAR o modo de operacao bigtech
    # logo no inicio da sessao. O reforco por turno fica no hook
    # bigtech_reinforce.py (UserPromptSubmit).
    if os.path.isfile(marker_path):
        porte = "classificado"
        try:
            with open(marker_path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.read(MAX_MARKER_BYTES)
            m = re.search(r"porte\s*=\s*([A-Za-z]+)", head)
            if m:
                porte = m.group(1).lower()
        except Exception:
            pass
        msg = (
            "[bigtech] Projeto classificado (porte=" + porte + "). MODO DE "
            "OPERACAO ATIVO: operar como a constelacao bigtech — negocio/produto/"
            "lideranca via C-levels. ORQUESTRADOR = Cosimo (Chief of Staff): "
            "classifica porte, monta o time e roteia. Para GERENCIAR o projeto ou "
            "os agentes dev: Cosimo (orquestra) + Cosmo (COO, execucao "
            "cross-funcional) + engineering-manager + scrum-master. Engenharia "
            "via /proj_software. Calibrar headcount pelo porte (anti "
            "over-engineering; a maioria dos C-levels fica dormente em projeto "
            "pequeno). Decisoes de alto valor (arquitetura/escopo/stack/go-no-go/"
            "gasto/irreversivel) -> SEMPRE AskUserQuestion ao usuario, que e o "
            "lider supremo (CEO) da propria bigtech. Agents devem "
            "contra-argumentar decisao destrutiva. Nao driftar pro assistente "
            "generico. Governanca nos manuais do plugin (docs/ORG.md, ...); o "
            "caminho absoluto e injetado no contexto da sessao (docs-bootstrap)."
        )
        out = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": msg,
            }
        }
        print(json.dumps(out))
        return 0

    if not is_code_project(cwd):
        return 0

    msg = (
        "[bigtech] Projeto de codigo sem porte classificado (sem arquivo "
        ".bigtech-porte). Considere rodar /bigtech: o Cosimo (Chief of Staff) "
        "classifica o porte (solo/early/scale/bigtech), seleciona a variante "
        "de pipeline (anti over-engineering) e monta a constelacao de agents. "
        "Apos classificar, grave o marcador .bigtech-porte na raiz do projeto "
        "para silenciar este lembrete. Governanca: docs/ORG.md (manuais do "
        "plugin; caminho absoluto injetado no contexto via docs-bootstrap)."
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
