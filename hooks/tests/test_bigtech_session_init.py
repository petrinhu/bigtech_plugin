"""Testes do hook SessionStart `bigtech_session_init.py`.

Cobre: docs-bootstrap (caminho docs/house), compatibilidade com caveman e o
aviso de dependencias recomendadas ausentes (CONS-14, texto de CONS-12A).

Isolamento: nenhum teste le o settings.json real. Os escopos (usuario,
projeto, local) apontam para diretorios temporarios.
"""
import json
import os
import subprocess
import sys

import bigtech_session_init as s

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_ROOT = os.path.dirname(HOOKS_DIR)

FORMA_CURTA = (
    "Falta {faltando}. Sem as dependências recomendadas o bigtech fica muito "
    "comprometido. Instale o pacote bigtech-completo."
)
PRECEDENCIA_LONGA = (
    "As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras "
    "que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste "
    "plugin em qualquer conflito. Onde divergirem, siga as do usuário."
)


def _settings(path, enabled):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"enabledPlugins": enabled}), encoding="utf-8")


def _cfg(tmp_path):
    cfg = tmp_path / "cfg"
    cfg.mkdir(exist_ok=True)
    return cfg


def _proj(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir(exist_ok=True)
    return proj


# ---------------------------------------------------------------------------
# Leitura dos escopos
# ---------------------------------------------------------------------------

def test_nome_curto_e_so_os_habilitados(tmp_path):
    cfg = _cfg(tmp_path)
    _settings(cfg / "settings.json", {
        "caveman@petrinhu": True,
        "playwright@claude-plugins-official": True,
        "superpowers@obra": False,
    })
    names, ilegiveis = s.coletar_habilitados(_proj(tmp_path), cfg)
    assert names == {"caveman", "playwright"}
    assert ilegiveis == []


def test_settings_ausente_nao_e_ilegivel_e_nao_habilita_nada(tmp_path):
    names, ilegiveis = s.coletar_habilitados(_proj(tmp_path), tmp_path / "vazio")
    assert names == set()
    assert ilegiveis == []


def test_settings_corrompido_vai_para_ilegiveis(tmp_path):
    cfg = _cfg(tmp_path)
    (cfg / "settings.json").write_text("{ nao eh json", encoding="utf-8")
    _, ilegiveis = s.coletar_habilitados(_proj(tmp_path), cfg)
    assert ilegiveis == [str(cfg / "settings.json")]


def test_dependencia_so_no_settings_do_projeto_conta(tmp_path):
    proj = _proj(tmp_path)
    _settings(proj / ".claude" / "settings.json", {"playwright@claude-plugins-official": True})
    names, _ = s.coletar_habilitados(proj, _cfg(tmp_path))
    assert "playwright" in names


def test_settings_local_do_projeto_conta(tmp_path):
    proj = _proj(tmp_path)
    _settings(proj / ".claude" / "settings.local.json", {"superpowers@claude-plugins-official": True})
    names, _ = s.coletar_habilitados(proj, _cfg(tmp_path))
    assert "superpowers" in names


# ---------------------------------------------------------------------------
# Quais dependencias faltam
# ---------------------------------------------------------------------------

def test_sem_nenhuma_dependencia_lista_as_quatro():
    assert s.dependencias_faltando(set()) == [
        "playwright", "superpowers", "frontend-design",
    ]


def test_todas_habilitadas_nao_falta_nenhuma():
    names = {"playwright", "superpowers", "frontend-design"}
    assert s.dependencias_faltando(names) == []


def test_frontend_design_vale_tambem_via_example_skills():
    names = {"playwright", "superpowers", "example-skills"}
    assert s.dependencias_faltando(names) == []


def test_so_uma_faltando_nomeia_so_ela():
    names = {"playwright", "frontend-design"}
    assert s.dependencias_faltando(names) == ["superpowers"]


# ---------------------------------------------------------------------------
# Texto do aviso (forma curta aprovada em CONS-12A)
# ---------------------------------------------------------------------------

def test_aviso_usa_a_forma_curta_literal_com_os_nomes(tmp_path):
    cfg = _cfg(tmp_path)
    _settings(cfg / "settings.json", {"superpowers@obra": True})
    bloco = s.deps_block(_proj(tmp_path), cfg)
    esperado = FORMA_CURTA.format(faltando="playwright, frontend-design")
    assert esperado in bloco


def test_aviso_vazio_quando_nada_falta(tmp_path):
    cfg = _cfg(tmp_path)
    _settings(cfg / "settings.json", {
        "playwright@claude-plugins-official": True,
        "superpowers@claude-plugins-official": True,
        "frontend-design@claude-plugins-official": True,
    })
    assert s.deps_block(_proj(tmp_path), cfg) == ""


def test_aviso_aparece_em_toda_sessao_sem_dependencia(tmp_path):
    cfg = _cfg(tmp_path)
    assert FORMA_CURTA.format(faltando="playwright, superpowers, frontend-design") \
        in s.deps_block(_proj(tmp_path), cfg)
    assert FORMA_CURTA.format(faltando="playwright, superpowers, frontend-design") \
        in s.deps_block(_proj(tmp_path), cfg)


def test_settings_ilegivel_nao_afirma_ausencia_e_diz_que_nao_conferiu(tmp_path):
    cfg = _cfg(tmp_path)
    (cfg / "settings.json").write_text("{ isto nao e json", encoding="utf-8")
    bloco = s.deps_block(_proj(tmp_path), cfg)
    assert "Não consegui conferir" in bloco
    assert "Falta" not in bloco
    assert "settings.json" in bloco


# ---------------------------------------------------------------------------
# Docs-bootstrap: caminho de docs/house
# ---------------------------------------------------------------------------

def test_docs_block_aponta_para_docs_house(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))
    block = s._docs_block()
    assert str(tmp_path / "docs" / "house") in block
    assert "REGRA:" in block


