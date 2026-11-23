#!/usr/bin/env bash
# preci.sh — os gates do job Ubuntu do CI do plugin "bigtech".
#
# E o que o job Ubuntu do CI (.github/workflows/ci.yml) roda, na ordem, e FALHA
# no primeiro erro (fail-fast). O CI e o portao, uma vez, depois do push: rodar
# este script na maquina e opcional e nao e exigido antes do push. Push so de
# docs pula os testes no CI; o segredo (gitleaks) e a privacidade
# (validate_plugin) tem jobs proprios, que rodam sempre.
#
# Gates (em ordem), sao 9 no total:
#   1. Gate ZERO-ORFAOS (spec 4.1)   -> python3 scripts/validate_plugin.py
#   2. Testes (hooks + scripts)      -> python3 -m pytest hooks/tests scripts/tests -q
#   3. JSON valido (4 manifestos)    -> python3 -m json.tool em cada um
#   4. Paridade de versao            -> plugin.json == marketplace.json (plugins[0].version)
#   5. Lint Python (se ruff existir) -> ruff check hooks/ scripts/   [degrada gracioso]
#   6. Smoke offline                 -> python3 scripts/smoke_offline.py (frontmatter + hooks)
#   7. Drift semântico (BT-7)        -> python3 scripts/check_semantic_drift.py [obrigatório]
#   8. Evals roteamento /bigtech     -> python3 evals/bigtech_routing/run_evals.py (BT-8)
#   9. sync docs/house (CONS-10)     -> gate_sync_house.py --check; sem chave ou vault
#                                      sai NAO CONFERIDO [nunca conta como PASS]
#
# Banner final: so diz "PRE-CI PASS" com os 9 gates passados e nenhum pulado
# nem nao conferido. Gate pulado (SKIP) nunca conta como passado; o banner lista
# quantos e quais foram pulados.
#
# Onde roda: no host (a suite de testes roda na maquina de quem chama). Para
# isolamento mais forte, rode o preci dentro de um container; a opcao fica
# aberta para quando as regras do usuario exigirem.
#
# Ferramenta opcional (ruff): se AUSENTE localmente, o gate avisa que "rodara no
# CI" e segue (nao falha); o CI a instala. Os gates 1-4 e 6-8 sao obrigatorios e
# usam so a stdlib do Python.
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
TOTAL_GATES=9
GATE_TITLE=""
# Contadores do banner final: cada gate cai em exatamente uma destas listas.
PASSED=()
SKIPPED=()
NAO_CONFERIDO=()

# Cabecalho de um gate (numerado).
gate() {
  GATE_NUM=$((GATE_NUM + 1))
  GATE_TITLE="gate ${GATE_NUM}: $1"
  printf '\n%s==> [gate %d/%d] %s%s\n' \
    "${C_BOLD}${C_BLUE}" "${GATE_NUM}" "${TOTAL_GATES}" "$1" "${C_RESET}"
}

pass() { printf '%s[PASS]%s %s\n' "${C_GREEN}" "${C_RESET}" "$1"; PASSED+=("${GATE_TITLE}"); }
skip() { printf '%s[SKIP]%s %s\n' "${C_YELLOW}" "${C_RESET}" "$1"; SKIPPED+=("${GATE_TITLE} (motivo: $1)"); }
# nao_conferido(): gate rodou sem conferencia completa (ex.: sem chave). Nao e PASS.
nao_conferido() { printf '%s[NAO CONFERIDO]%s %s\n' "${C_YELLOW}" "${C_RESET}" "$1"; NAO_CONFERIDO+=("${GATE_TITLE}"); }
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
# Gate 2 — Testes (hooks + scripts/gates)
# =================================================================================
gate "Testes: pytest hooks/tests scripts/tests"
if ! ${PY} -c 'import pytest' >/dev/null 2>&1; then
  fail "pytest nao instalado localmente. Instale com: ${PY} -m pip install pytest"
fi
if ${PY} -m pytest hooks/tests scripts/tests -q; then
  pass "suite de testes (hooks + scripts) verde."
else
  fail "pytest reprovou — veja a saida acima."
fi

