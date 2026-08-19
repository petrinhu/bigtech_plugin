#!/usr/bin/env python3
"""
tab_pendencias_reminder.py

Hook de tabela de pendencias (TODO.md). Lembrete leve, anti-ruido, com tres
gatilhos, multiplexados pelo evento (`hook_event_name`):

SessionStart:
  1. CRIAR  - projeto ja classificado (.bigtech-porte presente) mas SEM TODO.md
     -> lembra de rodar /tab_pendencias --create. (comportamento historico)
  2. STALENESS (C) - com TODO.md, mede a defasagem real da tabela via git:
     commits desde o ultimo toque no TODO.md e dias desde esse toque. Avisa
     conforme `modo` ("e" = ambos os limiares; "ou" = qualquer um).
  3. carimba o inicio da sessao (por session_id, em tempdir) para o gatilho 4.

UserPromptSubmit:
  4. TEMPO DE SESSAO - se a sessao atual passou de `horas_sessao` e o projeto e
     elegivel (.bigtech-porte + TODO.md), da um nudge de higiene (1x por sessao).

Gatilho sequencial com bigtech_porte_reminder.py: sem .bigtech-porte, quem
lembra e aquele hook (-> /bigtech, cujo Cosimo ja exige a tabela). Este so age
quando o porte ja foi classificado.

CONVIVENCIA COM O PRODUTO STANDALONE (ver `cede_ao_produto`): quando o hook do
produto `tab_pendencias` tambem esta registrado nas settings do usuario, os
gatilhos 1 e 2 sao cedidos a ele (que os reescreveu em 2026-08) e este hook
mantem so o 3 e o 4, que o produto nao tem. Sem o produto, comportamento
legado integral.

Config opcional `.tab-staleness.json` na raiz (defaults embutidos):
  {"off": false, "commits": 5, "dias": 2, "modo": "e", "horas_sessao": 2}
`off: true` desliga os gatilhos 2 e 4 (o gatilho 1 de CRIAR continua).

A skill /tab_pendencias so e iniciada pela THREAD PRINCIPAL (agents nao tem a
ferramenta Skill). Este hook apenas lembra; nunca reordena a tabela sozinho
(reordenar por WSJF/topological exige o time de agents da skill).

Saida: JSON com hookSpecificOutput.additionalContext quando dispara; nada caso
contrario. Fail-open: qualquer erro -> exit 0 sem avisar (nunca bloqueia).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

PORTE_MARKER = ".bigtech-porte"
TODO_FILE = "TODO.md"
CONFIG_FILE = ".tab-staleness.json"
STATE_PREFIX = "claude-tab-sess-"
STATE_TTL_S = 24 * 3600  # limpeza de carimbos de sessao velhos

DEFAULTS = {"off": False, "commits": 5, "dias": 2, "modo": "e", "horas_sessao": 2}

MODO_ENV = "BIGTECH_TAB_REMINDER"


# ------------------ convivencia com o produto standalone --------------------
#
# `tab_pendencias` virou produto standalone (repo proprio, GPL-3.0) e o motor
# de sinais dele (tools/session_signals.py, 2026-08) REESCREVEU os gatilhos 1
# (CRIAR -> TAB_TODO_CREATE_REQUIRED) e 2 (STALENESS ->
# TAB_STATUS_SYNC_RECOMMENDED), que nasceram aqui em 2026-06. Com os dois
# ligados, cada evento saia DUPLICADO: uma mensagem daqui e outra, de mesmo
# teor, do produto.
#
# Regra: se o produto estiver REGISTRADO como hook nas settings do usuario,
# este hook cede a ele os gatilhos 1 e 2 e mantem so o que o produto NAO tem
# -- o carimbo de sessao (3) e o nudge de tempo de sessao (4). Numa instalacao
# so-plugin (sem o produto) nada muda: comportamento legado integral.
#
# Lacunas conhecidas da cessao -- documentadas de proposito, nao perdidas em
# silencio (o produto nao cobre estes dois casos):
#   - projeto com .bigtech-porte que NAO e repo git: o produto exige git para
#     o TAB_TODO_CREATE_REQUIRED;
#   - TODO.md defasado sem nenhum item ⏳/🔄: o produto exige trabalho pendente
#     para o TAB_STATUS_SYNC_RECOMMENDED (havendo 🔍 costuma cair no
#     TAB_VERIFICATION_AGING, que e sinal proprio dele).
# Quem quiser o comportamento legado de volta: BIGTECH_TAB_REMINDER=full.

def modo_operacao():
    """auto (default) | full (nunca cede) | off (nao emite nada)."""
    v = (os.environ.get(MODO_ENV) or "auto").strip().lower()
    return v if v in ("auto", "full", "off") else "auto"


def _dirs_de_config():
    d = (os.environ.get("CLAUDE_CONFIG_DIR") or "").strip()
    return [d] if d else [os.path.join(os.path.expanduser("~"), ".claude")]


def _comandos_de_settings(caminho):
    """Strings `command + args` de todo hook declarado num settings.json."""
    achados = []
    try:
        with open(caminho, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return achados
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict):
        return achados
    for blocos in hooks.values():
        if not isinstance(blocos, list):
            continue
        for bloco in blocos:
            if not isinstance(bloco, dict):
                continue
            for h in bloco.get("hooks") or []:
                if not isinstance(h, dict):
                    continue
                partes = [str(h.get("command") or "")]
                args = h.get("args")
                if isinstance(args, list):
                    partes.extend(str(a) for a in args)
                achados.append(" ".join(partes))
    return achados


def produto_registrado():
    """True se o hook do produto standalone consta das settings do usuario.

    So conta registro que NAO aponta para dentro deste plugin -- o plugin se
    declara via hooks.json/${CLAUDE_PLUGIN_ROOT}, nunca via settings.json.
    """
    raiz_plugin = (os.environ.get("CLAUDE_PLUGIN_ROOT") or "").strip()
    for d in _dirs_de_config():
        for nome in ("settings.json", "settings.local.json"):
            for cmd in _comandos_de_settings(os.path.join(d, nome)):
                if "tab_pendencias" not in cmd:
                    continue
                if "CLAUDE_PLUGIN_ROOT" in cmd:
                    continue
                if raiz_plugin and raiz_plugin in cmd:
                    continue
                return True
    return False


def cede_ao_produto():
    """Se True, os gatilhos 1 e 2 sao do produto. Falha -> nao cede."""
    m = modo_operacao()
    if m == "full":
        return False
    if m == "off":
        return True
    try:
        return produto_registrado()
    except Exception:
        return False


# ----------------------------- config ---------------------------------------

def carregar_config(raiz):
    """Defaults + merge raso do .tab-staleness.json (tolerante a lixo)."""
    cfg = dict(DEFAULTS)
    try:
        with open(os.path.join(raiz, CONFIG_FILE), encoding="utf-8") as fh:
            bruto = json.load(fh)
        if isinstance(bruto, dict):
            for k in DEFAULTS:
                if k in bruto:
                    cfg[k] = bruto[k]
    except Exception:
        pass
    return cfg


# --------------------------- staleness (C) ----------------------------------

def _git(args, raiz):
    """Roda git em `raiz`; devolve stdout strip ou None em qualquer falha."""
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=raiz,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()

def staleness_git(raiz, agora):
    """(commits_desde, dias_desde) do ultimo toque no TODO.md.

    commits exige TODO.md versionado; se untracked, commits=None e dias cai no
    mtime do arquivo. Qualquer falha de git -> (None, None)."""
    if _git(["rev-parse", "--show-toplevel"], raiz) is None:
        # sem repo git: ainda da pra medir dias pelo mtime do arquivo.
        return None, _dias_por_mtime(raiz, agora)

    h = _git(["log", "-1", "--format=%H", "--", TODO_FILE], raiz)
    if not h:
        # TODO.md ainda nao commitado: sem baseline de commits, usa mtime.
        return None, _dias_por_mtime(raiz, agora)

    commits = None
    c = _git(["rev-list", "--count", f"{h}..HEAD"], raiz)
    if c is not None and c.isdigit():
        commits = int(c)

    dias = None
    ct = _git(["log", "-1", "--format=%ct", "--", TODO_FILE], raiz)
    if ct is not None and ct.isdigit():
        dias = max(0.0, (agora - int(ct)) / 86400.0)
    else:
        dias = _dias_por_mtime(raiz, agora)

    return commits, dias

def _dias_por_mtime(raiz, agora):
    try:
        m = os.path.getmtime(os.path.join(raiz, TODO_FILE))
    except Exception:
        return None
    return max(0.0, (agora - m) / 86400.0)

def msg_staleness(commits, dias, cfg):
    """Aplica limiares e `modo`; devolve a mensagem ou None."""
    lim_c, lim_d = cfg["commits"], cfg["dias"]
    bate_c = commits is not None and commits > lim_c
    bate_d = dias is not None and dias > lim_d
    modo = str(cfg.get("modo", "e")).lower()
    disparou = (bate_c and bate_d) if modo == "e" else (bate_c or bate_d)
    if not disparou:
        return None

    partes = []
    if commits is not None:
        partes.append(f"{commits} commits")
    if dias is not None:
        partes.append(f"{dias:.0f} dias")
    medida = " e ".join(partes) if partes else "tempo"
    conj = "e" if modo == "e" else "ou"
    return (
        f"[tab_pendencias] TODO.md possivelmente defasado: {medida} desde o "
        f"ultimo toque (limiar >{lim_c} commits {conj} >{lim_d} dias). ACAO "
        "BARATA primeiro: se ha item feito-no-codigo mas nao no Status, so "
        "atualize a coluna Status no TODO.md (implementacao entregue = "
        "'Pendente verificacao'; 'Concluido' so apos a onda de teste/auditoria) "
        "- isso NAO dispara o time de agents. ACAO CARA: reordenar via "
        "/tab_pendencias --reorder (dependencia + WSJF + ondas) SO se um input "
        "de priorizacao mudou (nova dependencia, INBOX nao-vazia, item ficou "
        "urgente). So a thread principal inicia a skill; o hook apenas lembra."
    )


# --------------------------- tempo de sessao --------------------------------

def _state_dir():
    return tempfile.gettempdir()

def caminho_sessao(session_id, state_dir=None):
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or ""))[:128]
    if not sid:
        return None
    return os.path.join(state_dir or _state_dir(), f"{STATE_PREFIX}{sid}.json")

def carimbar_sessao(session_id, agora, state_dir=None):
    """Grava {start, avisado:false} 1x por sessao (nao sobrescreve start)."""
    p = caminho_sessao(session_id, state_dir)
    if not p or os.path.isfile(p):
        return
    try:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"start": agora, "avisado": False}, fh)
    except Exception:
        pass

def ler_sessao(session_id, state_dir=None):
    p = caminho_sessao(session_id, state_dir)
    if not p:
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else None
    except Exception:
        return None

def _marcar_avisado(session_id, state_dir=None):
    p = caminho_sessao(session_id, state_dir)
    d = ler_sessao(session_id, state_dir)
    if not p or d is None:
        return
    d["avisado"] = True
    try:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(d, fh)
    except Exception:
        pass

def limpar_sessoes_antigas(agora, state_dir=None):
    d = state_dir or _state_dir()
    try:
        for nome in os.listdir(d):
            if not nome.startswith(STATE_PREFIX):
                continue
            fp = os.path.join(d, nome)
            try:
                if agora - os.path.getmtime(fp) > STATE_TTL_S:
                    os.remove(fp)
            except Exception:
                pass
    except Exception:
        pass


# ------------------------------ elegibilidade -------------------------------

def _cwd(data):
    cwd = (data.get("cwd") or os.getcwd() or "").strip()
    return cwd if cwd and os.path.isdir(cwd) else None

def _tem(raiz, nome):
    return os.path.isfile(os.path.join(raiz, nome))


# ------------------------------ avaliadores ---------------------------------

MSG_CRIAR = (
    "[tab_pendencias] Projeto ja classificado (.bigtech-porte presente) mas "
    "SEM TODO.md (tabela de pendencias). Considere rodar /tab_pendencias "
    "--create: gera a tabela ordenada por execucao (topological + WSJF + "
    "ondas, anti-retrabalho) e ja garante, com dupla-confirmacao, os testes "
    "nao-unitarios e as auditorias aplicaveis ao stack como itens de "
    "fechamento (cria ./TESTES.md e ./AUDITORIAS.md se faltarem). Quem inicia "
    "a skill e a thread principal (agents nao tem a ferramenta Skill). Apos "
    "criar o TODO.md, este lembrete vira checagem de defasagem."
)

def avaliar_sessionstart(data, agora, ceder=None):
    if modo_operacao() == "off":
        return None
    if ceder is None:
        ceder = cede_ao_produto()
    raiz = _cwd(data)
    if not raiz or not _tem(raiz, PORTE_MARKER):
        return None
    if not _tem(raiz, TODO_FILE):
        # gatilho 1 (CRIAR): do produto quando ele esta ligado.
        return None if ceder else MSG_CRIAR
    if ceder:
        # gatilho 2 (STALENESS): do produto quando ele esta ligado.
        return None
    cfg = carregar_config(raiz)
    if cfg.get("off"):
        return None
    commits, dias = staleness_git(raiz, agora)
    return msg_staleness(commits, dias, cfg)

def avaliar_userprompt(data, agora, state_dir=None):
    # Gatilho 4 NAO e cedido: o produto nao tem nocao de tempo de sessao.
    if modo_operacao() == "off":
        return None
    session_id = data.get("session_id")
    estado = ler_sessao(session_id, state_dir)
    if estado is None or estado.get("avisado"):
        return None
    raiz = _cwd(data)
    if not raiz or not _tem(raiz, PORTE_MARKER) or not _tem(raiz, TODO_FILE):
        return None
    cfg = carregar_config(raiz)
    if cfg.get("off"):
        return None
    try:
        start = float(estado.get("start"))
    except (TypeError, ValueError):
        return None
    horas = (agora - start) / 3600.0
    if horas <= float(cfg.get("horas_sessao", DEFAULTS["horas_sessao"])):
        return None
    _marcar_avisado(session_id, state_dir)
    return (
        f"[tab_pendencias] Sessao ha ~{horas:.0f}h com TODO.md presente. "
        "Higiene: marque no Status o que ja ficou pronto (acao barata, nao "
        "dispara o time de agents); reordene via /tab_pendencias --reorder so "
        "se a prioridade mudou (nova dependencia, INBOX nao-vazia, urgencia). "
        "Aviso unico por sessao."
    )


# --------------------------------- main -------------------------------------

def _emitir(event, msg):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": msg,
        }
    }))

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0

    agora = time.time()
    event = data.get("hook_event_name") or "SessionStart"

    try:
        if event == "UserPromptSubmit":
            msg = avaliar_userprompt(data, agora)
        else:
            carimbar_sessao(data.get("session_id"), agora)
            limpar_sessoes_antigas(agora)
            msg = avaliar_sessionstart(data, agora)
    except Exception:
        return 0

    if msg:
        _emitir(event, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
