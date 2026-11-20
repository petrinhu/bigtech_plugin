"""Formato de saida do hook do PRODUTO tab_pendencias (CONS-14A).

Contrato oficial (https://code.claude.com/docs/en/hooks): `additionalContext`
vai DENTRO de `hookSpecificOutput`, junto de `hookEventName` igual ao nome do
evento. Nenhum campo de contexto no topo do JSON; os campos de topo
documentados sao `continue`, `stopReason`, `suppressOutput`, `systemMessage`
e `terminalSequence`.

Roda o hook de verdade, em subprocess, com payload JSON do evento e perfil
descartavel (HOME, CLAUDE_CONFIG_DIR e XDG_RUNTIME_DIR em tmp_path). Nenhum
teste importa o modulo: a fronteira testada e o stdout do processo.
"""
import json
import os
import subprocess
import sys

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HOOKS_DIR)
HOOK_PRODUTO = os.path.join(
    ROOT, "skills", "tab_pendencias", "tools", "hooks", "tab_pendencias_reminder.py"
)
# Campos de topo do JSON de saida de hook, segundo a doc oficial: os universais
# (continue, stopReason, suppressOutput, systemMessage, terminalSequence) e o
# envelope `hookSpecificOutput`. `additionalContext` NAO esta na lista.
TOPO_PERMITIDO = {"continue", "stopReason", "suppressOutput", "systemMessage",
                  "terminalSequence", "hookSpecificOutput"}


def _env(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "BIGTECH_TAB_REMINDER"}
    for nome in ("home", "cfg", "xdg", "tmp"):
        (tmp_path / nome).mkdir(exist_ok=True)
    env["HOME"] = str(tmp_path / "home")
    env["CLAUDE_CONFIG_DIR"] = str(tmp_path / "cfg")
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "xdg")
    env["TMPDIR"] = str(tmp_path / "tmp")
    return env


def _rodar(evento, cwd, tmp_path):
    payload = json.dumps({"hook_event_name": evento, "cwd": str(cwd),
                          "session_id": f"formato-{evento}"})
    proc = subprocess.run(
        [sys.executable, HOOK_PRODUTO], input=payload, text=True,
        capture_output=True, env=_env(tmp_path), cwd=str(cwd), timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def _repo_git_sem_todo(path):
    """Gatilho CRIAR: git sem TODO.md (sinal de SessionStart)."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)


def _repo_com_inbox(path):
    """Gatilho de inbox concorrente (sinal de UserPromptSubmit)."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "TODO.md").write_text("# TODO\n", encoding="utf-8")
    (path / "inbox").mkdir()
    (path / "inbox" / "x.md").write_text("pendencia\n", encoding="utf-8")


def _exige_formato_oficial(saida, evento):
    assert "additionalContext" not in saida, (
        f"additionalContext no topo do JSON: {saida}"
    )
    assert set(saida) - TOPO_PERMITIDO == set(), f"campos de topo invalidos: {saida}"
    hso = saida.get("hookSpecificOutput")
    assert isinstance(hso, dict), f"falta hookSpecificOutput: {saida}"
    assert hso.get("hookEventName") == evento, hso
    ctx = hso.get("additionalContext")
    assert isinstance(ctx, str) and ctx.strip(), hso
    assert set(hso) == {"hookEventName", "additionalContext"}, hso


def test_session_start_emite_additional_context_so_dentro_de_hook_specific(tmp_path):
    repo = tmp_path / "proj"
    _repo_git_sem_todo(repo)
    saida = _rodar("SessionStart", repo, tmp_path)
    _exige_formato_oficial(saida, "SessionStart")
    assert "TAB_TODO_CREATE_REQUIRED" in saida["hookSpecificOutput"]["additionalContext"]


def test_user_prompt_submit_emite_additional_context_so_dentro_de_hook_specific(tmp_path):
    repo = tmp_path / "proj"
    _repo_com_inbox(repo)
    saida = _rodar("UserPromptSubmit", repo, tmp_path)
    _exige_formato_oficial(saida, "UserPromptSubmit")
    assert "TAB_CONCURRENT_INBOX_PRESENT" in saida["hookSpecificOutput"]["additionalContext"]


def test_sem_sinal_devolve_so_continue(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()  # nao e git e nao tem TODO.md: nenhum sinal
    saida = _rodar("SessionStart", repo, tmp_path)
    assert saida == {"continue": True}
