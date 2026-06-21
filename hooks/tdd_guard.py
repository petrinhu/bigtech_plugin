#!/usr/bin/env python3
"""PreToolUse: bloqueia escrita de codigo de producao sem teste vermelho.

Opt-in: so atua em projetos com .claude/tdd-guard.json. Sinal de red = exit
code do comando de teste, gravado por tdd_runner.py em last-run.json.
"""
import json
import os
import sys
from pathlib import Path

# Plugin-safe import: o hook e invocado via
# `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/tdd_guard.py"`, com cwd no projeto do
# usuario (nao em hooks/). Garante que `import tdd_common` resolva o modulo
# irmao, sem depender do cwd nem de qualquer path absoluto local.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tdd_common as c

MSG_NO_STATE = (
    "TDD guard: nenhuma execucao de teste registrada para este projeto.\n"
    "Voce esta tentando escrever codigo de producao ({rel}) sem um teste "
    "vermelho.\nEscreva primeiro um teste que falhe (red). Para refatorar com "
    "tudo verde, exporte TDD_PHASE=refactor. Para desligar, TDD_GUARD=off."
)
MSG_ALL_GREEN = (
    "TDD guard: a suite esta toda verde.\n"
    "Nao ha teste vermelho que justifique escrever producao ({rel}).\n"
    "Escreva um teste que falhe primeiro (red), ou exporte TDD_PHASE=refactor "
    "para refatorar, ou TDD_GUARD=off para desligar."
)
WARN_BROKEN = (
    "TDD guard: a ultima execucao de teste nao rodou (motivo: {reason}). "
    "Permitindo a edicao (fail-open). Verifique .claude/tdd-guard.json "
    "(test_command, timeout_sec) ou o ambiente de teste."
)
WARN_STATE_IO = (
    "TDD guard: falha de I/O ao ler o estado de teste ({err}). "
    "Permitindo a edicao (fail-open) para nao bloquear producao legitima por "
    "erro de leitura. Verifique permissoes/espaco em ~/.claude/state."
)


def evaluate(data: dict, env: dict):
    """Retorna (exit_code, message). 2 = bloqueia; 0 = permite."""
    if str(env.get("TDD_GUARD", "")).lower() == "off":
        return 0, ""

    fp = c.extract_file_path(data)
    if not fp:
        return 0, ""

    start = os.path.dirname(os.path.realpath(fp)) or os.getcwd()
    root, cfg = c.load_config(start)
    if cfg is None:
        return 0, ""          # projeto sem opt-in: inerte

    try:
        rel = os.path.relpath(os.path.realpath(fp), root)
    except ValueError:
        # Drives distintos no Windows (C:\ vs D:\) fazem relpath lancar
        # ValueError. FAIL-OPEN, simetrico ao tdd_runner._under(): permitir e
        # melhor que bloquear producao legitima por um caso de path do SO.
        return 0, ""
    if rel.startswith(".."):
        return 0, ""
    kind = c.classify(rel, cfg)
    if kind != "production":
        return 0, ""          # teste / excluido / ignorado: permite

    if str(env.get("TDD_PHASE", "")).lower() == "refactor":
        return 0, ""

    try:
        state = c.read_state(root)
    except OSError as e:
        # Erro de I/O ao ler o estado (HOME read-only, sem permissao, disco
        # cheio): FAIL-OPEN. Tratar como "sem teste" e bloquear seria punir
        # producao legitima por um problema de leitura. Distinto de None
        # (estado ausente), que continua bloqueando como antes.
        return 0, WARN_STATE_IO.format(err=e)
    if state is None:
        return 2, MSG_NO_STATE.format(rel=rel)
    if not state.get("ran", False):
        return 0, WARN_BROKEN.format(reason=state.get("reason", "desconhecido"))
    if state.get("has_red"):
        return 0, ""
    return 2, MSG_ALL_GREEN.format(rel=rel)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0   # stdin invalido: fail-open
    try:
        code, msg = evaluate(data, os.environ)
    except Exception as e:
        print(f"TDD guard: erro interno, permitindo ({e}).", file=sys.stderr)
        return 0   # qualquer erro: fail-open
    if msg:
        print(msg, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
