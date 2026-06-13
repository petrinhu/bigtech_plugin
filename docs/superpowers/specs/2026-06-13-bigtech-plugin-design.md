# Design — Plugin Claude Code `bigtech`

- **Data:** 2026-06-13
- **Autor:** Petrus (petrinhu)
- **Status:** aprovado para planejamento (aguarda review final do spec)
- **Repo de destino:** `https://codeberg.org/petrinhu/bigtech_plugin.git`
- **Licença:** Apache-2.0

---

## 1. Objetivo

Empacotar a organização "bigtech" (constelação de agents C-level + operacionais
de engenharia/produto/negócio, **sem** as vertentes de jogo e de perícia) como um
**plugin Claude Code distribuível** via marketplace. O plugin entrega:

1. A **constelação de agents** (50 agents) com o orquestrador Cósimo (Chief of Staff).
2. As **skills de orquestração**: `/bigtech` (monta a constelação) e `/proj_software`
   (motor de execução SDLC), mais `/tab_pendencias` (tabela de pendências WSJF).
3. **Hooks** de guard-rail e de governança: TDD, re-avaliação de porte, reforço de
   modo bigtech, e checagem de compatibilidade/dependências.
4. **Docs canônicos** que sustentam os agents/skills, empacotados e higienizados.

**Princípio inegociável:** o produto é **distribuível e público**. Não pode conter
referências locais (`~/.claude`, `/home/petrus`), wikilinks `[[X]]` do vault, nem
**identidade/infra pessoal** (nome do autor como soberano, stack imposta, servidores).

---

## 2. Conteúdo do plugin

### 2.1 Agents — 50 incluídos

**C-level (12):**
`caetano-cto`, `caio-caio`, `camilo-cmo`, `candido-cdo`, `capitolino-cpo`,
`celso-ceo`, `cicero-cro`, `claudio-clo`, `confucio-cfo`, `cosimo-chief-of-staff`,
`cosmo-coo`, `narciso-ciso`.

**Operacionais (38):**
- *Engenharia (14):* `software-architect`, `tech-lead`, `backend-engineer`,
  `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`,
  `hardware-engineer`, `devops-sre`, `performance-engineer`, `network-engineer`,
  `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.
- *Dados/IA (4):* `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.
- *Produto/UX/Design (7):* `product-manager`, `business-analyst`, `ux-researcher`,
  `ux-ui-designer`, `ux-writer`, `accessibility-specialist`, `art-director`.
- *Gestão/Pessoas (2):* `engineering-manager`, `scrum-master`.
- *Marketing/Crescimento/Receita (6):* `content-seo`, `pr-comms`, `growth-engineer`,
  `community-manager`, `customer-success`, `revenue-ops`.
- *Suporte/Docs/Legal/i18n (5):* `support-engineer`, `technical-writer`,
  `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`.

### 2.2 Agents — 20 excluídos

- **Jogo (10):** `3d-artist-rigger`, `audio-designer-composer`, `economy-designer`,
  `engine-graphics-programmer`, `game-animator`, `gameplay_engineer`, `game-producer`,
  `lead-game-designer`, `level-designer`, `narrative-designer`.
- **Perícia/forense (4):** `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`,
  `dr-medico-trabalho`.
- **Pessoal/literário/pedagógico (4):** `narrative-writer`, `revisor-textual`,
  `learning-designer`, `linux-diag`.
- **Removidos por sobreposição (2):** `engineering-coach` (sobrepõe `engineering-manager`),
  `product-marketing-manager` (sobrepõe `camilo-cmo` + `content-seo` + `pr-comms`).

### 2.3 Skills (3)

| Skill | Papel | Observação de higienização |
|---|---|---|
| `bigtech` | Orquestrador: invoca Cósimo, classifica porte, monta a constelação. | Remover menção a `/proj_jogo` e a agents excluídos; apontar docs para `docs/`. |
| `proj_software` | Motor de execução SDLC (engenharia, fases 4-9). | Validar que só referencia agents incluídos. |
| `tab_pendencias` | Tabela de pendências ordenada (WSJF, topológica). | Tem `references/`, LICENSE, SECURITY próprios; trocar wikilinks por refs em `docs/`. |

### 2.4 Hooks (6 scripts + registro)

