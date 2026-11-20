"""Lembrete unico da tabela de pendencias, pela invocacao REAL do hooks.json.

Roda, em subprocess e com perfis descartaveis (HOME, CLAUDE_CONFIG_DIR e
XDG_RUNTIME_DIR em tmp), todos os hooks de SessionStart que tocam
tab_pendencias. A regra: uma unica mensagem de criacao por sessao, e nenhuma
mensagem cita o comando sem o prefixo `bigtech:`.
"""
import json
import os
import re
import subprocess

import pytest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HOOKS_DIR)
HOOKS_JSON = os.path.join(HOOKS_DIR, "hooks.json")
# comando: /tab_pendencias seguido de espaco, pontuacao ou fim; caminho
# (/tab_pendencias_reminder.py, /tab_pendencias/tools) nao conta.
SEM_PREFIXO = re.compile(r"(?<!bigtech:)/tab_pendencias(?![\w/])")


def _tab_commands(event):
    """Comandos (args expandidos) dos hooks de `event` que tocam tab_pendencias."""
    with open(HOOKS_JSON, encoding="utf-8") as fh:
        data = json.load(fh)
    out = []
    for grupo in data["hooks"].get(event, []):
        for h in grupo.get("hooks", []):
            args = [str(a).replace("${CLAUDE_PLUGIN_ROOT}", ROOT) for a in h.get("args", [])]
            if any("tab_pendencias" in a for a in args):
                out.append([h["command"], *args])
    return out


def _env(tmp_path):
    env = dict(os.environ)
    env["HOME"] = str(tmp_path / "home")
    env["CLAUDE_CONFIG_DIR"] = str(tmp_path / "cfg")
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "xdg")
    env["TMPDIR"] = str(tmp_path / "tmp")
    env["CLAUDE_PLUGIN_ROOT"] = ROOT
    env.pop("BIGTECH_TAB_REMINDER", None)
    for d in ("home", "cfg", "xdg", "tmp"):
        (tmp_path / d).mkdir(exist_ok=True)
    return env


def _mensagens(stdout, evento):
    """Mensagens de uma saida de hook, pelo contrato do Claude Code.

    Contrato: `hookSpecificOutput` com `hookEventName` igual ao evento e o
    texto em `hookSpecificOutput.additionalContext`. `additionalContext` no
    topo do JSON e erro (o host nao o le ali).
    """
    texto = stdout.strip()
    if not texto:
        return []
    obj = json.loads(texto)
    assert "additionalContext" not in obj, f"additionalContext no topo: {obj}"
    if obj == {"continue": True}:
        return []  # saida sem mensagem do hook de produto
    hso = obj.get("hookSpecificOutput")
    assert isinstance(hso, dict), f"sem hookSpecificOutput: {obj}"
    assert hso.get("hookEventName") == evento, hso
    return [hso["additionalContext"]] if "additionalContext" in hso else []


def _rodar_session_start(tmp_path, cwd):
    env = _env(tmp_path)
    payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(cwd),
                          "session_id": "sess-e2e"})
    todas = []
    for cmd in _tab_commands("SessionStart"):
        proc = subprocess.run(cmd, input=payload, text=True, capture_output=True,
                              env=env, cwd=str(cwd), timeout=30)
        assert proc.returncode == 0, proc.stderr
        todas.extend(_mensagens(proc.stdout, "SessionStart"))
    return todas


