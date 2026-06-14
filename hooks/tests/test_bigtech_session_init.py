"""Testes do hook SessionStart `bigtech_session_init.py` (AUD-F08).

Exercita as funções puras importáveis (docs-bootstrap, leitura de enabledPlugins,
blocos de compatibilidade e de dependências) com asserts de VALOR, mais um teste
de contrato via subprocess (exit 0 + JSON parseável).

Isolamento: `_config_dir()` resolve CLAUDE_CONFIG_DIR ou $HOME/.claude. Todos os
testes que tocam settings.json apontam CLAUDE_CONFIG_DIR para um diretório
controlado (monkeypatch) — nunca lemos o settings.json real do usuário.
"""
import json
import os
import subprocess
import sys

import bigtech_session_init as s


# ---------------------------------------------------------------------------
# _enabled_plugin_names: lê settings.json -> enabledPlugins (best-effort).
# ---------------------------------------------------------------------------
def _write_settings(tmp_path, enabled_plugins):
    cfg = tmp_path / "config"
    cfg.mkdir(exist_ok=True)
    (cfg / "settings.json").write_text(
        json.dumps({"enabledPlugins": enabled_plugins}), encoding="utf-8"
    )
    return cfg


def test_enabled_plugin_names_extrai_nome_curto_e_filtra_desabilitados(tmp_path, monkeypatch):
    cfg = _write_settings(tmp_path, {
        "caveman@petrinhu": True,
        "playwright@anthropic": True,
        "superpowers@obra": False,     # desabilitado -> não entra
    })
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    names = s._enabled_plugin_names()
    assert names == {"caveman", "playwright"}


def test_enabled_plugin_names_arquivo_ausente_retorna_set_vazio(tmp_path, monkeypatch):
    # CLAUDE_CONFIG_DIR aponta para diretório sem settings.json -> set() vazio.
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "vazio"))
    assert s._enabled_plugin_names() == set()


def test_enabled_plugin_names_json_corrompido_retorna_set_vazio(tmp_path, monkeypatch):
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "settings.json").write_text("{ nao eh json", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    assert s._enabled_plugin_names() == set()


# ---------------------------------------------------------------------------
# _compat_block: aviso de incompatibilidade com caveman.
# ---------------------------------------------------------------------------
def test_compat_block_escala_aviso_quando_caveman_ativo():
    block = s._compat_block({"caveman", "playwright"})
    assert "INCOMPATIBILIDADE DETECTADA" in block
    assert "caveman" in block
    assert "DESATIVE" in block


def test_compat_block_aviso_generico_sem_caveman():
    block = s._compat_block({"playwright"})
    assert "INCOMPATIBILIDADE DETECTADA" not in block
    assert "caveman" in block      # ainda menciona o conflito potencial


# ---------------------------------------------------------------------------
# _deps_block: sugestão de dependências ausentes.
# ---------------------------------------------------------------------------
def test_deps_block_set_vazio_recomenda_generico():
    # Conjunto vazio = não conseguimos ler enabledPlugins; não afirmamos ausência.
    block = s._deps_block(set())
    assert "superpowers" in block and "playwright" in block
    assert "ausentes" not in block.lower()


def test_deps_block_lista_apenas_o_que_falta():
    # superpowers presente, playwright ausente -> só playwright é sugerido.
    block = s._deps_block({"superpowers"})
    assert "playwright" in block
    assert "superpowers" not in block
    assert "ausentes" in block.lower()


def test_deps_block_vazio_quando_todas_sugeridas_presentes():
    block = s._deps_block({"superpowers", "playwright"})
    assert block == ""


# ---------------------------------------------------------------------------
# _docs_block: docs-bootstrap com e sem CLAUDE_PLUGIN_ROOT.
# ---------------------------------------------------------------------------
def test_docs_block_usa_root_quando_presente(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))
    block = s._docs_block()
    assert "DOCS-BOOTSTRAP" in block
    assert str(tmp_path / "docs") in block      # caminho absoluto de docs/
    assert "ORG.md" in block
    assert "REGRA:" in block


def test_docs_block_fallback_sem_root(monkeypatch):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    block = s._docs_block()
    assert "CLAUDE_PLUGIN_ROOT ausente" in block
    assert "ORG.md" in block                     # manuais ainda listados
    assert "REGRA:" in block


# ---------------------------------------------------------------------------
# build_context: concatena os três blocos não-vazios.
# ---------------------------------------------------------------------------
def test_build_context_concatena_blocos(tmp_path, monkeypatch):
    cfg = _write_settings(tmp_path, {"caveman@x": True})
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))
    ctx = s.build_context()
    assert "DOCS-BOOTSTRAP" in ctx                 # _docs_block
    assert "INCOMPATIBILIDADE DETECTADA" in ctx    # _compat_block (caveman on)


# ---------------------------------------------------------------------------
# Contrato end-to-end via subprocess: exit 0 + JSON parseável.
# ---------------------------------------------------------------------------
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_subprocess_exit_0_e_json_parseavel(tmp_path):
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(tmp_path)
    env["CLAUDE_CONFIG_DIR"] = str(tmp_path / "config-vazio")   # sem settings.json
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_session_init.py")],
        input=json.dumps({"hook_event_name": "SessionStart"}),
        text=True, capture_output=True, env=env,
    )
    assert proc.returncode == 0
    obj = json.loads(proc.stdout)
    hso = obj["hookSpecificOutput"]
    assert hso["hookEventName"] == "SessionStart"
    assert "DOCS-BOOTSTRAP" in hso["additionalContext"]