| Hook | Evento | Função |
|---|---|---|
| `tdd_guard.py` (+ `tdd_common.py`, `tdd_runner.py`) | PreToolUse/edição | Guard-rail TDD (red/green/refactor). Tem suíte de testes própria. |
| `bigtech_porte_reminder.py` | SessionStart | Re-avalia o porte do projeto (escala ↑/↓); só dispara em projeto de código sem `.bigtech-porte`. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça modo bigtech (anti-drift) e roteia ativação por linguagem natural para `/bigtech`. Escopado por marcador (anti-ruído). |
| `bigtech_session_init.py` **(NOVO)** | SessionStart | **(a) Docs-bootstrap:** injeta no contexto o caminho absoluto de `docs/` (resolvido via `os.environ["CLAUDE_PLUGIN_ROOT"]`) + a regra imperativa de leitura dos manuais; **(b)** avisa se `caveman` está ativo (incompatível); **(c)** sugere instalar `playwright`/`superpowers` se ausentes. |

Todos os hooks: resolver paths via `${CLAUDE_PLUGIN_ROOT}` no `hooks/hooks.json` (único lugar onde a variável expande), nunca `~/.claude/hooks`. Registro central em `hooks/hooks.json`.

### 2.5 Docs empacotados — 12 docs (mapa origem → destino)

Higienizados **sem empobrecer o conteúdo técnico** (ver §4).

| Doc | Origem | Destino no plugin |
|---|---|---|
| ORG | `…/projetos_claudebrain/ORG.md` | `docs/ORG.md` |
| pipeline_release_1.0 | `…/projetos_claudebrain/pipeline_release_1.0.md` | `docs/pipeline_release_1.0.md` |
| lideranca_pipeline_release | `…/projetos_claudebrain/lideranca_pipeline_release.md` | `docs/lideranca_pipeline_release.md` |
| TOOLING | `…/projetos_claudebrain/TOOLING.md` | `docs/TOOLING.md` |
| CONTRACT | `…/projetos_claudebrain/CONTRACT.md` | `docs/manuals/CONTRACT.md` |
| TESTES | `…/projetos_claudebrain/TESTES.md` | `docs/manuals/TESTES.md` |
| AGILE | `…/projetos_claudebrain/AGILE.md` | `docs/manuals/AGILE.md` |
| DEPLOY_CHECKLIST | `…/projetos_claudebrain/DEPLOY_CHECKLIST.md` | `docs/manuals/DEPLOY_CHECKLIST.md` |
| AUDITORIAS | `…/projetos_claudebrain/AUDITORIAS.md` | `docs/manuals/AUDITORIAS.md` |
| arquitetura-principios | `~/.claude/docs/arquitetura-principios.md` | `docs/principles/arquitetura-principios.md` |
| agile-methodology | `~/.claude/docs/agile-methodology.md` | `docs/principles/agile-methodology.md` |
| anti-patterns | `~/.claude/docs/anti-patterns.md` | `docs/principles/anti-patterns.md` (higienização extra) |
| hardware-resource-limits | `~/.claude/memory/feedback_hardware_resource_limits.md` | `docs/principles/hardware-resource-limits.md` (generalizado, sem specs da máquina) |

São **13 docs**. Os 9 primeiros são referenciados via `[[ ]]` pelos agents/skills; os 3
seguintes são material de apoio (decisão do usuário); `hardware-resource-limits` é a regra
transversal citada por 20 agents (decisão Q1, empacotada sem as specs da máquina). Todos
entram **sem nenhum wikilink** (§4.1 + Apêndice A).

---

## 3. Layout do repositório

```
bigtech_plugin/                       # repo -> codeberg.org/petrinhu/bigtech_plugin
├── .claude-plugin/
│   ├── plugin.json                   # name: bigtech, version, description, author, license
│   └── marketplace.json              # marketplace de 1 plugin, source: "./"
├── agents/                           # 50 .md higienizados
├── skills/
│   ├── bigtech/SKILL.md
│   ├── proj_software/SKILL.md
│   └── tab_pendencias/               # SKILL.md + references/ + LICENSE + SECURITY
├── hooks/
│   ├── hooks.json
│   ├── tdd_guard.py · tdd_common.py · tdd_runner.py
│   ├── bigtech_porte_reminder.py
│   ├── bigtech_reinforce.py
│   └── bigtech_session_init.py        # docs-bootstrap + aviso caveman + sugestão de deps
├── docs/
│   ├── ORG.md · pipeline_release_1.0.md · lideranca_pipeline_release.md · TOOLING.md
│   ├── manuals/   CONTRACT.md · TESTES.md · AGILE.md · DEPLOY_CHECKLIST.md · AUDITORIAS.md
│   ├── principles/ arquitetura-principios.md · agile-methodology.md · anti-patterns.md · hardware-resource-limits.md
│   └── superpowers/specs/            # artefatos de processo (este spec) — inertes p/ o plugin
├── README.md
├── LICENSE                           # Apache-2.0
└── CHANGELOG.md
```

