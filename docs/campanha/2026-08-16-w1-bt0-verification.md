# W1 / BT-0 — verificação adversarial da PHASE 0

**Data da verificação:** 2026-08-16  
**Hora local (medida):** `16/08/26 - 23:46:05` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** auditor de campanha — host Grok, papel [grok][mais recente]  
**Item:** `BT-0` (PHASE 0 freeze / baseline / inventário)  
**DoD canônico:** `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` § PHASE 0 (linhas 677–684)  
**HEAD do plugin no início desta auditoria:** `26f8641edb56e0d9cacd42e3df2410b8c7752a32` (working tree limpa)  
**Método:** re-medição em disco/git. Prosa do baseline **não** foi aceita sem prova.

**Veredito:** **PASS em todos os itens materiais do DoD.**  
**Decisão autônoma (confirmar retroativamente):** promover `BT-0` para **✅ Concluído** e Estado Auditado **✓**. Não é promoção dos outros BT-\* (permanecem 🔍/⏳).

---

## Escopo e o que isto não é

- Isto fecha o **DoD da PHASE 0** (freeze SHA + inventário + modelos + “nenhum arquivo vivo removido”).
- **Não** fecha BT-3 / BT-2 / BT-4 / BT-1. After-metrics de BT-3 e o relatório de CI entram só como **artefatos esperados da campanha** listados na ordem de serviço W1.
- **Não** é cutover de `~/.claude`. **Não** houve push.

---

## Checklist DoD (item a item)

| # | Item | Veredito | Evidência âncora |
|---|---|:---:|---|
| 1 | baseline SHA dos 3 repos documentados | **PASS** | `docs/campanha/2026-08-16-phase0-baseline.md` + `phase0-metrics-before.json`; SHAs existem como commits; freeze plugin é ancestral de HEAD |
| 2 | inventário agents/skills/hooks (csv/md) | **PASS** | `phase0-agents-inventory.csv` (71 linhas) + seções 0.3–0.5 do baseline; remedir 51/71/4/7 |
| 3 | distribuição de modelos medida | **PASS** | JSON `models_plugin` + remedir live: plugin 51×`opus`; vault 70×`opus` + 1×`sonnet` (`linux-diag`) |
| 4 | métricas before/after BT-3 | **PASS** | `phase0-metrics-before.json` @ `8076cd1`; `phase0-metrics-after-bt3.json` @ `04193b9`; after remedir origin GitHub + `.forgejo` ausente + 0 refs operacionais nos paths de produto |
| 5 | docs/campanha baseline + house + CI report | **PASS** | baseline + `2026-08-16-phase0-house-plan.md` + `docs/house/` 10/10 + `2026-08-16-bt4-ci-multi-os.md` |
| 6 | nenhum arquivo vivo `~/.claude` destruído | **PASS** | HEAD vault ainda `5b19b52`; 0 deleções tracked; 71 agents / 46 skills / hooks flagged presentes; `settings.json` 21346 B; única sujeira = memórias de *projeto* (não agents/skills/hooks) |
| 7 | TODO BT-0 em 🔍 e artefatos no histórico | **PASS** (pré-promoção) | linha BT-0 em 🔍 desde o intake (`0f2b320`); artefatos PHASE 0 no commit `8076cd1` (filho direto de `61c3ea4`) |

Nenhum FAIL material. Residuais abaixo **não** impedem ✅.

---

## 1. Baseline SHA dos três repos

### Documentado (freeze)

Fonte: `docs/campanha/2026-08-16-phase0-baseline.md` (blob HEAD `d45f8d7…`) e `phase0-metrics-before.json` (blob HEAD `9098a88…`).

| Repo | Path | SHA documentado no freeze |
|---|---|---|
| plugin_bigtech | `…/Projects/plugin_bigtech` | `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` |
| claude-memory (`~/.claude`) | `/home/petrus/.claude` | `5b19b524a7409d5b60ea3a3912b2761877c6c7b8` |
| tab_pendencias (produto) | `…/Projects/tab_pendencias` | `0546c53ef5f97dc03975832842c8a73ef3c99e1f` |

### Re-medição (comandos)

