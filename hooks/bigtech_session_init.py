#!/usr/bin/env python3
"""
bigtech_session_init.py

Hook SessionStart do plugin bigtech. Tres funcoes, todas best-effort e
silent-fail (sempre exit 0; nunca bloqueia o turno):

(a) DOCS-BOOTSTRAP — resolve o caminho absoluto de `docs/` via
    os.environ["CLAUDE_PLUGIN_ROOT"] e injeta no contexto da sessao um bloco
    curto listando os manuais empacotados + a regra imperativa de leitura.
    Cobre a thread principal e as skills; subagents recebem o path repassado
    pela orquestracao (ver §4.3 do design).

(b) AVISO DE INCOMPATIBILIDADE COM caveman — o caveman comprime a comunicacao e
    conflita com o reforco de modo bigtech. Best-effort: le o mapa
    `enabledPlugins` de settings.json (CLAUDE_CONFIG_DIR ou $HOME/.claude). Se
    detecta caveman habilitado, escala o aviso; caso contrario, ainda inclui um
    aviso curto generico.

(c) SUGESTAO DE DEPENDENCIAS — sugere instalar `playwright` e `superpowers` se
    nao aparecerem habilitados (nao sao hard deps).

Saida: JSON com hookSpecificOutput.additionalContext. Sempre exit 0.
"""
import json
import os
import sys
from pathlib import Path

# Manuais empacotados (relativos a docs/). So texto; nao tocamos o disco para
# listar (o conteudo pode ainda nao ter sido populado, e o hook so precisa
# anunciar os caminhos canonicos).
MANUALS_TOP = [
    "ORG.md",
    "pipeline_release_1.0.md",
    "lideranca_pipeline_release.md",
    "TOOLING.md",
]
MANUALS_SUB = [
    "manuals/CONTRACT.md",
    "manuals/TESTES.md",
    "manuals/AGILE.md",
    "manuals/DEPLOY_CHECKLIST.md",
    "manuals/AUDITORIAS.md",
]
PRINCIPLES = "principles/*.md"

# Plugins sugeridos / incompativeis, no formato curto que aparece como sufixo
# da chave name@marketplace em enabledPlugins.
SUGGESTED = ("playwright", "superpowers")
INCOMPATIBLE = ("caveman",)


def _config_dir() -> Path:
    """Diretorio de config do Claude Code (CLAUDE_CONFIG_DIR ou $HOME/.claude).

    Resolvido em runtime contra o HOME de quem instalou o plugin; nenhum
    caminho e fixado no codigo.
    """
    env = os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if env:
        return Path(env)
    return Path(os.path.expanduser("~")) / ".claude"


def _enabled_plugin_names() -> set:
    """Conjunto de nomes-curtos de plugins habilitados (best-effort).

    Le settings.json -> enabledPlugins (mapa "name@marketplace": bool) e
    devolve o conjunto de `name` cujo valor e truthy. Em qualquer falha
    devolve conjunto vazio (e o chamador degrada para aviso generico).
    """
    try:
        settings = _config_dir() / "settings.json"
        with open(settings, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        enabled = data.get("enabledPlugins") or {}
        names = set()
        for key, val in enabled.items():
            if val:
                names.add(str(key).split("@", 1)[0].strip().lower())
        return names
    except Exception:
        return set()


def _docs_block() -> str:
    """Bloco de docs-bootstrap. Se CLAUDE_PLUGIN_ROOT estiver ausente, ainda
    emite a regra imperativa + caminhos relativos (fallback util)."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    docs_abs = ""
    if root:
        docs_abs = str(Path(root) / "docs")

    manuals = ", ".join(MANUALS_TOP + MANUALS_SUB + [PRINCIPLES])
    if docs_abs:
        head = (
            "[bigtech] DOCS-BOOTSTRAP — manuais do plugin em `" + docs_abs + "/`: "
            + manuals + ". "
        )
    else:
        head = (
            "[bigtech] DOCS-BOOTSTRAP — CLAUDE_PLUGIN_ROOT ausente; localize os "
            "manuais via Glob `**/bigtech/docs/**/<NOME>.md`. Manuais: "
            + manuals + ". "
        )
    rule = (
        "REGRA: ao aplicar governanca/codigo/teste/deploy/auditoria, LEIA o "
        "manual relevante (Read) ANTES de decidir. Ao despachar um subagent "
        "(Agent tool), inclua o caminho absoluto de docs/ no prompt da task — "
        "subagents nao herdam este contexto."
    )
    return head + rule


def _compat_block(enabled: set) -> str:
    caveman_on = any(p in enabled for p in INCOMPATIBLE)
    if caveman_on:
        return (
            " [bigtech] INCOMPATIBILIDADE DETECTADA: o plugin `caveman` parece "
            "ATIVO. Ele comprime a comunicacao e conflita com o reforco de modo "
            "bigtech. DESATIVE o caveman (/plugin) antes de operar a constelacao."
        )
    return (
        " [bigtech] Compatibilidade: se o plugin `caveman` estiver ativo, "
        "desative-o — ele conflita com o reforco de modo bigtech."
    )


def _deps_block(enabled: set) -> str:
    # Se nao conseguimos ler enabledPlugins (conjunto vazio), nao afirmamos que
    # estao ausentes; apenas recomendamos de forma generica.
    if not enabled:
        return (
            " [bigtech] Dependencias sugeridas (nao obrigatorias): `superpowers` "
            "e `playwright` enriquecem o fluxo; instale via /plugin se desejar."
        )
    missing = [p for p in SUGGESTED if p not in enabled]
    if not missing:
        return ""
    return (
        " [bigtech] Dependencias sugeridas ausentes (nao obrigatorias): "
        + ", ".join("`" + m + "`" for m in missing)
        + ". Considere instalar via /plugin."
    )


def build_context() -> str:
    enabled = _enabled_plugin_names()
    parts = [_docs_block(), _compat_block(enabled), _deps_block(enabled)]
    return "".join(p for p in parts if p)


def main() -> int:
    # Consumir stdin (payload SessionStart) sem depender dele.
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    try:
        out = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": build_context(),
            }
        }
        print(json.dumps(out))
    except Exception:
        # Silent-fail: nunca bloqueia o turno.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