# =================================================================================
# Gate 3 - JSON valido (4 manifestos: nucleo, marketplace, bundle, hooks)
# =================================================================================
gate "JSON valido: plugin.json, marketplace.json, bundle, hooks.json"
JSON_FILES=(
  ".claude-plugin/plugin.json"
  ".claude-plugin/marketplace.json"
  "bundles/bigtech-completo/.claude-plugin/plugin.json"
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
  pass "os 4 manifestos JSON sao validos."
else
  fail "ao menos um manifesto JSON e invalido/ausente."
fi

# =================================================================================
# Gate 4 - Paridade de versao: nucleo, duas entradas do marketplace e bundle
# =================================================================================
# A versao vive em quatro pontos (plugin.json, entrada bigtech, entrada
# bigtech-completo e bundles/bigtech-completo/plugin.json). A checagem fica em
# scripts/check_paridade_versao.py, com testes em scripts/tests. Saida 0 igual;
# 1 divergente; 2 ausente ou ilegivel. Qualquer uma reprova.
gate "Paridade de versao: nucleo, entradas do marketplace e bundle"
if ${PY} scripts/check_paridade_versao.py; then
  pass "versao identica nos quatro manifestos."
else
  fail "versao divergente ou manifesto ausente; sincronize antes de seguir."
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
# Gate 6 - Smoke offline (frontmatter parseavel + hooks executam)
# =================================================================================
gate "Smoke offline: smoke_offline.py"
if ${PY} scripts/smoke_offline.py; then
  pass "smoke offline: plugin carregavel; hooks executam e se comportam."
else
  fail "smoke offline reprovou — veja acima."
fi

# =================================================================================
# Gate 7 - Drift semântico (BT-7): registry agents/skills/hooks + porte/host
# =================================================================================
# Obrigatório, stdlib. Detecta name≠stem, contagem fora de EXPECTED_AGENT_COUNT, hook script ausente,
# porte legado "solo" como primário sem alias, e host legado Codeberg em produto.
gate "Drift semântico (BT-7): check_semantic_drift.py"
if ${PY} scripts/check_semantic_drift.py; then
  pass "drift semântico limpo."
else
  fail "drift semântico reprovou — veja acima."
fi

# =================================================================================
# Gate 8 - Evals de roteamento /bigtech (BT-8): hard, stdlib only
# =================================================================================
# Politica pos-BT-5: piso early, nunca profile=solo, headcount peso 0,
# criticidade eleva agents. Offline, sem LLM pago.
gate "Evals roteamento /bigtech: evals/bigtech_routing/run_evals.py"
if ${PY} evals/bigtech_routing/run_evals.py; then
  pass "evals de roteamento /bigtech verdes."
else
  fail "evals de roteamento /bigtech reprovaram - veja a tabela acima."
fi

# =================================================================================
# Gate 9 — sync docs/house (CONS-10). Sem vault ou sem chave sai NAO CONFERIDO:
# aparece como tal e nunca como PASS. Divergencia ou erro reprova.
# =================================================================================
gate "sync docs/house (CONS-10): gate_sync_house.py --check"
if sync_out="$(${PY} scripts/gate_sync_house.py --check 2>&1)"; then
  printf '%s\n' "${sync_out}"
  if printf '%s\n' "${sync_out}" | grep -q '^NAO CONFERIDO'; then
    nao_conferido "docs/house sem conferencia completa (sem vault ou chave): nao conta como PASS."
  else
    pass "docs/house conferido contra o vault (HMAC)."
  fi
else
  printf '%s\n' "${sync_out}" >&2
  fail "sync docs/house reprovou (divergencia ou erro de uso)."
fi

# =================================================================================
# Resumo: PASS so com os 9 gates passados e nenhum pulado nem nao conferido.
# =================================================================================
printf '\n%s========================================%s\n' "${C_BOLD}" "${C_RESET}"
N_PASS=${#PASSED[@]}
N_SKIP=${#SKIPPED[@]}
N_NAO=${#NAO_CONFERIDO[@]}
if [[ "${N_PASS}" -eq "${TOTAL_GATES}" && "${N_SKIP}" -eq 0 && "${N_NAO}" -eq 0 ]]; then
  printf '%s%s PRE-CI PASS%s: %d de %d gates passaram; nenhum pulado; nenhum nao conferido.\n' \
    "${C_BOLD}" "${C_GREEN}" "${C_RESET}" "${N_PASS}" "${TOTAL_GATES}"
else
  printf '%s%s PRE-CI SEM REPROVACAO%s: %d de %d gates passaram; NAO e PASS.\n' \
    "${C_BOLD}" "${C_YELLOW}" "${C_RESET}" "${N_PASS}" "${TOTAL_GATES}"
  printf '  pulados (%d):' "${N_SKIP}"
  if [[ "${N_SKIP}" -eq 0 ]]; then
    printf ' nenhum\n'
  else
    printf '\n'
    for s in "${SKIPPED[@]}"; do printf '    - %s\n' "${s}"; done
  fi
  printf '  nao conferidos (%d):' "${N_NAO}"
  if [[ "${N_NAO}" -eq 0 ]]; then
    printf ' nenhum\n'
  else
    printf '\n'
    for s in "${NAO_CONFERIDO[@]}"; do printf '    - %s\n' "${s}"; done
  fi
fi
printf '%s========================================%s\n' "${C_BOLD}" "${C_RESET}"
