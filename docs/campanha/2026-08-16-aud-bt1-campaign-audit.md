# AUD-BT-1 — auditoria de campanha bigtech 2026-08-16 (onda W7)

**Data da auditoria:** 2026-08-17  
**Hora local (medida):** `17/08/26 - 00:40:17` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** `internal-auditor` — host Grok, papel teto **[grok][mais recente]**  
**Item:** `AUD-BT-1` (auditoria ponta-a-ponta da campanha: SoT, dual-authority, porte, CI matrix, host legado, drift+evals, proteção de `main`, residual do `TODO.md`)  
**Runbook:** `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` + `AUDITORIAS.md` § Campanha 2026-08-16  
**Pré-reqs medidos na tabela (antes desta fatia):** `TST-BT-1` ✅✓ · `BT-0`..`BT-9` ✅✓ · `N9`/`OS-*`/`TOOL-*` 💡 cancelados (não reabertos)

**SHA sob auditoria / `origin/main` no início:** `914eb277533026445ce19be294306116508496a1`  
`docs(tst-bt1): CI #14 verde no SHA de verificação 82eb52e`  
`main` == `origin/main`; working tree limpa no início. `git ls-remote origin refs/heads/main` = o mesmo SHA.  
**Baseline de produto (não é o SHA desta auditoria):** tag `bigtech--v0.2.0` → `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6`  
**Método:** re-medição em disco + git + API GitHub (`gh api` GET). Relatório de fatia anterior **não** foi aceite sem prova. Cada gate abaixo foi re-executado ou re-lido nesta sessão.

**Veredito global:** **APROVADO** — **8/8 temas PASS**, **0 FAIL material**.  
**Score:** **96 / 100**  
**Decisão autônoma (confirmar retroativamente):** promover `AUD-BT-1` para **✅ Concluído** e Estado Auditado **✓**. Campanha BT-\* sem ⏳/🔍. Sem cutover de `~/.claude`. Sem reabrir N9/OS/TOOL. Push + tag `campanha/w7-aud-bt1` autorizados no fim da onda W7.

---

## Escopo e o que isto não é

- Fecha a **auditoria de campanha** (espírito de `AUD-REPORT`, sem recriar o REPORT 1.0).
- Re-mede os 8 temas do DoD desta ordem de serviço no HEAD `914eb27`.
- **Não** executa PHASE 11 / cutover da instalação viva.
- **Não** reabre N9 (marketplace community), OS-1..5 nem TOOL-1..4.
- **Não** é release de produto (`v*`), merge extra nem alteração de agents/skills/hooks.
- **Não** aceita “CI verde” pela mensagem de push: a prova é `gh run view --json`.

---

## Score e tabela PASS/FAIL

| # | Tema | Veredito | Pontos | Evidência âncora |
|---|---|:---:|---:|---|
| 1 | Source of truth (ADR + ZERO-ÓRFÃOS) | **PASS** | 12 | `docs/adr/ADR-source-of-truth.md` existe; `validate_plugin.py` 74 `.md` / 5 dimensões = 0 |
| 2 | Dual-authority (inventário + plano; sem cutover) | **PASS** | 12 | CSV+MD+plano versionados; vivo: vault 71, INTERSECTION **51**, PLUGIN_ONLY **0**; `celso-ceo` ainda em `~/.claude/agents/` |
| 3 | Porte (`early\|scale\|bigtech`; `solo`→`early`) | **PASS** | 13 | `argument-hint` sem `solo`; `DEPRECATED_PORTE_ALIASES={"solo":"early"}`; peer-primário = **0**; eval `FORBID-SOLO-ALIAS` PASS |
| 4 | CI matrix + preci + run recente | **PASS** | 13 | `preci.sh` **10/10**; CI **#15** `31991774322` SHA `914eb27` **8/8 success** |
| 5 | Host legado (0 `codeberg.org` operacional; origin GitHub) | **PASS** | 12 | origin GitHub; `.forgejo` ausente; 0 hits `codeberg.org` em paths de produto |
| 6 | Drift gate + evals | **PASS** | 13 | `check_semantic_drift.py` 0 findings; evals **10/10** |
| 7 | Branch protection (`GET` API) | **PASS** | 13 | `protected: true`; HTTP 200; 8 contexts; `strict=true`; force-push/delete off |
| 8 | TODO residual (campanha BT sem ⏳/🔍) | **PASS** | 12 | único ⏳ pré-auditoria = `AUD-BT-1`; após esta fatia, BT-\*/TST-BT-1/AUD-BT-1 todos ✅✓ |
| | **Total** | **APROVADO** | **96** | 4 pontos retidos por residuais públicos/processo (abaixo) — nenhum é FAIL |

