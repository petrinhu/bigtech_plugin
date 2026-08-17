# PHASE 0 — Baseline reproduzível (campanha bigtech)

> **Snapshot histórico PHASE 0 (freeze).** Estado medido no baseline; não é instrução operacional atual. Ordem 2026-08-16: GitHub único; purga host legado = BT-3.

**Data da medição:** 2026-08-16  
**Executor:** implementer (Grok, papel [sonnet]/[grok][modelo anterior ao mais recente])  
**Plano:** `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` § PHASE 0  
**Escopo:** só leitura de instalação viva + gravação de artefatos sob `docs/campanha/`  
**Declaração:** nenhum arquivo vivo removido; sem push/merge/tag/release.

Artefatos machine-readable:

- [`phase0-agents-inventory.csv`](phase0-agents-inventory.csv)
- [`phase0-metrics-before.json`](phase0-metrics-before.json)

---

## 0.1 Freeze / backup baseline

### plugin_bigtech

| Campo | Valor medido |
|---|---|
| Path | `/home/petrus/IDrive/Documentos/projetos_claudebrain/Projects/plugin_bigtech` |
| HEAD | `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` |
| Branch | `main` |
| Dirty | `?? PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` + artefatos `docs/campanha/` desta fase |
| `origin` | `https://codeberg.org/petrinhu/bigtech_plugin.git` (fetch+push) |
| GitHub (existe) | `https://github.com/petrinhu/bigtech_plugin` — `git ls-remote` HEAD = mesmo SHA local |
| Versão `plugin.json` | `0.2.0` |
| `.forgejo/` | **presente** (`.forgejo/workflows/ci.yml`) |
| `.github/workflows` | **ausente** |

### claude-memory (`~/.claude`)

| Campo | Valor medido |
|---|---|
| Path | `/home/petrus/.claude` |
| HEAD | `5b19b524a7409d5b60ea3a3912b2761877c6c7b8` |
| Branch | `main...github/main` (limpo no momento da medição) |
| Remote | `github` → `git@github.com:petrinhu/claude-memory.git` |
| `settings.json` no git? | **NÃO** — `git check-ignore`: `.gitignore:52:settings.json` |
| `settings.json` em disco | presente (~21 346 bytes); **não commitado nem copiado neste relatório** |

### tab_pendencias (produto)

| Campo | Valor medido |
|---|---|
| Path | `/home/petrus/IDrive/Documentos/projetos_claudebrain/Projects/tab_pendencias` |
| HEAD | `0546c53ef5f97dc03975832842c8a73ef3c99e1f` |
| Branch | `main` (limpo) |
| `origin` | `git@github.com:petrinhu/tab_pendencias.git` |
| Pin em `~/.claude` | submódulo `skills/tab_pendencias` = mesmo SHA (`v1.2.2`) |

---

## 0.2 Checkouts

| Repo | Path local | OK? |
|---|---|:---:|
| plugin_bigtech | cwd acima | ✅ |
| claude-memory | `~/.claude` | ✅ |
| tab_pendencias product | `Projects/tab_pendencias` | ✅ |

---

## 0.3 Interseção de agents (por `name:` no frontmatter)

Fonte: parser de YAML frontmatter em `agents/*.md` (não filename).

```
CORE_ONLY=0
VAULT_ONLY=20
INTERSECTION=51
DUPLICATE_NAME_WITHIN_SCOPE=plugin:{} vault:{}
```

| Escopo | Contagem | Nota |
|---|---:|---|
| Plugin | 51 | bate com AGENTS.md / `plugin.json` 0.2.0 |
| Vault `~/.claude/agents` | 71 | 51 ∩ plugin + 20 só-vault |
| Grok `~/.grok/agents` (nota host) | 71 | contagem separada; não entra na interseção produto×vault Claude |

**Interseção idêntica byte-a-byte (sha256):** **0 / 51**  
**Interseção divergente:** **51 / 51**

Amostra de divergência (bytes / sha12):

| name | bytes plugin | bytes vault | sha plugin… | sha vault… |
|---|---:|---:|---|---|
| cosimo-chief-of-staff | 8691 | 7180 | eec9f0c36230 | 36bef6ec0709 |
| caetano-cto | 6127 | 4617 | fa0cf2876de5 | bbbdbf6769f7 |
| celso-ceo | 5729 | 4141 | 8193801e7904 | 2b9694d4e4d6 |
| backend-engineer | 19961 | 18582 | 77754ce89138 | 67d37d8ccc60 |
| qa-engineer | 21448 | 20049 | 20ca86a10604 | 27802798d35f |
| visual-design-director | 23836 | 22847 | 942d3e04993f | 7e188dbd1e95 |

Skills core também divergem (`SKILL.md`):

