# W3 / BT-4 — verificação adversarial (CI multi-OS)

**Data da verificação:** 2026-08-16  
**Hora local (medida):** `16/08/26 - 23:56:58` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** verificador de campanha — host Grok, papel [grok][mais recente]  
**Item:** `BT-4` (CI multi-OS GitHub Actions: Ubuntu/Windows nativos + containers Debian/Fedora/Arch + gitleaks)  
**DoD desta ordem de serviço:**

1. `.github/workflows/ci.yml` existe com ubuntu+windows + containers debian/fedora/arch + gitleaks
2. último run verde no GitHub em `main` **ou** documentar run SHA + `conclusion=success`
3. `preci` local PASS
4. 147 pytest

**HEAD do plugin no início desta auditoria:** `5edd4cee3ba59ede6b030826092b28af62a57f66` (`main` == `origin/main`)  
**Árvore de trabalho:** suja com fatia **BT-5 em voo** (hooks/skills/docs de porte). Esta auditoria **não** leu nem commitou essa árvore. Prova de produto = `git archive HEAD` e `git archive 26f8641` em `/var/tmp`.  
**Método:** re-medição em disco + objeto git + API Actions. Prosa de `docs/campanha/2026-08-16-bt4-ci-multi-os.md` **não** foi aceita sem prova.

**Veredito global:** **HOLD — não promover `BT-4`.**  
A **máquina de CI** (item 1) e a **prova remota verde** (item 2, SHA `26f8641`) estão **PASS**.  
O **estado atual de `main`** (HEAD `5edd4ce`) **não** passa `preci` nem o último run do Actions. Item 3 = **FAIL no HEAD**. Item 4 (147 pytest) = **PASS**.  
Casa: CI vermelho bloqueia ✅; `✅` só depois do teste do estado sob auditoria. Confirmar retroativamente.

**Decisão autônoma (confirmar retroativamente):** manter `BT-4` em **🔍 Pendente verificação** e Estado Auditado **—**. Não é promoção de BT-1 / BT-5 / BT-9. Sem push. Sem patch de produto (verificador ≠ implementer).

---

## Escopo e o que isto não é

- Fecha a **prova** de que o workflow BT-4 existe, tem a matrix pedida, e **já correu verde** no remoto (8/8 jobs no SHA `26f8641`).
- Fecha **147 pytest** no blob commitado de HEAD.
- **Não** fecha “`main` está verde agora”. Run #8 em HEAD é `failure`.
- **Não** higieniza o ADR de BT-1 nem acrescenta `docs/adr` a `EXCLUDED_SUBTREES` (isso é implementação; outro agent).
- **Não** é proteção de `main` (BT-9). **Não** houve push, merge, tag de release nem cutover.

---

## Checklist DoD (item a item)

| # | Item | Veredito | Evidência âncora |
|---|---|:---:|---|
| 1 | `ci.yml` ubuntu+windows + debian/fedora/arch + gitleaks | **PASS** | ficheiro tracked; blob `4d0f2d2597fe48082018370dbede3fb9a0666524`; SHA-256 `1e52121e222d59ac0efb55fa5cc121b3de444df5c38d5c0be2c623fb7bc500ce`; 168 linhas |
| 2 | último run verde em `main` **ou** SHA+success | **PASS** (via SHA) | run **#7** `31988713862` SHA `26f8641edb56e0d9cacd42e3df2410b8c7752a32` `conclusion=success` **8/8 jobs**. HEAD run **#8** é `failure` (documentado abaixo) |
| 3 | `preci` local PASS | **FAIL no HEAD** | `validate_plugin` falha em `docs/adr/ADR-source-of-truth.md` (1 `local_paths` + 5 `personal`). No SHA verde `26f8641`: **PRE-CI PASS** 8/8 |
| 4 | 147 pytest | **PASS** | `147 passed` no archive de HEAD (`/var/tmp/bt4-verify-HEAD-5edd4ce`, 2.49s) e no archive de `26f8641` (2.43s) |

Itens 1, 2 e 4 não bastam para ✅ enquanto o item 3 falha no HEAD e o último Actions de `main` está vermelho.

---

## 1. Workflow no disco (item 1)

Path: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)  
Workflow GitHub: id `335880315`, nome `CI`, `state=active`, criado `2026-08-16T23:11:23-03:00`.  
URL: <https://github.com/petrinhu/bigtech_plugin/blob/main/.github/workflows/ci.yml>

Histórico do ficheiro (3 commits, todos BT-4):

