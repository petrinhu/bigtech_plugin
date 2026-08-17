# bigtech

![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Type](https://img.shields.io/badge/type-Claude%20Code%20Plugin-blue)
![Grok](https://img.shields.io/badge/Grok-compatible-black)
![Status](https://img.shields.io/badge/status-stable-brightgreen)
![Language](https://img.shields.io/badge/lang-pt--br%20%2F%20en-lightgrey)
![Agents](https://img.shields.io/badge/agents-51-yellow)
![CI](https://img.shields.io/github/actions/workflow/status/petrinhu/bigtech_plugin/ci.yml?label=CI)
![Release](https://img.shields.io/github/v/release/petrinhu/bigtech_plugin?label=release)

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

> Structure any project like a digital-product company: a constellation of 51 agents (12 C-level + 39 operational), 4 skills, and governance and TDD hooks. Scales from **early** through **scale** to **bigtech** (deprecated alias: `solo` → `early`).

### Welcome, supreme leader

You, who install and operate this plugin, are the **supreme leader of this organization: the CEO of your bigtech.** The C-level constellation (Celso/CEO included) proposes and executes, but **the final word is always yours.**

High-stakes decisions (macro architecture, scope, stack, go/no-go, irreversible deploys, spend, any hard-to-reverse choice) are yours. When in doubt, or when more than one viable option exists, the agents do not decide on their own: they ask (the recommended option comes first). The team works for you.

### What it is

`bigtech` packages a complete product-and-engineering organization as a plugin for Claude Code:

- **51 agents.** 12 C-level (strategy, product, engineering, marketing, operations, security, data, AI, finance, revenue, legal, chief of staff) and 39 operational agents that do the work.
- **4 skills.** 3 orchestration skills plus 1 agent shortcut. `/bigtech` assembles the constellation, `/proj_software` runs the software development life cycle (SDLC), `/tab_pendencias` plans the backlog by value and dependency; `/visual-design-director` is a shortcut that delegates to the visual-design-director agent for rendered high-fidelity design.
- **Governance and TDD hooks.** Test guard-rail (red, green, refactor), project-size reassessment, operating-mode reinforcement, and bootstrap of the manuals into the session.

The non-negotiable principle: **the process adapts to the size of the project, never the other way around.** A 200-line CLI does not summon the whole team. The Chief of Staff classifies the size and turns on only what is needed, preventing over-engineering.

**Canonical project sizes (porte):** `early` | `scale` | `bigtech`. Headcount is an auxiliary note, not a size value. Legacy `--porte solo` and marker `porte=solo` normalize to `early` (floor is always at least early).

### Installation

Install on **Claude Code** (native plugin) or **Grok** (compatible materialization). The two hosts do not share a plugin system.

#### Claude Code (native plugin)

**Prerequisite:** `python3` on your PATH (`python3 --version`). Hooks spawn as `python3`.

- **Linux:** usually present; else `sudo apt install python3` (or `dnf` / `pacman` / `zypper`).
- **macOS:** `xcode-select --install` or `brew install python`.
- **Windows (native):** Microsoft Store Python registers the `python3` alias (recommended). The python.org installer may only provide `python`/`py`; use the plugin's `bin/python3.cmd` shim on PATH, or **WSL**.

Optional companions (install via Claude Code, same on every OS):

```
/plugin install superpowers@claude-plugins-official
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

`superpowers` pairs well with the constellation; `frontend-design` (in `example-skills`) helps UI agents avoid generic templates. `playwright` is also useful for browser automation.

Install `bigtech`:

```
/plugin marketplace add https://github.com/petrinhu/bigtech_plugin
# or a local clone:
# /plugin marketplace add /path/to/bigtech_plugin
/plugin install bigtech@petrinhu
```

`bigtech@petrinhu` disambiguates the marketplace; if only this marketplace is registered, `/plugin install bigtech` also resolves.

**After install:** restart the Claude Code session so `bigtech_session_init` can inject manuals and mode reinforcement.

**Name conflicts.** If global agents, skills, or hooks in `~/.claude/` already use the same names as this plugin, do **not** install over them. Prefer an isolated profile (`CLAUDE_CONFIG_DIR=...`) or retire only the colliding **bigtech core** names. Do **not** delete personal or unrelated agents (`dr-*`, `game-*`, etc.). Detail: [AGENTS.md](AGENTS.md) and the [Installation wiki page](https://github.com/petrinhu/bigtech_plugin/wiki/Installation).

If you are an AI agent installing on behalf of a user, follow [AGENTS.md](AGENTS.md).

#### Grok (compatible; no Claude plugin system)

Grok does **not** load Claude Code marketplaces. **Grok-compatible** means you materialize this repo's agents, skills, and hooks on the Grok host. Example on Linux (paths are illustrative; use your clone path):

```bash
# 1) Clone (or use an existing checkout)
git clone https://github.com/petrinhu/bigtech_plugin.git /path/to/bigtech_plugin
CLONE=/path/to/bigtech_plugin

# 2) Agents: copy the 51 product agents; keep Grok-only agents that are not in the plugin
mkdir -p ~/.grok/agents
cp "$CLONE"/agents/*.md ~/.grok/agents/

# 3) Skills: symlink product skills into the Grok skills dir
mkdir -p ~/.grok/skills
ln -sfn "$CLONE"/skills/bigtech ~/.grok/skills/bigtech
ln -sfn "$CLONE"/skills/proj_software ~/.grok/skills/proj_software
ln -sfn "$CLONE"/skills/visual-design-director ~/.grok/skills/visual-design-director
# tab_pendencias: prefer the standalone product repo, not a fork of the copy inside this plugin
# ln -sfn /path/to/tab_pendencias ~/.grok/skills/tab_pendencias

# 4) Hooks: copy relevant Python scripts (prefer real files, not symlinks into another host)
mkdir -p ~/.grok/hooks/scripts
cp "$CLONE"/hooks/bigtech_*.py "$CLONE"/hooks/tdd_*.py \
   "$CLONE"/hooks/tab_pendencias_reminder.py \
   ~/.grok/hooks/scripts/
# Register events if your Grok host requires it. If Claude compat is on with
# hooks=false, bigtech/TDD hooks will not double-fire via that path.

# 5) Optional: ensure skills are discoverable
# In ~/.grok/config.toml, include ~/.grok/skills under [skills].paths

# 6) Restart Grok (/new or process restart) so agents and skills reload
```

Summary: **Claude** = install the marketplace plugin. **Grok** = copy/symlink agents, skills, and hooks from this repository onto the host. Runtime parity depends on the host; hooks and the subagent protocol are not identical across platforms.

### Usage

The 3 orchestration skills are the entry points. Invoke them with a slash or describe your intent in natural language; the mode reinforcement routes the request to the right skill. The 4th skill, `/visual-design-director`, is an agent shortcut for design work.

#### `/bigtech`: assemble the constellation

Business and leadership layer (product, marketing, sales, legal, finance, release). Invokes the Chief of Staff (Cósimo), who classifies the size, picks the pipeline variant, and returns the activation map: which C-levels and operational agents to turn on, and in which of the 12 phases.

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

#### `/tab_pendencias`: WSJF planning table

Creates and maintains a backlog table ordered top to bottom in the sequence that minimizes rework, combining topological ordering (dependency) with WSJF (value). The "Wave" column marks steps of equal value that run in parallel.

```
/tab_pendencias --create
/tab_pendencias --show
/tab_pendencias --reorder
```

Use it to plan steps, order the backlog, or ask "what's left" and "in what order to do it".

**Keeping the table fresh.** Marking a status is cheap and manual; reordering is expensive and rare. When you commit work that closes or advances a `TODO.md` item, cite the item ID in the commit message and touch the `Status` column in the same commit (delivered implementation → `🔍 Pendente verificação`; `✅` only after the test/audit wave). Reordering, by contrast, runs only through `--reorder`, and only when a prioritization input changes. See [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

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

#### Operational (39)

**Engineering (14):** `software-architect`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `devops-sre`, `performance-engineer`, `network-engineer`, `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.

**Data and AI (4):** `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.

**Product, UX, and Design (8):** `product-manager`, `business-analyst`, `ux-researcher`, `ux-ui-designer`, `visual-design-director`, `ux-writer`, `accessibility-specialist`, `art-director`.

**Management and People (2):** `engineering-manager`, `scrum-master`.

**Marketing, Growth, and Revenue (6):** `content-seo`, `pr-comms`, `growth-engineer`, `community-manager`, `customer-success`, `revenue-ops`.

**Support, Docs, Legal, and i18n (5):** `support-engineer`, `technical-writer`, `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`.

When invoked, every agent runs a pre-flight check on the backlog table (`TODO.md` at the root): the C-level agents require it as a precondition in the activation map; the operational agents flag it if missing and proceed with the task.

### Hooks

| Hook | Event | Function |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write/Edit) | TDD guard-rail: blocks code outside the red, green, refactor cycle. Opt-in per project. |
| `tdd_runner.py` | PostToolUse (Write/Edit) | Runs the test suite after the edit and reports the result to the TDD cycle. |
| `bigtech_session_init.py` | SessionStart | Injects the manuals' path into the context (docs-bootstrap), warns if `caveman` is active, and suggests the missing dependencies. |
| `bigtech_porte_reminder.py` | SessionStart | Reassesses the project size (scales up or down); only fires on a code project not yet classified. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Backlog-table staleness detector. Reminds you to generate the `TODO.md` via `/tab_pendencias` when the project is classified (`.bigtech-porte` marker) but has no table; once the table exists, measures its staleness via `git` (commits and days since the last touch to `TODO.md`) and, after a long session, nudges you to review and reorder it. Thresholds are tunable in an optional `.tab-staleness.json` at the project root. It only reminds, never blocks or reorders. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reinforces bigtech mode (anti-drift) and routes natural-language activation to `/bigtech`. Marker-scoped, noise-resistant. |

### Compatibility

**Platform.** Works on Linux, macOS, and Windows (native or WSL). The hooks are pure Python and run cross-platform; the hard prerequisite on Claude Code is `python3` on the PATH (see [Claude Code (native plugin)](#claude-code-native-plugin), notably the Windows note). When the `tab_pendencias` skill plans tests or audits that need external tools, each tool is offered for installation with your confirmation, using the command that fits your OS (apt/dnf/brew/winget/choco/scoop) and preferring cross-platform managers (pip/uv, cargo, npm). Nothing is installed silently.

**Built for Claude Code (Anthropic).** The official install path is the Claude Code plugin/marketplace format (life-cycle hooks, skills, subagent protocol). **Grok-compatible:** the same agents, skills, and hook scripts can be materialized on a Grok host (see [Grok (compatible)](#grok-compatible-no-claude-plugin-system)); that path is operational but not a second plugin system. Other assistants or code CLIs (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) are not supported without their own adaptation.

**Incompatible with the `caveman` plugin.** `caveman` compresses communication and conflicts with this plugin's mode reinforcement. Disable `caveman` before using `bigtech`; the session hook warns you if it detects both active at the same time.

**Suggested dependencies:** `playwright` and `superpowers`. They are not required, but they enable the full experience (browser automation and advanced flows). Install them to get the most out of the plugin; the session hook suggests installing them when they are absent.

### Orchestration model

By default, the agents use the **`opus`** model (always the latest Opus: the `model` field does not pin a version), and the **orchestration** (the Chief of Staff and the C-level assembling and coordinating the constellation) runs at **maximum effort**, for the deepest reasoning on the decisions that cut across the team. This is the recommended default.

You can change it manually: edit the `model` field in the header of any agent in `agents/<slug>.md` (accepted values: `opus`, `sonnet`, `haiku`) and adjust your session's effort level with `/effort`.

### Documentation

**Wiki (beginner-friendly, didactic):** the [project Wiki](https://github.com/petrinhu/bigtech_plugin/wiki) has one page per agent, hook, and skill, plus a glossary, an installation guide, and a step-by-step usage guide.

The governance manuals ship with the plugin in `docs/` and are injected into the session context:

- `docs/ORG.md`: governance manual for the constellation (RACI, sizes, pipeline routing).
- `docs/pipeline_release_1.0.md`: 12-phase release pipeline, from idea to 1.0.
- `docs/lideranca_pipeline_release.md`: C-level leadership theory and the named constellation.
- `docs/TOOLING.md`: catalog of free/open-source (FOSS) tools per agent.
- `docs/manuals/`: quality contract, tests, agile, deploy checklist, and audits.
- `docs/principles/`: architecture principles, agile methodology, anti-patterns, and hardware limits.

### Security

The hooks run code on your machine, and `tdd_runner` may run the test command declared by the project you open (trust parity with `make test`/`npm test`). Before using it with third-party repositories, read [SECURITY.md](./SECURITY.md): trust model, opt-in, and how to disable.

> **TDD mode runs a project-defined command as a shell.** The PostToolUse hook `tdd_runner` is opt-in: it only activates when the project you open contains a `.claude/tdd-guard.json` file. When it is active, the `fast_command`/`test_command` declared in that file is executed as a shell command after each edit. Treat `.claude/tdd-guard.json` as trusted code (the same trust you give to a `make test`/`npm test` target), and do not turn on TDD mode in an untrusted third-party repository without first inspecting that command.

### License

Distributed under the [Apache-2.0](./LICENSE) license.

---

## Português

> Estruture qualquer projeto como uma empresa de produto digital: uma constelação de 51 agents (12 C-level + 39 operacionais), 4 skills e hooks de governança e TDD. Dimensionável de **early** passando por **scale** até **bigtech** (alias depreciado: `solo` → `early`).

### Bem-vindo, líder supremo

Você, que instala e opera este plugin, é o **líder supremo desta organização: o CEO da sua bigtech.** A constelação C-level (Celso/CEO inclusive) propõe e executa, mas **a palavra final é sempre sua.**

Decisões de altíssimo valor (arquitetura macro, escopo, stack, go/no-go, deploy irreversível, gasto, qualquer escolha difícil de reverter) são suas. Diante de dúvida ou de mais de uma opção viável, os agents não decidem sozinhos: eles perguntam (a opção recomendada vem primeiro). O time trabalha para você.

### O que é

`bigtech` empacota uma organização completa de produto e engenharia em forma de plugin para o Claude Code:

- **51 agents.** 12 C-level (estratégia, produto, engenharia, marketing, operações, segurança, dados, IA, finanças, receita, jurídico, chief of staff) e 39 operacionais que executam o trabalho.
- **4 skills.** 3 de orquestração mais 1 atalho de agent. `/bigtech` monta a constelação, `/proj_software` toca o ciclo de vida de software (SDLC), `/tab_pendencias` planeja o backlog por valor e dependência; `/visual-design-director` é um atalho que delega ao agent visual-design-director para design de alta fidelidade renderizado.
- **Hooks de governança e TDD.** Guard-rail de testes (red, green, refactor), reavaliação de porte do projeto, reforço do modo de operação e bootstrap dos manuais na sessão.

O princípio inegociável: **o processo se adapta ao porte do projeto, nunca o contrário.** Um CLI de 200 linhas não chama o time inteiro. O Chief of Staff classifica o porte e liga só o necessário, prevenindo over-engineering.

**Portes canônicos:** `early` | `scale` | `bigtech`. Headcount é nota auxiliar, não valor de porte. Legado `--porte solo` e marcador `porte=solo` normalizam para `early` (piso sempre early).

### Instalação

Instale no **Claude Code** (plugin nativo) ou no **Grok** (materialização compatível). Os dois hosts não compartilham o mesmo sistema de plugins.

#### Claude Code (plugin nativo)

**Pré-requisito:** `python3` no PATH (`python3 --version`). Os hooks são invocados como `python3`.

- **Linux:** em geral já presente; senão `sudo apt install python3` (ou `dnf` / `pacman` / `zypper`).
- **macOS:** `xcode-select --install` ou `brew install python`.
- **Windows (nativo):** o Python da Microsoft Store registra o alias `python3` (recomendado). O instalador do python.org pode oferecer só `python`/`py`; use o shim `bin/python3.cmd` do plugin no PATH, ou **WSL**.

Companions opcionais (instalados pelo próprio Claude Code, iguais em todo SO):

```
/plugin install superpowers@claude-plugins-official
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

`superpowers` combina bem com a constelação; `frontend-design` (no `example-skills`) ajuda os agents de UI a evitar templates genéricos. `playwright` também é útil para automação de navegador.

Instale o `bigtech`:

```
/plugin marketplace add https://github.com/petrinhu/bigtech_plugin
# ou clone local:
# /plugin marketplace add /path/to/bigtech_plugin
/plugin install bigtech@petrinhu
```

`bigtech@petrinhu` desambigua o marketplace; se só este marketplace estiver registrado, `/plugin install bigtech` também resolve.

**Depois de instalar:** reinicie a sessão do Claude Code para o `bigtech_session_init` injetar os manuais e o reforço de modo.

**Conflito de nomes.** Se já houver agents, skills ou hooks globais em `~/.claude/` com os mesmos nomes deste plugin, **não** instale por cima. Prefira um perfil isolado (`CLAUDE_CONFIG_DIR=...`) ou aposente só os nomes do **núcleo bigtech** que colidem. **Não** apague agents pessoais ou de outros domínios (`dr-*`, `game-*`, etc.). Detalhe: [AGENTS.md](AGENTS.md) e a [página de Instalação da wiki](https://github.com/petrinhu/bigtech_plugin/wiki/Instalacao).

Se você é um agente de IA instalando a pedido de um usuário, siga [AGENTS.md](AGENTS.md).

#### Grok (compatível; sem o plugin system do Claude)

O Grok **não** carrega marketplaces do Claude Code. **Grok-compatible** significa materializar os agents, skills e hooks deste repositório no host Grok. Exemplo em Linux (caminhos ilustrativos; use o path do seu clone):

```bash
# 1) Clone (ou use um checkout já existente)
git clone https://github.com/petrinhu/bigtech_plugin.git /path/to/bigtech_plugin
CLONE=/path/to/bigtech_plugin

# 2) Agents: copie os 51 agents do produto; preserve agents só-Grok que não estão no plugin
mkdir -p ~/.grok/agents
cp "$CLONE"/agents/*.md ~/.grok/agents/

# 3) Skills: symlink das skills do produto no diretório de skills do Grok
mkdir -p ~/.grok/skills
ln -sfn "$CLONE"/skills/bigtech ~/.grok/skills/bigtech
ln -sfn "$CLONE"/skills/proj_software ~/.grok/skills/proj_software
ln -sfn "$CLONE"/skills/visual-design-director ~/.grok/skills/visual-design-director
# tab_pendencias: prefira o repositório standalone, não um fork da cópia embutida neste plugin
# ln -sfn /path/to/tab_pendencias ~/.grok/skills/tab_pendencias

# 4) Hooks: copie os scripts Python relevantes (prefira arquivos reais, não symlink para outro host)
mkdir -p ~/.grok/hooks/scripts
cp "$CLONE"/hooks/bigtech_*.py "$CLONE"/hooks/tdd_*.py \
   "$CLONE"/hooks/tab_pendencias_reminder.py \
   ~/.grok/hooks/scripts/
# Registre os eventos se o host Grok exigir. Se o compat Claude estiver com
# hooks=false, os hooks bigtech/TDD não disparam em dobro por esse caminho.

# 5) Opcional: garantir descoberta das skills
# Em ~/.grok/config.toml, inclua ~/.grok/skills em [skills].paths

# 6) Reinicie o Grok (/new ou restart do processo) para recarregar agents e skills
```

Resumo: **Claude** = instalar o plugin do marketplace. **Grok** = copiar/symlink de agents, skills e hooks deste repositório no host. A paridade de runtime depende do host; hooks e o protocolo de subagents não são idênticos entre plataformas.

### Uso

As 3 skills de orquestração são os pontos de entrada. Invoque por barra ou descreva a intenção em linguagem natural; o reforço de modo roteia o pedido para a skill certa. A 4ª skill, `/visual-design-director`, é um atalho de agent para trabalho de design.

#### `/bigtech`: montar a constelação

Camada de negócio e liderança (produto, marketing, vendas, jurídico, finanças, release). Invoca o Chief of Staff (Cósimo), que classifica o porte, escolhe a variante de pipeline e devolve o mapa de ativação: quais C-levels e operacionais ligar, em quais das 12 fases.

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

#### `/tab_pendencias`: tabela de planejamento WSJF

Cria e mantém uma tabela de pendências ordenada de cima para baixo na sequência que minimiza retrabalho, combinando ordenação topológica (dependência) com WSJF (valor). A coluna "Onda" marca passos de igual valor que rodam em paralelo.

```
/tab_pendencias --create
/tab_pendencias --show
/tab_pendencias --reorder
```

Use para planejar passos, ordenar backlog, ou perguntar "o que falta" e "em que ordem fazer".

**Manter a tabela fresca.** Marcar status é barato e manual; reordenar é caro e raro. Ao commitar trabalho que fecha ou avança um item do `TODO.md`, cite o ID do item na mensagem do commit e toque a coluna `Status` no mesmo commit (implementação entregue → `🔍 Pendente verificação`; `✅` só após a onda de teste/auditoria). Reordenar, por outro lado, só roda pelo `--reorder`, e só quando um input de priorização muda. Veja [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md).

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

#### Operacionais (39)

**Engenharia (14):** `software-architect`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `devops-sre`, `performance-engineer`, `network-engineer`, `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.

**Dados e IA (4):** `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.

**Produto, UX e Design (8):** `product-manager`, `business-analyst`, `ux-researcher`, `ux-ui-designer`, `visual-design-director`, `ux-writer`, `accessibility-specialist`, `art-director`.

**Gestão e Pessoas (2):** `engineering-manager`, `scrum-master`.

**Marketing, Crescimento e Receita (6):** `content-seo`, `pr-comms`, `growth-engineer`, `community-manager`, `customer-success`, `revenue-ops`.

**Suporte, Docs, Legal e i18n (5):** `support-engineer`, `technical-writer`, `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`.

Ao serem acionados, todos os agents fazem um pre-flight da tabela de pendências (`TODO.md` na raiz): os C-level a exigem como pré-condição no mapa de ativação; os operacionais sinalizam caso falte e seguem com a tarefa.

### Hooks

| Hook | Evento | Função |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write/Edit) | Guard-rail de TDD: bloqueia código fora do ciclo red, green, refactor. Opt-in por projeto. |
| `tdd_runner.py` | PostToolUse (Write/Edit) | Roda a suíte de testes após a edição e reporta o resultado ao ciclo TDD. |
| `bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto (docs-bootstrap), avisa se o `caveman` está ativo e sugere as dependências ausentes. |
| `bigtech_porte_reminder.py` | SessionStart | Reavalia o porte do projeto (escala para cima ou para baixo); só dispara em projeto de código ainda não classificado. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Detector de defasagem da tabela de pendências. Lembra de gerar o `TODO.md` via `/tab_pendencias` quando o projeto já foi classificado (marcador `.bigtech-porte`) mas ainda não tem a tabela; com a tabela presente, mede a defasagem dela via `git` (commits e dias desde o último toque no `TODO.md`) e, após uma sessão longa, dá um nudge para revisar e reordenar. Os limiares são ajustáveis num `.tab-staleness.json` opcional na raiz do projeto. Só lembra, nunca bloqueia nem reordena. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo bigtech (anti-drift) e roteia ativação por linguagem natural para `/bigtech`. Escopado por marcador, anti-ruído. |

### Compatibilidade

**Plataforma.** Funciona em Linux, macOS e Windows (nativo ou WSL). Os hooks são Python puro e rodam de forma cross-platform; o pré-requisito rígido no Claude Code é `python3` no PATH (veja [Claude Code (plugin nativo)](#claude-code-plugin-nativo), em especial a nota de Windows). Quando a skill `tab_pendencias` planeja testes ou auditorias que precisam de ferramentas externas, cada ferramenta é oferecida para instalação com a sua confirmação, no comando adequado ao seu SO (apt/dnf/brew/winget/choco/scoop) e preferindo gerenciadores cross-platform (pip/uv, cargo, npm). Nada é instalado em silêncio.

**Feito para o Claude Code (Anthropic).** O caminho oficial de instalação é o formato de plugin/marketplace do Claude Code (hooks de ciclo de vida, skills, protocolo de subagents). **Grok-compatible:** os mesmos agents, skills e scripts de hook podem ser materializados num host Grok (veja [Grok (compatível)](#grok-compatível-sem-o-plugin-system-do-claude)); esse caminho é operacional, mas não é um segundo sistema de plugins. Outros assistentes ou CLIs de código (Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, Aider, etc.) não são suportados sem adaptação própria.

**Incompatível com o plugin `caveman`.** O `caveman` comprime a comunicação e conflita com o reforço de modo deste plugin. Desative o `caveman` antes de usar o `bigtech`; o hook de sessão avisa caso detecte os dois ativos ao mesmo tempo.

**Dependências sugeridas:** `playwright` e `superpowers`. Não são obrigatórias, mas habilitam a experiência completa (automação de navegador e fluxos avançados). Instale-as para tirar o máximo do plugin; o hook de sessão sugere a instalação quando estão ausentes.

### Modelo de orquestração

Por padrão, os agents usam o modelo **`opus`** (sempre o Opus mais recente: o campo `model` não fixa versão), e a **orquestração** (o Chief of Staff e os C-level montando e coordenando a constelação) roda em **effort máximo**, para o raciocínio mais profundo nas decisões que cruzam o time. Esse é o default recomendado.

Você pode mudar manualmente: edite o campo `model` no cabeçalho de qualquer agent em `agents/<slug>.md` (valores aceitos: `opus`, `sonnet`, `haiku`) e ajuste o nível de esforço da sua sessão com `/effort`.

### Documentação

**Wiki (didática, para iniciantes):** a [Wiki do projeto](https://github.com/petrinhu/bigtech_plugin/wiki) tem uma página por agente, hook e skill, além de glossário, guia de instalação e de uso passo a passo.

Os manuais de governança acompanham o plugin em `docs/` e são injetados no contexto da sessão:

- `docs/ORG.md`: manual de governança da constelação (RACI, portes, roteamento de pipeline).
- `docs/pipeline_release_1.0.md`: pipeline de release em 12 fases, da ideia ao 1.0.
- `docs/lideranca_pipeline_release.md`: teoria de liderança C-level e a constelação nomeada.
- `docs/TOOLING.md`: catálogo de ferramentas livres (FOSS) por agent.
- `docs/manuals/`: contrato de qualidade, testes, agile, checklist de deploy e auditorias.
- `docs/principles/`: princípios de arquitetura, metodologia agile, anti-patterns e limites de hardware.

### Segurança

Os hooks executam código na sua máquina e o `tdd_runner` pode rodar o comando de teste declarado pelo projeto que você abrir (paridade de confiança com `make test`/`npm test`). Antes de usar com repositórios de terceiros, leia [SECURITY.md](./SECURITY.md): modelo de confiança, opt-in e como desativar.

> **O modo TDD roda como shell um comando definido pelo projeto.** O hook PostToolUse `tdd_runner` é opt-in: só liga quando o projeto que você abrir contém o arquivo `.claude/tdd-guard.json`. Quando está ligado, o `fast_command`/`test_command` declarado nesse arquivo é executado como comando de shell após cada edição. Trate o `.claude/tdd-guard.json` como código confiável (a mesma confiança que você dá a um alvo `make test`/`npm test`) e não ative o modo TDD em repositório de terceiro não-confiável sem antes inspecionar esse comando.

### Licença

Distribuído sob a licença [Apache-2.0](./LICENSE).