def _repo_git_com_porte(path):
    path.mkdir(parents=True, exist_ok=True)
    (path / ".bigtech-porte").write_text("porte=early\n", encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q"], cwd=path, env=env, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, env=env, check=True)
    subprocess.run(["git", "commit", "-qm", "boot"], cwd=path, env=env, check=True)


def test_hooks_json_registra_o_produto_nos_dois_eventos():
    assert _tab_commands("SessionStart"), "SessionStart sem hook de tab_pendencias"
    assert _tab_commands("UserPromptSubmit"), "UserPromptSubmit sem hook de tab_pendencias"
    registrados = [c for c in _tab_commands("SessionStart") if "skills" in " ".join(c)]
    assert registrados, "o hook do produto (skills/tab_pendencias) nao esta no hooks.json"


def test_repo_git_com_porte_sem_todo_emite_uma_unica_mensagem_de_criacao(tmp_path):
    repo = tmp_path / "proj"
    _repo_git_com_porte(repo)
    msgs = _rodar_session_start(tmp_path, repo)
    criacoes = [m for m in msgs if "--create" in m]
    assert len(criacoes) == 1, msgs
    assert "/bigtech:tab_pendencias --create" in criacoes[0]


def test_nenhuma_mensagem_cita_comando_sem_prefixo_bigtech(tmp_path):
    repo = tmp_path / "proj"
    _repo_git_com_porte(repo)
    for m in _rodar_session_start(tmp_path, repo):
        assert not SEM_PREFIXO.search(m), m


def test_sem_porte_nem_todo_nao_ha_mensagem(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    assert _rodar_session_start(tmp_path, repo) == []


@pytest.mark.parametrize("arquivo", [
    "hooks/tab_pendencias_reminder.py",
    "hooks/bigtech_session_init.py",
    "hooks/bigtech_porte_reminder.py",
    "hooks/bigtech_reinforce.py",
    "hooks/tdd_guard.py",
    "hooks/tdd_runner.py",
    "skills/tab_pendencias/tools/session_signals.py",
    "skills/tab_pendencias/tools/hooks/tab_pendencias_reminder.py",
])
def test_fonte_dos_hooks_nao_tem_comando_sem_prefixo(arquivo):
    with open(os.path.join(ROOT, arquivo), encoding="utf-8") as fh:
        for n, linha in enumerate(fh, 1):
            assert not SEM_PREFIXO.search(linha), f"{arquivo}:{n}: {linha.strip()}"


@pytest.mark.parametrize("saida", [
    '{"additionalContext": "texto no topo"}',
    '{"additionalContext": "x", "hookSpecificOutput": {"hookEventName": "SessionStart"}}',
])
def test_contrato_recusa_additionalContext_no_topo(saida):
    with pytest.raises(AssertionError, match="additionalContext no topo"):
        _mensagens(saida, "SessionStart")


def test_contrato_recusa_hookEventName_diferente_do_evento():
    saida = '{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "x"}}'
    with pytest.raises(AssertionError):
        _mensagens(saida, "SessionStart")


# --- CONS-R3: cada sinal sai de UM emissor so, uma vez por evento -----------

_SINAL_ID = re.compile(r"TAB_[A-Z_]+")


def _repo_com_todos_os_sinais(path):
    """Repo git com porte, TODO.md defasado (⏳ e 🔍 antigos), INBOX
    classificavel e inbox/ concorrente: ativa os sinais de SessionStart e de
    UserPromptSubmit de uma vez."""
    path.mkdir(parents=True, exist_ok=True)
    (path / ".bigtech-porte").write_text("porte=early\n", encoding="utf-8")
    (path / "TODO.md").write_text(
        "# TODO\n\n"
        "| ID | Item | Status | Prioridade |\n"
        "|---|---|---|---|\n"
        "| X-1 | item de teste | ⏳ Em andamento | P1 |\n"
        "| X-2 | outro item | 🔍 Pendente verificação | P2 |\n\n"
        "## INBOX\n\n"
        "- 2026-11-01 inbox-test [pendente]\n",
        encoding="utf-8",
    )
    (path / "inbox").mkdir()
    (path / "inbox" / "d1.md").write_text("descoberta\n", encoding="utf-8")
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        # commit antigo: a defasagem do TODO.md vira sinal de frescor
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
        # isolado do git global do usuario (git hooks, core.hooksPath)
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    subprocess.run(["git", "init", "-q"], cwd=path, env=env, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, env=env, check=True)
    subprocess.run(["git", "commit", "-qm", "boot"], cwd=path, env=env, check=True)


def _rodar_evento(tmp_path, cwd, evento):
    """Roda todos os hooks de tab_pendencias de `evento` e devolve as mensagens."""
    env = _env(tmp_path)
    payload = json.dumps({"hook_event_name": evento, "cwd": str(cwd),
                          "session_id": "sess-cons-r3"})
    todas = []
    for cmd in _tab_commands(evento):
        proc = subprocess.run(cmd, input=payload, text=True, capture_output=True,
                              env=env, cwd=str(cwd), timeout=30)
        assert proc.returncode == 0, proc.stderr
        todas.extend(_mensagens(proc.stdout, evento))
    return todas


@pytest.mark.parametrize("evento", ["SessionStart", "UserPromptSubmit"])
def test_cada_sinal_sai_de_um_emissor_so_e_uma_vez(tmp_path, evento):
    """Regra CONS-R3: cada sinal ativo aparece exatamente uma vez no evento,
    somando todos os hooks registrados. Antes, o hook do produto repetia o
    sinal (linha maquina + linha de prosa) na mesma mensagem."""
    repo = tmp_path / "proj"
    _repo_com_todos_os_sinais(repo)
    msgs = _rodar_evento(tmp_path, repo, evento)
    contagem = {}
    for m in msgs:
        for sid in _SINAL_ID.findall(m):
            contagem[sid] = contagem.get(sid, 0) + 1
    assert contagem, f"cenario nao ativou sinal algum em {evento}: {msgs}"
    repetidos = {sid: n for sid, n in contagem.items() if n != 1}
    assert not repetidos, f"sinal repetido em {evento}: {repetidos}\n{msgs}"
