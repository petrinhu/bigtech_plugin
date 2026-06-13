#!/usr/bin/env python3
"""
bigtech_reinforce.py

Hook UserPromptSubmit. Reforco por turno do MODO DE OPERACAO bigtech, escopado
por marcador para nao virar ruido global.

Dois modos, mutuamente exclusivos:

1) REFORCO (projeto ja classificado): se existe `.bigtech-porte` na raiz do
   projeto (cwd), injeta a cada turno um lembrete curto do MODO DE OPERACAO
   bigtech, para o modelo nao driftar de volta pro assistente generico quando
   outros plugins/skills injetam instrucoes concorrentes.

2) ROTEAMENTO (projeto ainda nao classificado): se o prompt do usuario pede a
   constelacao C-level ("c-level", "bigtech", "montar o time", ...), injeta um
   ponteiro forte para invocar /bigtech (Cosimo). Resolve o caso "peco a
   constelacao e ela nao e usada".

O marcador `.bigtech-porte` e relativo ao PROJETO do usuario (cwd), nao ao
plugin.

Anti-ruido: NUNCA injeta nos dois casos ao mesmo tempo; nao injeta em projeto
sem marcador quando o prompt nao pede a constelacao. Sempre exit 0; silent-fail
em qualquer erro (lembrete nunca bloqueia o turno).
"""
import json
import os
import re
import sys

MARKER = ".bigtech-porte"
MAX_MARKER_BYTES = 4096

# Gatilhos de linguagem natural que significam "quero a constelacao C-level".
# Inclui termos de orquestracao e gerencia (Cosimo = Chief of Staff orquestrador;
# C-levels = camada gerencial/lideranca). Aceita pt-br e ingles.
TRIGGER_RE = re.compile(
    r"(?:\b("
    # como o usuario pode chamar os C-levels:
    r"c-?level(?:s|es)?|clevel(?:s)?|c-?suite|"
    # a propria org / constelacao:
    r"bigtech|big\s*tech|constela\w*|constellation|"
    # papeis de orquestracao / gerencia / lideranca:
    r"orquestr\w*|orchestrat\w*|gerenc\w*|gerente|gestor|gest[ãa]o|manage\w*|"
    r"coorden\w*|chief\s+of\s+staff|c[óo]simo|cosmo|"
    # montar/estruturar o time/equipe/empresa:
    r"montar?\s+(?:o\s+)?time|monta\s+(?:o\s+)?time|montar?\s+a\s+equipe|"
    r"(?:montar?|estruturar|organizar)\s+a\s+empresa|build\s+the\s+team"
    r")\b)|(?:\btime\s+de\s+agent)|(?:\bagentes?\s+dev)|(?:\bdev\s+agent)",
    re.IGNORECASE,
)


def read_porte(marker_path: str) -> str:
    """Le a primeira linha do marcador e extrai 'porte=<x>'. Fallback seguro."""
    try:
        with open(marker_path, "r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(MAX_MARKER_BYTES)
    except Exception:
        return "classificado"
    m = re.search(r"porte\s*=\s*([A-Za-z]+)", head)
    return m.group(1).lower() if m else "classificado"


def emit(msg: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = (data.get("cwd") or os.getcwd() or "").strip()
    prompt = (data.get("prompt") or "")

    if not cwd or not os.path.isdir(cwd):
        return 0

    marker_path = os.path.join(cwd, MARKER)
    classificado = os.path.isfile(marker_path)

    # MODO 1 — reforco por turno em projeto ja classificado.
    if classificado:
        porte = read_porte(marker_path)
        emit(
            "BIGTECH ATIVO (porte=" + porte + "). Operar como a constelacao: "
            "negocio/produto/lideranca via C-levels. ORQUESTRADOR = Cosimo "
            "(Chief of Staff): classifica porte, monta o time, roteia (skill "
            "/bigtech). Para GERENCIAR projeto ou agentes dev: Cosimo (orquestra) "
            "+ Cosmo (COO, execucao cross-funcional) + engineering-manager "
            "(gestao de pessoas/eng) + scrum-master (cadencia/impedimentos). "
            "Engenharia via /proj_software. Calibrar headcount pelo porte (anti "
            "over-engineering). Decisao de alto valor (arquitetura/escopo/stack/"
            "go-no-go/gasto/irreversivel) -> SEMPRE AskUserQuestion ao usuario, "
            "que e o lider supremo (CEO) da propria bigtech. Dever de "
            "contra-argumentar decisao destrutiva (problema -> risco -> "
            "alternativa -> decisao do usuario). Nao driftar pro assistente generico."
        )
        return 0

    # MODO 2 — roteamento quando o usuario pede a constelacao num projeto ainda
    # nao classificado. So dispara se o prompt casa um gatilho.
    if prompt and TRIGGER_RE.search(prompt):
        emit(
            "[bigtech] O usuario quer a constelacao C-level / gerenciar projeto "
            "ou agentes dev. ROTEAR para /bigtech, que invoca o AGENTE "
            "ORQUESTRADOR = Cosimo (Chief of Staff): classifica o porte "
            "(solo/early/scale/bigtech, anti over-engineering), seleciona a "
            "variante de pipeline e monta o time de C-levels + agents operacionais. "
            "Para GERENCIAR projeto/agentes dev, os agentes sao: Cosimo (Chief of "
            "Staff, orquestrador) + Cosmo (COO, execucao cross-funcional) + "
            "engineering-manager (gestao de eng/pessoas) + scrum-master (cadencia/"
            "impedimentos) + product-manager. Engenharia pura -> /proj_software. "
            "NAO responder como assistente generico; usar a skill /bigtech. Apos "
            "classificar, gravar .bigtech-porte na raiz."
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