Nenhum FAIL material. Residuais **não** impedem APROVADO.

---

## 1. Source of truth

**Critério:** `docs/adr/ADR-source-of-truth.md` existe e está higienizado (ZERO-ÓRFÃOS PASS).

| Prova | Resultado |
|---|---|
| Ficheiro tracked | `docs/adr/ADR-source-of-truth.md` (366 linhas) + `docs/adr/README.md` (índice) |
| Status do ADR | Aceito (decisão autônoma 2026-08-16; confirmar retroativamente) |
| Item | BT-1 (D1–D10: owner = plugin; overlay; sem sync bidirecional; taxonomia D8; host só GitHub) |
| `python3 scripts/validate_plugin.py` | **PASS** EXIT=0 |
| Escopo do gate | 74 `.md` em `agents/`, `skills/`, `docs/` (exceto `docs/superpowers`, `docs/auditoria`, `docs/submission`, `docs/campanha`, `docs/house`) — **inclui** `docs/adr/` |
| Dimensões | wikilinks 0 · local_paths 0 · personal 0 · excluded 0 · orphan_links 0 |

`docs/house/` (10 manuais + README) está fora do gate por desenho (espelho vault). ADR não cita path de máquina, PII nem `[[wikilink]]`.

**Veredito: PASS.**

---

## 2. Dual-authority

**Critério:** inventário + plano de cutover existem; **sem** cutover real de `~/.claude`.

| Artefacto | Existe | Nota |
|---|:---:|---|
| `docs/campanha/2026-08-16-dual-authority-inventory.md` | sim | 51 CORE-GENERIC + 12 EXCLUSION + 8 OVERLAY |
| `docs/campanha/2026-08-16-dual-authority-inventory.csv` | sim | taxonomia ADR D8 |
| `docs/campanha/2026-08-16-dual-authority-cutover-plan.md` | sim | título “só plano”; §0 “Zero cutover real agora” |
| `docs/campanha/2026-08-16-verify-bt6.md` | sim | verificação adversarial já ✅ |

Re-medição viva nesta sessão (`name:` no frontmatter):

| Conjunto | N |
|---|---:|
| Plugin `agents/*.md` | 51 |
| Vault `~/.claude/agents/*.md` | 71 |
| INTERSECTION | **51** |
| VAULT_ONLY | **20** |
| PLUGIN_ONLY | **0** |
| `celso-ceo` / `cosimo-chief-of-staff` no vault | **ainda presentes** |

O plano **proíbe** `rm`/`git rm` de globais até PHASE 11 + canário + ordem do líder. Esta auditoria **não** moveu nenhum ficheiro em `~/.claude/`. Dual authority homônima permanece **por desenho** (ADR D2/D6) — não é defeito desta onda.

**Veredito: PASS.**

---

## 3. Porte

**Critério:** `solo` não é porte canônico; valores = `early|scale|bigtech`; alias `solo`→`early`.

| Superfície | Medição |
|---|---|
| `skills/bigtech/SKILL.md` L4 | `argument-hint: … [--porte early\|scale\|bigtech]` — `solo` **fora** do enum |
| Skill L18/L58/L104 | alias deprecado documentado; **nunca** gravar `porte=solo` |
| `agents/cosimo-chief-of-staff.md` L42 | “Valores de porte = só `early \| scale \| bigtech`” |
| `docs/ORG.md` L122–127 | tabela Pipeline-Early/Lean/Padrão/Completo; piso early; alias `solo`→`early` |
| `hooks/bigtech_porte_reminder.py` | `DEPRECATED_PORTE_ALIASES = {"solo": "early"}` |
| `hooks/bigtech_reinforce.py` | `VALID_PORTES = {early, scale, bigtech}` + mesmo alias |
| Peer-primário (`solo` ao lado de `early/scale` sem deprec/alias/teste) | **0** |
| Eval `FORBID-SOLO-ALIAS` | PASS (`got=early`) |

`solo` só sobrevive como deprecação, fixture de teste ou prosa de “não é porte”. Headcount não entra em `VALID_PORTES`.

**Veredito: PASS.**

---

## 4. CI matrix + preci + run recente

**Critério:** matrix multi-OS; `preci` local PASS; citar run CI success recente.

### 4.1 Workflow (`.github/workflows/ci.yml`)

Um workflow `CI`: `ubuntu-latest` + `windows-latest` × Python 3.11/3.12; containers Debian/Fedora/Arch; job `gitleaks`. Sem `continue-on-error` nos gates. Steps hard incluem pytest, `validate_plugin`, smoke, drift (BT-7) e evals (BT-8).

### 4.2 Pre-CI local (re-executado nesta sessão)

`NO_COLOR=1 bash scripts/preci.sh` — Python 3.14.6 — **PRE-CI PASS — 10/10** EXIT=0.

