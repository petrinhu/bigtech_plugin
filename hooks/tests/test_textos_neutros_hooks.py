"""Textos injetados pelos hooks do bigtech sao neutros (CONS-15c).

Nenhum hook se declara orquestrador nem autoridade sobre o modelo, e nenhum
manda desativar plugin do usuario. Os termos proibidos sao montados por
concatenacao para que este arquivo nao reintroduza o literal no repositorio.
"""
import io
import json
import sys

import bigtech_porte_reminder as p
import bigtech_reinforce as r
import bigtech_session_init as s
import pytest

PROIBIDOS = (
    "ORQUESTRADOR",
    "orquestrador",
    "assistente " + "generico",
    "drift" + "ar",
    "NAO responder",
    "DESATIVE",
)


def _saida(monkeypatch, capsys, modulo, payload):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    modulo.main()
    return capsys.readouterr().out


def _ctx(saida):
    if not saida.strip():
        return ""
    return json.loads(saida)["hookSpecificOutput"]["additionalContext"]


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Config do Claude Code isolada e projeto classificado."""
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".bigtech-porte").write_text("porte=early\n", encoding="utf-8")
    return {"cfg": cfg, "proj": proj}


def test_reforco_por_turno_sem_termos_proibidos(ambiente, monkeypatch, capsys):
    ctx = _ctx(_saida(monkeypatch, capsys, r,
                      {"cwd": str(ambiente["proj"]), "prompt": "ajusta o lint"}))
    assert ctx
    for termo in PROIBIDOS:
        assert termo not in ctx, termo
    assert "PLANEJADOR = Cosimo" in ctx
    assert "thread principal" in ctx


def test_roteamento_sem_termos_proibidos(tmp_path, monkeypatch, capsys):
    proj = tmp_path / "novo"
    proj.mkdir()
    ctx = _ctx(_saida(monkeypatch, capsys, r,
                      {"cwd": str(proj), "prompt": "montar o time c-level"}))
    assert ctx
    for termo in PROIBIDOS:
        assert termo not in ctx, termo
    assert "PLANEJADOR" in ctx


def test_porte_classificado_sem_termos_proibidos(ambiente, monkeypatch, capsys):
    ctx = _ctx(_saida(monkeypatch, capsys, p, {"cwd": str(ambiente["proj"])}))
    assert ctx
    for termo in PROIBIDOS:
        assert termo not in ctx, termo
    assert "PLANEJADOR = Cosimo" in ctx
    assert "thread principal" in ctx


def test_session_init_com_caveman_nao_manda_desativar(ambiente, monkeypatch, capsys):
    (ambiente["cfg"] / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"caveman@petrinhu": True}}), encoding="utf-8")
    ctx = _ctx(_saida(monkeypatch, capsys, s,
                      {"cwd": str(ambiente["proj"])}))
    assert "INCOMPATIBILIDADE DETECTADA" in ctx
    for termo in PROIBIDOS:
        assert termo not in ctx, termo
    assert "decisao" in ctx
