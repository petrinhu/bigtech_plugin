#!/bin/sh
# tools/hooks/_chain.sh
#
# SPDX-License-Identifier: Apache-2.0
# Licença: Apache-2.0 (ver NOTICE na raiz do plugin).
# Derivado do projeto standalone tab_pendencias, do mesmo autor, relicenciado sob Apache-2.0.
#
# Delega ao hook LOCAL do repo (.git/hooks/<nome>) que um core.hooksPath GLOBAL
# sombreia. Sem isto, definir core.hooksPath global desativaria silenciosamente
# os hooks proprios de cada repo (git-lfs, framework pre-commit, husky, etc.).
#
# E "sourced" pelos shims de pass-through (pre-commit, pre-push, ...). Usa o
# basename do hook chamador, acha o hook local pelo --git-common-dir (correto
# tambem em worktrees; NUNCA usa --git-path hooks, que devolveria o proprio dir
# global e causaria loop). Preserva args, stdin e exit code via exec, entao um
# hook local que BLOQUEIA (ex: pre-commit que falha) continua bloqueando.
__name=$(basename "$0")
__gd=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
__local="$__gd/hooks/$__name"
[ -x "$__local" ] && exec "$__local" "$@"
exit 0