| SHA | Mensagem |
|---|---|
| `b367e3402afcad46d32297651e530a986e2021e7` | `ci(bt-4): GitHub Actions multi-OS matrix + exclude campanha/house do zero-orfaos` |
| `30678286d6f6f742480bc9b738f3e94d5db9ba57` | `fix(bt-4): home USERPROFILE + pytest via sys.executable no TDD runner` |
| `4d00e1473abb79407b36c543f6df2ff3ae3ed8b8` | `fix(bt-4): smoke_offline cwd portátil e python3 no Windows CI` |

Última alteração de conteúdo = `4d00e14`. HEAD e `origin/main` ainda carregam esse blob.

### Células da matrix (enumeradas no YAML)

| Job | Células medidas no ficheiro |
|---|---|
| `test` | `os: [ubuntu-latest, windows-latest]` × `python-version: ["3.11", "3.12"]` = 4 nativos |
| `test-distros` | `debian` (`debian:12-slim@sha256:63a496b5…`), `fedora` (`fedora:41@sha256:68bb1ba8…`), `archlinux` (`archlinux:latest@sha256:87465c3a…`) |
| `secrets-scan` | `gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` (pin), `fetch-depth: 0` |

### Política do workflow (re-medida)

| Checagem | Resultado |
|---|---|
| Triggers `push`/`main` + `pull_request` + `workflow_dispatch` | **PASS** |
| `permissions.contents: read` | **PASS** |
| `fail-fast: false` (test + test-distros) | **PASS** |
| chave YAML `continue-on-error:` | **0** (só comentário de política na L4) |
| `\|\| true` em passo | **0** (só comentário de política na L5) |
| `preci.sh` só em Linux nativo | **PASS** (`if: runner.os == 'Linux'`) |
| shim `bin/` no PATH do Windows | **PASS** |
| containers: venv em `/tmp` (PEP 668) | **PASS** |

---

## 2. Actions no remoto (item 2)

Repo: `petrinhu/bigtech_plugin`. Filtro: workflow `ci.yml`, branch `main`. Total medido: **8** runs.

| # | SHA | conclusion | URL |
|---|---|---|---|
| 8 | `5edd4cee3ba5` (HEAD) | **failure** | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31989361960> |
| **7** | **`26f8641edb56`** | **success** | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31988713862> |
| 6 | `fac9e590ace8` | success | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31988635940> |
| 5 | `ff1115107b6e` | success | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31988315118> |
| 4 | `6944e8edb5a7` | success | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31987902132> |
| 3 | `4d00e1473abb` (último fix BT-4) | success | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31987571535> |
| 2 | `30678286d6f6` | failure | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31987418845> |
| 1 | `984838565e36` | failure | <https://github.com/petrinhu/bigtech_plugin/actions/runs/31987225288> |

`26f8641` é ancestral de HEAD. `git ls-remote origin refs/heads/main` = `5edd4ce…` (HEAD público = HEAD local).

### Run verde de referência (DoD item 2)

- **run_id:** `31988713862`
- **run_number:** 7
- **head_sha:** `26f8641edb56e0d9cacd42e3df2410b8c7752a32`
- **event:** `push`
- **status:** `completed`
- **conclusion:** `success`
- **quando:** `2026-08-17T02:40:29Z` → `2026-08-17T02:41:19Z`
- **jobs:** 8/8 `success`

| Job | conclusion |
|---|---|
| `validate (ubuntu-latest, py3.11)` | success (inclui passo `preci.sh`) |
| `validate (ubuntu-latest, py3.12)` | success (inclui passo `preci.sh`) |
| `validate (windows-latest, py3.11)` | success |
| `validate (windows-latest, py3.12)` | success |
| `validate (debian via container)` | success |
| `validate (fedora via container)` | success |
| `validate (archlinux via container)` | success |
| `gitleaks (secrets)` | success |

