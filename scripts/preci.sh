#!/usr/bin/env bash
# preci.sh — gates locais de pre-CI do plugin "bigtech" (TST-T15).
#
# Roda os mesmos gates que o CI do Codeberg (.forgejo/workflows/ci.yml), na ordem,
# e FALHA no primeiro erro (fail-fast). Rode-o antes de abrir PR / push pra pegar
# problema na maquina, sem gastar fila de runner.
#
# Gates (em ordem), sao 8 no total:
#   1. Gate ZERO-ORFAOS (spec 4.1)   -> python3 scripts/validate_plugin.py
#   2. Testes dos hooks (suite dos hooks) -> python3 -m pytest hooks/tests -q
#   3. JSON valido (3 manifestos)    -> python3 -m json.tool em cada um
#   4. Paridade de versao            -> plugin.json == marketplace.json (plugins[0].version)
#   5. Lint Python (se ruff existir) -> ruff check hooks/ scripts/   [degrada gracioso]
#   6. Secret scan (se gitleaks)     -> gitleaks detect ... -c .gitleaks.toml [degrada]
#   7. Smoke offline                 -> python3 scripts/smoke_offline.py (frontmatter + hooks)
#   8. claude plugin validate (x2)   -> --strict no diretorio e no plugin.json [degrada gracioso]
#
# Ferramentas opcionais (ruff, gitleaks, claude): se AUSENTES localmente, o gate
# avisa que "rodara no CI" e segue (nao falha); paridade total e garantida no CI,
# que as instala. Os gates 1-4 e 7 sao obrigatorios e usam so a stdlib do Python.
#
# Uso:
#   bash scripts/preci.sh        # da raiz do repo ou de qualquer lugar
#   ./scripts/preci.sh           # (apos chmod +x)
#
# Exit code: 0 se todos os gates obrigatorios PASS; !=0 no primeiro FAIL.

set -euo pipefail

# --- Localizacao: ancora na raiz do repo (pai de scripts/), independe do CWD. ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# --- Cores (desliga se nao for TTY ou se NO_COLOR estiver setado). ---------------
if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_RESET=$'\033[0m'; C_RED=$'\033[31m'; C_GREEN=$'\033[32m'
  C_YELLOW=$'\033[33m'; C_BLUE=$'\033[34m'; C_BOLD=$'\033[1m'
else
  C_RESET=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_BOLD=""
fi

GATE_NUM=0
TOTAL_GATES=8

# Cabecalho de um gate (numerado).
gate() {
  GATE_NUM=$((GATE_NUM + 1))
  printf '\n%s==> [gate %d/%d] %s%s\n' \
    "${C_BOLD}${C_BLUE}" "${GATE_NUM}" "${TOTAL_GATES}" "$1" "${C_RESET}"
}

pass() { printf '%s[PASS]%s %s\n' "${C_GREEN}" "${C_RESET}" "$1"; }
skip() { printf '%s[SKIP]%s %s\n' "${C_YELLOW}" "${C_RESET}" "$1"; }
# fail(): imprime e encerra com exit 1 (set -e ja interrompe; isto da a mensagem).
fail() { printf '%s[FAIL]%s %s\n' "${C_RED}" "${C_RESET}" "$1" >&2; exit 1; }

# Escolhe o interpretador Python (prefere python3, cai pra python).
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  printf '%s[FAIL]%s python3 nao encontrado — pre-requisito ausente.\n' \
    "${C_RED}" "${C_RESET}" >&2
  exit 1
fi

printf '%s== pre-CI do plugin bigtech (TST-T15) ==%s\n' "${C_BOLD}" "${C_RESET}"
printf 'raiz: %s\n' "${REPO_ROOT}"
printf 'python: %s (%s)\n' "${PY}" "$(${PY} --version 2>&1)"

# =================================================================================
# Gate 1 — ZERO-ORFAOS (spec 4.1)
# =================================================================================
gate "ZERO-ORFAOS (spec 4.1): validate_plugin.py"
if ${PY} scripts/validate_plugin.py; then
  pass "gate zero-orfaos limpo (5 dimensoes)."