| skill | bytes plugin | bytes vault | identical? |
|---|---:|---:|:---:|
| bigtech | 8267 | 6349 | no |
| proj_software | 16833 | 14679 | no |

### VAULT_ONLY (20) — classificação **sugerida** (heurística; não cutover)

| name | classification_sugerida | Heurística |
|---|---|---|
| 3d-artist-rigger | INTENTIONAL-EXCLUSION | stack game |
| audio-designer-composer | INTENTIONAL-EXCLUSION | stack game |
| economy-designer | INTENTIONAL-EXCLUSION | stack game |
| engine-graphics-programmer | INTENTIONAL-EXCLUSION | stack game |
| game-animator | INTENTIONAL-EXCLUSION | stack game |
| game-producer | INTENTIONAL-EXCLUSION | stack game |
| gameplay_engineer | INTENTIONAL-EXCLUSION | stack game |
| lead-game-designer | INTENTIONAL-EXCLUSION | stack game |
| level-designer | INTENTIONAL-EXCLUSION | stack game |
| narrative-designer | INTENTIONAL-EXCLUSION | stack game |
| narrative-writer | INTENTIONAL-EXCLUSION | stack game |
| learning-designer | INTENTIONAL-EXCLUSION | stack game |
| dr-advogado | PERSONAL-OVERLAY | stack médico/jurídico da casa |
| dr-medico-perito | PERSONAL-OVERLAY | stack médico |
| dr-medico-psiquiatra | PERSONAL-OVERLAY | stack médico |
| dr-medico-trabalho | PERSONAL-OVERLAY | stack médico |
| linux-diag | PERSONAL-OVERLAY | utilitário host |
| revisor-textual | PERSONAL-OVERLAY | casa |
| engineering-coach | PERSONAL-OVERLAY | casa |
| product-marketing-manager | PERSONAL-OVERLAY | fora do core 0.2.0 |

### INTERSECTION (51)

Todos com `classification_sugerida=CORE-GENERIC` e `identical=no`: papel de produto presente nos dois lados, conteúdo divergente. **Não** auto-classificados como STALE nesta fase (faltaria diff semântico por arquivo). Full table: CSV anexo.

---

## 0.4 Modelos / tools / tamanho (plugin)

### Contadores frontmatter (51 agents)

| Métrica | Valor |
|---|---:|
| `model: opus` | **51** |
| `model: sonnet` | 0 |
| herdado (sem `model:`) | 0 |
| outros | 0 |
| `effort` ausente | **51** |
| `maxTurns` ausente | **51** |
| `disallowedTools` ausente/vazio | **51** |
| com tool `Agent` | **12** (todos os C-level + CoS) |
| com tool `Bash` | **31** |
| sem `Bash` | 20 (C-levels de negócio + writers/PM/CS/etc.) |

Holders de `Agent`:  
`caetano-cto`, `caio-caio`, `camilo-cmo`, `candido-cdo`, `capitolino-cpo`, `celso-ceo`, `cicero-cro`, `claudio-clo`, `confucio-cfo`, `cosimo-chief-of-staff`, `cosmo-coo`, `narciso-ciso`.

Frequência de tools (plugin): Read/Edit/Write/Grep/Glob/WebFetch/Task*/AskUserQuestion = 51; WebSearch = 46; Bash = 31; Agent = 12.

### Vault models (nota)

| model | n |
|---|---:|
| opus | 70 |
| sonnet | 1 (`linux-diag`) |

### Top 10 prompts por bytes (plugin)

| # | name | bytes | model |
|---:|---|---:|---|
| 1 | security-engineer | 25862 | opus |
| 2 | data-engineer | 25478 | opus |
| 3 | devops-sre | 24484 | opus |
| 4 | visual-design-director | 23836 | opus |
| 5 | compliance-legal | 21452 | opus |
| 6 | qa-engineer | 21448 | opus |
| 7 | frontend-engineer | 19986 | opus |
| 8 | backend-engineer | 19961 | opus |
| 9 | data-scientist | 16988 | opus |
| 10 | i18n-l10n-specialist | 16780 | opus |

### Boilerplate repetido (grep barato, /51 agents)

| Frase / bloco | Ocorrências |
|---|---:|
| Bloco “Compatibilidade: plugin para o Claude Code” | 50 |
| “docs-bootstrap” | 50 |
| “NUNCA” | 50 |
| “AskUserQuestion” | 51 |
| “Leitura obrigatória antes de decidir” | 35 |
| “Conventional Commit” | 14 |

---

## 0.5 Hooks ativos reais

### Plugin (`hooks/hooks.json` + `.py`)

Eventos:

