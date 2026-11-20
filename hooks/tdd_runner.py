#!/usr/bin/env python3
"""PostToolUse: roda a suite apos editar codigo/teste e grava last-run.json.

Opt-in: so roda em projetos com .claude/tdd-guard.json. Nunca quebra o fluxo
(sempre exit 0). has_red = (exit_code != 0).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Plugin-safe import: o hook e invocado via
# `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/tdd_runner.py"`, com cwd no projeto do
# usuario (nao em hooks/). Garante que `import tdd_common` resolva o modulo
# irmao, sem depender do cwd nem de qualquer path absoluto local.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tdd_common as c


def run_suite(cfg: dict, project_root: str, runner=subprocess.run) -> dict:
    cmd = cfg.get("fast_command") or cfg.get("test_command")
    if not cmd:
        return {"ran": False, "reason": "sem test_command", "ts": int(time.time())}
    try:
        proc = runner(cmd, shell=True, cwd=project_root,
                      capture_output=True, text=True,
                      timeout=cfg.get("timeout_sec", 120))
    except FileNotFoundError as e:
        return {"ran": False, "reason": str(e), "ts": int(time.time())}
    except subprocess.TimeoutExpired:
        return {"ran": False, "reason": "timeout", "ts": int(time.time())}
    # 126/127 sao POSIX (nao executavel / nao encontrado). 9009 e o equivalente
    # do cmd.exe no Windows para "comando nao encontrado". Tratar como nao-rodou
    # evita registrar um falso has_red quando o test_command nem existe.
    if proc.returncode in (126, 127, 9009):
        return {"ran": False,
                "reason": f"comando nao executavel (exit {proc.returncode})",
                "ts": int(time.time())}
    out = (proc.stdout or "") + (proc.stderr or "")
    return {
        "ran": True,
        "command": cmd,
        "exit_code": proc.returncode,
        "has_red": proc.returncode != 0,
        "totals": c.parse_totals(out),
        "tail": "\n".join(out.splitlines()[-20:]),
        "ts": int(time.time()),
    }


def _under(path: str, base: str) -> bool:
    """True se `path` (real) estiver dentro de `base` (real). Mesma guarda
    de containment do tdd_guard.py (rel nao comeca com '..')."""
    try:
        rel = os.path.relpath(os.path.realpath(path), os.path.realpath(base))
    except ValueError:
        return False          # drives distintos no Windows, p.ex.
    return rel == "." or not rel.startswith("..")


def emite_aviso(msg: str) -> None:
    """Aviso com exit 0: JSON no stdout. A doc de hooks diz: "Claude never sees
    stderr from a hook that exits 0". `systemMessage` mostra ao usuario;
    `hookSpecificOutput.additionalContext` chega ao Claude, junto do resultado
    da ferramenta (PostToolUse aceita o campo)."""
    print(json.dumps({
        "systemMessage": msg,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        },
    }))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    aviso = None
    try:
        if str(os.environ.get("TDD_GUARD", "")).lower() == "off":
            return 0
        fp = c.extract_file_path(data)
        if not fp:
            return 0
        # Ancora a execucao no cwd da SESSAO (mesmo payload que os demais hooks
        # usam). So roda a suite se o arquivo editado estiver sob esse cwd; um
        # arquivo de projeto vizinho (com seu proprio .claude/tdd-guard.json)
        # nao dispara o test_command desta sessao. Sem cwd no payload, mantem
        # o comportamento anterior (nao usa os.getcwd() como cerca, pois seria
        # o cwd do runner do hook, nao o da sessao).
        session_cwd = (data.get("cwd") or "").strip()
        if session_cwd and not _under(fp, session_cwd):
            return 0          # arquivo fora do cwd da sessao; nao roda a suite
        start = os.path.dirname(os.path.realpath(fp)) or os.getcwd()
        root, cfg, motivo = c.load_config(start)
        if cfg is None:
            if motivo:
                # Config existe e esta invalida: o runner NAO roda a suite. Avisa
                # em JSON (exit 0) em vez de ficar inerte em silencio.
                emite_aviso(
                    f"TDD runner: config ignorada ({motivo}). O guard nao esta "
                    "ativo neste projeto ate a config ser corrigida.")
            return 0
        rel = os.path.relpath(os.path.realpath(fp), root)
        if c.classify(rel, cfg) not in ("production", "test"):
            return 0          # nada relevante mudou; nao roda a suite
        state = run_suite(cfg, root)
        c.write_state(root, state)
        if not state.get("ran"):
            aviso = f"TDD runner: testes nao rodaram ({state.get('reason')})."
    except Exception as e:
        aviso = f"TDD runner: erro interno ignorado ({e})."
    if aviso:
        emite_aviso(aviso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