```bash
git -C "$PLUGIN" rev-parse HEAD                          # 26f8641edb56e0d9cacd42e3df2410b8c7752a32
git -C "$PLUGIN" cat-file -t 61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6   # commit
git -C "$PLUGIN" merge-base --is-ancestor 61c3ea4… HEAD  # YES
git -C "$PLUGIN" rev-parse 'bigtech--v0.2.0^{commit}'    # 61c3ea4…  (tag == freeze)
git -C "$PLUGIN" log -1 --format='%P' 8076cd1            # 61c3ea4…  (baseline commit é filho do freeze)

git -C ~/.claude rev-parse HEAD                          # 5b19b524a7409d5b60ea3a3912b2761877c6c7b8
git -C ~/.claude cat-file -t 5b19b52…                    # commit
git -C ~/.claude check-ignore -v settings.json           # .gitignore:52:settings.json
wc -c < ~/.claude/settings.json                          # 21346

git -C "$TAB" rev-parse HEAD                             # 0546c53ef5f97dc03975832842c8a73ef3c99e1f
git -C ~/.claude submodule status skills/tab_pendencias  # 0546c53… (v1.2.2)
```

| Checagem | Resultado |
|---|---|
| Freeze plugin existe e é ancestral de HEAD | **PASS** |
| Tag `bigtech--v0.2.0` aponta para o freeze | **PASS** (`61c3ea4`) |
| Commit do baseline (`8076cd1`, 16/08/26 22:47:12 −03) é filho direto do freeze | **PASS** |
| `~/.claude` HEAD **ainda é** o SHA do freeze | **PASS** (não andou) |
| `tab_pendencias` HEAD **ainda é** o SHA do freeze | **PASS** |
| Pin Claude submodule = mesmo SHA (`v1.2.2`) | **PASS** |
| Symlink Grok `~/.grok/skills/tab_pendencias` → produto | **PASS** |
| `settings.json` gitignored e presente em disco | **PASS** |

### Residual (não-FAIL)

O runbook `PLANO-…` § I.1 cita `claude-memory` em `627e507fbee06b6ed4d8940526a43f76ffc1ddb1` (auto-snapshot 15/08/26). Esse SHA **existe** e é **ancestral** de `5b19b52` (auto-snapshot 16/08/26 22:31:34 −03). A PHASE 0 **re-mediu** o vault no dia da campanha; o plano ficou com o SHA da auditoria da véspera. Isso é staleness de prosa do plano, não buraco de freeze.

---

## 2. Inventário agents / skills / hooks

### Artefatos

| Artefato | Introduzido em | Blob HEAD |
|---|---|---|
| `docs/campanha/phase0-agents-inventory.csv` | `8076cd1` | `76568587187550bd5ef28c11ce750d56c2d75732` |
| `docs/campanha/2026-08-16-phase0-baseline.md` §§ 0.3–0.5 | `8076cd1` (+ apêndice after em `04193b9`) | `d45f8d7b8680acf1a72860330f7e513c7c21ab87` |

### CSV (parser próprio nesta auditoria)

```
rows=71
INTERSECTION=51  VAULT_ONLY=20  CORE_ONLY=0
identical yes=0  identical no=51
CORE-GENERIC=51  INTENTIONAL-EXCLUSION=12  PERSONAL-OVERLAY=8
has_Agent=12  has_Bash=31
```

Bate com o baseline (`CORE_ONLY=0 VAULT_ONLY=20 INTERSECTION=51`) e com `phase0-metrics-before.json`.

### Remedir live (16/08/26 23:4x)

| Superfície | Freeze / CSV | Live agora | Match? |
|---|---:|---:|:---:|
| plugin `agents/*.md` | 51 | 51 (names únicos 51) | ✅ |
| vault `~/.claude/agents/*.md` | 71 | 71 | ✅ |
| grok `~/.grok/agents/*.md` | 71 | 71 | ✅ |
| plugin skills | 4 (`bigtech`, `proj_software`, `tab_pendencias`, `visual-design-director`) | 4 mesmos dirs | ✅ |
| vault skills | 46 | 46 | ✅ |
| plugin hooks `.py` | 7 (3 bigtech + reminder + tdd_*) | 7 | ✅ |
| `hooks/hooks.json` eventos | SessionStart, UserPromptSubmit, PreToolUse, PostToolUse | mesmos 4 | ✅ |

