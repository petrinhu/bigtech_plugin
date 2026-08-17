# BT-6 - Inventário dual-authority (vault × plugin)

**Item:** BT-6 (W3). Status alvo nesta fatia: **🔍 Pendente verificação** (não ✅).  
**Data da medição:** 2026-08-16 / 2026-08-17 00:02 (hora local).  
**Autor:** `software-architect` / auditor (host Grok, papel teto desta fatia).  
**Taxonomia:** [`docs/adr/ADR-source-of-truth.md`](../adr/ADR-source-of-truth.md) D8.  
**Histórico PHASE 0 (não é estado operacional):** [`phase0-agents-inventory.csv`](phase0-agents-inventory.csv), [`2026-08-16-phase0-baseline.md`](2026-08-16-phase0-baseline.md).  
**CSV desta fatia:** [`2026-08-16-dual-authority-inventory.csv`](2026-08-16-dual-authority-inventory.csv).  
**Plano (sem execução):** [`2026-08-16-dual-authority-cutover-plan.md`](2026-08-16-dual-authority-cutover-plan.md).

## 0. Decisão autônoma (confirmar retroativamente)

**Não apagar, mover, renomear nem desativar arquivo em `~/.claude/` (nem `~/.grok/`) nesta fatia.**  
O inventário classifica. O cutover é PHASE 11, depois de canário verde. Dual authority homônima **permanece** até lá (ADR D2 / D6).

Sem push, sem merge, sem tag remota, sem release. Sem implementar BT-7 nem BT-8.

## 1. Escopo e SHAs medidos

Parser: `name:` no frontmatter YAML de `*.md` (não o filename). Árvores lidas:

| Superfície | Path | SHA / estado |
|---|---|---|
| Plugin (owner do núcleo) | `agents/` deste repo | `77c1f9e426ead89384f5997cd7c8bccc3e16f8a0` (HEAD na medição) |
| Vault Claude (instalação viva) | `~/.claude/agents/` | `claude-memory` `5b19b524a7409d5b60ea3a3912b2761877c6c7b8` (agents limpos; working tree só tem memória de projeto) |
| PHASE 0 freeze (prova histórica) | mesmo CSV | plugin `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` |
| Produto `tab_pendencias` | (D5; não é agent) | `0546c53ef5f97dc03975832842c8a73ef3c99e1f` |
| Grok (overlay de host, **não** 3ª SoT) | `~/.grok/agents/` | 71 ficheiros; **0** idênticos ao plugin e **0** idênticos ao vault |

`PLUGIN_ONLY` = 0. Todo agent do pacote 0.2.0 tem homônimo ativo no vault.

## 2. Contagens

| Conjunto | N | Classificação BT-6 | Ação cutover (futura) |
|---|---:|---|---|
| INTERSECTION | 51 | `CORE-GENERIC` (51) | **plugin wins**; depois **delete vault copy** |
| VAULT_ONLY | 20 | `INTENTIONAL-EXCLUSION` (12) + `PERSONAL-OVERLAY` (8) | **keep intentional** (12) / **vault overlay** (8) |
| Idênticos byte a byte (sha256) | **0 / 51** | - | nada a “syncar” às cegas |
| Plugin mudou desde PHASE 0 | 4 | ainda `CORE-GENERIC` | plugin já leva BT-5 (porte early) |
| Vault mudou desde PHASE 0 | **0** | - | cópia pessoal congelada no SHA PHASE 0 |

Os 4 hashes de plugin distintos da PHASE 0: `cosimo-chief-of-staff`, `devops-sre`, `qa-engineer`, `security-engineer` (onda BT-5, porte). O vault **não** absorveu essa mudança: prova viva de dual authority.

Nenhum agent inteiro foi classificado `STALE`. `STALE` aplica-se ao **resíduo** da cópia vault na interseção (wikilinks, identidade pessoal, `caveman`/`cavecrew`, rótulos solo/headcount) e ao **ficheiro** vault depois do canário.

## 3. Diff semântico (por que 0 idênticos não é “portar o vault”)

Padrão estável nos 51:

| Lado | O que é |
|---|---|
| Plugin (maior em todos os 51; Δ +835…+1806 bytes) | Produto higienizado: `color:`, tools `Task*`, banner de compatibilidade Claude Code, links relativos `docs/`, líder genérico (“CEO da sua bigtech”), pre-flight `TODO.md` com acentos. |
| Vault | Persona de casa: bloco de identidade do líder (nome + títulos), wikilinks `[[…]]`, tools sem a família `Task*` completa, “Referências canônicas” do vault. Subconjunto ainda cita `caveman`/`cavecrew` (proibido no produto), Brave, Qt23/Breeze. |