def test_manuais_anunciados_existem_em_docs_house():
    casa = os.path.join(PLUGIN_ROOT, "docs", "house")
    for nome in s.MANUALS:
        assert os.path.isfile(os.path.join(casa, nome)), nome


def test_docs_block_fallback_sem_root(monkeypatch):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    block = s._docs_block()
    assert "CLAUDE_PLUGIN_ROOT ausente" in block
    assert "ORG.md" in block
    assert "REGRA:" in block


def test_docs_block_declara_precedencia_do_usuario(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))
    assert PRECEDENCIA_LONGA in s._docs_block()


def test_docs_block_declara_precedencia_sem_root(monkeypatch):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    assert PRECEDENCIA_LONGA in s._docs_block()


# ---------------------------------------------------------------------------
# Compatibilidade com caveman (inalterada)
# ---------------------------------------------------------------------------

def test_compat_block_escala_aviso_quando_caveman_ativo():
    block = s._compat_block({"caveman", "playwright"})
    assert "INCOMPATIBILIDADE DETECTADA" in block
    assert "DESATIVE" not in block
    assert "decisao" in block


def test_compat_block_aviso_generico_sem_caveman():
    block = s._compat_block({"playwright"})
    assert "INCOMPATIBILIDADE DETECTADA" not in block


# ---------------------------------------------------------------------------
# Contrato end-to-end: subprocess, por sessao
# ---------------------------------------------------------------------------

def _run(tmp_path, cfg_dir, cwd=None):
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    env["CLAUDE_CONFIG_DIR"] = str(cfg_dir)
    payload = {"hook_event_name": "SessionStart", "cwd": str(cwd or tmp_path)}
    return subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_session_init.py")],
        input=json.dumps(payload), text=True, capture_output=True, env=env,
    )


def test_subprocess_exit_0_e_json_com_aviso(tmp_path):
    proc = _run(tmp_path, tmp_path / "config-vazio")
    assert proc.returncode == 0
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "DOCS-BOOTSTRAP" in ctx
    assert PRECEDENCIA_LONGA in ctx
    assert FORMA_CURTA.format(faltando="playwright, superpowers, frontend-design") in ctx


def test_subprocess_aviso_repete_na_segunda_sessao(tmp_path):
    cfg = tmp_path / "config-vazio"
    primeira = _run(tmp_path, cfg)
    segunda = _run(tmp_path, cfg)
    for proc in (primeira, segunda):
        ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "Falta playwright" in ctx


def test_subprocess_settings_ilegivel_nao_quebra_a_sessao(tmp_path):
    cfg = _cfg(tmp_path)
    (cfg / "settings.json").write_text("{ quebrado", encoding="utf-8")
    proc = _run(tmp_path, cfg)
    assert proc.returncode == 0
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Não consegui conferir" in ctx
