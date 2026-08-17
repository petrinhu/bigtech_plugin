# TST-BT-1 — revalidação da suíte de campanha (onda W6)

**Data da verificação:** 2026-08-17  
**Hora local (medida):** `17/08/26 - 00:34:14` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** QA/verificador de campanha — host Grok, papel [grok][mais recente]  
**Item:** `TST-BT-1` (revalidar suíte campanha: `preci.sh` + pytest + `validate_plugin` + smoke + drift + evals + CI multi-OS no SHA final, pós BT-5..BT-8)  
**DoD desta ordem de serviço:**

1. `python3 scripts/validate_plugin.py` **PASS**
2. `python3 -m pytest hooks/tests scripts/tests -q` **PASS** (contar N)
3. `python3 scripts/smoke_offline.py` **PASS**
4. `python3 scripts/check_semantic_drift.py` **PASS**
5. `python3 evals/bigtech_routing/run_evals.py` **10/10**
6. `bash scripts/preci.sh` **PRE-CI PASS** completo (10/10)
7. CI multi-OS no GitHub: run **verde** no SHA sob teste (8/8 jobs)

**SHA sob teste (produto / `origin/main` no início):** `0fd66cd2ad0e1a4385932519ff64b741cb53d9e4`  
`docs(bt-7): verificação drift gate — PASS, promove ✅`  
`main` == `origin/main`; working tree limpa. `git fetch origin` não avançou o ponteiro.  
**Pré-reqs medidos na tabela:** `BT-5` `BT-6` `BT-7` `BT-8` todos **✅** + Estado Auditado **✓**.  
**Python local:** 3.14.6  
**Método:** re-execução na working tree == blob de HEAD (árvore limpa). Relatório de agent anterior **não** foi aceite sem prova. CI remoto por `gh run view` (JSON), não pela mensagem de push.

**Veredito global:** **PASS nos 7 itens.**  
**Decisão autônoma (confirmar retroativamente):** promover `TST-BT-1` para **✅ Concluído** e Estado Auditado **✓** (o próprio item *é* o teste de campanha). **Não** promover `AUD-BT-1` (fica ⏳ — próxima onda W7). Sem patch de produto. Push + tag `campanha/w6-tst-bt1` autorizados no fim da onda W6.

---

## Escopo e o que isto não é

- Fecha a **revalidação** da suíte de campanha no SHA de produto após BT-5..BT-8 (e com BT-0..BT-4 e BT-9 já ✅).
- Fecha **preci local 10/10** e **CI remoto 8/8** no mesmo SHA `0fd66cd`.
- Espelha T15 (`preci`) + T14 (smoke de instalação, aqui na variante **offline** versionada) no recorte da campanha. Não recria T5/T12 (`TST-DEPS` já ✅).
- **Não** é `AUD-BT-1` (auditoria de campanha: SoT, porte, host legado, consolidação). Não abre escopo de auditoria.
- **Não** é eval com LLM real da skill `/bigtech` (o harness BT-8 é política de classificação offline).
- **Não** há merge, release tag de produto (`v*`) nem cutover de `~/.claude`.

---

## Checklist DoD (item a item)

| # | Gate | Veredito | Evidência âncora |
|---|---|:---:|---|
| 1 | `validate_plugin.py` | **PASS** | rc=0; 74 `.md`; 5/5 dimensões ZERO-ÓRFÃOS = 0 ocorrências |
| 2 | pytest `hooks/tests` + `scripts/tests` | **PASS** | **161 passed** (150 hooks + 11 scripts) em 2.93 s; collect-only 161 |
| 3 | `smoke_offline.py` | **PASS** | rc=0; 51 agents (12 orange / 39 blue); 4 skills; 7 hooks command / 6 scripts; 6 hooks executados |
| 4 | `check_semantic_drift.py` | **PASS** | rc=0; 51/51 agents; 4 skills; 6 scripts resolvidos; 0 findings |
| 5 | `evals/bigtech_routing/run_evals.py` | **PASS** | **10/10** PASS, 0 FAIL (CASE-A..D + 6 portes/política) |
| 6 | `bash scripts/preci.sh` | **PASS** | **PRE-CI PASS — 10/10** (gates 1–4, 7–9 obrigatórios; 5 ruff, 6 gitleaks, 10 claude validate também verdes) |
| 7 | CI multi-OS GitHub no SHA | **PASS** | produto **#13** `31991473856` SHA `0fd66cd` 8/8; verificação **#14** `31991691630` SHA `82eb52e` 8/8 |

Nenhum FAIL material. Residuais abaixo **não** impedem ✅.

---

## SHAs

| Ref | SHA | Nota |
|---|---|---|
| SHA sob teste / `origin/main` no início | `0fd66cd2ad0e1a4385932519ff64b741cb53d9e4` | produto + docs de verify BT-7; CI #13 verde |
| Implementação BT-8 (evals + UTF-8) | `4e8843f5b32ac2871bafe04cd1c8056487ed04c5` | último blob de produto dos evals; CI #12 também 8/8 |
| Implementação BT-7 (drift) | `4ebacb0fc1e5c5bec5456126469411035372711f` | checker ainda idêntico no HEAD |
| Tag de produto baseline | `bigtech--v0.2.0` → `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` | não é o SHA desta revalidação |
| Este relatório | `82eb52ec908d0f7ecbdf45bf56b84cab6ee368bd` | docs + TODO; tag `campanha/w6-tst-bt1`; CI #14 verde |

