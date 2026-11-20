# tools/casa/__init__.py -- convencoes da CASA (opt-in), isoladas do nucleo
# SPDX-License-Identifier: Apache-2.0
# Licença: Apache-2.0 (ver NOTICE na raiz do plugin).
# Derivado do projeto standalone tab_pendencias, do mesmo autor, relicenciado sob Apache-2.0.
"""
tools/casa/

Subpacote reservado para a logica de checks `profile == "casa"` (ADR-0001,
secao (a)): convencoes especificas da casa do autor (hoje so CHK-14,
Wiki+doc-iniciante -- ainda por implementar em CHK-CASA, W8). Nenhum check
`profile == "core"` pode importar nada daqui; `tools/todo_audit.py` prova
isso em CI via `core_boundary_violations()`, que verifica em que ARQUIVO
(nao so nome de modulo -- `tools/` nao e um pacote Python formal, os scripts
sao importados como modulos soltos via sys.path) o `run` de cada check
`core` foi definido.

Este arquivo fica vazio de checks de proposito ate a fatia CHK-CASA. A
funcao abaixo existe SO para o teste de fronteira de AUDIT-ENG poder provar
(antes de existir qualquer check 'casa' de verdade) que a deteccao de
violacao PEGA um caso real -- nunca e registrada em `tools.todo_audit.CHECKS`.
"""


def _only_for_boundary_test(ctx):
    """Nunca chamada em producao. Existe so para os testes de fronteira
    core-x-casa de `tools/todo_audit.py` terem uma funcao real, definida
    fisicamente neste arquivo, para apontar como violacao sintetica."""
    return []
