# W2 / BT-3 — verificação adversarial (GitHub canônico)

**Data da verificação:** 2026-08-16  
**Hora local (medida):** `16/08/26 - 23:50:37` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** auditor de campanha — host Grok, papel [grok][mais recente]  
**Item:** `BT-3` (remote GitHub canônico + purge CI/host legado + 0 refs operacionais em paths de produto)  
**DoD desta fatia (ordem de serviço W2):**

1. `git remote` = `github.com/petrinhu/bigtech_plugin`
2. `.forgejo` ausente
3. paths de produto (README, AGENTS, plugin.json, SECURITY, PRIVACY, DEVELOPMENT, CHANGELOG, agents, skills, hooks, scripts, bin): **0** hits `codeberg.org|forgejo|woodpecker` (exceto residual justificado nas métricas *before*)
4. métricas after-bt3 existem

**HEAD do plugin no início desta auditoria:** `2ea32f52fd11780b7042c7afcb51cb51cee9351b` (working tree limpa; `main` ahead 2 de `origin/main`, commits locais W1/BT-0 + W2/BT-1)  
**Método:** re-medição em disco/git. Prosa do after-JSON e do baseline **não** foi aceita sem prova.

**Veredito:** **PASS em todos os itens do DoD BT-3.**  
**Decisão autônoma (confirmar retroativamente):** promover `BT-3` para **✅ Concluído** e Estado Auditado **✓**. Não é promoção de BT-1 / BT-2 / BT-4 (permanecem 🔍). Sem push.

---

## Escopo e o que isto não é

- Isto fecha o **DoD de distribuição BT-3**: host operacional = GitHub; CI/host legado (`.forgejo`) fora da árvore; zero refs operacionais nos paths de produto listados.
- **Não** fecha BT-4 (Actions multi-OS no remoto). A presença local de `.github/workflows/ci.yml` é entrega de BT-4, ainda 🔍.
- **Não** apaga histórico git. Commits e snapshots *before* continuam a citar o host legado como **prova histórica**.
- **Não** é cutover de `~/.claude`. **Não** houve push.

---

## Checklist DoD (item a item)

| # | Item | Veredito | Evidência âncora |
|---|---|:---:|---|
| 1 | `git remote` = `github.com/petrinhu/bigtech_plugin` | **PASS** | único remote `origin` → `https://github.com/petrinhu/bigtech_plugin.git` (fetch+push); zero remoto não-GitHub |
| 2 | `.forgejo` ausente | **PASS** | `test -d/.e .forgejo` negativo; `git ls-tree HEAD .forgejo` vazio; delete em `766eb5a` |
| 3 | 0 hits `codeberg.org\|forgejo\|woodpecker` nos paths de produto | **PASS** | remedir `rg -i` = 0 linhas / 0 ficheiros em todos os 12 paths; CHANGELOG também 0 (sem residual histórico operacional) |
| 4 | after-bt3 metrics existem | **PASS** | `docs/campanha/phase0-metrics-after-bt3.json` no histórico desde `04193b9`; blob HEAD `1f31dc1c5b1867a8bf6f739173837156a1f24cfb` |

Nenhum FAIL material. Residuais abaixo **não** impedem ✅.

---

## 1. Remote GitHub canônico

```bash
git remote -v
# origin  https://github.com/petrinhu/bigtech_plugin.git (fetch)
# origin  https://github.com/petrinhu/bigtech_plugin.git (push)

git remote | wc -l          # 1
git remote get-url origin   # https://github.com/petrinhu/bigtech_plugin.git
git remote -v | grep -vi github   # vazio (NO_NON_GITHUB_REMOTE)
```

| Checagem | Resultado |
|---|---|
| Único remote = `origin` | **PASS** |
| URL fetch+push = `https://github.com/petrinhu/bigtech_plugin.git` | **PASS** |
| Host = `github.com/petrinhu/bigtech_plugin` | **PASS** |
| Nenhum remote Codeberg/Forgejo/outro | **PASS** |
| `plugin.json` `homepage` + `repository` | `https://github.com/petrinhu/bigtech_plugin` |
| `plugin.json` `author.url` | `https://github.com/petrinhu` |
| README / AGENTS clone + marketplace | `github.com/petrinhu/bigtech_plugin` |

`git remote show origin` confirma Fetch/Push URL iguais e `main` tracking `origin/main` (fast-forwardable). `git ls-remote origin HEAD` (leitura) devolve `26f8641edb56e0d9cacd42e3df2410b8c7752a32` — o remoto público ainda não tem os 2 commits locais W1/BT-1. Isto **não** é falha de BT-3 (host canónico já é GitHub); é atraso de push da onda, proibido nesta fatia.