**Conclusão de port:** não há lacuna `CORE-GENERIC` no plugin que obrigue copiar texto do vault. O que o vault tem a mais é overlay pessoal ou `STALE`. Candidato opcional (não bloqueia cutover): fallbacks de captura desktop (grim/spectacle) no `visual-design-director`; o plugin já tem MCP `chrome-devtools` + launchers por SO. **Não** portar Brave-específico nem stack Qt23.

Marcadores de resíduo vault (interseção):

- `identity_lider`: **51 / 51**
- `wikilinks`: 40 / 51
- `caveman`: 12 / 51 (`backend-engineer`, `data-engineer`, `data-scientist`, `devops-sre`, `frontend-engineer`, `product-manager`, `qa-engineer`, `security-engineer`, `software-architect`, `tech-lead`, `ux-ui-designer` + refs `cavecrew`)
- `qt23` / `brave`: minoria (frontend, QA, visual, security, architect, …)

Esse resíduo **já vive** em `CLAUDE.md` / memória / `docs/stack-padrao` da casa. Não precisa do ficheiro-agent vault para sobreviver ao cutover.

## 4. INTERSECTION (51) - `CORE-GENERIC`

Ação única: **plugin wins; depois delete vault copy**.  
“Depois” = PHASE 11, canário verde, backup no histórico git. Não agora.

### 4.1 C-level (12)