> O Claude Code só carrega `.claude-plugin/`, `agents/`, `skills/`, `hooks/`,
> `commands/`. Arquivos extras no repo (docs de processo) são inertes no plugin instalado.

---

## 4. Estratégia de higienização (preserva conteúdo técnico)

Regra: **só remover o que prende ao ambiente/identidade local; nunca simplificar o
conteúdo técnico** (decisão do usuário). Despersonalizar ≠ empobrecer.

### 4.1 Higienização técnica — política **zero `[[ ]]`, zero órfãos**

**Regra-mãe (decisão do usuário):** o produto final **não contém nenhum `[[wikilink]]`**.
Cada `[[X]]` é *eliminado* de uma de duas formas, e **nunca** vira um ponteiro pendurado:
- **Alvo empacotado** (os 13 docs) → vira **link Markdown relativo** (`[X](../docs/...)`).
- **Alvo não empacotado** (PARA, projetos, memórias não incluídas, link quebrado) → a frase é
  **reescrita como texto autossuficiente**, sem nenhum "ver [[X]]" apontando para o vazio.
- **Exceção:** `[[nodiscard]]` e outros **atributos C++** em blocos/trechos de código são
  preservados (não são wikilinks).

Detalhamento por categoria de alvo no **Apêndice A** (mapa de rastreabilidade).

1. **Wikilinks** — eliminar 100% conforme a regra-mãe acima (link relativo ou reescrita).
2. **Paths locais** `~/.claude`, `/home/petrus` → removidos ou `${CLAUDE_PLUGIN_ROOT}` (só em `hooks.json`).
3. **Refs cruzadas a agents/skills excluídos** (jogo, perícia, `/proj_jogo`, `/pericia-medica`,
   `dr-*`, `engineering-coach`, `product-marketing-manager`) → removidas/reescritas.
   `cosimo-chief-of-staff` e skill `bigtech` listam só os 50 incluídos; `caetano-cto` não
   aponta para `/proj_jogo`; `art-director` perde as refs aos colegas de jogo.
4. **Validação final (critério de aceitação):** fora de blocos de código,
   `grep -rn '\[\['` = **0**; `grep -rn '/home/petrus\|~/\.claude'` = **0**; **nenhum** link
   Markdown relativo apontando para arquivo inexistente (checagem ativa de órfãos); zero
   menções aos 20 excluídos e aos termos pessoais da §4.2.

### 4.2 Despersonalização (decisão: generalizar mantendo o conceito)
1. **Identidade pessoal** (`petrus`, `Kaiser`, `Presidente`, `Rei`, `Soberano`, e-mail,
   nome próprio do autor como soberano) → generalizar para **"o usuário/operador (você)"**.
2. **Transferência de título ao novo dono (feature de produto):** o conceito de
   autoridade suprema NÃO some — passa para quem instala. Reescrever **ORG §0** como:
   *"Você, que opera este plugin, é o **líder supremo** desta organização — o **CEO da sua
   bigtech**. A constelação C-level propõe e executa; a palavra final é sua. Diante de
   dúvida ou mais de uma opção, os agents perguntam via AskUserQuestion."*
   Adicionar no **README** um "ritual de boas-vindas" que recebe o usuário como CEO/líder
   supremo da própria bigtech.
3. **Stack imposta** (`C++/Qt`, `Breeze` como default obrigatório) → "stack do projeto
   (configurável)"; manter exemplos como exemplos, não como lei pessoal.
4. **Infra pessoal** (`Hostinger`, instâncias `Forgejo`/`Codeberg` pessoais, MCPs/tokens) →
   genérica ("seu provedor de git/hosting") ou removida.
5. **`anti-patterns.md`** recebe revisão item a item (tem proibições atreladas ao fluxo
   pessoal); manter as universais (ex.: `--force`, `--no-verify`), generalizar o resto.

### 4.3 Acesso aos docs em runtime (híbrido robusto)

**Problema:** hoje as referências aos manuais são passivas (`"Governança: [[ORG]]"`) e
dependem do resolvedor de wikilinks do vault, que não viaja com o plugin. Além disso,
`${CLAUDE_PLUGIN_ROOT}` só expande no `hooks.json` (não no corpo de agent/skill), e
**subagents não herdam o `additionalContext`** injetado na thread principal. Logo, o
acesso precisa ser garantido em três frentes:

1. **Hook `bigtech_session_init.py` (SessionStart) — docs-bootstrap.** Lê
   `os.environ["CLAUDE_PLUGIN_ROOT"]`, resolve o caminho absoluto de `docs/` e injeta via
   `hookSpecificOutput.additionalContext` um bloco curto: *"Manuais do plugin bigtech em
   `<ABS>/docs/`: ORG, pipeline_release_1.0, lideranca_pipeline_release, manuals/{CONTRACT,
   TESTES,AGILE,DEPLOY_CHECKLIST,AUDITORIAS}, TOOLING, principles/*. Ao aplicar regras de
   governança/código/teste/deploy/auditoria, **leia o manual relevante antes de decidir**."*
   Cobre a thread principal e as skills.
2. **Skills (`/bigtech`, `/proj_software`, `/tab_pendencias`).** Instrução imperativa +
   path relativo ao diretório da skill (padrão idiomático: *"leia `../../docs/manuals/AGILE.md`
   antes do WSJF"*). Como a skill é carregada de diretório conhecido, o Read relativo funciona.
3. **Agents (50).** Trocar a linha passiva por **instrução imperativa autocontida**, ex.:
   *"Governança/manuais (ORG, CONTRACT, …) acompanham o plugin; o caminho absoluto é
   fornecido no contexto de sessão (docs-bootstrap). **Leia o manual citado antes de
   decidir.** Se o caminho não estiver no contexto, localize via Glob `**/bigtech/docs/**/<NOME>.md`."*
4. **Orquestração repassa o path.** Quando `/bigtech` (Cósimo) e os C-levels disparam um
   subagent via Agent tool, **incluem o caminho absoluto de `docs/` no prompt da task** —
   garante que o subagent (que não herda o `additionalContext`) tenha o path para Read.
5. **Fallback Glob** no corpo do agent (item 3) cobre o uso avulso fora do fluxo orquestrado.

> Resultado: thread principal (1), skills (2), fluxo orquestrado/subagents (4) e uso avulso
> (3+5) todos com caminho resolvido e ordem explícita de leitura.

---

## 5. Distribuição, compatibilidade e dependências

- **Marketplace:** `marketplace.json` com 1 plugin (`source: "./"`); instalável via
  `/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin` + `/plugin install bigtech`.
- **Incompatibilidade com `caveman`:** sem campo nativo no `plugin.json`. Tratada em
  (a) README e (b) `bigtech_session_init.py`, que avisa se o caveman estiver ativo (o caveman
  comprime a comunicação e conflita com o reforço de modo bigtech).
- **Dependências sugeridas:** `playwright` e `superpowers` (não são hard deps; o
  `bigtech_session_init.py` sugere instalação e o README documenta).
- **Licença:** Apache-2.0 (LICENSE + NOTICE quando aplicável).

---

## 6. Execução da implementação (delegada a agents)

Conforme a regra do usuário (toda alteração de produto por agent especialista, nunca
inline; orquestração por C-level via `Workflow` quando possível):

- **Orquestração:** `caetano-cto` (ou `cosmo-coo`).
- **Higienização de docs/agents/skills + despersonalização + README/ritual:** `technical-writer` (+ `ux-writer`).
- **Acesso a docs em runtime (§4.3):** `technical-writer` reescreve as referências passivas
  dos 50 agents em instruções imperativas de leitura e ajusta a orquestração de `/bigtech`/C-levels
  para repassar o path aos subagents; `devops-sre` implementa o docs-bootstrap no `bigtech_session_init.py`.
- **Hooks, `hooks.json`, adaptação de paths, `bigtech_session_init.py`, CI:** `devops-sre`.
- **`plugin.json` / `marketplace.json` / estrutura:** `software-architect` + `devops-sre`.
- **Validação (varredura de refs/termos, testes dos hooks, smoke test de instalação):** `qa-engineer`.
- **Revisão legal da licença/atribuições:** `compliance-legal`.

Detalhamento em ondas/dependências na **tabela de pendências** (`/tab_pendencias --create`,
artefato de planejamento canônico do usuário) — ver `TODO.md` na raiz do projeto.

---

## 7. Decisões registradas

| # | Decisão | Valor |
|---|---|---|
| 1 | Escopo de agents | 50 incluídos; 20 excluídos (jogo 10, perícia 4, pessoal 4, sobreposição 2). |
| 2 | Skills | `/tab_pendencias` + `/bigtech` + `/proj_software`. |
| 3 | Hooks | TDD + `bigtech_porte_reminder` + `bigtech_reinforce` + `bigtech_session_init` (novo). |
| 4 | Docs | **13 docs** empacotados (9 canônicos + arquitetura-principios + agile-methodology + anti-patterns + hardware-resource-limits). |
| 5 | Compat/deps | README + hook `bigtech_session_init`. |
| 6 | Licença | Apache-2.0. |
| 7 | Zona cinzenta | Só `art-director`. |
| 8 | Despersonalização | Generalizar identidade/infra/stack; **transferir o título de líder supremo/CEO ao usuário que instala**. |
| 9 | Acesso a docs em runtime | Híbrido robusto (§4.3): docs-bootstrap por hook + instrução imperativa nos agents + skills relativas + orquestração repassa path + fallback Glob. |
| 10 | Wikilinks | **Zero `[[ ]]` no produto, sem órfãos** (§4.1 + Apêndice A): link relativo (alvo empacotado) ou reescrita autossuficiente; atributos C++ preservados. |
| 11 | Limites de hardware | `feedback_hardware_resource_limits` → empacotado generalizado (sem specs da máquina), 20 agents referenciam o doc. |
| 12 | Prioridade MCP / exemplos | "Prioridade MCP" generalizada leve; exemplos de projetos reais → substituídos por genéricos. |

---

## 8. Fora de escopo (YAGNI)

- Vertentes de jogo e de perícia (e suas skills `/proj_jogo`, `/pericia-medica`).
- `/memo_persistente`.
- `engineering-coach`, `product-marketing-manager` (removidos por sobreposição).
- Hook `no_mdash.py` (preferência estilística pessoal).
- Campo de dependência forte no `plugin.json` (não existe no schema atual).

---

## Apêndice A — Mapa de rastreabilidade (política: zero `[[ ]]`, zero órfãos)

No produto final **não existe nenhum `[[wikilink]]`** (exceto atributos C++ em código).
Cada alvo abaixo tem destino: empacotado (vira link Markdown relativo) ou reescrito como
texto autossuficiente. **Nenhuma frase aponta para alvo ausente.** Levantado por varredura
determinística sobre os 50 agents + 3 skills + 13 docs.

| # | Categoria | Alvos (ocorrências) | Ação (elimina `[[ ]]` sem órfão) |
|---|---|---|---|
| 1 | Docs canônicos | TOOLING(40), ORG(27), pipeline_release_1.0(26), lideranca(12), DEPLOY_CHECKLIST(11), CONTRACT(10), TESTES(8), AUDITORIAS(7), AGILE(5) + arquitetura-principios, agile-methodology, anti-patterns | `[[X]]` → link Markdown relativo (`[X](../docs/…)`) |
| 2 | Atributo C++ (não é wikilink) | `[[nodiscard]]` (CONTRACT:811) e similares | **preservar** — não tocar |
| 3 | Memória transversal (empacotar) | `feedback_hardware_resource_limits` (20) | empacotada generalizada → `docs/principles/hardware-resource-limits.md` (link relativo) |
| 4 | Memórias (absorver/generalizar) | `feedback_mcp_priority`, `feedback-tests-real-db`, `user-lider-supremo` | `[[X]]` removido; vira texto generalizado (MCP leve / §4.2) |
| 5 | Estrutura PARA do vault | `Standards`(14), `Journal`, `Inbox`, `Areas`, `Resources`, `Resources/Standards/*` | reescrever p/ texto ("seus padrões", "seu changelog") |
| 6 | Projetos pessoais | `Projects/site_consultorio`, `rag_maker`, `PokemonTCGViewer`, `transcritor`, `my_comp`, `astrometrica`, `orcamento-pessoal`, `driver_brother_hl_l1222`, `ESP32`, `bcklight`, `*/reports`, `*/TODO` | substituir por exemplos genéricos (decisão Q3) |
| 7 | Genéricos contextuais | `CLAUDE`(9), `TODO`(5) | → "o CLAUDE.md / TODO.md do projeto" (texto) |
| 8 | Link já quebrado | `SEGURANCA`(1) | remover (não existe nem no original) |
| 9 | Agents/skills excluídos | `proj_jogo`, `pericia-medica`, `engineering-coach`, `product-marketing-manager`, `dr-*`, 10 de jogo (`art-director` cita vários), `narrative-writer`, `revisor-textual`, `linux-diag` | reescrever listas da constelação p/ os 50; remover delegações |
| 10 | Paths locais (8 arquivos) | `~/.claude/*`, `/home/petrus/*`, `no_mdash.py`, `templates/*` | remover / `${CLAUDE_PLUGIN_ROOT}` (só em hooks.json) |
| 11 | Ref interna válida | `tab_pendencias` (skill incluída) | manter como menção textual à skill |

**Validação automatizável (qa-engineer), fora de blocos de código:** `grep -rn '\[\['` = 0
· `grep -rn '/home/petrus\|~/\.claude'` = 0 · checagem ativa de links Markdown órfãos = 0 ·
menções aos 20 excluídos = 0 · termos pessoais (§4.2) = 0.
```