### Integridade SHA256 do CSV

Parser: `sha256` do blob vs coluna do CSV.

| Lado | Contra o quê | Resultado |
|---|---|---|
| plugin INTERSECTION (51) | blob `8076cd1:agents/<file>` | **51/51 SHA idênticos ao CSV** |
| plugin INTERSECTION (51) | working tree atual | **48/51** — 3 divergiram *depois* do freeze |
| vault (71) | working tree atual | **71/71 SHA idênticos ao CSV** |
| arquivos vault do inventário ausentes agora | — | **[]** |

Os 3 plugin agents cujo SHA live ≠ CSV (esperado: purge BT-3 em `1bfc800`):

| name | sha256 CSV (freeze) | sha256 live |
|---|---|---|
| `devops-sre` | `9f890fb88991…` | `e3e94a9215a2…` |
| `qa-engineer` | `20ca86a10604…` | `13d695ece988…` |
| `security-engineer` | `6b30c738eff5…` | `950e30896865…` |

Isto **confirma** que o CSV é snapshot de freeze, não um inventário “sempre atual”. Para BT-0 isso é o comportamento correto.

Bytes amostrados no blob `8076cd1` vs tabela 0.3 do baseline: `cosimo` 8691, `caetano-cto` 6127, `celso-ceo` 5729, `backend-engineer` 19961, `qa-engineer` 21448, `visual-design-director` 23836, `security-engineer` 25862 — **todos batem**.

### Hooks: plugin × vault (bytes)

| Arquivo | plugin freeze `8076cd1` | plugin now | vault live | Nota baseline |
|---|---:|---:|---:|---|
| `bigtech_porte_reminder.py` | 4870 | 4870 | 4591 | 4870 vs 4591 — **bate** |
| `bigtech_reinforce.py` | 7470 | 7470 | 7319 | sha diferente — **bate o facto** |
| `tdd_guard.py` | 3883 | 3883 | 3195 | diferente — **bate** |
| `tdd_runner.py` | 4102 | 4102 | 2466 | diferente — **bate** |
| `tdd_common.py` | 7784 | **7899** | 6249 | drift **pós-freeze** no plugin (BT-4 portabilidade) |
| `bigtech_session_init.py` | presente | presente | **ausente** | “só plugin” — **bate** |

`tab_pendencias_reminder.py` no vault continua no path da skill produto (não em `~/.claude/hooks/`), como o baseline descreveu.

---

## 3. Distribuição de modelos

Fonte documentada: baseline § 0.4 + `phase0-metrics-before.json` → `models_plugin`.

| Métrica | Documentado | Remedir live plugin | Remedir live vault |
|---|---:|---:|---:|
| `model: opus` | 51 / 70 | **51** | **70** |
| `model: sonnet` | 0 / 1 | **0** | **1** (`linux-diag.md`) |
| herdado (sem `model:`) | 0 | **0** | 0 |
| `effort` ausente | 51 | **51** | — |
| `maxTurns` ausente | 51 | **51** | — |
| tool `Agent` | 12 C-level+CoS | **12** | — |
| tool `Bash` | 31 | **31** | — |

Holders de `Agent` no CSV (`has_Agent_plugin=yes`): os 12 C-level + CoS listados no baseline. Remedir por frontmatter `tools:` confirma o mesmo conjunto.

Top-10 por bytes no freeze (blob `8076cd1`) coincide com a tabela do baseline (`security-engineer` 25862 … `i18n-l10n-specialist` 16780).

---

## 4. Métricas before / after BT-3

| Arquivo | Commit | Blob HEAD |
|---|---|---|
| `docs/campanha/phase0-metrics-before.json` | `8076cd1` | `9098a8878f633fbf2c8183e02dacd3f2fc067d90` |
| `docs/campanha/phase0-metrics-after-bt3.json` | `04193b9` | `1f31dc1c5b1867a8bf6f739173837156a1f24cfb` |

### Before (claims históricos — não reescritos)

No freeze o JSON registra: `origin` Codeberg, `.forgejo` presente, `.github/workflows` ausente, 13 refs operacionais, plugin 0.2.0, `alive_files_removed: false`. Isso é **prova histórica**; o origin atual já é GitHub (BT-3). Não se exige que o before ainda descreva o working tree de agora.

