#!/usr/bin/env python3
"""
tab_pendencias_reminder.py

Hook do plugin para a tabela de pendencias (TODO.md). Depois da CONS-14 ele
tem so os dois gatilhos que o produto `tab_pendencias` nao cobre:

SessionStart:
  - carimba o inicio da sessao (por session_id, em diretorio privado do
    usuario, nunca no tempdir compartilhado), para o gatilho 4.

UserPromptSubmit:
  - TEMPO DE SESSAO: se a sessao atual passou de `horas_sessao` e o projeto e
    elegivel (.bigtech-porte + TODO.md), da um nudge de higiene (1x por sessao).

CRIAR (TODO.md ausente) e STALENESS (defasagem da tabela) sao do produto
standalone, que o plugin registra em hooks.json (skills/tab_pendencias/tools/
hooks/tab_pendencias_reminder.py). Ter os dois emissores aqui duplicaria a
mensagem, por isso este arquivo nao emite CRIAR nem STALENESS.

Config opcional `.tab-staleness.json` na raiz: {"off": true} desliga o
gatilho 4. Defaults: horas_sessao 2.

Estado do carimbo (CONS-14B): diretorio `$XDG_RUNTIME_DIR/bigtech_tab_sessao`
ou, na falta dele, `~/.cache/bigtech_tab_sessao`, modo 0700. Symlink e
diretorio de outro dono sao recusados: nada e gravado (fail-open).

A skill /bigtech:tab_pendencias so e iniciada pela THREAD PRINCIPAL (agents nao
tem a ferramenta Skill). Este hook apenas lembra; nunca reordena a tabela.

Saida: JSON com hookSpecificOutput.additionalContext quando dispara; nada caso
contrario. Fail-open: qualquer erro -> exit 0 sem avisar (nunca bloqueia).
"""
import json
import os
import re
import stat
import sys
import time

PORTE_MARKER = ".bigtech-porte"
TODO_FILE = "TODO.md"
CONFIG_FILE = ".tab-staleness.json"
STATE_DIRNAME = "bigtech_tab_sessao"  # diferente de tab_pendencias_hook_state (skill)
STATE_PREFIX = "claude-tab-sess-"
STATE_TTL_S = 24 * 3600  # limpeza de carimbos de sessao velhos

DEFAULTS = {"off": False, "horas_sessao": 2}

MODO_ENV = "BIGTECH_TAB_REMINDER"


def modo_operacao():
    """auto (default) | full | off (nao emite nada deste hook)."""
    v = (os.environ.get(MODO_ENV) or "auto").strip().lower()
    return v if v in ("auto", "full", "off") else "auto"


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


# --------------------------- tempo de sessao --------------------------------

def default_state_dir():
    """Diretorio de estado do carimbo, PRIVADO DO USUARIO. Nunca o tempdir.

    /tmp e compartilhado entre usuarios; um nome fixo ali permite ataque por
    symlink. Ordem: `$XDG_RUNTIME_DIR` (ja e por usuario) e, se ausente,
    `~/.cache`. Devolve None se nao ha HOME absoluto (fail-open, nao grava).
    """
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime and os.path.isdir(runtime):
        return os.path.join(runtime, STATE_DIRNAME)
    home = os.path.expanduser("~")
    if not home or not os.path.isabs(home):
        return None
    return os.path.join(home, ".cache", STATE_DIRNAME)


def _dono_e_proprio(st):
    return not hasattr(os, "getuid") or st.st_uid == os.getuid()


def verificar_diretorio_privado(base):
    """True se `base` existe, nao e symlink, e do usuario, sem escrita de
    grupo/outros. Nunca cria nada e nunca segue symlink (lstat)."""
    try:
        st = os.lstat(base)
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        return False
    if not _dono_e_proprio(st):
        return False
    return not (st.st_mode & 0o022)