Isto **prova** a matrix completa pedida (nativos Ubuntu+Windows × 3.11/3.12 + 3 containers + gitleaks). Cinco runs verdes consecutivos (#3–#7) depois do último fix BT-4.

### Run atual em HEAD (não é o verde)

- **run_id:** `31989361960`
- **run_number:** 8
- **head_sha:** `5edd4cee3ba59ede6b030826092b28af62a57f66`
- **conclusion:** `failure`
- **quando:** `2026-08-17T02:53:09Z` → `2026-08-17T02:53:42Z` (~33 s — curto demais para a matrix inteira; bateu no `validate_plugin`)

| Job | conclusion | passo que falhou |
|---|---|---|
| `gitleaks (secrets)` | **success** | — |
| `validate (ubuntu-latest, py3.11)` | failure | `validate_plugin (ZERO-ORFAOS)`; pytest **antes** passou |
| `validate (ubuntu-latest, py3.12)` | failure | idem |
| `validate (windows-latest, py3.11)` | failure | idem |
| `validate (windows-latest, py3.12)` | failure | idem |
| `validate (debian via container)` | failure | idem (pytest passou) |
| `validate (fedora via container)` | failure | idem |
| `validate (archlinux via container)` | failure | idem |

Causa remota = a mesma do `preci` local no HEAD (secção 3). **Não** é falha de runner, digest de container, Windows shim nem gitleaks.

Commits entre o último verde e o HEAD (todos docs de verificação W1/W2 + ADR BT-1):

```
a5c0779 docs(bt-1): ADR source-of-truth - PHASE 1 FABLE-ORG-ARCH
2ea32f5 docs(bt-0): W1 verificação PHASE 0 — DoD campanha fechado
8f637dd docs(bt-3): W2 verificação GitHub canónico — DoD campanha fechado
5edd4ce docs(bt-2): W2 verificação docs/house — 10 manuais + README
```

O ADR nasce em `a5c0779`. `docs/campanha/*` está em `EXCLUDED_SUBTREES`; o ADR em `docs/adr/` **não**.

---

## 3. `preci` local (item 3)

### 3.1 HEAD commitado (`5edd4ce`) — FAIL

Comando: `bash scripts/preci.sh` na working tree (gate 1 aborta antes dos outros).  
Repetido no archive `git archive HEAD` → `/var/tmp/bt4-verify-HEAD-5edd4ce` (sem a sujeira BT-5).

```
escopo: agents, skills, docs (exceto docs/superpowers, docs/auditoria,
        docs/submission, docs/campanha, docs/house)
arquivos .md validados: 74
[FAIL] local_paths  1 violação
       docs/adr/ADR-source-of-truth.md:349  `~/.claude` / `~/.grok`
[FAIL] personal     5 violações
       :5   "petrus (líder)"
       :69  github.com/petrinhu/bigtech_plugin
       :70  marketplace `petrinhu`
       :144 github.com/petrinhu/tab_pendencias
       :242 github.com/petrinhu/bigtech_plugin
RESULTADO: FAIL — dimensoes com violacao: local_paths, personal
[FAIL] gate zero-orfaos reprovou
```

`EXCLUDED_SUBTREES` (validate_plugin L57–62) **não** inclui `docs/adr`.  
As 4 hits `petrinhu` em URL pública do marketplace são o mesmo identificador que `plugin.json` já usa — o gate trata-as como termo pessoal porque o ADR está no escopo de `.md`. A hit `~/.claude` é path local real.

Isto **não** é defeito da matrix BT-4. É conteúdo de **BT-1** (ADR, status 🔍) a cair no gate 4.1 que o próprio BT-4 passou a correr em todos os jobs.

### 3.2 SHA do último run verde (`26f8641`) — PASS

Archive `git archive 26f8641` → `/var/tmp/bt4-verify-26f8641` (sem `.git`; gitleaks varreu árvore, 0 leaks).

```
== pre-CI do plugin bigtech (TST-T15) ==
python: python3 (Python 3.14.6)
[gate 1/8] ZERO-ORFAOS  PASS  (72 .md; 5 dimensões limpas)
[gate 2/8] pytest       PASS  147 passed in 2.43s
[gate 3/8] JSON         PASS  3 manifestos
[gate 4/8] paridade     PASS  versao casada: 0.2.0
[gate 5/8] ruff         PASS
[gate 6/8] gitleaks     PASS  (0 leaks; aviso "not a git repository" no archive)
[gate 7/8] smoke        PASS
[gate 8/8] claude plugin validate  PASS  (marketplace --strict + plugin.json;
           1 warning conhecido de CLAUDE.md de processo)
========================================
 PRE-CI PASS  — todos os gates obrigatorios verdes.
========================================
```

No remoto, o passo `preci.sh (Ubuntu only)` do run #7 também foi `success` (jobs ubuntu 3.11 e 3.12).

**Item 3 no critério da OS (“preci local PASS” sobre o HEAD sob auditoria): FAIL.**  
Prova de que o preci *da fatia BT-4* passa: só no SHA `26f8641` (e nos 4 verdes anteriores).

---

## 4. 147 pytest (item 4)

| Onde | Resultado |
|---|---|
| `git archive HEAD` `/var/tmp/bt4-verify-HEAD-5edd4ce` | **147 passed in 2.49s** |
| `git archive 26f8641` `/var/tmp/bt4-verify-26f8641` | **147 passed in 2.43s** |
| working tree (com edits BT-5 em voo) | 147 passed — **não** usado como prova |

Jobs remotos do run #8: passo `pytest hooks/tests` **success** em todos os jobs que chegaram lá (nativos + 3 containers) **antes** de `validate_plugin` falhar. O vermelho de HEAD **não** é regressão da suíte.

---

## 5. O que impede ✅

1. **HEAD `5edd4ce` / run #8 = failure.** Promover BT-4 com o último Actions de `main` vermelho mentiria sobre o estado público.
2. **`preci` no HEAD falha.** A OS pedia PASS local; não há.
3. Causa única medida: `docs/adr/ADR-source-of-truth.md` (commit `a5c0779`, item **BT-1**). Fora do escopo desta verificação consertar.

Caminhos possíveis *depois* (não feitos aqui):

- higienizar o ADR (tirar `petrus`, `~/.claude`, ou citar `petrinhu` só em fence/excepção do gate);
- **ou** acrescentar `docs/adr` a `EXCLUDED_SUBTREES` (ADR é processo, irmão de `docs/campanha`) — decisão de desenho, precisa de implementer + aprovação;
- re-correr Actions / `preci` no HEAD limpo;
- só então TST/AUD promovem BT-4.

---

## 6. Residuais (não bloqueiam a *máquina* de CI; bloqueiam a promoção)

| Residual | Classe |
|---|---|
| Run #8 HEAD vermelho por ADR BT-1 | **bloqueia ✅** |
| `preci` HEAD FAIL | **bloqueia ✅** |
| 4/5 hits `personal` = URL `github.com/petrinhu/…` (identidade pública) | ruído do gate no ADR; não é secret |
| Description GitHub do repo ainda diz “Mirror of codeberg.org… Source of truth: Codeberg” | metadado do host; fora do DoD BT-4 (produto já limpo em BT-3) |
| Working tree suja com BT-5 (porte solo→early) | **não auditada**; outro agent |
| BT-9 (proteção de `main`) | ⏳; pré-req BT-4 ainda 🔍 |

---

## 7. O que isto não promove / não faz

- **Não** promove `BT-4` (fica 🔍 / Estado Auditado —).
- **Não** promove `BT-1` (o ADR é a causa do vermelho).
- **Não** fecha BT-5 / BT-9.
- **Não** houve push, merge, tag de release, nem edição de `TODO.md`.
- Tag local pedida: `campanha/w3-bt4-ci-verify` no SHA **deste** commit de relatório.

---

## Apêndice — comandos da prova

```bash
date '+%d/%m/%y - %H:%M:%S'          # 16/08/26 - 23:56:58
git rev-parse HEAD                   # 5edd4cee3ba59ede6b030826092b28af62a57f66
git ls-remote origin refs/heads/main # mesmo SHA
git rev-parse HEAD:.github/workflows/ci.yml
# 4d0f2d2597fe48082018370dbede3fb9a0666524
sha256sum .github/workflows/ci.yml
# 1e52121e222d59ac0efb55fa5cc121b3de444df5c38d5c0be2c623fb7bc500ce

# API (MCP github__actions_list)
# workflows: CI id=335880315 active
# runs main: 8 rows (tabela da secção 2)
# jobs run 31988713862: 8 success
# jobs run 31989361960: 7 failure (validate_plugin) + 1 success (gitleaks)

git archive HEAD    | tar -C /var/tmp/bt4-verify-HEAD-5edd4ce -xf -
git archive 26f8641 | tar -C /var/tmp/bt4-verify-26f8641 -xf -
python3 -m pytest hooks/tests -q     # 147 passed (nos dois archives)
bash scripts/preci.sh                # FAIL no HEAD; PASS em 26f8641
```

---

## 8. Unblock após sanitize do ADR (pós-auditoria)

**Data da nota:** 2026-08-16  
**Hora local (medida):** `17/08/26 - 00:00:23`  
**Causa do HOLD original:** `docs/adr/ADR-source-of-truth.md` (BT-1) violava `local_paths` + `personal` no gate ZERO-ORFAOS; `preci` e o Actions no HEAD falhavam **fora** da matrix BT-4.

**Desbloqueio (implementação BT-1 sanitizada, local):**

| Item DoD | Estado após sanitize |
|---|---|
| 1 — `ci.yml` matrix | **PASS** (inalterado; blob já verde em `26f8641`) |
| 2 — run verde SHA | **PASS** (run #7 em `26f8641`; remoto no HEAD antigo continua histórico) |
| 3 — `preci` local | **PASS** 8/8 (medido pós-sanitize; 150 pytest) |
| 4 — pytest hooks | **PASS** (`150 passed`) |

**Veredito atualizado:** **PROMOTE `BT-4` → ✅ + Estado Auditado ✓**.  
O bloqueio era o ADR de BT-1 no escopo do `validate_plugin`, não defeito da matrix multi-OS. Re-medição: `python3 scripts/validate_plugin.py` PASS; `bash scripts/preci.sh` PRE-CI PASS.  
Sem push nesta fatia (main pusha a onda). Actions no remoto só re-verifica após o push da onda.
