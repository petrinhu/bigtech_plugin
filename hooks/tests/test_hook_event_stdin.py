"""hookEventName sai do `hook_event_name` do stdin, com o valor atual de fallback.

O host informa o evento no payload. Os hooks do bigtech ecoam esse nome e
caem no valor fixo ("SessionStart" ou "UserPromptSubmit") quando o campo
falta, nao e texto ou nao e um identificador simples. O valor sentinela
("EventoSentinela") prova que o nome vem do stdin e nao do codigo.
"""
import io
import json
import sys

import bigtech_porte_reminder as p
import bigtech_reinforce as r
import bigtech_session_init as s
import pytest

SENTINELA = "EventoSentinela"


def _hso(monkeypatch, capsys, modulo, payload):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    modulo.main()
    saida = capsys.readouterr().out
    assert saida.strip(), "o hook deveria ter emitido saida"
    return json.loads(saida)["hookSpecificOutput"]


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".bigtech-porte").write_text("porte=early\n", encoding="utf-8")
    return str(proj)


@pytest.mark.parametrize("modulo, padrao, extra", [
    (s, "SessionStart", {}),
    (p, "SessionStart", {}),
    (r, "UserPromptSubmit", {"prompt": "ajusta o lint"}),
])
def test_stdin_fornece_o_nome_do_evento(ambiente, monkeypatch, capsys,
                                        modulo, padrao, extra):
    payload = {"cwd": ambiente, "hook_event_name": SENTINELA, **extra}
    assert _hso(monkeypatch, capsys, modulo, payload)["hookEventName"] == SENTINELA


@pytest.mark.parametrize("modulo, padrao, extra", [
    (s, "SessionStart", {}),
    (p, "SessionStart", {}),
    (r, "UserPromptSubmit", {"prompt": "ajusta o lint"}),
])
@pytest.mark.parametrize("campo", [
    "AUSENTE",         # campo nao enviado
    42,                # nao-string
    "Evento Ruim!",    # fora de identificador simples
    "",                # vazio
])
def test_sem_nome_valido_cai_no_valor_atual(ambiente, monkeypatch, capsys,
                                            modulo, padrao, extra, campo):
    payload = {"cwd": ambiente, **extra}
    if campo != "AUSENTE":
        payload["hook_event_name"] = campo
    assert _hso(monkeypatch, capsys, modulo, payload)["hookEventName"] == padrao
