import json
import os
import subprocess

import pytest

import tab_pendencias_reminder as t

# ------------------------------- helpers ------------------------------------


@pytest.fixture(autouse=True)
def _modo_legado(monkeypatch):
    """Isola a suite da maquina: por padrao testa o contrato do plugin SOZINHO.

    Sem isto, `cede_ao_produto()` leria o settings.json real do usuario e os
    testes de gatilho 1/2 passariam ou falhariam conforme o produto standalone
    `tab_pendencias` estivesse ou nao registrado naquela maquina. Os testes da
    cessao (abaixo) sobrescrevem a env explicitamente.
    """
    monkeypatch.setenv(t.MODO_ENV, "full")

def _proj(tmp_path, porte=True, todo=True, cfg=None):
    if porte:
        (tmp_path / t.PORTE_MARKER).write_text("early\n")
    if todo:
        (tmp_path / t.TODO_FILE).write_text("# TODO\n")
    if cfg is not None:
        (tmp_path / t.CONFIG_FILE).write_text(json.dumps(cfg))
    return {"cwd": str(tmp_path)}


def _git_init(raiz):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    def run(args):
        subprocess.run(["git", *args], cwd=raiz, env=env,
                       capture_output=True, check=True)
    run(["init", "-q"])
    return run


# ------------------------------ gatilho 1: criar ----------------------------

def test_sem_porte_e_inerte(tmp_path):
    data = _proj(tmp_path, porte=False, todo=False)
    assert t.avaliar_sessionstart(data, 1000.0) is None


def test_porte_sem_todo_lembra_criar(tmp_path):
    data = _proj(tmp_path, porte=True, todo=False)
    msg = t.avaliar_sessionstart(data, 1000.0)
    assert msg and "--create" in msg


# ------------------------------ gatilho 2: staleness ------------------------

def test_msg_staleness_modo_e_precisa_dos_dois():
    cfg = dict(t.DEFAULTS)  # commits>5 e dias>2
    assert t.msg_staleness(6, 3, cfg) is not None
    assert t.msg_staleness(6, 1, cfg) is None      # so commits
    assert t.msg_staleness(3, 3, cfg) is None      # so dias
    assert t.msg_staleness(3, 1, cfg) is None


def test_msg_staleness_modo_ou_basta_um():
    cfg = {**t.DEFAULTS, "modo": "ou"}
    assert t.msg_staleness(6, 1, cfg) is not None
    assert t.msg_staleness(3, 3, cfg) is not None
    assert t.msg_staleness(3, 1, cfg) is None


def test_msg_staleness_none_safe():
    assert t.msg_staleness(None, None, t.DEFAULTS) is None


def test_off_desliga_staleness(tmp_path):
    data = _proj(tmp_path, cfg={"off": True})
    # com TODO.md presente e off, nao avisa (gatilho 2 desligado)
    assert t.avaliar_sessionstart(data, 1e12) is None


def test_staleness_git_conta_commits(tmp_path):
    run = _git_init(tmp_path)
    (tmp_path / t.TODO_FILE).write_text("# TODO\n")
    run(["add", "TODO.md"])
    run(["commit", "-qm", "todo"])
    for i in range(7):
        (tmp_path / f"f{i}.txt").write_text("x")
        run(["add", f"f{i}.txt"])
        run(["commit", "-qm", f"c{i}"])
    commits, dias = t.staleness_git(str(tmp_path), __import__("time").time())
    assert commits == 7
    assert dias is not None and dias < 1


def test_staleness_git_todo_untracked_usa_mtime(tmp_path):
    _git_init(tmp_path)
    (tmp_path / t.TODO_FILE).write_text("# TODO\n")  # nunca commitado
    commits, dias = t.staleness_git(str(tmp_path), __import__("time").time())
    assert commits is None
    assert dias is not None and dias < 1


def test_sem_git_retorna_dias_por_mtime(tmp_path):
    (tmp_path / t.TODO_FILE).write_text("# TODO\n")
    commits, dias = t.staleness_git(str(tmp_path), __import__("time").time())
    assert commits is None
    assert dias is not None


# ------------------------------ gatilho 4: tempo de sessao ------------------

def test_carimbo_roundtrip_e_nao_sobrescreve(tmp_path):
    sd = str(tmp_path)
    t.carimbar_sessao("sess-1", 100.0, state_dir=sd)
    t.carimbar_sessao("sess-1", 999.0, state_dir=sd)  # nao sobrescreve start
    estado = t.ler_sessao("sess-1", state_dir=sd)
    assert estado["start"] == 100.0
    assert estado["avisado"] is False


def test_userprompt_avisa_apos_limiar_uma_vez(tmp_path):
    sd = str(tmp_path)
    data = _proj(tmp_path)
    data["session_id"] = "abc"
    t.carimbar_sessao("abc", 0.0, state_dir=sd)
    # 3h depois (> default 2h): avisa
    msg = t.avaliar_userprompt(data, 3 * 3600.0, state_dir=sd)
    assert msg and "Sessao" in msg
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