| Gate | Resultado |
|---:|---|
| 1/10 ZERO-ÓRFÃOS | PASS (74 `.md`, 5×0) |
| 2/10 pytest hooks+scripts | **161 passed** em 2.69 s |
| 3/10 JSON (3 manifestos) | PASS |
| 4/10 paridade de versão | PASS `0.2.0` == `0.2.0` |
| 5/10 ruff | PASS |
| 6/10 gitleaks | PASS (88 commits; 0 leaks) |
| 7/10 smoke offline | PASS (51 agents / 4 skills / 7 hooks) |
| 8/10 drift | PASS |
| 9/10 evals | PASS 10/10 |
| 10/10 `claude plugin validate` | PASS (1 warning de `CLAUDE.md` de processo — já aceite) |

### 4.3 CI remoto recente (prova `gh run view --json`)

| Campo | Valor |
|---|---|
| Número | **#15** |
| ID | `31991774322` |
| URL | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31991774322> |
| Evento | `push` em `main` |
| HEAD | `914eb277533026445ce19be294306116508496a1` (SHA sob auditoria) |
| `conclusion` | **`success`** |
| Janela UTC | 2026-08-17T03:37:50Z → 03:38:37Z |

**8/8 jobs — todos `success`:**

| Job | Conclusão |
|---|:---:|
| validate (ubuntu-latest, py3.11) | success |
| validate (ubuntu-latest, py3.12) | success |
| validate (windows-latest, py3.11) | success |
| validate (windows-latest, py3.12) | success |
| validate (debian via container) | success |
| validate (fedora via container) | success |
| validate (archlinux via container) | success |
| gitleaks (secrets) | success |

Runs imediatamente anteriores, mesma matrix 8/8 success: **#14** `31991691630` (`82eb52e`, verificação TST-BT-1) e **#13** `31991473856` (`0fd66cd`, produto+docs BT-7). Falhas históricas #10/#11 (UTF-8 no Windows) já foram fechadas em `4e8843f` (CI #12).

**Veredito: PASS.**

---

## 5. Host legado

**Critério:** 0 `codeberg.org` operacional em product paths; `origin` GitHub.

| Prova | Resultado |
|---|---|
| `git remote -v` | só `origin` → `https://github.com/petrinhu/bigtech_plugin.git` (fetch+push) |
| Extra remotes | nenhum |
| `.forgejo/` | **ausente** |
| `rg -i codeberg\.org` em README, AGENTS, SECURITY, PRIVACY, DEVELOPMENT, CHANGELOG, `.claude-plugin`, `agents/`, `skills/`, `hooks/`, `scripts/`, `bin/`, `docs/principles`, `docs/ORG.md`, `docs/TOOLING.md`, `docs/adr` | **0 hits** |
| `git grep -i codeberg.org` excluindo `docs/campanha/` | **0** (prosa operacional de produto) |

Menções restantes de `codeberg.org` estão **só** em snapshots PHASE 0 (`phase0-metrics-before.json`, `2026-08-16-phase0-baseline.md`) e em relatórios de campanha que *medem* a ausência — prova histórica, não instrução (ADR D10). O checker `scripts/check_semantic_drift.py` (`check_codeberg`) saiu 0 findings.

**Residual (não-FAIL, já notado em BT-4):** a *description* do repositório no GitHub ainda diz *“Mirror of https://codeberg.org/petrinhu/bigtech_plugin … Source of truth: Codeberg.”* Isto é metadado do host, **fora** dos product paths. Não aponta o `origin`. Recomendação: o líder atualizar a description via UI/`gh repo edit` (não feito aqui — não é cutover nem patch de produto).

**Veredito: PASS.**

---

## 6. Drift gate + evals

**Critério:** scripts PASS (re-executados).

```
== Drift semântico (BT-7) ==
  · agents encontrados: 51 (esperado 51)
  · skills encontradas: 4
  · hooks type=command: 7; scripts resolvidos: 6
[PASS] drift semântico limpo (agents/skills/hooks/porte/host).
EXIT=0
```

```
policy: profiles=['early', 'scale', 'bigtech'] floor=early solo->early headcount_weight=0
CASE-A..D, PORTE-EARLY-PMF, PORTE-SCALE, PORTE-BIGTECH,
FORBID-SOLO-ALIAS, CRIT-MONEY, IA-CENTRAL
resultado: 10/10 PASS, 0 FAIL
EXIT=0
```

Os dois gates estão no `preci.sh` (8 e 9) e em todos os jobs da matrix CI.

**Veredito: PASS.**

---

## 7. Branch protection

**Critério:** `main` protegida — prova por `GET` API (não por relato).