`git diff 0fd66cd HEAD` no início desta fatia = vazio.

---

## 1. `validate_plugin.py` (item 1)

```
== Gate ZERO-ORFAOS (spec 4.1) -- plugin bigtech ==
raiz: …/plugin_bigtech
escopo: agents, skills, docs (exceto docs/superpowers, docs/auditoria, docs/submission, docs/campanha, docs/house)
arquivos .md validados: 74
[PASS] wikilinks     ZERO `[[ ]]` fora de codigo  (0)
[PASS] local_paths   ZERO paths locais  (0)
[PASS] personal      ZERO termos pessoais do autor  (0)
[PASS] excluded      ZERO refs aos 20 excluidos + /proj_jogo + /pericia-medica  (0)
[PASS] orphan_links  ZERO links Markdown relativos .md orfaos  (0)
RESULTADO: PASS — todas as 5 dimensoes do gate 4.1 limpas.
EXIT=0
```

`docs/campanha/` e `docs/house/` estão fora do escopo do gate (prova histórica / espelho vault). Esperado.

---

## 2. pytest (item 2)

```
python3 -m pytest hooks/tests scripts/tests -q
........................................................................ [ 44%]
........................................................................ [ 89%]
.................                                                        [100%]
161 passed in 2.93s
EXIT=0
```

| Pacote | Collect |
|---|---:|
| `hooks/tests` | 150 |
| `scripts/tests` | 11 |
| **Total** | **161** |

Recontado no `preci` (gate 2): **161 passed in 2.76s**. Mesma N.

---

## 3. `smoke_offline.py` (item 3)

```
[1] Manifestos — 3 checados
[2] Agents — 51 | color orange=12 blue=39
[3] Skills — 4
[4] hooks.json — 7 type=command (command=python3 + args[]); 6 scripts resolvíveis
[5] Execução real (env simulado)
    session_init: docs-bootstrap OK
    reinforce: roteamento /bigtech OK
    porte_reminder: exit 0 (silent) OK
    tdd_guard: fail-open sem config OK
    tab_pendencias_reminder: lembrete /tab_pendencias OK
    tdd_runner: inerte sem config (exit 0) OK
RESULTADO: PASS - plugin carregavel; hooks executam e se comportam como esperado.
EXIT=0
```

Isto é o smoke **offline** versionado (T14 no recorte da campanha). Não instala o plugin num Claude Code vivo.

---

## 4. `check_semantic_drift.py` (item 4)

```
== Drift semântico (BT-7) ==
  · agents encontrados: 51 (esperado 51)
  · skills encontradas: 4
  · hooks type=command: 7; scripts resolvidos: 6
[PASS] drift semântico limpo (agents/skills/hooks/porte/host).
EXIT=0
```

Confirma o fecho de BT-7 no mesmo HEAD (0 findings). Não reabre a auditoria da fatia.

---

## 5. Evals de roteamento (item 5)

```
policy: profiles=['early', 'scale', 'bigtech'] floor=early solo->early headcount_weight=0

ID                 STATUS  GOT      EXPECTED
CASE-A             PASS    early    early
CASE-B             PASS    scale    scale
CASE-C             PASS    early    early
CASE-D             PASS    early    early
PORTE-EARLY-PMF    PASS    early    early
PORTE-SCALE        PASS    scale    scale
PORTE-BIGTECH      PASS    bigtech  bigtech
FORBID-SOLO-ALIAS  PASS    early    early
CRIT-MONEY         PASS    early    early
IA-CENTRAL         PASS    early    early

resultado: 10/10 PASS, 0 FAIL
EXIT=0
```

Confirma o fecho de BT-8 (política pós-BT-5: piso early, `solo` não é perfil).

---

## 6. `preci.sh` completo (item 6)

`NO_COLOR=1 bash scripts/preci.sh` — **PRE-CI PASS**. Python 3.14.6. Fail-fast (`set -euo pipefail`).

| Gate | Nome | Resultado |
|---:|---|---|
| 1/10 | ZERO-ÓRFÃOS (`validate_plugin.py`) | **PASS** (mesmo output do item 1) |
| 2/10 | pytest hooks + scripts | **PASS** 161 |
| 3/10 | JSON válido (3 manifestos) | **PASS** plugin / marketplace / hooks |
| 4/10 | Paridade de versão | **PASS** `0.2.0` == `0.2.0` |
| 5/10 | ruff (opcional local; presente) | **PASS** All checks passed |
| 6/10 | gitleaks (opcional local; presente) | **PASS** 86 commits; 0 leaks |
| 7/10 | smoke offline | **PASS** (mesmo do item 3) |
| 8/10 | drift semântico (BT-7) | **PASS** (mesmo do item 4) |
| 9/10 | evals roteamento (BT-8) | **PASS** 10/10 |
| 10/10 | `claude plugin validate` | **PASS** marketplace `--strict` limpo; plugin.json 1 warning de `CLAUDE.md` de processo (já aceite na suíte) |

