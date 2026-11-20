#!/usr/bin/env python3
"""
bigtech_session_init.py

Hook SessionStart do plugin bigtech. Tres funcoes, todas best-effort e
silent-fail (sempre exit 0; nunca bloqueia o turno):

(a) DOCS-BOOTSTRAP: resolve o caminho absoluto de `docs/house/` via
    os.environ["CLAUDE_PLUGIN_ROOT"] e injeta no contexto da sessao um bloco
    curto listando os manuais empacotados + a regra imperativa de leitura.
    Subagents recebem o path repassado pela orquestracao.

(b) AVISO DE INCOMPATIBILIDADE COM caveman: o caveman comprime a comunicacao e
    conflita com o reforco de modo bigtech. Le `enabledPlugins` de
    settings.json (CLAUDE_CONFIG_DIR ou $HOME/.claude).

(c) AVISO DE DEPENDENCIAS RECOMENDADAS AUSENTES (CONS-14, texto de CONS-12A):
    confere playwright, superpowers e frontend-design nos escopos que
    a sessao le (settings.json e settings.local.json do usuario; settings.json
    e settings.local.json do projeto, a partir do `cwd` do payload). Se alguma
    faltar, emite a forma curta aprovada nomeando as que faltam. frontend-design
    tambem conta via example-skills. Se um settings existir e nao puder ser
    lido, diz que nao conseguiu conferir (nao afirma ausencia).

Saida: JSON com hookSpecificOutput.additionalContext. Sempre exit 0.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bigtech_hook_io import nome_evento

# Manuais empacotados em docs/house/ (copia unica, CONS-13).
MANUALS = [
    "ORG.md",
    "pipeline_release_1.0.md",
    "lideranca_pipeline_release.md",
    "TOOLING.md",
    "CONTRACT.md",
    "TESTES.md",
    "AGILE.md",
    "DEPLOY_CHECKLIST.md",
    "AUDITORIAS.md",
]

# Precedência das instruções do usuário sobre o plugin (forma longa, CONS-04A).
PRECEDENCIA_LONGA = (
    "As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras "
    "que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste "
    "plugin em qualquer conflito. Onde divergirem, siga as do usuário."
)

# Forma curta aprovada (CONS-12A, seção 3). {faltando} recebe os nomes.
FORMA_CURTA = (
    "Falta {faltando}. Sem as dependências recomendadas o bigtech fica muito "
    "comprometido. Instale o pacote bigtech-completo."
)

# Dependências recomendadas: rotulo -> nomes-curtos que a satisfazem.
DEPENDENCIAS = (
    ("playwright", ("playwright",)),
    ("superpowers", ("superpowers",)),
    ("frontend-design", ("frontend-design", "example-skills")),
)

INCOMPATIBLE = ("caveman",)

# Arquivos de settings lidos por escopo, na ordem de leitura.
SETTINGS_USUARIO = ("settings.json", "settings.local.json")
SETTINGS_PROJETO = (".claude/settings.json", ".claude/settings.local.json")


def _config_dir() -> Path:
    """Diretorio de config do Claude Code (CLAUDE_CONFIG_DIR ou $HOME/.claude)."""
    env = os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if env:
        return Path(env)
    return Path(os.path.expanduser("~")) / ".claude"


def _ler_enabled(caminho: Path, ilegiveis: list) -> set:
    """Nomes-curtos habilitados em `caminho`. Ausente -> vazio.

    Arquivo que existe e nao le (JSON invalido, sem permissao) vai para
    `ilegiveis` e devolve vazio.
    """
    if not caminho.is_file():
        return set()
    try:
        with open(caminho, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        enabled = data.get("enabledPlugins") or {}
        if not isinstance(enabled, dict):
            raise TypeError("enabledPlugins nao e um objeto")
        return {
            str(chave).split("@", 1)[0].strip().lower()
            for chave, val in enabled.items()
            if val
        }
    except Exception:
        ilegiveis.append(str(caminho))
        return set()


def coletar_habilitados(cwd, config_dir):
    """(nomes habilitados em todos os escopos lidos, caminhos ilegiveis)."""
    ilegiveis: list = []
    nomes: set = set()
    for nome in SETTINGS_USUARIO:
        nomes |= _ler_enabled(Path(config_dir) / nome, ilegiveis)
    if cwd:
        for relativo in SETTINGS_PROJETO:
            nomes |= _ler_enabled(Path(cwd) / relativo, ilegiveis)
    return nomes, ilegiveis


def dependencias_faltando(names: set) -> list:
    """Rotulos das dependencias recomendadas sem nenhum nome habilitado."""
    return [rotulo for rotulo, aceitos in DEPENDENCIAS
            if not any(a in names for a in aceitos)]


def _docs_block() -> str:
    """Bloco de docs-bootstrap. Sem CLAUDE_PLUGIN_ROOT, ainda emite a regra e
    os nomes dos manuais (fallback util)."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    nomes = ", ".join(MANUALS)
    if root:
        head = (
            "[bigtech] DOCS-BOOTSTRAP: manuais do plugin em `"
            + str(Path(root) / "docs" / "house")
            + "/`: " + nomes + ". Principios em `"
            + str(Path(root) / "docs" / "principles")
            + "/*.md`. "
        )
    else:
        head = (
            "[bigtech] DOCS-BOOTSTRAP: CLAUDE_PLUGIN_ROOT ausente; localize os "
            "manuais via Glob `**/bigtech/docs/house/<NOME>.md`. Manuais: "
            + nomes + ". "
        )
    rule = (
        "REGRA: ao aplicar governanca/codigo/teste/deploy/auditoria, LEIA o "
        "manual relevante (Read) ANTES de decidir. Ao despachar um subagent "
        "(Agent tool), inclua o caminho absoluto de docs/house/ no prompt da task: "
        "subagents nao herdam este contexto."
    )
    return head + rule + " " + PRECEDENCIA_LONGA


