import subprocess
import tdd_runner as r


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_run_suite_red_when_nonzero():
    def fake(cmd, **kw):
        return _FakeProc(1, "=== 1 failed, 2 passed ===")
    st = r.run_suite({"test_command": "pytest", "timeout_sec": 30}, "/proj", fake)
    assert st["ran"] is True
    assert st["has_red"] is True
    assert st["exit_code"] == 1
    assert st["totals"] == {"passed": 2, "failed": 1}


def test_run_suite_green_when_zero():
    def fake(cmd, **kw):
        return _FakeProc(0, "=== 3 passed ===")
    st = r.run_suite({"test_command": "pytest", "timeout_sec": 30}, "/proj", fake)
    assert st["has_red"] is False


def test_run_suite_uses_fast_command_when_present():
    seen = {}
    def fake(cmd, **kw):
        seen["cmd"] = cmd
        return _FakeProc(0)
    r.run_suite({"test_command": "slow", "fast_command": "fast",
                 "timeout_sec": 30}, "/proj", fake)
    assert seen["cmd"] == "fast"


def test_run_suite_file_not_found_handler():
    # handler defensivo: FileNotFoundError nao dispara com shell=True, mas cobre shell=False futuro
    def fake(cmd, **kw):
        raise FileNotFoundError("no such file")
    st = r.run_suite({"test_command": "naoexiste", "timeout_sec": 30}, "/proj", fake)
    assert st["ran"] is False


def test_run_suite_timeout_is_not_ran():
    def fake(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd="x", timeout=30)
    st = r.run_suite({"test_command": "x", "timeout_sec": 30}, "/proj", fake)
    assert st["ran"] is False


def test_run_suite_command_not_found_is_not_ran():
    def fake(cmd, **kw):
        return _FakeProc(127, "", "sh: pytst: command not found")
    st = r.run_suite({"test_command": "pytst", "timeout_sec": 30}, "/proj", fake)
    assert st["ran"] is False


def test_run_suite_not_executable_is_not_ran():
    def fake(cmd, **kw):
        return _FakeProc(126)
    st = r.run_suite({"test_command": "x", "timeout_sec": 30}, "/proj", fake)
    assert st["ran"] is False


def test_run_suite_no_command_is_not_ran():
    st = r.run_suite({"timeout_sec": 30}, "/proj", lambda *a, **k: _FakeProc(0))
    assert st["ran"] is False


# ---------------------------------------------------------------------------
# Task 10: Integracao real — ciclo red -> green
# ---------------------------------------------------------------------------
import json
import os
import sys

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_hook(script, payload, home):
    import site
    env = dict(os.environ)
    env["HOME"] = home
    # Preserva site-packages do usuario real para que pytest seja importavel
    # mesmo quando HOME aponta para tmp_path (que nao tem .local/lib)
    user_site = site.getusersitepackages()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{user_site}:{existing}" if existing else user_site
    return subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, script)],
        input=json.dumps(payload), text=True, capture_output=True, env=env,
    )


def test_full_cycle_red_then_green(tmp_path):
    import pytest
    check = subprocess.run([sys.executable, "-m", "pytest", "--version"],
                           capture_output=True)
    if check.returncode != 0:
        pytest.skip("pytest indisponivel no subprocess; pulando integracao")

    # Projeto pytest minimo com config opt-in
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "tdd-guard.json").write_text(
        json.dumps({"preset": "python-pytest", "timeout_sec": 60}))
    (tmp_path / "tests").mkdir()
    # conftest.py vazio na raiz garante que pytest adicione rootdir ao sys.path
    (tmp_path / "conftest.py").write_text("")

    # Teste que importa funcao ainda inexistente -> RED
    (tmp_path / "tests" / "test_soma.py").write_text(
        "from soma import soma\n\ndef test_soma():\n    assert soma(2, 3) == 5\n")

    payload_test = {"tool_name": "Write",
                    "tool_input": {"file_path": str(tmp_path / "tests" / "test_soma.py")}}
    proc = _run_hook("tdd_runner.py", payload_test, str(tmp_path))
    assert proc.returncode == 0   # runner nunca quebra o fluxo

    import hashlib
    h = hashlib.sha256(os.path.realpath(str(tmp_path)).encode()).hexdigest()[:16]
    found = str(tmp_path / ".claude" / "state" / "tdd-guard" / h / "last-run.json")
    assert os.path.exists(found), f"estado nao gravado em {found}"

    st = json.load(open(found))
    assert st["ran"] is True and st["has_red"] is True   # RED confirmado

    # Implementa soma -> GREEN
    (tmp_path / "soma.py").write_text("def soma(a, b):\n    return a + b\n")
    payload_prod = {"tool_name": "Write",
                    "tool_input": {"file_path": str(tmp_path / "soma.py")}}
    _run_hook("tdd_runner.py", payload_prod, str(tmp_path))

    st = json.load(open(found))
    assert st["ran"] is True and st["has_red"] is False  # GREEN confirmado
