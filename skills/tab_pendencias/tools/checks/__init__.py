# tools/checks/__init__.py -- checks concretos do catalogo CHK-01..14
# SPDX-License-Identifier: Apache-2.0
# Licença: Apache-2.0 (ver NOTICE na raiz do plugin).
# Derivado do projeto standalone tab_pendencias, do mesmo autor, relicenciado sob Apache-2.0.
"""
tools/checks/

Subpacote com os checks concretos do catalogo (CHK-01..14), um modulo por
fatia (ex.: `chk_graph.py` para CHK-05/06/07 -- CHK-GRAPH). Todos os checks
aqui sao `profile == "core"` a menos que a propria fatia diga o contrario;
nenhum modulo deste subpacote importa nada de `tools/casa/` (fronteira
ADR-0001 secao a). `tools/todo_audit.py` importa cada modulo e registra os
`Check` correspondentes em `CHECKS` -- este subpacote nao registra nada
sozinho, so define funcoes `run(ctx) -> list[Finding]` e (opcionalmente)
helpers puros de deteccao/parsing reutilizados pelos testes.
"""