def _compat_block(enabled: set) -> str:
    caveman_on = any(p in enabled for p in INCOMPATIBLE)
    if caveman_on:
        return (
            " [bigtech] INCOMPATIBILIDADE DETECTADA: o plugin `caveman` parece "
            "ATIVO. Ele comprime a comunicacao e pode interferir no reforco de "
            "modo bigtech. Informe o usuario; manter ou desativar plugins e "
            "decisao dele."
        )
    return (
        " [bigtech] Compatibilidade: se o plugin `caveman` estiver ativo, ele "
        "pode interferir no reforco de modo bigtech; a decisao de mante-lo e do "
        "usuario."
    )


def deps_block(cwd, config_dir) -> str:
    """Aviso de dependencias recomendadas. Vazio quando nada falta."""
    names, ilegiveis = coletar_habilitados(cwd, config_dir)
    if ilegiveis:
        return (
            " [bigtech] Não consegui conferir as dependências recomendadas: "
            + ", ".join(ilegiveis) + " não pode ser lido. Verifique o arquivo; "
            "até lá não afirmo quais dependências faltam."
        )
    faltando = dependencias_faltando(names)
    if not faltando:
        return ""
    return " " + FORMA_CURTA.format(faltando=", ".join(faltando))


def build_context(cwd=None) -> str:
    cwd = cwd or os.getcwd()
    names, _ = coletar_habilitados(cwd, _config_dir())
    parts = [_docs_block(), _compat_block(names), deps_block(cwd, _config_dir())]
    return "".join(p for p in parts if p)


def _cwd_do_payload(payload) -> str:
    if isinstance(payload, dict):
        cwd = str(payload.get("cwd") or "").strip()
        if cwd and os.path.isdir(cwd):
            return cwd
    return os.getcwd()


def main() -> int:
    payload = None
    try:
        payload = json.load(sys.stdin)
    except Exception:
        pass
    try:
        out = {
            "hookSpecificOutput": {
                "hookEventName": nome_evento(payload, "SessionStart"),
                "additionalContext": build_context(_cwd_do_payload(payload)),
            }
        }
        print(json.dumps(out))
    except Exception:
        # Silent-fail: nunca bloqueia o turno.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