```
GET /repos/petrinhu/bigtech_plugin/branches/main/protection
GET /repos/petrinhu/bigtech_plugin/branches/main
```

| Campo | Valor medido |
|---|---|
| `branches/main.protected` | **true** |
| Protection endpoint | HTTP 200 (não 404) |
| `required_status_checks.strict` | **true** |
| Contexts (8) | ubuntu 3.11/3.12, windows 3.11/3.12, debian/fedora/arch, gitleaks — `app_id` 15368 (Actions) |
| `required_pull_request_reviews` | `null` (solo maintainer; decisão BT-9) |
| `enforce_admins` | false |
| `allow_force_pushes` | **false** |
| `allow_deletions` | **false** |
| `restrictions` | `null` |
| SHA de `main` no GET | `914eb277533026445ce19be294306116508496a1` |

Bate com `docs/campanha/2026-08-16-w5-bt9-branch-protection.md`. Esta auditoria só leu (GET); não fez PUT.

**Veredito: PASS.**

---

## 8. TODO residual

**Critério:** só `AUD-BT-1` era ⏳; após a auditoria, campanha BT sem ⏳/🔍. Não reabrir N9/OS/TOOL.

Estado **antes** desta fatia (parser da tabela principal):

| ID campanha | Status | Estado Auditado |
|---|---|---|
| BT-0..BT-9 | ✅ Concluído | ✓ |
| TST-BT-1 | ✅ Concluído | ✓ |
| AUD-BT-1 | **⏳ Pendente** | — |
| N9, OS-1..5, TOOL-1..4 | 💡 Decisão tomada (cancelado 2026-08-16) | — |

Único ⏳/🔍/🔄 na tabela inteira (101 linhas parseadas): **`AUD-BT-1`**.  
Após este commit: `AUD-BT-1` → **✅ Concluído** + Estado Auditado **✓**. Campanha BT-\* fecha sem ⏳/🔍. Cancelamentos 💡 **intocados**.

**Veredito: PASS.**

---

## Residuais não-bloqueantes

1. **Description GitHub** ainda anuncia Codeberg como SoT (metadado do host). Product paths e `origin` já estão limpos. Ação futura do líder: `gh repo edit --description …`.
2. **`CLAUDE.md` de processo** (raiz) ainda dizia BT-3/BT-4 `🔍` — prosa de mid-campanha, não status da tabela. Corrigido nesta fatia para refletir ✅ já medidos. O `claude plugin validate` continua a emitir 1 warning (*CLAUDE.md at the plugin root is not loaded as project context*) — aceite desde TST-BT-1 (ficheiro de processo, não skill).
3. **Smoke é offline.** T14 original fala em `/plugin install` vivo. A campanha aceita `scripts/smoke_offline.py` como smoke versionável. Instalação viva = PHASE 11 / canário, fora desta auditoria.
4. **Dual authority viva** (51 homônimos em `~/.claude/agents/`) é o estado transitório do ADR até o canário. Não é gap de AUD-BT-1.
5. **ADR “Aceito em modo autônomo”** e várias decisões BT-\* pedem confirmação retroativa do líder. Não bloqueia o fecho da tabela.
6. **`docs/campanha/` excluído** do ZERO-ÓRFÃOS — este relatório cita SHAs, URLs e `~/.claude` sem disparar o gate. Esperado.

---

## O que esta auditoria não promove / não faz

| Superfície | Estado |
|---|---|
| `AUD-BT-1` | **✅ Concluído** + Estado Auditado **✓** (este commit) |
| BT-0..BT-9, TST-BT-1 | já ✅✓; não reabertos |
| N9 / OS-1..5 / TOOL-1..4 | 💡 cancelados; **não reabertos** |
| PHASE 11 / cutover `~/.claude` | **não** |
| Tag de release `v*` / merge extra | **não** |
| Description GitHub (Codeberg) | residual; não editada |

---

## Decisão

| Campo | Valor |
|---|---|
| Veredito | **APROVADO** (8/8 PASS, 0 FAIL material) |
| Score | **96 / 100** |
| TODO `AUD-BT-1` Status | **✅ Concluído** |
| TODO `AUD-BT-1` Estado Auditado | **✓** |
| Campanha BT residual ⏳/🔍 | **0** |
| Push | **sim** (`origin main` + tags) — fim da onda W7, autorizado no contexto |
| Tag | `campanha/w7-aud-bt1` (anotada) neste commit de auditoria |

**Decisão autônoma (confirmar retroativamente):** APROVADO material. `AUD-BT-1` → **✅ Concluído** + Estado Auditado **✓** no mesmo commit deste relatório. Tag `campanha/w7-aud-bt1`. Push de `main` + tags. Sem cutover. Sem N9/OS/TOOL.
