"""Testes do hook SessionStart `bigtech_porte_reminder.py` (AUD-F08).

Exercita a função pura `is_code_project` (detecção de projeto de código por
manifesto/glob) com asserts de VALOR, mais os dois ramos de `main()`
(já classificado vs. código sem porte vs. silêncio) e um contrato via subprocess
(exit 0 + JSON parseável).

`main()` é rodada in-process com stdin simulado e stdout capturado, sempre com
`cwd` explícito no payload para não depender do os.getcwd() do runner.
"""
import io
import json
import os
import subprocess
import sys

import bigtech_porte_reminder as p

MARKER = p.MARKER     # ".bigtech-porte"


# ---------------------------------------------------------------------------
# is_code_project: equivalence partitioning sobre marcadores e globs.
# ---------------------------------------------------------------------------
def test_is_code_project_falso_em_dir_vazio(tmp_path):
    assert p.is_code_project(str(tmp_path)) is False


def test_is_code_project_falso_so_com_claude_md_ou_git(tmp_path):
    # CLAUDE.md / .git sozinhos são amplos demais e NÃO contam como projeto.
    (tmp_path / "CLAUDE.md").write_text("doc\n")
    (tmp_path / ".git").mkdir()
    assert p.is_code_project(str(tmp_path)) is False


def test_is_code_project_verdadeiro_por_manifesto(tmp_path):
    # Cobre um representante de cada classe de manifesto exato.
    for marker in ("CMakeLists.txt", "package.json", "pyproject.toml",
                   "go.mod", "Cargo.toml", "Makefile"):
        d = tmp_path / marker.replace(".", "_")
        d.mkdir()
        (d / marker).write_text("x\n")
        assert p.is_code_project(str(d)) is True, marker


def test_is_code_project_verdadeiro_por_glob(tmp_path):
    # Marcadores por extensão (ex.: *.csproj, *.pro).
    for fname in ("App.csproj", "projeto.pro", "Solution.sln"):
        d = tmp_path / fname.replace(".", "_")
        d.mkdir()
        (d / fname).write_text("x\n")
        assert p.is_code_project(str(d)) is True, fname


# ---------------------------------------------------------------------------
# Helper para main() in-process.
# ---------------------------------------------------------------------------
def _run_main(monkeypatch, payload):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = p.main()
    return rc, captured.getvalue()


# --- main(): projeto JÁ classificado (.bigtech-porte presente) --------------

def test_main_ancora_modo_quando_ja_classificado(tmp_path, monkeypatch):
    (tmp_path / MARKER).write_text("porte=scale\n")
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path)})
    assert rc == 0
    obj = json.loads(out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]
    assert obj["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "porte=scale" in ctx          # porte lido do marcador
    assert "Cosimo" in ctx               # ancora o orquestrador


def test_main_classificado_porte_default_quando_marcador_sem_campo(tmp_path, monkeypatch):
    (tmp_path / MARKER).write_text("sem campo de porte aqui\n")
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path)})
    assert rc == 0
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "porte=classificado" in ctx   # fallback seguro


# --- main(): projeto de código SEM porte -> lembra /bigtech -----------------

def test_main_lembra_bigtech_em_projeto_de_codigo_sem_porte(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path)})
    assert rc == 0
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "/bigtech" in ctx
    assert ".bigtech-porte" in ctx       # instrui a gravar o marcador


# --- main(): silêncio em dir que não é projeto de código --------------------

def test_main_silencia_em_dir_nao_codigo(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("doc\n")
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path)})
    assert rc == 0
    assert out == ""


def test_main_cwd_inexistente_exit_0_silencioso(tmp_path, monkeypatch):
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path / "fantasma")})
    assert rc == 0
    assert out == ""


# ---------------------------------------------------------------------------
# Contrato end-to-end via subprocess: exit 0 + JSON parseável.
# ---------------------------------------------------------------------------
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_subprocess_classificado_exit_0_json(tmp_path):
    (tmp_path / MARKER).write_text("porte=early\n")
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_porte_reminder.py")],
        input=json.dumps({"cwd": str(tmp_path)}),
        text=True, capture_output=True,
    )
    assert proc.returncode == 0
    obj = json.loads(proc.stdout)
    assert obj["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "porte=early" in obj["hookSpecificOutput"]["additionalContext"]


def test_subprocess_stdin_invalido_exit_0(tmp_path):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_porte_reminder.py")],
        input="nao eh json", text=True, capture_output=True,
    )
    assert proc.returncode == 0


# ---------------------------------------------------------------------------
# FAIL-OPEN: stdin com JSON VALIDO porem NAO-dict (null, [], "x", 12).
# Antes do fix, data.get(...) lancava AttributeError -> exit 1 (bloqueava).
# ---------------------------------------------------------------------------
import pytest   # noqa: E402

NON_DICT_JSON = ("null", "[]", '"x"', "12", "[1, 2, 3]", "true", "3.14")


def _run_main_raw(monkeypatch, raw_text):
    """Como _run_main, mas injeta o texto bruto de stdin (sem json.dumps)."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(raw_text))
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = p.main()
    return rc, captured.getvalue()


@pytest.mark.parametrize("raw", NON_DICT_JSON)
def test_main_json_valido_nao_dict_exit_0(tmp_path, monkeypatch, raw):
    # Sem cwd no payload (nao e dict): cai no os.getcwd(); apontamos para um
    # diretorio sem marcadores -> silencio, e o essencial: NAO quebra (exit 0).
    monkeypatch.chdir(tmp_path)
    rc, out = _run_main_raw(monkeypatch, raw)
    assert rc == 0
    assert out == ""


@pytest.mark.parametrize("raw", NON_DICT_JSON)
def test_subprocess_json_valido_nao_dict_exit_0(raw):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_porte_reminder.py")],
        input=raw, text=True, capture_output=True,
    )
    assert proc.returncode == 0
