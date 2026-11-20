"""Saida dos hooks em pipe com code page cp1252 (CONS-R11).

No Windows, um pipe de stdout usa o code page ANSI (cp1252) salvo PYTHONUTF8=1.
Um hook que escreve texto fora do cp1252 (o status de TODO.md, com ⏳ e 🔍)
levanta UnicodeEncodeError, e o fail-open engole a excecao: o hook sai 0 e
fica mudo. No Linux reproduzimos o pipe com PYTHONIOENCODING=cp1252 e lemos
a saida em bytes, como o host faz.
"""

import json
import subprocess

import pytest
from test_hooks_json_sessionstart import (
    _env,
    _mensagens,
    _repo_com_todos_os_sinais,
    _tab_commands,
)

CP1252 = { "PYTHONIOENCODING": "cp1252"}


@pytest.mark.parametrize("evento", ["SessionStart", "UserPromptSubmit"])
def test_hooks_do_produto_emitem_sinal_com_stdout_cp1252(tmp_path, evento):
    repo = tmp_path / "proj"
    _repo_com_todos_os_sinais(repo)
    env = {**_env(tmp_path), **CP1252}
    payload = json.dumps({"hook_event_name": evento, "cwd": str(repo),
                          "session_id": "sess-cp1252"})
    msgs = []
    for cmd in _tab_commands(evento):
        proc = subprocess.run(cmd, input=payload.encode("utf-8"), capture_output=True,
                              env=env, cwd=str(repo), timeout=30)
        assert proc.returncode == 0, proc.stderr
        msgs.extend(_mensagens(proc.stdout.decode("utf-8"), evento))
    assert any("TAB_" in m for m in msgs), (
        f"hook mudo em {evento} com stdout cp1252; stdout bruto nao foi emitido"
    )
