import json
import os
import subprocess
import sys
import tdd_guard as g
import tdd_common as c


def _project(tmp_path, raw=None):
    raw = raw or {"preset": "python-pytest"}
    d = tmp_path / ".claude"
    d.mkdir()
    (d / "tdd-guard.json").write_text(json.dumps(raw))
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    return tmp_path


def _write(tmp_path, name="Write", fp="src/x.py"):
    return {"tool_name": name, "tool_input": {"file_path": str(tmp_path / fp)}}


def test_no_config_is_inert(tmp_path):
    code, _ = g.evaluate({"tool_input": {"file_path": str(tmp_path / "x.py")}}, {})
    assert code == 0


def test_guard_off_permits(tmp_path, monkeypatch):
    _project(tmp_path)
    code, _ = g.evaluate(_write(tmp_path), {"TDD_GUARD": "off"})
    assert code == 0


def test_writing_test_is_always_allowed(tmp_path, monkeypatch):
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    code, _ = g.evaluate(_write(tmp_path, fp="tests/test_x.py"), {})
    assert code == 0


def test_nested_conftest_is_test_not_blocked(tmp_path, monkeypatch):
    """conftest.py aninhado (pkg/conftest.py) e arquivo de TESTE: nunca deve
    ser bloqueado, mesmo sem estado de teste registrado (preset python-pytest).
    Antes do fix, so o conftest.py da raiz era reconhecido."""
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "pkg").mkdir()
    code, _ = g.evaluate(_write(tmp_path, fp="pkg/conftest.py"), {})
    assert code == 0          # classificado como teste -> permite


def test_production_blocked_when_state_absent(tmp_path, monkeypatch):
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    code, msg = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 2
    assert "teste" in msg.lower()


def test_production_allowed_when_red(tmp_path, monkeypatch):
    root = _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    c.write_state(os.path.realpath(str(root)), {"ran": True, "has_red": True})
    code, _ = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 0


def test_production_blocked_when_all_green(tmp_path, monkeypatch):
    root = _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    c.write_state(os.path.realpath(str(root)), {"ran": True, "has_red": False})
    code, msg = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 2
    assert "refactor" in msg.lower()


def test_refactor_toggle_permits_green(tmp_path, monkeypatch):
    root = _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    c.write_state(os.path.realpath(str(root)), {"ran": True, "has_red": False})
    code, _ = g.evaluate(_write(tmp_path, fp="src/x.py"), {"TDD_PHASE": "refactor"})
    assert code == 0


def test_runner_broken_fails_open(tmp_path, monkeypatch):
    root = _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    c.write_state(os.path.realpath(str(root)), {"ran": False, "reason": "timeout"})
    code, msg = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 0
    assert msg != ""        # avisa, mas nao bloqueia


def test_state_io_error_fails_open(tmp_path, monkeypatch):
    """read_state lancando OSError (HOME read-only, sem permissao, disco cheio)
    NAO pode bloquear producao legitima: o guard FAIL-OPEN (exit 0) com aviso.
    Distinto de estado AUSENTE (None), que continua bloqueando (exit 2)."""
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    def boom(_root):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(c, "read_state", boom)
    code, msg = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 0          # NAO bloqueia
    assert msg != ""          # mas avisa em stderr


def test_state_io_oserror_fails_open(tmp_path, monkeypatch):
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    def boom(_root):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(c, "read_state", boom)
    code, _ = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 0


def test_state_absent_still_blocks(tmp_path, monkeypatch):
    """Contraste explicito: estado AUSENTE (None) continua bloqueando (exit 2).
    Garante que o fix de I/O nao afrouxou o caminho legitimo de bloqueio."""
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(c, "read_state", lambda _root: None)
    code, msg = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 2
    assert "teste" in msg.lower()


def test_excluded_file_permitted(tmp_path, monkeypatch):
    _project(tmp_path, {"preset": "python-pytest", "exclude_globs": ["src/**"]})
    monkeypatch.setenv("HOME", str(tmp_path))
    code, _ = g.evaluate(_write(tmp_path, fp="src/x.py"), {})
    assert code == 0


def test_file_outside_root_is_inert(tmp_path, monkeypatch):
    """Arquivo fora da raiz do projeto (relpath começa com '..') retorna 0 sem bloquear."""
    _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    # fora.py está no diretório pai de tmp_path, fora da raiz do projeto
    outside_fp = str(tmp_path.parent / "fora.py")
    data = {"tool_input": {"file_path": outside_fp}}
    code, msg = g.evaluate(data, {})
    assert code == 0


# ---------------------------------------------------------------------------
# Task 8: contrato end-to-end via subprocess
# ---------------------------------------------------------------------------

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_guard(payload, env):
    full = dict(os.environ)
    full.update(env)
    return subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "tdd_guard.py")],
        input=json.dumps(payload), text=True, capture_output=True, env=full,
    )


def test_subprocess_blocks_production_green(tmp_path, monkeypatch):
    root = _project(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))   # processo de teste e subprocess no mesmo HOME
    c.write_state(os.path.realpath(str(root)), {"ran": True, "has_red": False})
    proc = _run_guard(_write(tmp_path, fp="src/x.py"), {"HOME": str(tmp_path)})
    assert proc.returncode == 2
    assert "refactor" in proc.stderr.lower()


def test_subprocess_invalid_stdin_fails_open(tmp_path):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "tdd_guard.py")],
        input="nao eh json", text=True, capture_output=True,
    )
    assert proc.returncode == 0