---

## 2. `.forgejo` ausente

```bash
test -d .forgejo; test -e .forgejo     # ambos falham → AUSENTE
git ls-tree -d HEAD .forgejo           # vazio
git log --diff-filter=D --summary -- .forgejo
# 766eb5a5dd7237cc0c3a23629bc5dc7904d6e17c
#   delete mode 100644 .forgejo/workflows/ci.yml
```

| Checagem | Resultado |
|---|---|
| Directório `.forgejo` na working tree | **ausente** |
| Entrada `.forgejo` no tree de HEAD | **ausente** |
| Commit de remoção no ancestral de HEAD | `766eb5a` (`chore(bt-3): origin GitHub + remove .forgejo + metadados/install paths`, 16/08/26 22:57:29 −03) |
| Ancestral de HEAD? | **sim** (`merge-base --is-ancestor`) |

O after-JSON regista `has_forgejo_workflows: false`. Remedir confirma.  
`has_github_workflows: false` no after era verdade em `1bfc800`; **agora** existe `.github/workflows/ci.yml` (BT-4, fora desta fatia). Não se reescreve o after.

---

## 3. Zero refs operacionais nos paths de produto

Padrão: `codeberg\.org|forgejo|woodpecker` (case-insensitive).  
Paths da OS (e do after-JSON; `plugin.json` ⊂ `.claude-plugin`):

```
README.md
AGENTS.md
SECURITY.md
PRIVACY.md
DEVELOPMENT.md
CHANGELOG.md
.claude-plugin          # inclui plugin.json + marketplace.json
agents
skills
hooks
scripts
bin
```

Remedir (`rg -i -c` + `-l`, excluindo `__pycache__`):

| Path | match lines | files | Veredito |
|---|---:|---:|:---:|
| `README.md` | 0 | 0 | PASS |
| `AGENTS.md` | 0 | 0 | PASS |
| `SECURITY.md` | 0 | 0 | PASS |
| `PRIVACY.md` | 0 | 0 | PASS |
| `DEVELOPMENT.md` | 0 | 0 | PASS |
| `CHANGELOG.md` | 0 | 0 | PASS |
| `.claude-plugin` (`plugin.json` + `marketplace.json`) | 0 | 0 | PASS |
| `agents/` | 0 | 0 | PASS |
| `skills/` | 0 | 0 | PASS |
| `hooks/` | 0 | 0 | PASS |
| `scripts/` | 0 | 0 | PASS |
| `bin/` | 0 | 0 | PASS |
| **Total produto** | **0** | **0** | **PASS** |

`git grep -i -l 'codeberg\.org\|forgejo\|woodpecker' HEAD -- <mesmos paths>` → `NONE_IN_HEAD_PRODUCT`.

O after-JSON previa exclusão de narrativa histórica no CHANGELOG. **Não foi necessária:** CHANGELOG live = 0 hits. Não há residual operacional a justificar nos paths de produto.

Extra (fora da OS, para recorte): `wiki/` + `docs/pipeline_release_1.0.md` + `docs/manuals/` + `docs/house/` + `docs/ORG.md` + `docs/TOOLING.md` + `docs/principles/` também **0** hits. Os 13 ficheiros listados no *before* como refs operacionais foram purgados nos commits `766eb5a` + `1bfc800` (os que ainda existem no produto estão limpos; `CLAUDE.md` / `TODO.md` / `docs/campanha/*` restam só como prosa de campanha — ver residuais).

---

## 4. Métricas after-bt3 existem

| Arquivo | Commit de introdução | Blob HEAD | sha256 working tree |
|---|---|---|---|
| `docs/campanha/phase0-metrics-after-bt3.json` | `04193b9ec4ecedf8e1aea755ab28267f0a760e22` (16/08/26 23:03:30 −03) | `1f31dc1c5b1867a8bf6f739173837156a1f24cfb` | `d8ef929109b908b0070299f6505c37a989ea3e5bfa6c3c474547e89cc763777e` |
| `docs/campanha/phase0-metrics-before.json` (prova histórica, não reescrita) | `8076cd1` | `9098a8878f633fbf2c8183e02dacd3f2fc067d90` | — |

O after declara `status: implemented_pending_verification` — coerente com a fatia em 🔍 **antes** desta auditoria.

### Claims after vs remedir agora

