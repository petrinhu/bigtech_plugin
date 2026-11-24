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

> Structure any project like a digital-product company: a constellation of 71 agents (12 C-level + 59 operational), 16 skills, and governance and TDD hooks. Scales from **early** through **scale** to **bigtech** (deprecated alias: `solo` → `early`).

### Welcome, supreme leader

You, who install and operate this plugin, are the **supreme leader of this organization: the CEO of your bigtech.** The C-level constellation (Celso/CEO included) proposes and executes, but **the final word is always yours.**

High-stakes decisions (macro architecture, scope, stack, go/no-go, irreversible deploys, spend, any hard-to-reverse choice) are yours. When in doubt, or when more than one viable option exists, the agents do not decide on their own: they ask (the recommended option comes first). The team works for you.

### What it is

`bigtech` packages a complete product-and-engineering organization as a plugin for Claude Code:

- **71 agents.** 12 C-level (strategy, product, engineering, marketing, operations, security, data, AI, finance, revenue, legal, chief of staff) and 59 operational agents that do the work, including the game-development squad and the medical-expert agents.
- **16 skills.** Orchestration skills (`/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo`, `/bigtech:tab_pendencias`), agent shortcuts (`/bigtech:dr-advogado`, `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-psiquiatra`, `/bigtech:dr-medico-trabalho`, `/bigtech:learning-designer`, `/bigtech:suporte-linux`, `/bigtech:visual-design-director`), the case orchestrator `/bigtech:pericia-medica`, and four operational skills: `/bigtech:watchcode`, `/bigtech:manter_ligado`, `/bigtech:olhe_agentes` and `/bigtech:eficacia`. `github-gossips` left the plugin and stays available outside it.
- **Governance and TDD hooks.** Test guard-rail (red, green, refactor), a reminder to classify the project size, operating-mode reinforcement, bootstrap of the manuals into the session, and the `eficacia` skill's "leader asleep" lock, which queues questions and permission requests instead of leaving a session waiting for you.

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