else
  fail "gate zero-orfaos reprovou — veja as violacoes acima."
fi

# =================================================================================
# Gate 2 — Testes dos hooks (suite dos hooks)
# =================================================================================
gate "Testes dos hooks: pytest hooks/tests"
if ! ${PY} -c 'import pytest' >/dev/null 2>&1; then
  fail "pytest nao instalado localmente. Instale com: ${PY} -m pip install pytest"
fi
if ${PY} -m pytest hooks/tests -q; then
  pass "suite de testes dos hooks verde."
else
  fail "pytest reprovou — veja a saida acima."
fi

# =================================================================================
# Gate 3 — JSON valido (3 manifestos)
# =================================================================================
gate "JSON valido: plugin.json, marketplace.json, hooks.json"
JSON_FILES=(
  ".claude-plugin/plugin.json"
  ".claude-plugin/marketplace.json"
  "hooks/hooks.json"
)
json_ok=1
for jf in "${JSON_FILES[@]}"; do
  if [[ ! -f "${jf}" ]]; then
    printf '  %s[FAIL]%s ausente: %s\n' "${C_RED}" "${C_RESET}" "${jf}" >&2
    json_ok=0
    continue
  fi
  # json.tool escreve o JSON formatado em stdout se valido; -> /dev/null.
  if ${PY} -m json.tool "${jf}" >/dev/null 2>&1; then
    printf '  %s[ok]%s %s\n' "${C_GREEN}" "${C_RESET}" "${jf}"
  else
    printf '  %s[FAIL]%s JSON invalido: %s\n' "${C_RED}" "${C_RESET}" "${jf}" >&2
    # Re-roda mostrando o erro do parser (sem redirecionar stderr).
    ${PY} -m json.tool "${jf}" >/dev/null || true
    json_ok=0
  fi
done
if [[ "${json_ok}" -eq 1 ]]; then
  pass "os 3 manifestos JSON sao validos."
else
  fail "ao menos um manifesto JSON e invalido/ausente."
fi

# =================================================================================
# Gate 4 - Paridade de versao (plugin.json == marketplace.json)
# =================================================================================
# A versao do plugin vive em dois lugares (plugin.json::version e
# marketplace.json::plugins[0].version). Divergencia gera um pacote inconsistente
# e e facil de esquecer ao bumpar. Este gate FALHA se as duas nao baterem.
# Python stdlib (json), sem dependencia externa.
gate "Paridade de versao: plugin.json vs marketplace.json"
if ${PY} - <<'PYEOF'
import json
import sys

PLUGIN = ".claude-plugin/plugin.json"
MARKET = ".claude-plugin/marketplace.json"

try:
    with open(PLUGIN, encoding="utf-8") as fh:
        plugin_ver = json.load(fh).get("version")
    with open(MARKET, encoding="utf-8") as fh:
        market = json.load(fh)
    plugins = market.get("plugins") or []
    market_ver = plugins[0].get("version") if plugins else None
except (OSError, ValueError, IndexError, AttributeError) as exc:
    print(f"  erro ao ler as versoes: {exc}", file=sys.stderr)
    sys.exit(2)

if not plugin_ver:
    print(f"  {PLUGIN}: campo 'version' ausente ou vazio.", file=sys.stderr)
    sys.exit(2)
if not market_ver:
    print(f"  {MARKET}: 'plugins[0].version' ausente ou vazio.", file=sys.stderr)
    sys.exit(2)