### After BT-3 — remedir agora

```bash
git -C "$PLUGIN" remote get-url origin     # https://github.com/petrinhu/bigtech_plugin.git
test -d "$PLUGIN/.forgejo"                 # AUSENTE
# rg -i 'codeberg\.org|forgejo|woodpecker' nos paths de produto do JSON
# README AGENTS SECURITY PRIVACY DEVELOPMENT .claude-plugin agents skills hooks scripts bin
# matches = 0
```

| Claim after (`phase0-metrics-after-bt3.json`) | Remedir 23:4x | Match? |
|---|---|:---:|
| `origin_is_github: true` | origin = `https://github.com/petrinhu/bigtech_plugin.git` | ✅ |
| `has_forgejo_workflows: false` | `.forgejo` ausente | ✅ |
| `refs_host_legado_operacionais_produto.value: 0` | 0 ficheiros nos paths listados | ✅ |
| `delivery_commits` `766eb5a` + `1bfc800` | ambos no `git log` | ✅ |
| `has_github_workflows: false` | **era verdade em `1bfc800`**; **agora** existe `.github/workflows/ci.yml` (BT-4, `b367e34`) | histórico ✅ |

O after é snapshot **da fatia BT-3**, não do HEAD atual. A adição posterior de Actions **não** invalida o after; pertence a BT-4 (ainda 🔍, fora desta fatia).

---

## 5. Baseline + house + CI report

| Artefato esperado | Em HEAD? | Commit de introdução | Veredito |
|---|:---:|---|:---:|
| `docs/campanha/2026-08-16-phase0-baseline.md` | sim | `8076cd1` | **PASS** |
| `docs/campanha/phase0-agents-inventory.csv` | sim | `8076cd1` | **PASS** |
| `docs/campanha/phase0-metrics-before.json` | sim | `8076cd1` | **PASS** |
| `docs/campanha/phase0-metrics-after-bt3.json` | sim | `04193b9` | **PASS** |
| `docs/campanha/2026-08-16-phase0-house-plan.md` | sim | `24b1e8f` | **PASS** |
| `docs/house/` 10 manuais + README | sim | `24b1e8f` | **PASS** |
| `docs/campanha/2026-08-16-bt4-ci-multi-os.md` | sim | `9848385` | **PASS** |

`docs/house/` presente: `AGILE.md` `AUDITORIAS.md` `CONTRACT.md` `DEPLOY_CHECKLIST.md` `lideranca_pipeline_release.md` `ORG.md` `pipeline_release_1.0.md` `README.md` `Standards.md` `TESTES.md` `TOOLING.md`.

O gap P0 do baseline (`Standards.md` ausente no plugin) foi preenchido **depois** do freeze, na fatia house (`24b1e8f`). PHASE 0 documentou o gap; BT-2 entregou a cópia (BT-2 permanece 🔍 — não promovido aqui).

CI report existe e declara BT-4 ainda 🔍 (prova remota Actions pendente). Coerente com a TODO.

---

## 6. Nenhum arquivo vivo `~/.claude` destruído

Afirmação **só** porque a evidência aponta para preservação, não porque o baseline o disse.

```bash
git -C ~/.claude rev-parse HEAD                 # 5b19b52…  (= freeze)
git -C ~/.claude log --oneline 5b19b52..HEAD    # vazio
git -C ~/.claude diff --diff-filter=D --name-only HEAD   # vazio
git -C ~/.claude status --porcelain
#  M  …/plugin-bigtech/memory/MEMORY.md
#  M  …/plugin-bigtech/memory/project_session_atual.md
# ??  …/plugin-bigtech/memory/feedback_main_orquestrador_only.md
# ??  …/plugin-bigtech/memory/project_campanha_bigtech_2026_08_16.md
```