def garantir_diretorio_privado(base):
    """Cria `base` com 0700 se faltar; se ja existir e for do usuario, fecha
    permissao de grupo/outros. Levanta PermissionError (symlink, nao-diretorio
    ou dono alheio). Nunca segue symlink."""
    try:
        os.makedirs(base, mode=0o700)
    except FileExistsError:
        pass  # symlink pendurado ou arquivo: a conferencia abaixo recusa
    st = os.lstat(base)
    if stat.S_ISLNK(st.st_mode):
        raise PermissionError("estado: diretorio e symlink; recusado")
    if not stat.S_ISDIR(st.st_mode):
        raise PermissionError("estado: caminho nao e diretorio; recusado")
    if not _dono_e_proprio(st):
        raise PermissionError("estado: diretorio pertence a outro usuario")
    if st.st_mode & 0o077:
        os.chmod(base, 0o700)  # e nosso: fecha o modo
    return base


def _base_para_escrita(state_dir=None):
    base = state_dir or default_state_dir()
    if not base:
        return None
    try:
        return garantir_diretorio_privado(base)
    except OSError:
        return None


def _base_para_leitura(state_dir=None):
    base = state_dir or default_state_dir()
    if not base or not verificar_diretorio_privado(base):
        return None
    return base


def caminho_sessao(session_id, state_dir=None):
    """Caminho do carimbo da sessao dentro de `state_dir` (ou do padrao), ou
    None sem session_id. Nao cria diretorio."""
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or ""))[:128]
    if not sid:
        return None
    base = state_dir or default_state_dir()
    if not base:
        return None
    return os.path.join(base, f"{STATE_PREFIX}{sid}.json")


def _escrever_json_seguro(path, payload):
    """Grava JSON sem seguir symlink (O_NOFOLLOW): symlink vira OSError."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


def carimbar_sessao(session_id, agora, state_dir=None):
    """Grava {start, avisado:false} 1x por sessao (nao sobrescreve start).
    Fail-open: diretorio recusado ou erro de IO -> nao grava, nao levanta."""
    base = _base_para_escrita(state_dir)
    if not base:
        return
    p = caminho_sessao(session_id, base)
    if not p or os.path.lexists(p):
        return
    try:
        _escrever_json_seguro(p, {"start": agora, "avisado": False})
    except OSError:
        pass


def ler_sessao(session_id, state_dir=None):
    base = _base_para_leitura(state_dir)
    if not base:
        return None
    p = caminho_sessao(session_id, base)
    if not p or os.path.islink(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _marcar_avisado(session_id, state_dir=None):
    base = _base_para_leitura(state_dir)
    if not base:
        return
    p = caminho_sessao(session_id, base)
    d = ler_sessao(session_id, base)
    if not p or d is None:
        return
    d["avisado"] = True
    try:
        _escrever_json_seguro(p, d)
    except OSError:
        pass


def limpar_sessoes_antigas(agora, state_dir=None):
    """Remove carimbos velhos, so dentro de diretorio conferido e so arquivos
    regulares (nunca symlink, nunca fora do diretorio de estado)."""
    base = _base_para_leitura(state_dir)
    if not base:
        return
    try:
        nomes = os.listdir(base)
    except OSError:
        return
    for nome in nomes:
        if not nome.startswith(STATE_PREFIX):
            continue
        fp = os.path.join(base, nome)
        try:
            st = os.lstat(fp)
            if not stat.S_ISREG(st.st_mode):
                continue
            if agora - st.st_mtime > STATE_TTL_S:
                os.remove(fp)
        except OSError:
            pass


# ------------------------------ elegibilidade -------------------------------

def _cwd(data):
    cwd = (data.get("cwd") or os.getcwd() or "").strip()
    return cwd if cwd and os.path.isdir(cwd) else None


def _tem(raiz, nome):
    return os.path.isfile(os.path.join(raiz, nome))


# ------------------------------ avaliadores ---------------------------------

def avaliar_userprompt(data, agora, state_dir=None):
    """Gatilho 4 (tempo de sessao). O produto nao tem essa nocao."""
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
        "[tab_pendencias] Lembrete de higiene da tabela (uma vez por sessao, "
        "com TODO.md presente): marque no Status, no commit que fecha o item e citando o "
        "ID, o que ja foi entregue (status de verificacao pendente, nunca "
        "concluido direto). Reordenar e decisao do usuario: use "
        "/bigtech:tab_pendencias --reorder quando a prioridade mudar (nova "
        "dependencia, INBOX nao-vazia, urgencia). Aviso unico por sessao."
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
            msg = None
    except Exception:
        return 0

    if msg:
        _emitir(event, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