def test_limpa_sessoes_antigas(tmp_path):
    sd = str(tmp_path)
    t.carimbar_sessao("velha", 0.0, state_dir=sd)
    p = t.caminho_sessao("velha", state_dir=sd)
    os.utime(p, (0, 0))  # mtime epoch -> bem antiga
    t.limpar_sessoes_antigas(t.STATE_TTL_S + 10, state_dir=sd)
    assert not os.path.isfile(p)


# ------------- cessao dos gatilhos 1 e 2 ao produto standalone --------------

def _settings(tmp_path, comandos):
    """Escreve um ~/.claude/settings.json sintetico com os hooks dados."""
    d = tmp_path / "cfg"
    d.mkdir(exist_ok=True)
    blocos = [{"hooks": [{"type": "command", "command": c}]} for c in comandos]
    (d / "settings.json").write_text(
        json.dumps({"hooks": {"SessionStart": blocos}}), encoding="utf-8"
    )
    return str(d)


def test_produto_registrado_detecta_comando_em_settings(tmp_path, monkeypatch):
    cfg = _settings(tmp_path, [
        "python3 $HOME/.claude/skills/tab_pendencias/tools/hooks/"
        "tab_pendencias_reminder.py",
    ])
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", cfg)
    assert t.produto_registrado() is True


def test_produto_registrado_ignora_o_proprio_plugin(tmp_path, monkeypatch):
    cfg = _settings(tmp_path, [
        "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/tab_pendencias_reminder.py",
    ])
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", cfg)
    assert t.produto_registrado() is False


def test_produto_registrado_ignora_caminho_do_plugin_root(tmp_path, monkeypatch):
    cfg = _settings(tmp_path, [
        "python3 /opt/plug/hooks/tab_pendencias_reminder.py",
    ])
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", cfg)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", "/opt/plug")
    assert t.produto_registrado() is False


def test_produto_ausente_quando_settings_nao_existe(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "vazio"))
    assert t.produto_registrado() is False


def test_settings_corrompido_nao_levanta(tmp_path, monkeypatch):
    d = tmp_path / "cfg"
    d.mkdir()
    (d / "settings.json").write_text("{ isto nao e json", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(d))
    assert t.produto_registrado() is False


def test_cede_suprime_gatilho_criar(tmp_path):
    data = _proj(tmp_path, porte=True, todo=False)
    assert t.avaliar_sessionstart(data, 1000.0, ceder=True) is None
    assert t.avaliar_sessionstart(data, 1000.0, ceder=False) is not None


def test_cede_suprime_gatilho_staleness(tmp_path):
    run = _git_init(tmp_path)
    data = _proj(tmp_path, porte=True, todo=True, cfg={"commits": 0, "dias": 0})
    run(["add", "-A"])
    run(["commit", "-qm", "boot"])
    (tmp_path / "x.txt").write_text("x")
    run(["add", "-A"])
    run(["commit", "-qm", "c1"])
    agora = 9e9  # muito no futuro -> dias estoura qualquer limiar
    assert t.avaliar_sessionstart(data, agora, ceder=False) is not None
    assert t.avaliar_sessionstart(data, agora, ceder=True) is None


def test_cede_nao_afeta_gatilho_4_tempo_de_sessao(tmp_path, monkeypatch):
    """O nudge de tempo de sessao nao existe no produto -> nunca e cedido."""
    cfg = _settings(tmp_path, [
        "python3 $HOME/.claude/skills/tab_pendencias/tools/hooks/"
        "tab_pendencias_reminder.py",
    ])
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", cfg)
    monkeypatch.setenv(t.MODO_ENV, "auto")
    assert t.cede_ao_produto() is True

    sd = str(tmp_path / "state")
    os.makedirs(sd, exist_ok=True)
    data = _proj(tmp_path, porte=True, todo=True)
    data["session_id"] = "s-gate-1"
    t.carimbar_sessao("s-gate-1", 0.0, state_dir=sd)
    msg = t.avaliar_userprompt(data, 10 * 3600.0, state_dir=sd)
    assert msg and "Sessao ha" in msg


def test_modo_off_silencia_tudo(tmp_path, monkeypatch):
    monkeypatch.setenv(t.MODO_ENV, "off")
    data = _proj(tmp_path, porte=True, todo=False)
    assert t.avaliar_sessionstart(data, 1000.0) is None
    sd = str(tmp_path / "state2")
    os.makedirs(sd, exist_ok=True)
    data["session_id"] = "s-off-1"
    t.carimbar_sessao("s-off-1", 0.0, state_dir=sd)
    assert t.avaliar_userprompt(data, 10 * 3600.0, state_dir=sd) is None


def test_modo_invalido_cai_em_auto(monkeypatch):
    monkeypatch.setenv(t.MODO_ENV, "lixo")
    assert t.modo_operacao() == "auto"