| Evento | Scripts |
|---|---|
| SessionStart | `bigtech_session_init.py`, `bigtech_porte_reminder.py`, `tab_pendencias_reminder.py` |
| UserPromptSubmit | `bigtech_reinforce.py`, `tab_pendencias_reminder.py` |
| PreToolUse (Write\|Edit\|MultiEdit) | `tdd_guard.py` |
| PostToolUse (Write\|Edit\|MultiEdit) | `tdd_runner.py` |

Arquivos `.py`: `bigtech_session_init.py`, `bigtech_porte_reminder.py`, `bigtech_reinforce.py`, `tab_pendencias_reminder.py`, `tdd_common.py`, `tdd_guard.py`, `tdd_runner.py` (+ `tests/`, `README-tdd.md`).

### Vault vivo (`~/.claude/settings.json` — só nomes/eventos; **sem secrets**)

`enabledPlugins`: **nenhuma** entrada `bigtech*` (plugin **não** instalado/habilitado no snapshot). Marketplaces extras: `life-sciences`, `claude-community`.

Hooks flagged bigtech/TDD/tab (6):

| Evento | Comando (redigido) |
|---|---|
| PreToolUse | `python3 ~/.claude/hooks/tdd_guard.py` |
| PostToolUse | `python3 ~/.claude/hooks/tdd_runner.py` |
| SessionStart | `python3 ~/.claude/hooks/bigtech_porte_reminder.py` |
| SessionStart | `python3 ~/.claude/skills/tab_pendencias/tools/hooks/tab_pendencias_reminder.py` |
| UserPromptSubmit | `python3 ~/.claude/hooks/bigtech_reinforce.py` |
| UserPromptSubmit | `python3 …/tab_pendencias_reminder.py` |

Outros hooks globais (não bigtech): `no_mdash.py`, `trash-guard.py`, `play_den_den_alert.sh` (vários eventos), `pubmed_fda_crosslink.py`, `session_models_apply.py`, `regua_glintfx.py`.

### Diff plugin × vault (hooks)

| Arquivo | plugin vs vault |
|---|---|
| `bigtech_session_init.py` | **só plugin** (ausente em `~/.claude/hooks/`) |
| `bigtech_porte_reminder.py` | sha256 **diferente** (4870 vs 4591 bytes) |
| `bigtech_reinforce.py` | sha256 **diferente** |
| `tdd_guard.py` / `tdd_runner.py` / `tdd_common.py` | todos **diferentes** |
| `tab_pendencias_reminder.py` | plugin embute cópia; vault usa skill product (3956 bytes, path skill) |

### Risco de duplicação se instalar plugin **com** globals presentes

