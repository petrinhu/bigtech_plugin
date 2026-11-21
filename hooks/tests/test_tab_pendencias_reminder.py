import json
import os

import pytest
import tab_pendencias_reminder as t

# Apos CONS-14 o plugin so emite o gatilho 4 (tempo de sessao) e carimba a
# sessao. CRIAR e STALENESS sao do produto `tab_pendencias`, registrado
# diretamente em hooks.json (ver test_hooks_json_sessionstart.py).


@pytest.fixture(autouse=True)
def _modo_padrao(monkeypatch):
    """Isola a suite da maquina: o modo do usuario nao altera os testes."""
    monkeypatch.delenv(t.MODO_ENV, raising=False)


def _proj(tmp_path, porte=True, todo=True):
    if porte:
        (tmp_path / t.PORTE_MARKER).write_text("early\n")
    if todo:
        (tmp_path / t.TODO_FILE).write_text("# TODO\n")
    return {"cwd": str(tmp_path)}


# ------------------------------ carimbo de sessao ---------------------------

def test_carimbo_roundtrip_e_nao_sobrescreve(tmp_path):
    sd = str(tmp_path)
    t.carimbar_sessao("sess-1", 100.0, state_dir=sd)
    t.carimbar_sessao("sess-1", 999.0, state_dir=sd)  # nao sobrescreve start
    estado = t.ler_sessao("sess-1", state_dir=sd)
    assert estado["start"] == 100.0
    assert estado["avisado"] is False


def test_limpa_sessoes_antigas(tmp_path):
    sd = str(tmp_path)
    t.carimbar_sessao("velha", 0.0, state_dir=sd)
    p = t.caminho_sessao("velha", state_dir=sd)
    os.utime(p, (0, 0))  # mtime epoch -> bem antiga
    t.limpar_sessoes_antigas(t.STATE_TTL_S + 10, state_dir=sd)
    assert not os.path.isfile(p)


# ------------------------------ gatilho 4: tempo de sessao ------------------

def test_userprompt_avisa_apos_limiar_uma_vez(tmp_path):
    sd = str(tmp_path)
    data = _proj(tmp_path)
    data["session_id"] = "abc"
    t.carimbar_sessao("abc", 0.0, state_dir=sd)
    # 3h depois (> default 2h): avisa
    msg = t.avaliar_userprompt(data, 3 * 3600.0, state_dir=sd)
    assert msg and "higiene" in msg
    assert "decisao do usuario" in msg
    assert "so se a prioridade" not in msg
    assert "/bigtech:tab_pendencias --reorder" in msg
    # segunda chamada na mesma sessao: silencioso (avisado=True)
    assert t.avaliar_userprompt(data, 4 * 3600.0, state_dir=sd) is None


def test_userprompt_silencioso_antes_do_limiar(tmp_path):
    sd = str(tmp_path)
    data = _proj(tmp_path)
    data["session_id"] = "abc"
    t.carimbar_sessao("abc", 0.0, state_dir=sd)
    assert t.avaliar_userprompt(data, 1 * 3600.0, state_dir=sd) is None


def test_userprompt_sem_estado_e_inerte(tmp_path):
    data = _proj(tmp_path)
    data["session_id"] = "nunca-carimbada"
    assert t.avaliar_userprompt(data, 9e9, state_dir=str(tmp_path)) is None


def test_userprompt_exige_porte_e_todo(tmp_path):
    sd = str(tmp_path)
    data = _proj(tmp_path, porte=True, todo=False)  # sem TODO.md
    data["session_id"] = "abc"
    t.carimbar_sessao("abc", 0.0, state_dir=sd)
    assert t.avaliar_userprompt(data, 9e9, state_dir=sd) is None


def test_off_em_config_silencia_gatilho_4(tmp_path):
    sd = str(tmp_path)
    data = _proj(tmp_path, porte=True, todo=True)
    (tmp_path / t.CONFIG_FILE).write_text(json.dumps({"off": True}))
    data["session_id"] = "abc"
    t.carimbar_sessao("abc", 0.0, state_dir=sd)
    assert t.avaliar_userprompt(data, 10 * 3600.0, state_dir=sd) is None


def test_modo_off_silencia_tudo(tmp_path, monkeypatch):
    monkeypatch.setenv(t.MODO_ENV, "off")
    sd = str(tmp_path / "state2")
    os.makedirs(sd, exist_ok=True)
    data = _proj(tmp_path, porte=True, todo=True)
    data["session_id"] = "s-off-1"
    t.carimbar_sessao("s-off-1", 0.0, state_dir=sd)
    assert t.avaliar_userprompt(data, 10 * 3600.0, state_dir=sd) is None


def test_modo_invalido_cai_em_auto(monkeypatch):
    monkeypatch.setenv(t.MODO_ENV, "lixo")
    assert t.modo_operacao() == "auto"


# ------------------- lembrete unico: texto sempre com prefixo -----------------

def test_plugin_nao_emite_criar_nem_staleness(tmp_path):
    """CRIAR e STALENESS sao do produto; o plugin nao tem mais esses gatilhos."""
    assert not hasattr(t, "avaliar_sessionstart")
    assert not hasattr(t, "msg_staleness")
    assert not hasattr(t, "produto_registrado")


# ------------- CONS-R11: Windows nao tem bits de modo POSIX -----------------

def test_estado_legivel_em_sistema_sem_bits_posix(tmp_path, monkeypatch):
    """No Windows os.stat devolve 0o777: o bit de grupo/outros nao diz nada
    sobre o dono. O hook precisa ler o proprio carimbo mesmo assim."""
    monkeypatch.setattr(t, "_modo_posix", lambda: False)
    sd = tmp_path / "estado"
    sd.mkdir()
    os.chmod(sd, 0o777)
    t.carimbar_sessao("win", 100.0, state_dir=str(sd))
    estado = t.ler_sessao("win", state_dir=str(sd))
    assert estado is not None
    assert estado["start"] == 100.0
