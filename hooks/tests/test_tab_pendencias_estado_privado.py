"""Carimbo de sessao do hook da raiz em diretorio privado do usuario (CONS-14B).

Contrato testado:
  - o carimbo nunca vai para `tempfile.gettempdir()` (/tmp e compartilhado);
  - o diretorio de estado e `$XDG_RUNTIME_DIR/<nome>` ou `~/.cache/<nome>`,
    criado com modo 0700;
  - symlink no diretorio e diretorio de outro dono sao recusados: nada e
    gravado e nenhuma excecao escapa (fail-open).

Todo teste isola HOME, XDG_RUNTIME_DIR e o tempdir compartilhado em tmp_path.
Nada e escrito fora dele.
"""

import io
import json
import os
import stat
import tempfile

import pytest
import tab_pendencias_reminder as t

NOME_DIR = "bigtech_tab_sessao"  # diretorio dedicado, diferente do da skill


@pytest.fixture(autouse=True)
def _modo_padrao(monkeypatch):
    monkeypatch.delenv(t.MODO_ENV, raising=False)


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """HOME e XDG em tmp_path; tempdir compartilhado simulado em tmp_path."""
    home = tmp_path / "home"
    home.mkdir()
    run = tmp_path / "run"
    run.mkdir(mode=0o700)
    compartilhado = tmp_path / "tmp_compartilhado"
    compartilhado.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(run))
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(compartilhado))
    return {"home": home, "run": run, "compartilhado": compartilhado}


def _vazio(d):
    return os.listdir(d) == []


# ------------------------------ local do estado ------------------------------

def test_carimbo_nao_vai_para_tempdir_compartilhado(ambiente):
    t.carimbar_sessao("s1", 1.0)
    p = t.caminho_sessao("s1")
    assert p is not None
    assert p.startswith(str(ambiente["run"]))
    assert os.path.isfile(p)
    assert _vazio(ambiente["compartilhado"])


def test_sem_xdg_cai_em_home_cache(ambiente, monkeypatch):
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    t.carimbar_sessao("s2", 1.0)
    p = t.caminho_sessao("s2")
    assert p.startswith(os.path.join(str(ambiente["home"]), ".cache", NOME_DIR))
    assert os.path.isfile(p)
    assert _vazio(ambiente["compartilhado"])


def test_diretorio_criado_com_modo_0700(ambiente):
    t.carimbar_sessao("s3", 1.0)
    d = os.path.dirname(t.caminho_sessao("s3"))
    assert stat.S_IMODE(os.stat(d).st_mode) == 0o700


def test_diretorio_frouxo_do_proprio_usuario_e_fechado(ambiente):
    d = ambiente["run"] / NOME_DIR
    d.mkdir(mode=0o755)
    os.chmod(d, 0o755)
    t.carimbar_sessao("s4", 1.0)
    assert stat.S_IMODE(os.stat(d).st_mode) == 0o700


# ----------------------- recusa: symlink e dono alheio -----------------------

def test_symlink_no_diretorio_e_recusado_sem_gravar(ambiente, tmp_path):
    alvo = tmp_path / "alvo"
    alvo.mkdir()
    (ambiente["run"] / NOME_DIR).symlink_to(alvo, target_is_directory=True)
    t.carimbar_sessao("s5", 1.0)  # nao levanta
    assert _vazio(alvo)
    assert _vazio(ambiente["compartilhado"])
    assert t.ler_sessao("s5") is None


def test_diretorio_de_outro_dono_e_recusado_sem_gravar(ambiente, monkeypatch):
    d = ambiente["run"] / NOME_DIR
    d.mkdir(mode=0o700)
    uid_real = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: uid_real + 1)
    t.carimbar_sessao("s6", 1.0)  # nao levanta
    assert _vazio(d)
    assert _vazio(ambiente["compartilhado"])


def test_carimbo_symlink_nao_e_seguido(ambiente, tmp_path):
    vitima = tmp_path / "vitima.txt"
    vitima.write_text("NAO PODE MUDAR\n")
    d = ambiente["run"] / NOME_DIR
    d.mkdir(mode=0o700)
    os.symlink(vitima, t.caminho_sessao("s7"))
    t.carimbar_sessao("s7", 1.0)
    assert vitima.read_text() == "NAO PODE MUDAR\n"
    assert t.ler_sessao("s7") is None


def test_session_start_com_diretorio_recusado_sai_zero(ambiente, tmp_path, monkeypatch, capsys):
    alvo = tmp_path / "alvo2"
    alvo.mkdir()
    (ambiente["run"] / NOME_DIR).symlink_to(alvo, target_is_directory=True)
    entrada = json.dumps({"hook_event_name": "SessionStart", "session_id": "s8",
                          "cwd": str(tmp_path)})
    monkeypatch.setattr("sys.stdin", io.StringIO(entrada))
    assert t.main() == 0
    assert _vazio(alvo)
    assert _vazio(ambiente["compartilhado"])
