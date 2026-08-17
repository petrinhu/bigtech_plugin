# BT-4 — CI multi-OS GitHub Actions (2026-08-16)

Item: **BT-4**. Commit de implementação: `b367e34` (workflow + exclusões validate).  
Status na `TODO.md`: **🔍 Pendente verificação** (não ✅ — falta prova no remoto).

## Jobs / matrix

Workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)

| Job | Onde | Células |
|---|---|---|
| `test` | nativo | `ubuntu-latest` × py 3.11/3.12; `windows-latest` × py 3.11/3.12 |
| `test-distros` | container em ubuntu-latest | Debian 12-slim, Fedora 41, Arch (digests pinados) |
| `secrets-scan` | ubuntu-latest | gitleaks (histórico completo, hard gate) |

Gates no job `test` (todas as células): `pytest hooks/tests`, `validate_plugin.py`, `smoke_offline.py`, JSON dos 3 manifests, paridade de versão plugin↔marketplace, `ruff check hooks/ scripts/`.  
Ubuntu only: `bash scripts/preci.sh` (pre-CI completo).  
Containers: pytest + validate + smoke (venv em `/tmp` por PEP 668).

Triggers: `push` em `main`, `pull_request`, `workflow_dispatch`. `fail-fast: false`. Sem `continue-on-error` nos gates hard.

## Exclusões do validate (ZERO-ORFAOS)

Em `scripts/validate_plugin.py`, `EXCLUDED_SUBTREES` inclui, entre outras:

- **`docs/campanha`** — snapshots/métricas da campanha (paths de máquina, nomes, prova histórica). Não é produto distribuído ao instalador.
- **`docs/house`** — cópia canônica do vault (wikilinks e papéis por desenho). O gate zero-órfãos **não** re-higieniza o vault; higiene do produto fica em `agents/`, `skills/` e no restante de `docs/`.

Sem essas exclusões, o gate 4.1 falharia em material de processo/cópia de vault legítimo, sem ganho de higiene no pacote instalável.

## Prova local (esta máquina, re-medida na fatia F2)

HEAD de partida F2: `b367e3402afcad46d32297651e530a986e2021e7`.

| Gate | Resultado |
|---|---|
| `python3 scripts/validate_plugin.py` | PASS (5 dimensões, 72 `.md` no escopo) |
| `python -m pytest hooks/tests -q` | **147 passed** |
| `python3 scripts/smoke_offline.py` | PASS |
| `bash scripts/preci.sh` | **PRE-CI PASS** (8/8 gates, incl. gitleaks + `claude plugin validate`) |

## Próximo

Observar **GitHub Actions** após push de `main` (main/orquestrador; sem push nesta fatia).  
DoD remoto: matrix completa verde (nativos + containers + gitleaks), não só job local Ubuntu.  
Só então TST/AUD podem promover BT-4 para ✅.
