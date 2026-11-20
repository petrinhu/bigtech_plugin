#!/usr/bin/env python3
# tools/diretorio_seguro.py -- diretorio de escrita do tab_pendencias sem symlink alheio (CONS-05S)
# SPDX-License-Identifier: Apache-2.0
# Licença: Apache-2.0 (ver NOTICE na raiz do plugin).
"""
Conferencia de diretorio antes de gravar estado.

Recusa, com erro claro e sem gravar nada:
  - symlink (lstat, nunca stat: o alvo do link nao e confiado);
  - caminho que existe mas nao e diretorio;
  - diretorio cujo dono nao e o usuario do processo (POSIX).

Limite declarado: a checagem e lstat no ultimo componente. Quem ja roda como
o mesmo usuario tem escrita no repo e nao e o adversario modelado aqui; a
checagem fecha o caso de repo clonado de terceiro (symlink versionado) e de
diretorio plantado por outro usuario.
"""
from __future__ import annotations

import os
import stat


class DiretorioInseguro(PermissionError):
    """Diretorio de escrita recusado (symlink, nao-diretorio ou dono alheio)."""


def verificar_diretorio_proprio(path: str) -> str:
    """Confere `path` com lstat. Devolve `path` se estiver ok; senão levanta
    DiretorioInseguro. Nunca segue symlink."""
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        raise DiretorioInseguro(
            f"diretorio {path!r} e symlink; recusado, nada foi gravado")
    if not stat.S_ISDIR(st.st_mode):
        raise DiretorioInseguro(
            f"{path!r} nao e diretorio; recusado, nada foi gravado")
    if hasattr(os, "getuid") and st.st_uid != os.getuid():
        raise DiretorioInseguro(
            f"diretorio {path!r} pertence a outro usuario (uid {st.st_uid}); "
            "recusado, nada foi gravado")
    return path


def garantir_diretorio_proprio(path: str, mode: int = 0o700) -> str:
    """Cria `path` se faltar (com `mode`) e confere com
    verificar_diretorio_proprio. Um symlink ja existente e recusado, mesmo que
    aponte para um diretorio valido."""
    try:
        os.makedirs(path, mode=mode, exist_ok=True)
    except FileExistsError:
        # symlink pendurado ou arquivo no lugar: a conferencia abaixo diz o motivo
        pass
    return verificar_diretorio_proprio(path)
