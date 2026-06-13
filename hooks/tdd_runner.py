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
    if proc.returncode in (126, 127):
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


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        if str(os.environ.get("TDD_GUARD", "")).lower() == "off":
            return 0
        fp = c.extract_file_path(data)
        if not fp:
            return 0
        start = os.path.dirname(os.path.realpath(fp)) or os.getcwd()
        root, cfg = c.load_config(start)
        if cfg is None:
            return 0
        rel = os.path.relpath(os.path.realpath(fp), root)
        if c.classify(rel, cfg) not in ("production", "test"):
            return 0          # nada relevante mudou; nao roda a suite
        state = run_suite(cfg, root)
        c.write_state(root, state)
        if not state.get("ran"):
            print(f"TDD runner: testes nao rodaram ({state.get('reason')}).",
                  file=sys.stderr)
    except Exception as e:
        print(f"TDD runner: erro interno ignorado ({e}).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
