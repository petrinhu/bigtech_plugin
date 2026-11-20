#!/usr/bin/env python3
"""Gate 4 do preci: paridade de versao entre os manifestos do plugin (CONS-16).

Confere que estes quatro pontos existem, tem versao nao vazia e sao iguais:
  - .claude-plugin/plugin.json (nucleo)
  - .claude-plugin/marketplace.json, entrada "bigtech"
  - .claude-plugin/marketplace.json, entrada "bigtech-completo"
  - bundles/bigtech-completo/.claude-plugin/plugin.json (bundle)

Codigos de saida: 0 igual; 1 divergente; 2 ausente, vazio ou ilegivel (reprova).

Uso: python3 scripts/check_paridade_versao.py [--root DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NUCLEO = ".claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"
BUNDLE = "bundles/bigtech-completo/.claude-plugin/plugin.json"
ENTRADAS = ("bigtech", "bigtech-completo")


class ErroDeLeitura(Exception):
    """Manifesto ausente, ilegivel ou sem versao: o gate reprova com saida 2."""


def _carrega(raiz: Path, relativo: str) -> dict:
    caminho = raiz / relativo
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ErroDeLeitura(f"{relativo}: ausente ou ilegivel ({exc})") from exc
    if not isinstance(dados, dict):
        raise ErroDeLeitura(f"{relativo}: a raiz do JSON nao e um objeto")
    return dados


def _versao(valor: object, rotulo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErroDeLeitura(f"{rotulo}: campo 'version' ausente ou vazio")
    return valor


def coleta(raiz: Path) -> dict[str, str]:
    """Devolve {ponto: versao} dos quatro pontos. Levanta ErroDeLeitura."""
    versoes: dict[str, str] = {}
    versoes[NUCLEO] = _versao(_carrega(raiz, NUCLEO).get("version"), NUCLEO)

    marketplace = _carrega(raiz, MARKETPLACE)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise ErroDeLeitura(f"{MARKETPLACE}: 'plugins' ausente ou nao e lista")
    por_nome = {p.get("name"): p for p in plugins if isinstance(p, dict)}
    for nome in ENTRADAS:
        entrada = por_nome.get(nome)
        if entrada is None:
            raise ErroDeLeitura(f"{MARKETPLACE}: entrada '{nome}' ausente")
        ponto = f"{MARKETPLACE} entrada {nome}"
        versoes[ponto] = _versao(entrada.get("version"), ponto)

    versoes[BUNDLE] = _versao(_carrega(raiz, BUNDLE).get("version"), BUNDLE)
    return versoes


def confere(raiz: Path) -> tuple[int, str]:
    """Devolve (codigo, mensagem) para a raiz dada."""
    try:
        versoes = coleta(raiz)
    except ErroDeLeitura as exc:
        return 2, f"erro: {exc}"
    distintas = set(versoes.values())
    if len(distintas) != 1:
        linhas = "\n".join(f"  {ponto}: {v}" for ponto, v in versoes.items())
        return 1, f"divergencia entre manifestos:\n{linhas}"
    return 0, f"versao casada em {len(versoes)} pontos: {distintas.pop()}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paridade de versao dos manifestos do plugin.")
    parser.add_argument("--root", default=".", type=Path, help="raiz do plugin (padrao: .)")
    args = parser.parse_args(argv)
    codigo, mensagem = confere(args.root)
    print(mensagem, file=sys.stderr if codigo else sys.stdout)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