| Claim after | Remedir 23:50 | Match? |
|---|---|:---:|
| `origin_is_github: true` | `https://github.com/petrinhu/bigtech_plugin.git` | ✅ |
| `origin` GitHub | único remote, mesmo URL | ✅ |
| `has_forgejo_workflows: false` | `.forgejo` ausente no disco e no tree | ✅ |
| `refs_host_legado_operacionais_produto.value: 0` | 0 hits / 0 files nos paths listados | ✅ |
| `delivery_commits` `766eb5a` + `1bfc800` | ambos commits existem e são ancestrais de HEAD | ✅ |
| `has_github_workflows: false` | **era verdade em `1bfc800`**; **agora** `.github/workflows/ci.yml` existe (BT-4) | histórico ✅ |
| `alive_files_removed: false` / `push_performed: false` | esta fatia também não removeu vivos nem pushou | ✅ |

O after é snapshot **da fatia BT-3**, não do HEAD atual. A adição posterior de Actions **não** invalida o after.

### Before (não reescrito — residual justificado)

`phase0-metrics-before.json` e o corpo *before* de `2026-08-16-phase0-baseline.md` ainda citam `origin=codeberg.org`, `.forgejo` presente e 13 refs. O after lista essas exclusões explicitamente. Isto é **prova histórica do freeze** (`61c3ea4`), não instrução operacional. A OS autoriza este residual.

---

## Entrega no histórico (não só working tree)

```
766eb5a chore(bt-3): origin GitHub + remove .forgejo + metadados/install paths
        .forgejo/workflows/ci.yml deleted
        plugin.json / marketplace / README / AGENTS / SECURITY / PRIVACY /
        DEVELOPMENT / scripts/preci.sh / CLAUDE.md → GitHub
1bfc800 docs(bt-3): purge Codeberg/Forgejo/Woodpecker from docs wiki agents TODO
        CHANGELOG, plano, TODO, agents (devops-sre, qa-engineer, security-engineer),
        docs/manuals/CONTRACT.md, docs/pipeline_release_1.0.md
04193b9 docs(bt-3): status 🔍 + after metrics; prosa residual sem host legado operacional
        phase0-metrics-after-bt3.json + TODO 🔍
```

`TODO.md` antes desta auditoria (`git grep '^| BT-3 ' HEAD`):

```
| BT-3 | W2 | … | 🔍 Pendente verificação | — |
```

Nenhum commit anterior promoveu BT-3 a ✅.

---

## Residuais (não-FAIL)

1. **Snapshots PHASE 0** (`phase0-metrics-before.json`, corpo *before* do baseline) citam Codeberg/`.forgejo`/13 refs. Justificado no after (`exclusions`) e na OS (“exceto residual justificado em métricas before”).
2. **Prosa de campanha** ainda contém as palavras da busca: `TODO.md` (descrição do próprio item BT-3), `CLAUDE.md` (estado 🔍 pré-promoção), `docs/campanha/*` (relatórios), ADR D10 (“Sem remoto operacional para Forgejo/Codeberg”). **Não** são paths de produto da OS e **não** são URLs operacionais de clone/CI/marketplace.
3. **`has_github_workflows: false` no after** ficou stale após BT-4. Não reescrever. BT-4 continua 🔍.
4. **`origin/main` remoto** ainda em `26f8641` (sem os commits locais W1/BT-1). Host já é GitHub; o atraso é “sem push” da campanha, não host legado.
5. **`CLAUDE.md` linha Host git** ainda diz BT-3 em 🔍. Esta auditoria **não** edita `CLAUDE.md` (mesmo recorte que W1/BT-0: só relatório + célula TODO).
6. **Histórico git** continua a conter o host legado (commits, diffs, `.forgejo` no passado). Contrato BT-3: *sem apagar histórico*.
7. **BT-1 / BT-2 / BT-4** continuam 🔍. Esta auditoria **não** os promove.

---

## Decisão autônoma

**Promover BT-3 → ✅ Concluído, Estado Auditado → ✓.**

Motivo: os quatro itens da OS W2 estão **provados em disco/git** (remote único GitHub, `.forgejo` fora da árvore e do HEAD, 0 hits nos 12 paths de produto, after-metrics no objeto `04193b9`). A promoção é da **fatia de distribuição**, não do CI remoto (BT-4) nem da proteção de `main` (BT-9).

Confirmar retroativamente se o líder quiser critério mais rígido (ex.: exigir `origin/main` já contendo esta tag — isso é push de onda, proibido aqui).

---

## O que foi alterado nesta verificação

| Path | Ação |
|---|---|
| `docs/campanha/2026-08-16-w2-bt3-verification.md` | criado (este arquivo) |
| `TODO.md` linha BT-3 | Status `🔍` → `✅ Concluído`; Estado Auditado `—` → `✓` |
| tag local `campanha/w2-bt3-github-verify` | anotada no SHA do commit desta fatia |

Sem push. Sem edição de outros IDs BT-\*.
