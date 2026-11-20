# bigtech

![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Type](https://img.shields.io/badge/type-Claude%20Code%20Plugin-blue)
![Status](https://img.shields.io/badge/status-stable-brightgreen)
![Language](https://img.shields.io/badge/lang-pt--br%20%2F%20en-lightgrey)
![Agents](https://img.shields.io/badge/agents-71-yellow)
![Skills](https://img.shields.io/badge/skills-16-yellow)
![CI](https://img.shields.io/github/actions/workflow/status/petrinhu/bigtech_plugin/ci.yml?label=CI)
![Release](https://img.shields.io/github/v/release/petrinhu/bigtech_plugin?label=release)

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

> Structure any project like a digital-product company: a constellation of 71 agents (12 C-level + 59 operational), 15 skills, and governance and TDD hooks. Scales from **early** through **scale** to **bigtech** (deprecated alias: `solo` → `early`).

### Welcome, supreme leader

You, who install and operate this plugin, are the **supreme leader of this organization: the CEO of your bigtech.** The C-level constellation (Celso/CEO included) proposes and executes, but **the final word is always yours.**

High-stakes decisions (macro architecture, scope, stack, go/no-go, irreversible deploys, spend, any hard-to-reverse choice) are yours. When in doubt, or when more than one viable option exists, the agents do not decide on their own: they ask (the recommended option comes first). The team works for you.

### What it is

`bigtech` packages a complete product-and-engineering organization as a plugin for Claude Code:

- **71 agents.** 12 C-level (strategy, product, engineering, marketing, operations, security, data, AI, finance, revenue, legal, chief of staff) and 59 operational agents that do the work, including the game-development squad and the medical-expert agents.
- **15 skills.** Orchestration skills (`/bigtech`, `/proj_software`, `/proj_jogo`, `/bigtech:tab_pendencias`), agent shortcuts (`/dr-advogado`, `/dr-medico-perito`, `/dr-medico-psiquiatra`, `/dr-medico-trabalho`, `/learning-designer`, `/suporte-linux`, `/visual-design-director`), the case orchestrator `/pericia-medica`, and three new skills: `/watchcode`, `/manter_ligado` and `/olhe_agentes`. `github-gossips` left the plugin and stays available outside it.
- **Governance and TDD hooks.** Test guard-rail (red, green, refactor), project-size reassessment, operating-mode reinforcement, and bootstrap of the manuals into the session.

The core principle: **the process adapts to the size of the project, never the other way around.** A 200-line CLI does not summon the whole team. The Chief of Staff classifies the size and turns on only what is needed, preventing over-engineering.

**Canonical project sizes (porte):** `early` | `scale` | `bigtech`. Headcount is an auxiliary note, not a size value. Legacy `--porte solo` and marker `porte=solo` normalize to `early` (floor is always at least early).

### Installation

Install on **Claude Code** (native plugin). Each step below is a command you run in your terminal.

#### Claude Code (native plugin)

**Prerequisite:** `python3` on your PATH (`python3 --version`). Hooks spawn as `python3`.

- **Linux:** usually present; else `sudo apt install python3` (or `dnf` / `pacman` / `zypper`).
- **macOS:** `xcode-select --install` or `brew install python`.
- **Windows (native):** Microsoft Store Python registers the `python3` alias (recommended). The python.org installer may only provide `python`/`py`; use the plugin's `bin/python3.cmd` shim on PATH, or **WSL**.

#### Recommended dependencies

**Warning: without the recommended dependencies, bigtech is heavily compromised.** Install the full bundle, `bigtech-completo`, which brings everything at once. If you decline the dependencies, know what stops working:

- **Without `superpowers`:** `/bigtech:proj_software` and `visual-design-director`, when they run in the main conversation (not inside an agent), lose the brainstorming (a conversation to settle an unclear request), the written plan, and the test-first cycle (TDD). Engineering agents keep working, just without that reference.
- **Without `playwright`:** the session cannot control a browser (open a page, click, take a screenshot). `accessibility-specialist` loses browser checks. `playwright` downloads the `@playwright/mcp` package from the internet every time its server starts.
- **Without `frontend-design`:** interface design uses only the principles already built into the frontend and visual design agents. You lose the newer, canonical version of the skill. The impact is small.

**How to install.** First add the marketplaces (the catalogs where plugins come from), then install the bundle. If a marketplace is already added, skip its line:

```
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add https://github.com/petrinhu/bigtech_plugin
claude plugin install bigtech-completo@petrinhu
```

**To decline the dependencies**, install only the core. No dependency comes with it:

```
claude plugin install bigtech@petrinhu
```

**Limits you should know:**

- If the full bundle is installed without the marketplaces above, it stays installed but does not load. bigtech warns about this at the start of each session.
- To decline ONE recommended plugin after installing the full bundle, you must uninstall the bundle: `claude plugin uninstall bigtech-completo@petrinhu`. The dependencies stay active after that.
- `claude plugin prune` removes the leftover dependencies, but it also removes `bigtech`, which then has to be installed again.
- `playwright` downloads the `@playwright/mcp` package from the internet at every start. Without network access, the session has no browser.

**After install:** restart the Claude Code session so `bigtech_session_init` can inject manuals and mode reinforcement.

**Name conflicts.** If global agents, skills, or hooks in `~/.claude/` already use the same names as this plugin, do **not** install over them. Prefer an isolated profile (`CLAUDE_CONFIG_DIR=...`) or retire only the colliding **bigtech core** names. Do **not** delete personal or unrelated agents (`dr-*`, `game-*`, etc.). Detail: [LLM.md](LLM.md) and the [Installation wiki page](https://github.com/petrinhu/bigtech_plugin/wiki/Installation).

If you are an AI agent installing on behalf of a user, follow [LLM.md](LLM.md).

#### Optional: manter_ligado (Linux with systemd only)

`manter_ligado` keeps the data connection alive with the lid closed and saves the state of the sessions at 5% battery, without shutting the machine down. It depends on systemd and runs only on Linux with systemd.

### Usage

The user's instructions (the global CLAUDE.md and the project CLAUDE.md, and the rules they reference) take precedence over this plugin's manuals, agents, and reminders in any conflict. Where they diverge, follow the user's instructions.

The 2 orchestration skills are the entry points. Invoke them with a slash or describe your intent in natural language; the mode reinforcement routes the request to the right skill. The other skills are agent shortcuts, a case orchestrator, or operational tools, listed under [Skills](#skills).

#### `/bigtech`: assemble the constellation

Business and leadership layer (product, marketing, sales, legal, finance, release). Invokes the Chief of Staff (Cósimo), who classifies the size, recommends the pipeline variant (the user confirms), and returns the activation map: which C-levels and operational agents to turn on, and in which of the 12 phases.

```
/bigtech ./my-project
/bigtech "scheduling app for clinics" --porte early --dispatch
```

Use it when you want to "assemble the team", "organize it like a bigtech", "which pipeline and which agents", "who leads this", or "classify the size".

#### `/proj_software`: SDLC engine

Orchestrates the software development life cycle across 5 macro-phases, allocating the engineering agents by level, with an anti-over-engineering gatekeeper and cross-cutting security (shift-left). This is where `/bigtech` delegates engineering execution.

```
/proj_software
/proj_software "payments API with idempotency"
```

Use it when starting a new software project: "I'm going to build software", "new system", "build a feature", "which flow to follow".

#### `/bigtech:tab_pendencias`: WSJF planning table

Creates and maintains a backlog table ordered top to bottom in the sequence that minimizes rework, combining topological ordering (dependency) with WSJF (value). The "Wave" column marks steps of equal value that run in parallel.

```
/bigtech:tab_pendencias --create
/bigtech:tab_pendencias --show
/bigtech:tab_pendencias --reorder
```

Use it to plan steps, order the backlog, or ask "what's left" and "in what order to do it".

**Keeping the table fresh.** Marking a status is cheap and manual; reordering is expensive and rare. When you commit work that closes or advances a `TODO.md` item, cite the item ID in the commit message and touch the `Status` column in the same commit (delivered implementation → `🔍 Pendente verificação`; `✅` only after the test/audit wave). Reordering, by contrast, runs only through `--reorder`, and only when a prioritization input changes and you decide to reorder. See [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

### Skills

| Skill | Kind | Function |
|---|---|---|
| `bigtech` | orchestration | Assembles the constellation and classifies the project size. |
| `proj_software` | orchestration | Runs the software life cycle (SDLC) in 5 macro-phases. |
| `proj_jogo` | orchestration | Runs game development (game-dev SDLC) with the game squad, from game jam to AAA. |
| `tab_pendencias` | orchestration | Creates and orders the WSJF backlog table (`TODO.md`). |
| `visual-design-director` | agent shortcut | High-fidelity visual design, rendered and checked on screen. |
| `dr-advogado` | agent shortcut | Brazilian legal work: case analysis, sourced research, legal drafts. |
| `dr-medico-perito` | agent shortcut | Medical-expert work: reports, causal nexus, damage and incapacity. |
| `dr-medico-psiquiatra` | agent shortcut | Forensic psychiatry: criminal responsibility, civil capacity, psychic damage. |
| `dr-medico-trabalho` | agent shortcut | Occupational medicine: occupational nexus, insalubrity, hazard pay. |
| `pericia-medica` | case orchestrator | Runs a medical-legal case with the quartet of medical-expert and legal agents. |
| `learning-designer` | agent shortcut | Instructional design: lessons, activities, quizzes, and course outlines. |
| `suporte-linux` | agent shortcut | Interactive Linux support: detects the distro first and asks before each command. |
| `watchcode` | operational | Watches the journal and coredumps during agent work and captures real crashes. |
| `manter_ligado` | operational | Keeps the connection alive with the lid closed and saves sessions at 5% battery (Linux with systemd only). |
| `olhe_agentes` | operational | Turns the agent monitor on or off and reports idle agents on a 5-minute tick. |

Shortcuts such as `/dr-advogado` and `/learning-designer` call the agent of the same name, with the `bigtech:` prefix (for example, `bigtech:dr-advogado`).

### Agents

#### C-level (12)

| Agent | Role | Domain |
|---|---|---|
| `celso-ceo` | CEO | Strategy and arbitration |
| `capitolino-cpo` | CPO | Product and design |
| `caetano-cto` | CTO | Product engineering |
| `camilo-cmo` | CMO | Marketing and go-to-market |
| `cosmo-coo` | COO | Cross-functional execution |
| `narciso-ciso` | CISO | Security |
| `candido-cdo` | CDO | Data, analytics, and ML |
| `caio-caio` | CAIO | AI as a capability |
| `confucio-cfo` | CFO | Finance and budget |
| `cicero-cro` | CRO | Revenue and sales |
| `claudio-clo` | CLO | Legal (general counsel) |
| `cosimo-chief-of-staff` | Chief of Staff | Pipeline routing, anti-over-engineering |

#### Operational (59)

**Engineering (15):** `software-architect`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `linux-diag`, `devops-sre`, `performance-engineer`, `network-engineer`, `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.

**Data and AI (4):** `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.

**Product, UX, and Design (8):** `product-manager`, `business-analyst`, `ux-researcher`, `ux-ui-designer`, `visual-design-director`, `ux-writer`, `accessibility-specialist`, `art-director`.

**Management and People (3):** `engineering-manager`, `scrum-master`, `engineering-coach`.

**Marketing, Growth, and Revenue (7):** `content-seo`, `pr-comms`, `growth-engineer`, `community-manager`, `customer-success`, `revenue-ops`, `product-marketing-manager`.

**Support, Docs, Legal, Education, and i18n (7):** `support-engineer`, `technical-writer`, `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`, `revisor-textual`, `learning-designer`.

**Game development (11):** `game-producer`, `lead-game-designer`, `economy-designer`, `level-designer`, `narrative-designer`, `narrative-writer`, `gameplay-engineer`, `engine-graphics-programmer`, `game-animator`, `3d-artist-rigger`, `audio-designer-composer`.

**Medical-expert and legal (4):** `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho`.

When invoked, every agent runs a pre-flight check on the backlog table (`TODO.md` at the root): the C-level agents require it as a precondition in the activation map; the operational agents flag it if missing and proceed with the task.

### Hooks

| Hook | Event | Function |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write\|Edit) | TDD guard-rail: blocks code outside the red, green, refactor cycle. Opt-in per project. |
| `tdd_runner.py` | PostToolUse (Write\|Edit) | Runs the test suite after the edit and reports the result to the TDD cycle. |
| `bigtech_session_init.py` | SessionStart | Injects the manuals' path into the context (docs-bootstrap), warns if `caveman` is active, and warns about recommended dependencies that are missing. |
| `bigtech_porte_reminder.py` | SessionStart | Reassesses the project size (scales up or down); only fires on a code project not yet classified. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Backlog-table staleness detector. Reminds you to generate the `TODO.md` via `/bigtech:tab_pendencias` when the project is classified (`.bigtech-porte` marker) but has no table; once the table exists, measures its staleness via `git` (commits and days since the last touch to `TODO.md`) and, after a long session, nudges you to review and reorder it. Thresholds are tunable in an optional `.tab-staleness.json` at the project root. It only reminds, never blocks or reorders. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reinforces bigtech mode and routes natural-language activation to `/bigtech`. Marker-scoped, noise-resistant. |

The plugin declares 9 hook entries across 5 events; the smoke test checks each one.

### Compatibility

**Platform.** Works on Linux, macOS, and Windows (native or WSL). The hooks are pure Python and run cross-platform; the hard prerequisite on Claude Code is `python3` on the PATH (see [Claude Code (native plugin)](#claude-code-native-plugin), notably the Windows note). When the `tab_pendencias` skill plans tests or audits that need external tools, each tool is offered for installation with your confirmation, using the command that fits your OS (apt/dnf/brew/winget/choco/scoop) and preferring cross-platform managers (pip/uv, cargo, npm). Nothing is installed silently.

**Built for Claude Code (Anthropic).** The official install path is the Claude Code plugin/marketplace format (life-cycle hooks, skills, subagent protocol). Other assistants or code CLIs (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) are not supported without their own adaptation.

**Possible conflict with the `caveman` plugin.** `caveman` compresses communication and can interfere with this plugin's mode reinforcement and routing. The session hook warns you if it detects both active at the same time. Whether to keep `caveman` is your decision; if you keep both, make sure requests for the constellation still reach `/bigtech`.

### Model and effort

The agents ship with `model: inherit`: each one runs on the model of the thread that dispatches it, so the model choice follows your session and your own instructions. If your instructions define how models and effort are chosen, they take precedence over this plugin.

To pin a model for one agent, edit the `model` field in the header of `agents/<slug>.md` (accepted values: `inherit`, `opus`, `sonnet`, `haiku`) and adjust the effort level with `/effort`.

### Documentation

**Wiki (beginner-friendly, didactic):** the [project Wiki](https://github.com/petrinhu/bigtech_plugin/wiki) has one page per agent, hook, and skill, plus a glossary, an installation guide, and a step-by-step usage guide.

The governance manuals ship with the plugin in `docs/house/` and are injected into the session context:

- `docs/house/ORG.md`: governance manual for the constellation (RACI, sizes, pipeline routing).
- `docs/house/pipeline_release_1.0.md`: 12-phase release pipeline, from idea to 1.0.
- `docs/house/lideranca_pipeline_release.md`: C-level leadership theory and the named constellation.
- `docs/house/TOOLING.md`: catalog of free/open-source (FOSS) tools per agent.
- `docs/house/`: quality contract, tests, agile, deploy checklist, and audits.
- `docs/principles/`: architecture principles, agile methodology, anti-patterns, and hardware limits.

### Security

The hooks run code on your machine, and `tdd_runner` may run the test command declared by the project you open (trust parity with `make test`/`npm test`). Before using it with third-party repositories, read [SECURITY.md](./SECURITY.md): trust model, opt-in, and how to disable.

> **TDD mode runs a project-defined command as a shell.** The PostToolUse hook `tdd_runner` is opt-in: it only activates when the project you open contains a `.claude/tdd-guard.json` file. When it is active, the `fast_command`/`test_command` declared in that file is executed as a shell command after each edit. Treat `.claude/tdd-guard.json` as trusted code (the same trust you give to a `make test`/`npm test` target), and do not turn on TDD mode in an untrusted third-party repository without first inspecting that command. Prefer pointing `test_command` at an isolated executor (container or sandbox) with a process limit; run it on the host only where your rules allow.

### License

Distributed under the [Apache-2.0](./LICENSE) license.

---

## Português

> Estruture qualquer projeto como uma empresa de produto digital: uma constelação de 71 agents (12 C-level + 59 operacionais), 15 skills e hooks de governança e TDD. Dimensionável de **early** passando por **scale** até **bigtech** (alias depreciado: `solo` → `early`).

### Bem-vindo, líder supremo

Você, que instala e opera este plugin, é o **líder supremo desta organização: o CEO da sua bigtech.** A constelação C-level (Celso/CEO inclusive) propõe e executa, mas **a palavra final é sempre sua.**

Decisões de altíssimo valor (arquitetura macro, escopo, stack, go/no-go, deploy irreversível, gasto, qualquer escolha difícil de reverter) são suas. Diante de dúvida ou de mais de uma opção viável, os agents não decidem sozinhos: eles perguntam (a opção recomendada vem primeiro). O time trabalha para você.

### O que é

`bigtech` empacota uma organização completa de produto e engenharia em forma de plugin para o Claude Code:

- **71 agents.** 12 C-level (estratégia, produto, engenharia, marketing, operações, segurança, dados, IA, finanças, receita, jurídico, chief of staff) e 59 operacionais que executam o trabalho, incluindo o time de desenvolvimento de jogos e os agents médico-periciais.
- **15 skills.** Skills de orquestração (`/bigtech`, `/proj_software`, `/proj_jogo`, `/bigtech:tab_pendencias`), atalhos de agent (`/dr-advogado`, `/dr-medico-perito`, `/dr-medico-psiquiatra`, `/dr-medico-trabalho`, `/learning-designer`, `/suporte-linux`, `/visual-design-director`), o orquestrador de caso `/pericia-medica` e três skills novas: `/watchcode`, `/manter_ligado` e `/olhe_agentes`. `github-gossips` saiu do plugin e continua disponível fora dele.
- **Hooks de governança e TDD.** Guard-rail de testes (red, green, refactor), reavaliação de porte do projeto, reforço do modo de operação e bootstrap dos manuais na sessão.

O princípio central: **o processo se adapta ao porte do projeto, nunca o contrário.** Um CLI de 200 linhas não chama o time inteiro. O Chief of Staff classifica o porte e liga só o necessário, prevenindo over-engineering.

**Portes canônicos:** `early` | `scale` | `bigtech`. Headcount é nota auxiliar, não valor de porte. Legado `--porte solo` e marcador `porte=solo` normalizam para `early` (piso sempre early).

### Instalação

Instale no **Claude Code** (plugin nativo). Cada passo abaixo é um comando que você roda no terminal.

#### Claude Code (plugin nativo)

**Pré-requisito:** `python3` no PATH (`python3 --version`). Os hooks são invocados como `python3`.

- **Linux:** em geral já presente; senão `sudo apt install python3` (ou `dnf` / `pacman` / `zypper`).
- **macOS:** `xcode-select --install` ou `brew install python`.
- **Windows (nativo):** o Python da Microsoft Store registra o alias `python3` (recomendado). O instalador do python.org pode oferecer só `python`/`py`; use o shim `bin/python3.cmd` do plugin no PATH, ou **WSL**.

#### Dependências recomendadas

**Aviso: sem as dependências recomendadas o bigtech fica muito comprometido.** Instale o pacote completo, `bigtech-completo`, que traz tudo de uma vez. Se você recusar as dependências, saiba o que deixa de funcionar:

- **Sem `superpowers`:** o `/bigtech:proj_software` e o `visual-design-director`, quando rodam na conversa principal (não num agent), perdem o brainstorming (a conversa para fechar um pedido ambíguo), o plano escrito e o ciclo de testes antes do código (TDD). Os agents de engenharia continuam funcionando, só sem essa referência.
- **Sem `playwright`:** a sessão não controla o navegador (abrir página, clicar, tirar captura de tela). O `accessibility-specialist` perde a verificação no navegador. O `playwright` baixa o pacote `@playwright/mcp` da internet toda vez que o servidor dele inicia.
- **Sem `frontend-design`:** o design de interface usa só os princípios já embutidos nos agents de frontend e de design visual. Perde-se a versão atualizada da skill. O impacto é pequeno.

**Como instalar.** Primeiro adicione os marketplaces (as lojas de onde os plugins vêm), depois instale o pacote. Se um marketplace já estiver adicionado, pule a linha dele:

```
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add https://github.com/petrinhu/bigtech_plugin
claude plugin install bigtech-completo@petrinhu
```

**Para recusar as dependências**, instale só o núcleo. Nenhuma dependência vem junto:

```
claude plugin install bigtech@petrinhu
```

**Limites que você precisa conhecer:**

- Se o pacote completo for instalado sem os marketplaces acima, ele fica instalado mas não carrega. O bigtech avisa isso no início de cada sessão.
- Para recusar UM recomendado depois de instalar o pacote completo, é preciso desinstalar o pacote: `claude plugin uninstall bigtech-completo@petrinhu`. As dependências continuam ativas depois disso.
- `claude plugin prune` remove as dependências que sobraram, mas também remove o `bigtech`, que então precisa ser instalado de novo.
- O `playwright` baixa o pacote `@playwright/mcp` da internet a cada início. Se a rede não estiver disponível, a sessão fica sem navegador.

**Depois de instalar:** reinicie a sessão do Claude Code para o `bigtech_session_init` injetar os manuais e o reforço de modo.

**Conflito de nomes.** Se já houver agents, skills ou hooks globais em `~/.claude/` com os mesmos nomes deste plugin, **não** instale por cima. Prefira um perfil isolado (`CLAUDE_CONFIG_DIR=...`) ou aposente só os nomes do **núcleo bigtech** que colidem. **Não** apague agents pessoais ou de outros domínios (`dr-*`, `game-*`, etc.). Detalhe: [LLM.md](LLM.md) e a [página de Instalação da wiki](https://github.com/petrinhu/bigtech_plugin/wiki/Instalacao).

Se você é um agente de IA instalando a pedido de um usuário, siga [LLM.md](LLM.md).

#### Opcional: manter_ligado (só Linux com systemd)

`manter_ligado` mantém a conexão de dados viva com a tampa fechada e salva o estado das sessões com 5% de bateria, sem desligar a máquina. Depende do systemd e roda só em Linux com systemd.

### Uso

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.

As 2 skills de orquestração são os pontos de entrada. Invoque por barra ou descreva a intenção em linguagem natural; o reforço de modo roteia o pedido para a skill certa. As demais skills são atalhos de agent, um orquestrador de caso ou ferramentas operacionais, listadas em [Skills](#skills).

#### `/bigtech`: montar a constelação

Camada de negócio e liderança (produto, marketing, vendas, jurídico, finanças, release). Invoca o Chief of Staff (Cósimo), que classifica o porte, recomenda a variante de pipeline (o usuário confirma) e devolve o mapa de ativação: quais C-levels e operacionais ligar, em quais das 12 fases.

```
/bigtech ./meu-projeto
/bigtech "app de agenda para clínicas" --porte early --dispatch
```

Use quando quiser "montar o time", "organizar como bigtech", "qual pipeline e quais agents", "quem lidera isso" ou "classificar o porte".

#### `/proj_software`: motor de SDLC

Orquestra o ciclo de vida de software em 5 macrofases, alocando os agents de engenharia por nível, com gatekeeper anti-over-engineering e segurança transversal (shift-left). É para onde o `/bigtech` delega a execução de engenharia.

```
/proj_software
/proj_software "API de pagamentos com idempotência"
```

Use quando começar um projeto novo de software: "vou criar um software", "novo sistema", "construir feature", "qual fluxo seguir".

#### `/bigtech:tab_pendencias`: tabela de planejamento WSJF

Cria e mantém uma tabela de pendências ordenada de cima para baixo na sequência que minimiza retrabalho, combinando ordenação topológica (dependência) com WSJF (valor). A coluna "Onda" marca passos de igual valor que rodam em paralelo.

```
/bigtech:tab_pendencias --create
/bigtech:tab_pendencias --show
/bigtech:tab_pendencias --reorder
```

Use para planejar passos, ordenar backlog, ou perguntar "o que falta" e "em que ordem fazer".

**Manter a tabela fresca.** Marcar status é barato e manual; reordenar é caro e raro. Ao commitar trabalho que fecha ou avança um item do `TODO.md`, cite o ID do item na mensagem do commit e toque a coluna `Status` no mesmo commit (implementação entregue → `🔍 Pendente verificação`; `✅` só após a onda de teste/auditoria). Reordenar, por outro lado, só roda pelo `--reorder`, e só quando um input de priorização muda e você decide reordenar. Veja [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

### Skills

| Skill | Tipo | Função |
|---|---|---|
| `bigtech` | orquestração | Monta a constelação e classifica o porte do projeto. |
| `proj_software` | orquestração | Toca o ciclo de vida de software (SDLC) em 5 macrofases. |
| `proj_jogo` | orquestração | Toca o desenvolvimento de jogo com o time de game, de game jam a AAA. |
| `tab_pendencias` | orquestração | Cria e ordena a tabela de backlog WSJF (`TODO.md`). |
| `visual-design-director` | atalho de agent | Design visual de alta fidelidade, renderizado e conferido na tela. |
| `dr-advogado` | atalho de agent | Trabalho jurídico brasileiro: análise de processo, pesquisa com fonte, peças. |
| `dr-medico-perito` | atalho de agent | Perícia médica: laudos, nexo causal, dano e incapacidade. |
| `dr-medico-psiquiatra` | atalho de agent | Psiquiatria forense: imputabilidade, capacidade civil, dano psíquico. |
| `dr-medico-trabalho` | atalho de agent | Medicina do trabalho: nexo ocupacional, insalubridade, periculosidade. |
| `pericia-medica` | orquestrador de caso | Conduz um caso médico-jurídico com o quarteto de agents médicos e jurídico. |
| `learning-designer` | atalho de agent | Design instrucional: aulas, atividades, quizzes e planos de curso. |
| `suporte-linux` | atalho de agent | Suporte Linux interativo: detecta a distro primeiro e pergunta antes de cada comando. |
| `watchcode` | operacional | Vigia o journal e os coredumps durante o trabalho dos agents e captura crashes reais. |
| `manter_ligado` | operacional | Mantém a conexão com a tampa fechada e salva as sessões com 5% de bateria (só Linux com systemd). |
| `olhe_agentes` | operacional | Liga, desliga ou mostra o monitor de agents, com tick a cada 5 minutos. |

Atalhos como `/dr-advogado` e `/learning-designer` chamam o agent de mesmo nome, com o prefixo `bigtech:` (por exemplo, `bigtech:dr-advogado`).

### Agents

#### C-level (12)

| Agent | Cargo | Domínio |
|---|---|---|
| `celso-ceo` | CEO | Estratégia e arbitragem |
| `capitolino-cpo` | CPO | Produto e design |
| `caetano-cto` | CTO | Engenharia do produto |
| `camilo-cmo` | CMO | Marketing e go-to-market |
| `cosmo-coo` | COO | Execução cross-funcional |
| `narciso-ciso` | CISO | Segurança |
| `candido-cdo` | CDO | Dados, analytics e ML |
| `caio-caio` | CAIO | IA como capability |
| `confucio-cfo` | CFO | Finanças e orçamento |
| `cicero-cro` | CRO | Receita e vendas |
| `claudio-clo` | CLO | Jurídico (general counsel) |
| `cosimo-chief-of-staff` | Chief of Staff | Roteamento de pipeline, anti-over-engineering |

#### Operacionais (59)

**Engenharia (15):** `software-architect`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `linux-diag`, `devops-sre`, `performance-engineer`, `network-engineer`, `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.

**Dados e IA (4):** `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.

**Produto, UX e Design (8):** `product-manager`, `business-analyst`, `ux-researcher`, `ux-ui-designer`, `visual-design-director`, `ux-writer`, `accessibility-specialist`, `art-director`.

**Gestão e Pessoas (3):** `engineering-manager`, `scrum-master`, `engineering-coach`.

**Marketing, Crescimento e Receita (7):** `content-seo`, `pr-comms`, `growth-engineer`, `community-manager`, `customer-success`, `revenue-ops`, `product-marketing-manager`.

**Suporte, Docs, Legal, Educação e i18n (7):** `support-engineer`, `technical-writer`, `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`, `revisor-textual`, `learning-designer`.

**Desenvolvimento de jogos (11):** `game-producer`, `lead-game-designer`, `economy-designer`, `level-designer`, `narrative-designer`, `narrative-writer`, `gameplay-engineer`, `engine-graphics-programmer`, `game-animator`, `3d-artist-rigger`, `audio-designer-composer`.

**Perícia médica e jurídico (4):** `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho`.

Ao serem acionados, todos os agents fazem um pre-flight da tabela de pendências (`TODO.md` na raiz): os C-level a exigem como pré-condição no mapa de ativação; os operacionais sinalizam caso falte e seguem com a tarefa.

### Hooks

| Hook | Evento | Função |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write\|Edit) | Guard-rail de TDD: bloqueia código fora do ciclo red, green, refactor. Opt-in por projeto. |
| `tdd_runner.py` | PostToolUse (Write\|Edit) | Roda a suíte de testes após a edição e reporta o resultado ao ciclo TDD. |
| `bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto (docs-bootstrap), avisa se o `caveman` está ativo e avisa das dependências recomendadas que faltam. |
| `bigtech_porte_reminder.py` | SessionStart | Reavalia o porte do projeto (escala para cima ou para baixo); só dispara em projeto de código ainda não classificado. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Detector de defasagem da tabela de pendências. Lembra de gerar o `TODO.md` via `/bigtech:tab_pendencias` quando o projeto já foi classificado (marcador `.bigtech-porte`) mas ainda não tem a tabela; com a tabela presente, mede a defasagem dela via `git` (commits e dias desde o último toque no `TODO.md`) e, após uma sessão longa, dá um lembrete para revisar e reordenar. Os limiares são ajustáveis num `.tab-staleness.json` opcional na raiz do projeto. Só lembra, nunca bloqueia nem reordena. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo bigtech e roteia ativação por linguagem natural para `/bigtech`. Escopado por marcador, anti-ruído. |

O plugin declara 9 entradas de hook em 5 eventos; o smoke test confere cada uma.

### Compatibilidade

**Plataforma.** Funciona em Linux, macOS e Windows (nativo ou WSL). Os hooks são Python puro e rodam de forma cross-platform; o pré-requisito rígido no Claude Code é `python3` no PATH (veja [Claude Code (plugin nativo)](#claude-code-plugin-nativo), em especial a nota de Windows). Quando a skill `tab_pendencias` planeja testes ou auditorias que precisam de ferramentas externas, cada ferramenta é oferecida para instalação com a sua confirmação, no comando adequado ao seu SO (apt/dnf/brew/winget/choco/scoop) e preferindo gerenciadores cross-platform (pip/uv, cargo, npm). Nada é instalado em silêncio.

**Feito para o Claude Code (Anthropic).** O caminho oficial de instalação é o formato de plugin/marketplace do Claude Code (hooks de ciclo de vida, skills, protocolo de subagents). Outros assistentes ou CLIs de código (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) não são suportados sem adaptação própria.

**Possível conflito com o plugin `caveman`.** O `caveman` comprime a comunicação e pode interferir no reforço de modo e no roteamento deste plugin. O hook de sessão avisa caso detecte os dois ativos ao mesmo tempo. Manter ou desativar o `caveman` é decisão sua; se mantiver os dois, garanta que os pedidos da constelação ainda cheguem ao `/bigtech`.

### Modelo e esforço

Os agents vêm com `model: inherit`: cada um roda no modelo da thread que o despacha, então a escolha do modelo segue a sua sessão e as suas instruções. Se as suas instruções definirem como modelo e esforço são escolhidos, elas prevalecem sobre este plugin.

Para fixar um modelo em um agent, edite o campo `model` no cabeçalho de `agents/<slug>.md` (valores aceitos: `inherit`, `opus`, `sonnet`, `haiku`) e ajuste o nível de esforço com `/effort`.

### Documentação

**Wiki (didática, para iniciantes):** a [Wiki do projeto](https://github.com/petrinhu/bigtech_plugin/wiki) tem uma página por agente, hook e skill, além de glossário, guia de instalação e de uso passo a passo.

Os manuais de governança acompanham o plugin em `docs/house/` e são injetados no contexto da sessão:

- `docs/house/ORG.md`: manual de governança da constelação (RACI, portes, roteamento de pipeline).
- `docs/house/pipeline_release_1.0.md`: pipeline de release em 12 fases, da ideia ao 1.0.
- `docs/house/lideranca_pipeline_release.md`: teoria de liderança C-level e a constelação nomeada.
- `docs/house/TOOLING.md`: catálogo de ferramentas livres (FOSS) por agent.
- `docs/house/`: contrato de qualidade, testes, agile, checklist de deploy e auditorias.
- `docs/principles/`: princípios de arquitetura, metodologia agile, anti-patterns e limites de hardware.

### Segurança

Os hooks executam código na sua máquina e o `tdd_runner` pode rodar o comando de teste declarado pelo projeto que você abrir (paridade de confiança com `make test`/`npm test`). Antes de usar com repositórios de terceiros, leia [SECURITY.md](./SECURITY.md): modelo de confiança, opt-in e como desativar.

> **O modo TDD roda como shell um comando definido pelo projeto.** O hook PostToolUse `tdd_runner` é opt-in: só liga quando o projeto que você abrir contém o arquivo `.claude/tdd-guard.json`. Quando está ligado, o `fast_command`/`test_command` declarado nesse arquivo é executado como comando de shell após cada edição. Trate o `.claude/tdd-guard.json` como código confiável (a mesma confiança que você dá a um alvo `make test`/`npm test`) e não ative o modo TDD em repositório de terceiro não-confiável sem antes inspecionar esse comando. Prefira apontar o `test_command` para um executor isolado (container ou sandbox) com limite de processos; rode no host só onde as suas regras permitirem.

### Licença

Distribuído sob a licença [Apache-2.0](./LICENSE).