if plugin_ver != market_ver:
    print(
        f"  divergencia: plugin.json={plugin_ver!r} != "
        f"marketplace.json plugins[0].version={market_ver!r}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"  versao casada: {plugin_ver}")
sys.exit(0)
PYEOF
then
  pass "versao identica em plugin.json e marketplace.json."
else
  fail "versao divergente entre plugin.json e marketplace.json; sincronize antes de seguir."
fi

# =================================================================================
# Gate 5 - Lint Python (ruff): opcional, degrada gracioso
# =================================================================================
gate "Lint Python: ruff check hooks/ scripts/"
if command -v ruff >/dev/null 2>&1; then
  if ruff check hooks/ scripts/; then
    pass "ruff sem reclamacoes."
  else
    fail "ruff encontrou problemas — veja acima."
  fi
else
  skip "ruff ausente localmente — rodara no CI (pip install ruff)."
fi

# =================================================================================
# Gate 6 - Secret scan (gitleaks): opcional, degrada gracioso
# =================================================================================
gate "Secret scan: gitleaks detect"
if command -v gitleaks >/dev/null 2>&1; then
  GITLEAKS_ARGS=(detect --no-banner --redact)
  if [[ -f ".gitleaks.toml" ]]; then
    GITLEAKS_ARGS+=(-c .gitleaks.toml)
  fi
  # --no-git: varre a arvore de trabalho (nao so historico) — pega secret nao
  # commitado ainda. Em repo git tambem cobre o que esta staged/working.
  GITLEAKS_ARGS+=(--source ".")
  if gitleaks "${GITLEAKS_ARGS[@]}"; then
    pass "gitleaks: nenhum secret detectado."
  else
    fail "gitleaks DETECTOU possivel secret — investigue antes de commitar."
  fi
else
  skip "gitleaks ausente localmente — rodara no CI (binario de release)."
fi

# =================================================================================
# Gate 7 - Smoke offline (frontmatter parseavel + hooks executam)
# =================================================================================
gate "Smoke offline: smoke_offline.py"
if ${PY} scripts/smoke_offline.py; then
  pass "smoke offline: plugin carregavel; hooks executam e se comportam."
else
  fail "smoke offline reprovou — veja acima."
fi

# =================================================================================
# Gate 8 - claude plugin validate --strict (x2): opcional, degrada gracioso
# =================================================================================
# Validacao oficial da CLI do Claude Code, em DOIS alvos (cobre marketplace +
# manifesto do plugin):
#   a) no diretorio (.)            -> resolve o marketplace.json e o(s) plugin(s)
#   b) em ./.claude-plugin/plugin.json -> valida o manifesto do plugin direto
# Se a CLI `claude` NAO estiver no runner, o gate faz SKIP avisando (degradacao
# graciosa, igual ruff/gitleaks); nao falha o pre-CI por ausencia da CLI.
gate "claude plugin validate --strict (diretorio + plugin.json)"
if command -v claude >/dev/null 2>&1; then
  validate_ok=1
  if claude plugin validate --strict .; then
    printf '  %s[ok]%s validate --strict no diretorio (marketplace).\n' \
      "${C_GREEN}" "${C_RESET}"
  else
    printf '  %s[FAIL]%s validate --strict reprovou no diretorio.\n' \
      "${C_RED}" "${C_RESET}" >&2
    validate_ok=0
  fi
  if claude plugin validate --strict ./.claude-plugin/plugin.json; then
    printf '  %s[ok]%s validate --strict no plugin.json.\n' \
      "${C_GREEN}" "${C_RESET}"
  else
    printf '  %s[FAIL]%s validate --strict reprovou no plugin.json.\n' \
      "${C_RED}" "${C_RESET}" >&2
    validate_ok=0
  fi
  if [[ "${validate_ok}" -eq 1 ]]; then
    pass "claude plugin validate --strict limpo nos dois alvos."
  else
    fail "claude plugin validate --strict reprovou; veja acima."
  fi
else
  skip "CLI 'claude' ausente no runner; validate --strict roda em quem tiver a CLI."
fi

# =================================================================================
# Resumo
# =================================================================================
printf '\n%s========================================%s\n' "${C_BOLD}" "${C_RESET}"
printf '%s%s PRE-CI PASS %s — todos os gates obrigatorios verdes.\n' \
  "${C_BOLD}" "${C_GREEN}" "${C_RESET}"
printf '%s========================================%s\n' "${C_BOLD}" "${C_RESET}"
