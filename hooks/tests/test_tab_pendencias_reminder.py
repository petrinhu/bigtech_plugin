"""Testes do hook SessionStart `tab_pendencias_reminder.py` (AUD-F07).

Cobre o gatilho SEQUENCIAL anti-ruído: só dispara o lembrete de /tab_pendencias
quando o projeto JÁ foi classificado (existe `.bigtech-porte` na raiz) mas ainda
NÃO tem a tabela de pendências (`TODO.md`). Em qualquer outro caso, silêncio.
E sempre exit 0 (lembrete nunca bloqueia o turno).

Estratégia:
- `main()` é exercitada in-process capturando stdout (capsys) e isolando o cwd
  com monkeypatch.chdir, porque o hook usa `os.getcwd()` como fallback quando o
  payload não traz `cwd`. Para forçar um payload sem `cwd` válido, apontamos o
  diretório corrente para um caminho controlado.
- Um teste de contrato roda o hook via subprocess (returncode 0).
"""
import io
import json
import os
import subprocess
import sys

import tab_pendencias_reminder as t

PORTE = t.PORTE_MARKER     # ".bigtech-porte"
TODO = t.TODO_FILE         # "TODO.md"


# ---------------------------------------------------------------------------
# Helper: roda main() in-process com um stdin simulado e devolve (rc, stdout).
# ---------------------------------------------------------------------------
def _run_main(monkeypatch, payload_text):
    """Substitui sys.stdin pelo texto dado e captura o stdout de main()."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload_text))
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = t.main()
    return rc, captured.getvalue()


# --- Entrada degenerada: nunca quebra, nunca fala ---------------------------

def test_stdin_malformado_exit_0_sem_stdout(tmp_path, monkeypatch):
    # cwd corrente vazio de marcadores: garante que, mesmo se o fallback
    # os.getcwd() for usado, não há gatilho.
    monkeypatch.chdir(tmp_path)
    rc, out = _run_main(monkeypatch, "isto nao eh json {")
    assert rc == 0
    assert out == ""


def test_stdin_vazio_exit_0(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc, out = _run_main(monkeypatch, "")
    assert rc == 0
    assert out == ""


def test_cwd_ausente_no_payload_usa_corrente_e_silencia(tmp_path, monkeypatch):
    # Payload válido porém SEM a chave 'cwd': o hook cai no os.getcwd().
    # Apontamos o corrente para um tmp_path sem marcadores -> silêncio.
    monkeypatch.chdir(tmp_path)
    rc, out = _run_main(monkeypatch, json.dumps({"hook_event_name": "SessionStart"}))
    assert rc == 0
    assert out == ""


def test_cwd_inexistente_exit_0_silencioso(tmp_path, monkeypatch):
    # cwd explícito apontando para diretório que não existe: isdir() falha,
    # retorna 0 sem stdout, sem tentar ler arquivos.
    ghost = str(tmp_path / "nao-existe")
    rc, out = _run_main(monkeypatch, json.dumps({"cwd": ghost}))
    assert rc == 0
    assert out == ""


# --- Gatilho POSITIVO: .bigtech-porte presente E sem TODO.md ----------------

def test_dispara_quando_porte_presente_e_sem_todo(tmp_path, monkeypatch):
    (tmp_path / PORTE).write_text("porte=early\n")
    # NÃO criamos TODO.md de propósito.
    rc, out = _run_main(monkeypatch, json.dumps({"cwd": str(tmp_path)}))
    assert rc == 0
    assert out.strip() != ""

    payload = json.loads(out)
    hso = payload["hookSpecificOutput"]
    assert hso["hookEventName"] == "SessionStart"
    # O lembrete deve direcionar explicitamente para a skill /tab_pendencias.
    assert "/tab_pendencias" in hso["additionalContext"]


# --- Gatilhos NEGATIVOS: silêncio ------------------------------------------

def test_silencia_sem_porte(tmp_path, monkeypatch):
    # Sem .bigtech-porte: quem lembra é o bigtech_porte_reminder (-> /bigtech).
    # Mesmo havendo (ou não) TODO.md, este hook cala.
    rc, out = _run_main(monkeypatch, json.dumps({"cwd": str(tmp_path)}))
    assert rc == 0
    assert out == ""


def test_silencia_com_porte_e_com_todo(tmp_path, monkeypatch):
    # Já classificado E já com a tabela: nada a lembrar.
    (tmp_path / PORTE).write_text("porte=scale\n")
    (tmp_path / TODO).write_text("# Pendencias\n")
    rc, out = _run_main(monkeypatch, json.dumps({"cwd": str(tmp_path)}))
    assert rc == 0
    assert out == ""


# ---------------------------------------------------------------------------
# Contrato end-to-end via subprocess: returncode 0 sempre.
# ---------------------------------------------------------------------------
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_hook(payload_text):
    return subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "tab_pendencias_reminder.py")],
        input=payload_text, text=True, capture_output=True,
    )


def test_subprocess_dispara_json_valido(tmp_path):
    (tmp_path / PORTE).write_text("porte=early\n")
    proc = _run_hook(json.dumps({"cwd": str(tmp_path)}))
    assert proc.returncode == 0
    obj = json.loads(proc.stdout)        # stdout é JSON parseável
    assert obj["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "/tab_pendencias" in obj["hookSpecificOutput"]["additionalContext"]


def test_subprocess_stdin_invalido_exit_0(tmp_path):
    # Garante o silent-fail também atravessando o processo real.
    proc = _run_hook("nao eh json")
    assert proc.returncode == 0