| name | classificação | ação cutover | Δbytes | plugin≠P0 | resíduos vault |
|---|---|---|---:|:---:|---|
| `caetano-cto` | CORE-GENERIC | plugin wins; depois delete vault copy | 1510 | no | identity_lider;wikilinks |
| `caio-caio` | CORE-GENERIC | plugin wins; depois delete vault copy | 1352 | no | identity_lider;wikilinks |
| `camilo-cmo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1359 | no | identity_lider;wikilinks |
| `candido-cdo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1421 | no | identity_lider;wikilinks |
| `capitolino-cpo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1434 | no | identity_lider;wikilinks |
| `celso-ceo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1588 | no | identity_lider;wikilinks |
| `cicero-cro` | CORE-GENERIC | plugin wins; depois delete vault copy | 1300 | no | identity_lider;wikilinks |
| `claudio-clo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1293 | no | identity_lider;wikilinks |
| `confucio-cfo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1314 | no | identity_lider;wikilinks |
| `cosimo-chief-of-staff` | CORE-GENERIC | plugin wins; depois delete vault copy | 1582 | yes | identity_lider;wikilinks |
| `cosmo-coo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1256 | no | identity_lider;wikilinks |
| `narciso-ciso` | CORE-GENERIC | plugin wins; depois delete vault copy | 1490 | no | identity_lider;wikilinks |

`cosimo-chief-of-staff` vault ainda fala “NUNCA classificar como solo” / rótulos Early-stage. Isso é **STALE** face a BT-5 (piso early no plugin). Mais um motivo para o plugin vencer; não portar o texto vault.

### 4.2 Operacionais (39)

| name | classificação | ação cutover | Δbytes | plugin≠P0 | resíduos vault |
|---|---|---|---:|:---:|---|
| `accessibility-specialist` | CORE-GENERIC | plugin wins; depois delete vault copy | 1225 | no | identity_lider;wikilinks |
| `applied-ai-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1192 | no | identity_lider;wikilinks |
| `art-director` | CORE-GENERIC | plugin wins; depois delete vault copy | 1806 | no | identity_lider |
| `backend-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1379 | no | identity_lider;wikilinks;caveman;qt23 |
| `business-analyst` | CORE-GENERIC | plugin wins; depois delete vault copy | 877 | no | identity_lider;wikilinks |
| `community-manager` | CORE-GENERIC | plugin wins; depois delete vault copy | 849 | no | identity_lider;wikilinks |
| `compliance-legal` | CORE-GENERIC | plugin wins; depois delete vault copy | 1491 | no | identity_lider;wikilinks |
| `content-seo` | CORE-GENERIC | plugin wins; depois delete vault copy | 1088 | no | identity_lider;wikilinks |
| `customer-success` | CORE-GENERIC | plugin wins; depois delete vault copy | 844 | no | identity_lider;wikilinks |
| `data-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1135 | no | identity_lider;wikilinks;caveman;qt23 |
| `data-scientist` | CORE-GENERIC | plugin wins; depois delete vault copy | 1312 | no | identity_lider;wikilinks;caveman |
| `devops-sre` | CORE-GENERIC | plugin wins; depois delete vault copy | 1341 | yes | identity_lider;wikilinks;caveman |
| `embedded-firmware-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1549 | no | identity_lider |
| `engineering-manager` | CORE-GENERIC | plugin wins; depois delete vault copy | 1262 | no | identity_lider |
| `frontend-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1345 | no | identity_lider;wikilinks;caveman;brave;qt23 |
| `growth-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1068 | no | identity_lider;wikilinks |
| `hardware-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1489 | no | identity_lider |
| `i18n-l10n-specialist` | CORE-GENERIC | plugin wins; depois delete vault copy | 958 | no | identity_lider |
| `internal-auditor` | CORE-GENERIC | plugin wins; depois delete vault copy | 1230 | no | identity_lider;wikilinks |
| `ml-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1467 | no | identity_lider;wikilinks |
| `mobile-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1299 | no | identity_lider;wikilinks |
| `network-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1260 | no | identity_lider;wikilinks |
| `network-security-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1322 | no | identity_lider;wikilinks |
| `performance-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1278 | no | identity_lider;wikilinks |
| `pr-comms` | CORE-GENERIC | plugin wins; depois delete vault copy | 841 | no | identity_lider;wikilinks |
| `product-manager` | CORE-GENERIC | plugin wins; depois delete vault copy | 1163 | no | identity_lider;caveman;qt23 |
| `qa-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1379 | yes | identity_lider;wikilinks;caveman;brave |
| `release-manager` | CORE-GENERIC | plugin wins; depois delete vault copy | 937 | no | identity_lider;wikilinks |
| `revenue-ops` | CORE-GENERIC | plugin wins; depois delete vault copy | 835 | no | identity_lider;wikilinks |
| `scrum-master` | CORE-GENERIC | plugin wins; depois delete vault copy | 937 | no | identity_lider |
| `security-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1610 | yes | identity_lider;wikilinks;caveman;qt23 |
| `software-architect` | CORE-GENERIC | plugin wins; depois delete vault copy | 1727 | no | identity_lider;wikilinks;caveman;qt23 |
| `support-engineer` | CORE-GENERIC | plugin wins; depois delete vault copy | 907 | no | identity_lider;wikilinks |
| `tech-lead` | CORE-GENERIC | plugin wins; depois delete vault copy | 1449 | no | identity_lider;wikilinks;caveman |
| `technical-writer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1136 | no | identity_lider;wikilinks |
| `ux-researcher` | CORE-GENERIC | plugin wins; depois delete vault copy | 874 | no | identity_lider;wikilinks |
| `ux-ui-designer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1326 | no | identity_lider;caveman;qt23 |
| `ux-writer` | CORE-GENERIC | plugin wins; depois delete vault copy | 1087 | no | identity_lider |
| `visual-design-director` | CORE-GENERIC | plugin wins; depois delete vault copy | 989 | no | identity_lider;wikilinks;brave;qt23 |

## 5. VAULT_ONLY (20)

Confirmado contra spec 2026-06-13 §2.2 e heurística ADR D8. Nenhuma destas entra no pacote público nesta campanha.

| name | classificação | ação | bytes | model | resíduos |
|---|---|---|---:|---|---|
| `3d-artist-rigger` | INTENTIONAL-EXCLUSION | keep intentional | 11571 | opus | identity_lider |
| `audio-designer-composer` | INTENTIONAL-EXCLUSION | keep intentional | 13268 | opus | identity_lider |
| `economy-designer` | INTENTIONAL-EXCLUSION | keep intentional | 12776 | opus | identity_lider |
| `engine-graphics-programmer` | INTENTIONAL-EXCLUSION | keep intentional | 13195 | opus | identity_lider |
| `game-animator` | INTENTIONAL-EXCLUSION | keep intentional | 12969 | opus | identity_lider |
| `game-producer` | INTENTIONAL-EXCLUSION | keep intentional | 13673 | opus | identity_lider |
| `gameplay_engineer` | INTENTIONAL-EXCLUSION | keep intentional | 9162 | opus | identity_lider |
| `lead-game-designer` | INTENTIONAL-EXCLUSION | keep intentional | 12742 | opus | identity_lider |
| `level-designer` | INTENTIONAL-EXCLUSION | keep intentional | 12135 | opus | identity_lider |
| `narrative-designer` | INTENTIONAL-EXCLUSION | keep intentional | 19393 | opus | identity_lider |
| `narrative-writer` | INTENTIONAL-EXCLUSION | keep intentional | 23205 | opus | identity_lider |
| `learning-designer` | INTENTIONAL-EXCLUSION | keep intentional | 15125 | opus | identity_lider |
| `dr-advogado` | PERSONAL-OVERLAY | vault overlay | 15995 | opus | identity_lider |
| `dr-medico-perito` | PERSONAL-OVERLAY | vault overlay | 16485 | opus | identity_lider |
| `dr-medico-psiquiatra` | PERSONAL-OVERLAY | vault overlay | 16751 | opus | identity_lider |
| `dr-medico-trabalho` | PERSONAL-OVERLAY | vault overlay | 18170 | opus | identity_lider |
| `linux-diag` | PERSONAL-OVERLAY | vault overlay | 4722 | sonnet | identity_lider;wikilinks |
| `engineering-coach` | PERSONAL-OVERLAY | vault overlay | 12672 | opus | identity_lider |
| `product-marketing-manager` | PERSONAL-OVERLAY | vault overlay | 3127 | opus | identity_lider;wikilinks |
| `revisor-textual` | PERSONAL-OVERLAY | vault overlay | 12813 | opus | identity_lider;**paths_or_project** |

`revisor-textual` contém paths de máquina e nome de projeto privado. **Nunca** publicar no `bigtech_plugin` (ADR D3). `linux-diag` é o único `model: sonnet` do vault; fica overlay.

Jogo (10) + `narrative-writer` + `learning-designer` = 12 exclusões. Perícia (4) + host/coach/PMM/revisor = 8 overlay.

## 6. Grok (`~/.grok/agents/`) - residual de host

71 ficheiros, mesmos `name:` que o vault. **Nenhum** sha256 igual ao plugin ou ao vault (cópia adaptada: `model:` omitido na amostra C-level). ADR D2: Grok não é terceira fonte de verdade do produto. Cutover futuro não pode deixar 51 homônimos ativos no segundo host. Fora desta fatia (ver plano).

## 7. Skills e hooks (contexto; inventário de agent é o DoD de BT-6)

Não é BT-7 (drift gate) nem implementação. Medição pontual para o plano:

| Superfície | Plugin | `~/.claude` | Nota |
|---|---|---|---|
| Skills core | 4 (`bigtech`, `proj_software`, `visual-design-director`, `tab_pendencias` embutida) | 46; as 4 core **divergem** (sha distinto) | Grok: symlink das 3 primeiras → Claude; `tab_pendencias` → produto (D5 correto no Grok) |
| Hooks `*.py` | 7 (6 core + shim `tab_pendencias_reminder`) | 13 (os 6/7 core + pessoais) | Homônimos TDD/bigtech = risco ALTO de execução dupla se o plugin ligar **com** os globais |

Classificação de superfície (não ficheiro a ficheiro de hook):

- Skills `bigtech` / `proj_software` / `visual-design-director`: `CORE-GENERIC` → plugin wins; vault vira wrapper D4 ou some.
- Skill `tab_pendencias` embutida no plugin: `STALE` (D5). Owner = produto standalone.
- Hooks `bigtech_*` + `tdd_*`: `CORE-GENERIC` → um registro ativo (plugin) após canário.
- Hooks `no_mdash`, `trash-guard`, `token_alert_*`, `pubmed_fda_crosslink`, `regua_glintfx`, `session_models_apply`: `PERSONAL-OVERLAY`.

## 8. O que este inventário **não** faz

- Não remove globais. Não edita `~/.claude` / `~/.grok`.
- Não altera `agents/` do plugin (nenhum port nesta fatia: gap `CORE-GENERIC` = 0).
- Não implementa gate de drift (BT-7) nem evals `/bigtech` (BT-8).
- Não promove ✅ (falta TST/AUD de campanha).
- Não republica o CSV PHASE 0 (fica como before).

## 9. Reversibilidade da classificação

Classe de um ficheiro é *two-way door* (ADR). Reclassificar um `VAULT_ONLY` (ex.: se o líder quiser um game-agent no produto) não exige reescrever o núcleo. A ação **delete vault copy** só é *one-way* depois de executada; por isso fica no plano, com rollback, e não nesta fatia.