**ALTO.** Mesmos eventos (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`) e papéis homônimos (`tdd_*`, `bigtech_*`, `tab_pendencias_reminder`). TDD opt-in por `.claude/tdd-guard.json` mitiga efeito colateral de suite, mas **dois runners no mesmo evento** ainda são risco de execução dupla quando o projeto tem o arquivo. AGENTS.md do plugin já prevê perfil isolado (`CLAUDE_CONFIG_DIR`) ou remoção dos globais.

---

## Métricas primárias da campanha — valores **ANTES**

| Métrica | Baseline medido agora | Alvo (plano) |
|---|---|---|
| Fontes de verdade ativas (núcleo bigtech) | **≥2** (plugin 0.2.0 não habilitado + vault global vivo) | 1 |
| Agents core duplicados (interseção) | **51** (0 identical) | 0 |
| Hooks bigtech/TDD/tab globais | **sim** (6 entradas; plugin off) | 0 pós-migração |
| `solo` como porte/classificação | **presente** (6 arquivos skills/agents/hooks) | 0 |
| Headcount determina perfil | **presente** (skill `/bigtech` tabela Headcount + hooks) | 0 |
| Refs Codeberg/Forgejo operacionais | **13 arquivos** + `origin`=Codeberg + `.forgejo/workflows` | 0 |
| GitHub Actions multi-OS | **0** workflows em `.github/` | matrix completa verde |
| Proteção de `main` | **desativada** (`gh api` → 404 “Branch not protected”) | ativada |
| Override `model=fable` (Agent tool) | **presente no vault** (watchcode, modelos_sessao, session_models_apply); **não** no frontmatter dos agents | 0 |
| Drift gate semântico | **ausente** (`validate_plugin.py` existe; sem gate drift registry↔docs) | gate obrigatório |
| Evals de roteamento `/bigtech` | **ausente** | suite versionada verde |

---

## Inventário skills

| Lado | Skills |
|---|---|
| Plugin | `bigtech`, `proj_software`, `tab_pendencias`, `visual-design-director` (4) |
| Vault | 46 skills sob `~/.claude/skills/` (inclui `bigtech` divergente, pin `tab_pendencias` v1.2.2, watchcode, modelos_sessao, etc.) |

---

## Manuais house (existência; sem cópia nesta fase)

| Manual vault | No plugin? | Path plugin |
|---|:---:|---|
| CONTRACT.md | ✅ | `docs/manuals/CONTRACT.md` |
| TESTES.md | ✅ | `docs/manuals/TESTES.md` |
| TOOLING.md | ✅ | `docs/TOOLING.md` |
| pipeline_release_1.0.md | ✅ | `docs/pipeline_release_1.0.md` |
| DEPLOY_CHECKLIST.md | ✅ | `docs/manuals/DEPLOY_CHECKLIST.md` |
| lideranca_pipeline_release.md | ✅ | `docs/lideranca_pipeline_release.md` |
| ORG.md | ✅ | `docs/ORG.md` |
| **Standards.md** | ❌ | **GAP** |
| AGILE.md | ✅ | `docs/manuals/AGILE.md` |
| AUDITORIAS.md | ✅ | `docs/manuals/AUDITORIAS.md` |

**Gap P0 docs house:** copiar/sincronizar `Standards.md` (e depois medir drift vault×plugin nos 9 já presentes — fora do escopo de cutover Phase 0).

---

## tab_pendencias health (medir only)

### `todo_health.py` (produto; saída capturada)

Rodado contra o TODO do **produto** tab_pendencias no ambiente de invocação:

- 69 itens reportados pelo health; INBOX classifiable = 0  
- 59 ✅; 1 ⏳/🔄; 9 🔍 (OS-1..5, TOOL-1..4)  
- `TAB_STATUS_SYNC_RECOMMENDED` (24 commits / 64 dias sem touch)  
- Adesão citar ID: 8/13 (62%)

### `todo_audit.py --profile casa`

**plugin_bigtech/TODO.md:**

- Achados: **38** (1 CRÍTICO, 36 IMPORTANTE, 1 COSMÉTICO)  
- **CHK-11 CRÍTICO:** health conta 69 vs contagem independente 88 (delta 19)  
- CHK-05 pré-reqs `D1*` inexistentes; CHK-07 ondas; CHK-12 AUD-R*; CHK-14 wiki fim de tabela  
- Schema header: **9 colunas** (ID, Onda, Grupo, Descrição, Prioridade, Pré-requisito, Dificuldade, Status, Estado Auditado) — OK  
- **IDs `BT-*`:** **não existem** ainda  

**tab_pendencias/TODO.md (produto):**

- Achados: **34** (0 crítico; 33 CHK-07; 1 CHK-14)

### Recomendação Phase 0

Não migrar TODO nesta fase. Antes de backlog BT-* da campanha: sanear CHK-11 no TODO do plugin (ou regenerar tabela canônica). Criar IDs BT-* só quando a fase de backlog autorizar.

---

## Gaps P0 (lista curta, factual)

1. **Dual authority:** 51 agents + skills core divergentes; plugin **não** está em `enabledPlugins`.  
2. **Hooks globais** bigtech/TDD/tab ativos no vault; instalar plugin sem cutover = **execução dupla**.  
3. **`origin` ainda Codeberg** + `.forgejo` + 13 refs; **zero** GitHub Actions no plugin.  
4. **`main` sem branch protection** no GitHub.  
5. **`solo`/headcount** ainda na skill `/bigtech` e hooks (contradiz piso early do Cosimo em parte do texto).  
6. **`Standards.md` ausente** no plugin.  
7. **Sem evals `/bigtech`** e **sem drift gate**.  
8. **TODO plugin** com CHK-11 crítico (contagem); sem IDs de campanha BT-*.  
9. **`model: opus` em 100%** dos agents do plugin; `effort`/`maxTurns` ausentes em todos.  
10. **`model=fable`** ainda instruído em skills vault (watchcode / modelos_sessao).

---

## DoD Phase 0

| Item | Status |
|---|:---:|
| baseline SHA dos três repos relevantes | ✅ |
| inventário exato de agents | ✅ |
| inventário exato de skills | ✅ |
| inventário exato de hooks | ✅ |
| distribuição de modelos medida | ✅ |
| nenhum arquivo vivo removido | ✅ |

---

## Comandos âncora (reprodução)

```bash
git -C "$PLUGIN" rev-parse HEAD   # 61c3ea4…
git -C ~/.claude rev-parse HEAD   # 5b19b52…
git -C "$TAB" rev-parse HEAD      # 0546c53…
git -C "$PLUGIN" remote -v        # no freeze: origin → host legado; alvo atual: GitHub
gh api repos/petrinhu/bigtech_plugin/branches/main/protection  # 404
# parser agents → docs/campanha/phase0-agents-inventory.csv
# metrics → docs/campanha/phase0-metrics-before.json
```

Fim do relatório Phase 0.