**Name conflicts.** If global agents, skills, or hooks in `~/.claude/` already use the same names as this plugin, do **not** install over them. Prefer an isolated profile (`CLAUDE_CONFIG_DIR=...`) or retire only the global copies whose names this plugin ships (listed under Agents and Skills below). Since 2.0.0 that list includes the `dr-*` agents and the game-development squad, so global copies of them collide too. Do **not** delete personal agents whose names are not in this plugin. Detail: [LLM.md](LLM.md) and the [Installation wiki page](https://github.com/petrinhu/bigtech_plugin/wiki/Instalacao).

If you are an AI agent installing on behalf of a user, follow [LLM.md](LLM.md).

#### Optional: manter_ligado (Linux with systemd only)

`manter_ligado` keeps the data connection alive with the lid closed and saves the state of the sessions at 5% battery, without shutting the machine down. It depends on systemd and runs only on Linux with systemd.

### Usage

The user's instructions (the global CLAUDE.md and the project CLAUDE.md, and the rules they reference) take precedence over this plugin's manuals, agents, and reminders in any conflict. Where they diverge, follow the user's instructions.

The 4 orchestration skills are the entry points: `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo` and `/bigtech:tab_pendencias`. Invoke them with a slash or describe your intent in natural language: Claude picks the skill whose description matches the request, and, in a project not yet classified, the mode reinforcement points requests for the constellation to `/bigtech:bigtech`. The other skills are agent shortcuts, a case orchestrator, or operational tools, listed under [Skills](#skills).

Always type the `bigtech:` prefix. With it, the command reaches the plugin's skill even when another skill has the same name; the name without the prefix only works while no other skill or command uses it.

#### `/bigtech:bigtech`: assemble the constellation

Business and leadership layer (product, marketing, sales, legal, finance, release). Invokes the Chief of Staff (Cósimo), who classifies the size, recommends the pipeline variant (the user confirms), and returns the activation map: which C-levels and operational agents to turn on, and in which of the 12 phases.

```
/bigtech:bigtech ./my-project
/bigtech:bigtech "scheduling app for clinics" --porte early --dispatch
```

Use it when you want to "assemble the team", "organize it like a bigtech", "which pipeline and which agents", "who leads this", or "classify the size".

#### `/bigtech:proj_software`: SDLC engine

Orchestrates the software development life cycle across 5 macro-phases, allocating the engineering agents by level, with an anti-over-engineering gatekeeper and cross-cutting security (shift-left). This is where `/bigtech:bigtech` delegates engineering execution.

```
/bigtech:proj_software
/bigtech:proj_software "payments API with idempotency"
```

Use it when starting a new software project: "I'm going to build software", "new system", "build a feature", "which flow to follow".

#### `/bigtech:proj_jogo`: game-development engine

The game counterpart of `/bigtech:proj_software`: runs the game-development life cycle across 5 macro-phases with the game squad, with an anti-over-engineering gatekeeper sized from game jam to AAA.

```
/bigtech:proj_jogo
/bigtech:proj_jogo "2D platformer for a 48-hour game jam"
```

Use it when the project is a game: "I'm going to make a game", "new game", "game design", "game jam".

#### `/bigtech:tab_pendencias`: WSJF planning table

Creates and maintains a backlog table ordered top to bottom in the sequence that minimizes rework, combining topological ordering (dependency) with WSJF (value). The "Wave" column marks steps of equal value that run in parallel.

```
/bigtech:tab_pendencias --create
/bigtech:tab_pendencias --show
/bigtech:tab_pendencias --reorder
```

Use it to plan steps, order the backlog, or ask "what's left" and "in what order to do it".

**Keeping the table fresh.** Marking a status is cheap and manual; reordering is expensive and rare. When you commit work that closes or advances a `TODO.md` item, cite the item ID in the commit message and touch the `Status` column in the same commit (delivered implementation → `🔍 Pendente verificação`; `✅` once the branch CI is green). Reordering, by contrast, runs only through `--reorder`, and only when a prioritization input changes and you decide to reorder. See [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

### Skills

Each skill is invoked with the plugin prefix, as `/bigtech:<skill>`.

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
| `eficacia` | operational | More useful work for less spend: a model-free system timer watches the sessions, and a manager or project session queues questions for the leader instead of blocking (the timer needs systemd --user). |

Shortcuts such as `/bigtech:dr-advogado` and `/bigtech:learning-designer` call the agent of the same name, which also carries the `bigtech:` prefix (for example, the agent `bigtech:dr-advogado`).

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

When invoked, 63 of the 71 agents run a pre-flight check on the backlog table (`TODO.md` at the root): the 12 C-level agents require it as a precondition in the activation map; 51 operational agents flag it if missing and proceed with the task. The other 8 skip this check: `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho`, `learning-designer`, `linux-diag`, `narrative-writer`, and `revisor-textual`.

### Hooks

| Hook | Event | Function |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write\|Edit) | TDD guard-rail: blocks code outside the red, green, refactor cycle. Opt-in per project. |
| `tdd_runner.py` | PostToolUse (Write\|Edit) | Runs the test suite after the edit and reports the result to the TDD cycle. |
| `bigtech_session_init.py` | SessionStart | Injects the manuals' path into the context (docs-bootstrap), warns if `caveman` is active, and warns about recommended dependencies that are missing. |
| `bigtech_porte_reminder.py` | SessionStart | With the `.bigtech-porte` marker at the project root, anchors bigtech operating mode at session start and cites the recorded size. Without the marker, on a code project (one with a build file or manifest, such as `package.json` or `pyproject.toml`), it reminds you to classify the size with `/bigtech:bigtech`. Silent otherwise. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Session-length reminder for the backlog table. On SessionStart it records when the session started; on UserPromptSubmit, once per session, if the project has the `.bigtech-porte` marker and a `TODO.md` and the session has run for more than 2 hours, it reminds you to mark delivered items in the `Status` column and to reorder through `/bigtech:tab_pendencias --reorder` only when priorities change. The time limit, or turning the reminder off, goes in an optional `.tab-staleness.json` at the project root. It only reminds, never blocks or reorders. |
| `skills/tab_pendencias/tools/hooks/tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Freshness signals of the backlog table, from the `tab_pendencias` skill. On SessionStart: a `git` repository without `TODO.md` (suggests `/bigtech:tab_pendencias --create`), a table with pending or in-progress items that has not been touched for several commits or days (measured with read-only `git`), an INBOX that needs triage, items piling up while waiting for verification, decisions waiting for you that have aged, and unfinished intake-journal entries. On UserPromptSubmit: new notes in `inbox/` written by another session. Thresholds go in the `[signals]` section of an optional `.tab_pendencias.ini` next to `TODO.md`. It only reminds, never blocks or reorders. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reinforces bigtech mode and routes natural-language activation to `/bigtech:bigtech`. Marker-scoped, noise-resistant. |
| `skills/eficacia/bin/hook_lider_dormindo.sh` | PreToolUse (AskUserQuestion) | From the `eficacia` skill. While the "leader asleep" flag exists, it denies the question, writes it with its options to a local queue, and tells the agent to take a technical doubt to the C-level of the domain or to switch to other work. Without the flag, it exits silently. |
| `skills/eficacia/bin/hook_permissao.sh` | PermissionRequest | From the `eficacia` skill. While the flag exists, it denies the permission request, writes the tool and a summary (the command or the file path) to the same queue, and tells the agent to switch to other work. Without the flag, it exits silently and the request reaches you as usual. |
| `skills/eficacia/bin/hook_fim_turno.sh` | Stop | From the `eficacia` skill. While the flag exists, it blocks the end of the turn once and points the agent to an item in `TODO.md` that does not depend on the pending answer or, when the choice is reversible, to the recommended option on a branch of its own, with no merge; if nothing is left, the agent may stop. The next attempt to stop goes through (`stop_hook_active`), so there is no loop. Without the flag, it exits silently. |

The plugin declares 12 hook entries across 6 events (SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, Stop, and PostToolUse), served by 10 scripts (7 in Python and 3 in bash); the smoke test checks each one. The "leader asleep" flag belongs to your user, not to one project: while it exists, the three `eficacia` hooks act in every Claude Code session you run on the machine.

### Compatibility

**Platform.** Works on Linux, macOS, and Windows (native or WSL). The governance and TDD hooks are pure Python and run cross-platform; the hard prerequisite on Claude Code is `python3` on the PATH (see [Claude Code (native plugin)](#claude-code-native-plugin), notably the Windows note). The three hooks of the `eficacia` skill run with `bash` and also call `python3` and `flock`; the skill's timer and automatic flag need Linux with systemd (`systemctl --user` and `loginctl`). When the `tab_pendencias` skill plans tests or audits that need external tools, each tool is offered for installation with your confirmation, using the command that fits your OS (apt/dnf/brew/winget/choco/scoop) and preferring cross-platform managers (pip/uv, cargo, npm). Nothing is installed silently.

**Built for Claude Code (Anthropic).** The official install path is the Claude Code plugin/marketplace format (life-cycle hooks, skills, subagent protocol). Other assistants or code CLIs (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) are not supported without their own adaptation.

**Possible conflict with the `caveman` plugin.** `caveman` compresses communication and can interfere with this plugin's mode reinforcement and routing. The session hook warns you if it detects both active at the same time. Whether to keep `caveman` is your decision; if you keep both, make sure requests for the constellation still reach `/bigtech:bigtech`.

### Model and effort

The agents ship with `model: inherit`: each one runs on the model of the thread that dispatches it, so the model choice follows your session and your own instructions. If your instructions define how models and effort are chosen, they take precedence over this plugin.

To pin a model for one agent, edit the `model` field in the header of `agents/<slug>.md` (accepted values: `inherit`, `opus`, `sonnet`, `haiku`) and adjust the effort level with `/effort`.

### Documentation

**Wiki (beginner-friendly, didactic):** the [project Wiki](https://github.com/petrinhu/bigtech_plugin/wiki) has one page per agent, hook, and skill (the three `eficacia` hooks are explained on the skill's page), plus a glossary, an installation guide, and a step-by-step usage guide.

The governance manuals ship with the plugin in `docs/house/` and are injected into the session context:

- `docs/house/ORG.md`: governance manual for the constellation (RACI, sizes, pipeline routing).
- `docs/house/pipeline_release_1.0.md`: 12-phase release pipeline, from idea to 1.0.
- `docs/house/lideranca_pipeline_release.md`: C-level leadership theory and the named constellation.
- `docs/house/TOOLING.md`: catalog of free/open-source (FOSS) tools per agent.
- `docs/house/`: quality contract, tests, agile, deploy checklist, and audits.
- `docs/principles/`: architecture principles, agile methodology, anti-patterns, and hardware limits.

### Security

The hooks run code on your machine, and `tdd_runner` may run the test command declared by the project you open (trust parity with `make test`/`npm test`). Before using it with third-party repositories, read [SECURITY.md](./SECURITY.md): trust model, opt-in, and how to disable.

The three hooks of the `eficacia` skill act only while the "leader asleep" flag exists, and then in every session of your user. The skill's timer is installed only with your yes and stays installed if you remove the plugin, so run the skill's `vigia.sh remover` first. [SECURITY.md](./SECURITY.md) has the details.

> **TDD mode runs a project-defined command as a shell.** The PostToolUse hook `tdd_runner` is opt-in: it only activates when the project you open contains a `.claude/tdd-guard.json` file. When it is active, the `fast_command`/`test_command` declared in that file is executed as a shell command after each edit. Treat `.claude/tdd-guard.json` as trusted code (the same trust you give to a `make test`/`npm test` target), and do not turn on TDD mode in an untrusted third-party repository without first inspecting that command. Prefer pointing `test_command` at an isolated executor (container or sandbox) with a process limit; run it on the host only where your rules allow.

### License

Distributed under the [Apache-2.0](./LICENSE) license.

---

## Português

> Estruture qualquer projeto como uma empresa de produto digital: uma constelação de 71 agents (12 C-level + 59 operacionais), 16 skills e hooks de governança e TDD. Dimensionável de **early** passando por **scale** até **bigtech** (alias depreciado: `solo` → `early`).

### Bem-vindo, líder supremo

Você, que instala e opera este plugin, é o **líder supremo desta organização: o CEO da sua bigtech.** A constelação C-level (Celso/CEO inclusive) propõe e executa, mas **a palavra final é sempre sua.**

Decisões de altíssimo valor (arquitetura macro, escopo, stack, go/no-go, deploy irreversível, gasto, qualquer escolha difícil de reverter) são suas. Diante de dúvida ou de mais de uma opção viável, os agents não decidem sozinhos: eles perguntam (a opção recomendada vem primeiro). O time trabalha para você.

### O que é

`bigtech` empacota uma organização completa de produto e engenharia em forma de plugin para o Claude Code:

- **71 agents.** 12 C-level (estratégia, produto, engenharia, marketing, operações, segurança, dados, IA, finanças, receita, jurídico, chief of staff) e 59 operacionais que executam o trabalho, incluindo o time de desenvolvimento de jogos e os agents médico-periciais.
- **16 skills.** Skills de orquestração (`/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo`, `/bigtech:tab_pendencias`), atalhos de agent (`/bigtech:dr-advogado`, `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-psiquiatra`, `/bigtech:dr-medico-trabalho`, `/bigtech:learning-designer`, `/bigtech:suporte-linux`, `/bigtech:visual-design-director`), o orquestrador de caso `/bigtech:pericia-medica` e quatro skills operacionais: `/bigtech:watchcode`, `/bigtech:manter_ligado`, `/bigtech:olhe_agentes` e `/bigtech:eficacia`. `github-gossips` saiu do plugin e continua disponível fora dele.
- **Hooks de governança e TDD.** Guard-rail de testes (red, green, refactor), lembrete de classificar o porte do projeto, reforço do modo de operação, bootstrap dos manuais na sessão e a trava "líder dormindo" da skill `eficacia`, que põe perguntas e pedidos de permissão numa fila em vez de deixar a sessão parada à sua espera.

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

**Conflito de nomes.** Se já houver agents, skills ou hooks globais em `~/.claude/` com os mesmos nomes deste plugin, **não** instale por cima. Prefira um perfil isolado (`CLAUDE_CONFIG_DIR=...`) ou aposente só as cópias globais cujos nomes este plugin traz (listados nas seções Agents e Skills abaixo). Desde a 2.0.0 essa lista inclui os agents `dr-*` e o time de desenvolvimento de jogos, então cópias globais deles também colidem. **Não** apague agents pessoais cujos nomes não estão neste plugin. Detalhe: [LLM.md](LLM.md) e a [página de Instalação da wiki](https://github.com/petrinhu/bigtech_plugin/wiki/Instalacao).

Se você é um agente de IA instalando a pedido de um usuário, siga [LLM.md](LLM.md).

#### Opcional: manter_ligado (só Linux com systemd)

`manter_ligado` mantém a conexão de dados viva com a tampa fechada e salva o estado das sessões com 5% de bateria, sem desligar a máquina. Depende do systemd e roda só em Linux com systemd.

### Uso

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.

As 4 skills de orquestração são os pontos de entrada: `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo` e `/bigtech:tab_pendencias`. Invoque por barra ou descreva a intenção em linguagem natural: o Claude escolhe a skill cuja descrição casa com o pedido e, em projeto ainda não classificado, o reforço de modo aponta os pedidos da constelação para o `/bigtech:bigtech`. As demais skills são atalhos de agent, um orquestrador de caso ou ferramentas operacionais, listadas em [Skills](#skills).

Digite sempre o prefixo `bigtech:`. Com ele, o comando chega à skill do plugin mesmo quando outra skill tem o mesmo nome; o nome sem o prefixo só funciona enquanto nenhuma outra skill ou comando o usa.

#### `/bigtech:bigtech`: montar a constelação

Camada de negócio e liderança (produto, marketing, vendas, jurídico, finanças, release). Invoca o Chief of Staff (Cósimo), que classifica o porte, recomenda a variante de pipeline (o usuário confirma) e devolve o mapa de ativação: quais C-levels e operacionais ligar, em quais das 12 fases.

```
/bigtech:bigtech ./meu-projeto
/bigtech:bigtech "app de agenda para clínicas" --porte early --dispatch
```

Use quando quiser "montar o time", "organizar como bigtech", "qual pipeline e quais agents", "quem lidera isso" ou "classificar o porte".

#### `/bigtech:proj_software`: motor de SDLC

Orquestra o ciclo de vida de software em 5 macrofases, alocando os agents de engenharia por nível, com gatekeeper anti-over-engineering e segurança transversal (shift-left). É para onde o `/bigtech:bigtech` delega a execução de engenharia.

```
/bigtech:proj_software
/bigtech:proj_software "API de pagamentos com idempotência"
```

Use quando começar um projeto novo de software: "vou criar um software", "novo sistema", "construir feature", "qual fluxo seguir".

#### `/bigtech:proj_jogo`: motor de desenvolvimento de jogo

O par do `/bigtech:proj_software` para jogos: toca o ciclo de desenvolvimento de jogo em 5 macrofases com o time de game, com gatekeeper anti-over-engineering calibrado de game jam a AAA.

```
/bigtech:proj_jogo
/bigtech:proj_jogo "jogo de plataforma 2D para uma game jam de 48 horas"
```

Use quando o projeto for um jogo: "vou fazer um jogo", "novo jogo", "game design", "game jam".

#### `/bigtech:tab_pendencias`: tabela de planejamento WSJF

Cria e mantém uma tabela de pendências ordenada de cima para baixo na sequência que minimiza retrabalho, combinando ordenação topológica (dependência) com WSJF (valor). A coluna "Onda" marca passos de igual valor que rodam em paralelo.

```
/bigtech:tab_pendencias --create
/bigtech:tab_pendencias --show
/bigtech:tab_pendencias --reorder
```

Use para planejar passos, ordenar backlog, ou perguntar "o que falta" e "em que ordem fazer".

**Manter a tabela fresca.** Marcar status é barato e manual; reordenar é caro e raro. Ao commitar trabalho que fecha ou avança um item do `TODO.md`, cite o ID do item na mensagem do commit e toque a coluna `Status` no mesmo commit (implementação entregue → `🔍 Pendente verificação`; `✅` quando o CI do ramo fecha verde). Reordenar, por outro lado, só roda pelo `--reorder`, e só quando um input de priorização muda e você decide reordenar. Veja [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

### Skills

Cada skill é invocada com o prefixo do plugin, como `/bigtech:<skill>`.

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
| `eficacia` | operacional | Mais trabalho útil pelo menor gasto: um timer do sistema, sem modelo, vigia as sessões, e a sessão de gerência ou de projeto enfileira a pergunta ao líder em vez de bloquear (o timer exige systemd --user). |

Atalhos como `/bigtech:dr-advogado` e `/bigtech:learning-designer` chamam o agent de mesmo nome, que também leva o prefixo `bigtech:` (por exemplo, o agent `bigtech:dr-advogado`).

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

Ao serem acionados, 63 dos 71 agents fazem um pre-flight da tabela de pendências (`TODO.md` na raiz): os 12 C-level a exigem como pré-condição no mapa de ativação; 51 operacionais sinalizam caso falte e seguem com a tarefa. Os outros 8 não fazem essa checagem: `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho`, `learning-designer`, `linux-diag`, `narrative-writer` e `revisor-textual`.

### Hooks

| Hook | Evento | Função |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write\|Edit) | Guard-rail de TDD: bloqueia código fora do ciclo red, green, refactor. Opt-in por projeto. |
| `tdd_runner.py` | PostToolUse (Write\|Edit) | Roda a suíte de testes após a edição e reporta o resultado ao ciclo TDD. |
| `bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto (docs-bootstrap), avisa se o `caveman` está ativo e avisa das dependências recomendadas que faltam. |
| `bigtech_porte_reminder.py` | SessionStart | Com o marcador `.bigtech-porte` na raiz do projeto, ancora o modo de operação bigtech no início da sessão e cita o porte registrado. Sem o marcador, em projeto de código (com arquivo de build ou manifesto, como `package.json` ou `pyproject.toml`), lembra de classificar o porte com `/bigtech:bigtech`. Fora disso, fica em silêncio. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Lembrete de tempo de sessão da tabela de pendências. No SessionStart, registra a hora de início da sessão; no UserPromptSubmit, uma vez por sessão, se o projeto tem o marcador `.bigtech-porte` e um `TODO.md` e a sessão já passou de 2 horas, lembra de marcar no `Status` os itens entregues e de reordenar pelo `/bigtech:tab_pendencias --reorder` só quando a prioridade mudar. O limite de tempo, ou o desligamento do lembrete, fica num `.tab-staleness.json` opcional na raiz do projeto. Só lembra, nunca bloqueia nem reordena. |
| `skills/tab_pendencias/tools/hooks/tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Sinais de frescor da tabela de pendências, da skill `tab_pendencias`. No SessionStart: repositório `git` sem `TODO.md` (sugere `/bigtech:tab_pendencias --create`), tabela com itens pendentes ou em andamento sem toque há vários commits ou dias (medido com `git` só para leitura), INBOX que precisa de triagem, itens acumulados à espera de verificação, decisões à sua espera que envelheceram e entradas inacabadas no journal de intake. No UserPromptSubmit: notas novas em `inbox/`, escritas por outra sessão. Os limiares ficam na seção `[signals]` de um `.tab_pendencias.ini` opcional ao lado do `TODO.md`. Só lembra, nunca bloqueia nem reordena. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo bigtech e roteia ativação por linguagem natural para `/bigtech:bigtech`. Escopado por marcador, anti-ruído. |
| `skills/eficacia/bin/hook_lider_dormindo.sh` | PreToolUse (AskUserQuestion) | Da skill `eficacia`. Enquanto a bandeira "líder dormindo" existir, nega a pergunta, grava-a com as opções numa fila local e manda o agente levar a dúvida técnica ao C-level do domínio ou trocar de trabalho. Sem a bandeira, sai em silêncio. |
| `skills/eficacia/bin/hook_permissao.sh` | PermissionRequest | Da skill `eficacia`. Enquanto a bandeira existir, nega o pedido de permissão, grava na mesma fila a ferramenta e um resumo (o comando ou o caminho do arquivo) e manda o agente trocar de trabalho. Sem a bandeira, sai em silêncio e o pedido chega a você como sempre. |
| `skills/eficacia/bin/hook_fim_turno.sh` | Stop | Da skill `eficacia`. Enquanto a bandeira existir, bloqueia uma vez o fim do turno e aponta um item do `TODO.md` que não dependa da resposta pendente ou, se a escolha for reversível, a opção recomendada num ramo próprio, sem merge; se nada sobrar, o agente pode parar. A tentativa seguinte de parar passa (`stop_hook_active`), sem laço. Sem a bandeira, sai em silêncio. |

O plugin declara 12 entradas de hook em 6 eventos (SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, Stop e PostToolUse), servidas por 10 scripts (7 em Python e 3 em bash); o smoke test confere cada uma. A bandeira "líder dormindo" é do seu usuário, não de um projeto: enquanto ela existir, os três hooks da `eficacia` agem em todas as sessões do Claude Code que você roda na máquina.

### Compatibilidade

**Plataforma.** Funciona em Linux, macOS e Windows (nativo ou WSL). Os hooks de governança e TDD são Python puro e rodam de forma cross-platform; o pré-requisito rígido no Claude Code é `python3` no PATH (veja [Claude Code (plugin nativo)](#claude-code-plugin-nativo), em especial a nota de Windows). Os três hooks da skill `eficacia` rodam com `bash` e também chamam `python3` e `flock`; o timer e a bandeira automática da skill exigem Linux com systemd (`systemctl --user` e `loginctl`). Quando a skill `tab_pendencias` planeja testes ou auditorias que precisam de ferramentas externas, cada ferramenta é oferecida para instalação com a sua confirmação, no comando adequado ao seu SO (apt/dnf/brew/winget/choco/scoop) e preferindo gerenciadores cross-platform (pip/uv, cargo, npm). Nada é instalado em silêncio.

**Feito para o Claude Code (Anthropic).** O caminho oficial de instalação é o formato de plugin/marketplace do Claude Code (hooks de ciclo de vida, skills, protocolo de subagents). Outros assistentes ou CLIs de código (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) não são suportados sem adaptação própria.

**Possível conflito com o plugin `caveman`.** O `caveman` comprime a comunicação e pode interferir no reforço de modo e no roteamento deste plugin. O hook de sessão avisa caso detecte os dois ativos ao mesmo tempo. Manter ou desativar o `caveman` é decisão sua; se mantiver os dois, garanta que os pedidos da constelação ainda cheguem ao `/bigtech:bigtech`.

### Modelo e esforço

Os agents vêm com `model: inherit`: cada um roda no modelo da thread que o despacha, então a escolha do modelo segue a sua sessão e as suas instruções. Se as suas instruções definirem como modelo e esforço são escolhidos, elas prevalecem sobre este plugin.

Para fixar um modelo em um agent, edite o campo `model` no cabeçalho de `agents/<slug>.md` (valores aceitos: `inherit`, `opus`, `sonnet`, `haiku`) e ajuste o nível de esforço com `/effort`.

### Documentação

**Wiki (didática, para iniciantes):** a [Wiki do projeto](https://github.com/petrinhu/bigtech_plugin/wiki) tem uma página por agente, hook e skill (os três hooks da `eficacia` estão explicados na página da skill), além de glossário, guia de instalação e de uso passo a passo.

Os manuais de governança acompanham o plugin em `docs/house/` e são injetados no contexto da sessão:

- `docs/house/ORG.md`: manual de governança da constelação (RACI, portes, roteamento de pipeline).
- `docs/house/pipeline_release_1.0.md`: pipeline de release em 12 fases, da ideia ao 1.0.
- `docs/house/lideranca_pipeline_release.md`: teoria de liderança C-level e a constelação nomeada.
- `docs/house/TOOLING.md`: catálogo de ferramentas livres (FOSS) por agent.
- `docs/house/`: contrato de qualidade, testes, agile, checklist de deploy e auditorias.
- `docs/principles/`: princípios de arquitetura, metodologia agile, anti-patterns e limites de hardware.

### Segurança

Os hooks executam código na sua máquina e o `tdd_runner` pode rodar o comando de teste declarado pelo projeto que você abrir (paridade de confiança com `make test`/`npm test`). Antes de usar com repositórios de terceiros, leia [SECURITY.md](./SECURITY.md): modelo de confiança, opt-in e como desativar.

Os três hooks da skill `eficacia` só agem enquanto a bandeira "líder dormindo" existir, e então em todas as sessões do seu usuário. O timer da skill só é instalado com o seu sim e continua instalado se você remover o plugin; por isso, rode antes o `vigia.sh remover` da skill. O [SECURITY.md](./SECURITY.md) traz o detalhe.

> **O modo TDD roda como shell um comando definido pelo projeto.** O hook PostToolUse `tdd_runner` é opt-in: só liga quando o projeto que você abrir contém o arquivo `.claude/tdd-guard.json`. Quando está ligado, o `fast_command`/`test_command` declarado nesse arquivo é executado como comando de shell após cada edição. Trate o `.claude/tdd-guard.json` como código confiável (a mesma confiança que você dá a um alvo `make test`/`npm test`) e não ative o modo TDD em repositório de terceiro não-confiável sem antes inspecionar esse comando. Prefira apontar o `test_command` para um executor isolado (container ou sandbox) com limite de processos; rode no host só onde as suas regras permitirem.

### Licença

Distribuído sob a licença [Apache-2.0](./LICENSE).