```
========================================
 PRE-CI PASS  — todos os gates obrigatorios verdes.
========================================
EXIT=0
```

Gate 10 warning (não FAIL): *«CLAUDE.md at the plugin root is not loaded as project context»* — documento de processo da campanha, não skill. O `preci` trata como OK.

---

## 7. CI multi-OS no GitHub (item 7)

**Run no SHA sob teste:**

| Campo | Valor |
|---|---|
| Número | **#13** |
| ID | `31991473856` |
| URL | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31991473856> |
| Evento | `push` em `main` |
| HEAD | `0fd66cd2ad0e1a4385932519ff64b741cb53d9e4` |
| Título | `docs(bt-7): verificação drift gate — PASS, promove ✅` |
| `conclusion` | **`success`** |
| Wall-clock | 48 s (jobs em paralelo; 2026-08-17T03:32:23Z → 03:33:11Z) |

**8/8 jobs — todos `success`:**

| Job | Conclusão | Janela UTC |
|---|:---:|---|
| validate (ubuntu-latest, py3.11) | success | 03:32:26–03:32:43 |
| validate (ubuntu-latest, py3.12) | success | 03:32:27–03:32:47 |
| validate (windows-latest, py3.11) | success | 03:32:29–03:33:09 |
| validate (windows-latest, py3.12) | success | 03:32:28–03:33:10 |
| validate (debian via container) | success | 03:32:27–03:32:52 |
| validate (fedora via container) | success | 03:32:26–03:32:51 |
| validate (archlinux via container) | success | 03:32:26–03:32:58 |
| gitleaks (secrets) | success | 03:32:26–03:32:34 |

Matrix bate com `.github/workflows/ci.yml`: 2 OS nativos × 2 Pythons + 3 distros em container + gitleaks. Sem `continue-on-error` nos gates.

Run imediatamente anterior de produto com o mesmo 8/8: **#12** `31990648852` SHA `4e8843f` (`fix(bt-8): UTF-8/ASCII-safe stdout`). Commits entre `4e8843f` e `0fd66cd` são só docs de verificação (BT-5/6/8/7) + TODO — não tocam os scripts dos gates.

**CI no SHA deste commit de verificação** (`82eb52e`, docs+TODO, sem patch de produto):

| Campo | Valor |
|---|---|
| Número | **#14** |
| ID | `31991691630` |
| URL | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31991691630> |
| Evento | `push` em `main` |
| HEAD | `82eb52ec908d0f7ecbdf45bf56b84cab6ee368bd` |
| `conclusion` | **`success`** |
| Jobs | **8/8** (mesma matrix: ubuntu/windows × 3.11/3.12 + debian/fedora/arch + gitleaks) |
| Janela UTC | 2026-08-17T03:36:17Z → 03:37:05Z |

Prova medida com `gh run view 31991691630 --json` após `git ls-remote origin refs/heads/main` = `82eb52e`. Item 7 vale no SHA de produto **e** no SHA de verificação.

---

## Residuais (não-FAIL)

- **Smoke é offline.** T14 original fala em `/plugin install` num Claude Code real. A campanha aceita `scripts/smoke_offline.py` (já no preci/CI) como o smoke versionável e multi-OS. Instalação viva fica fora desta fatia.
- **`claude plugin validate` warning** no `CLAUDE.md` da raiz (contexto de campanha, não skill). Não falha o gate 10.
- **`docs/campanha/` excluído** do ZERO-ÓRFÃOS — este relatório pode citar SHAs e paths de máquina nas provas sem disparar o gate.
- **AUD-BT-1 não executado** (próxima onda).

---

## O que esta verificação não promove

| ID | Estado após esta fatia |
|---|---|
| `TST-BT-1` | **✅ Concluído** + Estado Auditado **✓** |
| `AUD-BT-1` | **⏳ Pendente** (W7; não tocado) |
| `BT-5`..`BT-8` | já ✅; não reabertos |
| Tag de release `v*` / merge extra | **não** |
| Cutover `~/.claude` | **não** |

---

## Decisão

| Campo | Valor |
|---|---|
| Veredito | **PASS** (7/7) |
| TODO `TST-BT-1` Status | **✅ Concluído** |
| TODO `TST-BT-1` Estado Auditado | **✓** |
| `AUD-BT-1` | **intocado** (⏳) |
| Push | **sim** (`origin main` + tags) — fim da onda W6 de teste, autorizado no contexto |
| Tag | `campanha/w6-tst-bt1` (anotada) neste commit de verificação |

**Decisão autônoma (confirmar retroativamente):** PASS material. `TST-BT-1` → **✅ Concluído** + Estado Auditado **✓** no mesmo commit deste relatório. Tag `campanha/w6-tst-bt1`. Push de `main` + tags. Sem `AUD-BT-1`.
