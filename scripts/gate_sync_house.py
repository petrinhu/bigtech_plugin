#!/usr/bin/env python3
"""Trava de CI e do preci para o sync de docs/house (CONS-10).

Traduz o codigo de saida de sync_house.py num veredito que nao pode ser confundido:

  0            -> PASS: conferido contra o vault, versao autenticada por HMAC.
  3            -> NAO CONFERIDO: aviso. Nunca PASS. No GitHub Actions vira ::warning::.
  1, 2 e outro -> REPROVADO (saida 1). Divergencia ou erro de uso reprova.

Uso: python3 scripts/gate_sync_house.py --check [--vault DIR] [--house DIR]
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_house as sh

MSG_NAO_CONFERIDO = (
    "docs/house nao foi conferido por completo (falta o vault ou a chave local). "
    "Este gate nao conta como conferido."
)


def _anuncia(linha: str) -> None:
    print(linha)
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumo:
        with open(resumo, "a", encoding="utf-8") as fh:
            fh.write(linha + "\n\n")


def main(argv: Sequence[str] | None = None) -> int:
    rc = sh.main(argv)
    if rc == 0:
        _anuncia("PASS: docs/house conferido contra o vault (versao autenticada por HMAC).")
        return 0
    if rc == 3:
        _anuncia("NAO CONFERIDO: " + MSG_NAO_CONFERIDO)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning::{MSG_NAO_CONFERIDO}")
        return 0
    _anuncia(f"REPROVADO: sync docs/house saiu {rc} (1 divergencia, 2 erro de uso).")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