| Superfície viva | Freeze | Agora | Destruição? |
|---|---|---|---|
| HEAD git | `5b19b52` | `5b19b52` | não |
| `agents/*.md` | 71 | 71; SHA = CSV 71/71 | não |
| `skills/` | 46 | 46 | não |
| hooks flagged (`tdd_*`, `bigtech_porte_reminder`, `bigtech_reinforce`) | presentes | presentes (bytes batem tabela) | não |
| `bigtech_session_init.py` no vault | já ausente | ainda ausente | N/A (nunca esteve) |
| `settings.json` | ~21346 B, gitignored | 21346 B | não |
| Deleções tracked | — | 0 | não |

Sujeira no vault = **memórias do projeto plugin_bigtech** (2 modificadas + 2 untracked). Não é agent/skill/hook/settings. Não constitui destruição de arquivo vivo da constelação.

**PASS.** Se no futuro alguém apagar `~/.claude/agents` ou hooks, esta afirmação caduca — re-medir.

---

## 7. TODO BT-0 em 🔍 + artefatos commitados

```bash
git grep '^| BT-0 ' HEAD -- TODO.md
# | BT-0 | W1 | … | 🔍 Pendente verificação | — |
```

Histórico do ID:

- `06791a0` / `0f2b320` — intake BT-0..BT-9; BT-0 já nasceu em 🔍 (medição PHASE 0 já estava em `8076cd1`).
- `ff11151` — reorder para W1; status 🔍 mantido.
- Nenhum commit anterior a esta auditoria promoveu BT-0 a ✅.

Artefatos PHASE 0 no objeto git (não só working tree):

```
8076cd1 docs(campanha): PHASE 0 baseline measurements
        2026-08-16-phase0-baseline.md
        phase0-agents-inventory.csv
        phase0-metrics-before.json
24b1e8f docs(house): sync 10 manuais canônicos do vault (PHASE 0)
04193b9 docs(bt-3): … + phase0-metrics-after-bt3.json
9848385 docs(bt-4): … + 2026-08-16-bt4-ci-multi-os.md
```

Working tree do plugin no início da auditoria: **limpa** (`git status --porcelain` vazio).

---

## Residuais (não-FAIL)

1. **Prosa do plano § I.1** ainda cita `~/.claude` em `627e507` (15/08). Freeze PHASE 0 é `5b19b52` (16/08). Corrigir o plano é fora de BT-0.
2. **3 agents do plugin** mudaram SHA após o freeze (purge BT-3). Inventário continua válido como snapshot.
3. **`hooks/tdd_common.py`** plugin 7784 → 7899 após o freeze (BT-4). Inventário de hooks da PHASE 0 não foi reescrito — correto.
4. **After BT-3** diz `has_github_workflows: false` (verdade em `1bfc800`). BT-4 adicionou `.github/workflows/ci.yml`. Não reescrever o after.
5. **Classificações `CORE-GENERIC` / `PERSONAL-OVERLAY` / `INTENTIONAL-EXCLUSION`** no CSV são heurística (o próprio baseline diz). Zero `STALE`. Classificação semântica = BT-6 / PHASE 1, não BT-0.
6. **BT-2 / BT-3 / BT-4** continuam 🔍. Esta auditoria **não** os promove.
7. **`TODO.md` caminho crítico** ainda lista `BT-0 (W1)` como passo — prosa de navegação; só a célula Status/Auditado de BT-0 muda nesta fatia.

---

## Decisão autônoma

**Promover BT-0 → ✅ Concluído, Estado Auditado → ✓.**

Motivo: DoD PHASE 0 do plano (SHA ×3, inventário agents/skills/hooks, modelos, nenhum vivo removido) está **provado em disco/git**, e os artefatos extras da OS (before/after BT-3, house, CI report) existem e estão no histórico. A promoção é da **fatia de medição/freeze**, não das fatias de execução posteriores.

Confirmar retroativamente se o líder quiser critério mais rígido (ex.: exigir Actions remoto verde — isso é BT-4/BT-9, não PHASE 0).

---

## O que foi alterado nesta verificação

| Path | Ação |
|---|---|
| `docs/campanha/2026-08-16-w1-bt0-verification.md` | criado (este arquivo) |
| `TODO.md` linha BT-0 | Status `🔍` → `✅ Concluído`; Estado Auditado `—` → `✓` |
| tag local `campanha/w1-bt0-verify` | anotada no SHA do commit desta fatia |

Sem push. Sem edição de outros IDs BT-\*.
