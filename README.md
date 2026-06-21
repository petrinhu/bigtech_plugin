# bigtech

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-4C8EDA?style=for-the-badge)](./LICENSE)

[![Release](https://img.shields.io/gitea/v/release/petrinhu/bigtech_plugin?gitea_url=https://codeberg.org&style=for-the-badge&color=2EA043&label=release)](https://codeberg.org/petrinhu/bigtech_plugin/releases)
[![CI status (Forgejo Actions)](https://codeberg.org/petrinhu/bigtech_plugin/actions/workflows/ci.yml/badge.svg)](https://codeberg.org/petrinhu/bigtech_plugin/actions)

[![Agents](https://img.shields.io/badge/agents-51-4F4F4F?style=for-the-badge)](#what-it-is)
[![Skills](https://img.shields.io/badge/skills-4-4F4F4F?style=for-the-badge)](#what-it-is)
[![Hooks](https://img.shields.io/badge/hooks-6-4F4F4F?style=for-the-badge)](#hooks)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-4F4F4F?style=for-the-badge)](https://codeberg.org/petrinhu/bigtech_plugin/pulls)

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

> Structure any project like a digital-product company: a constellation of 51 agents (12 C-level + 39 operational), 4 skills, and governance and TDD hooks. Scales from solo founder to bigtech.

### Welcome, supreme leader

You, who install and operate this plugin, are the **supreme leader of this organization: the CEO of your bigtech.** The C-level constellation (Celso/CEO included) proposes and executes, but **the final word is always yours.**

High-stakes decisions (macro architecture, scope, stack, go/no-go, irreversible deploys, spend, any hard-to-reverse choice) are yours. When in doubt, or when more than one viable option exists, the agents do not decide on their own: they ask (the recommended option comes first). The team works for you.

### What it is

`bigtech` packages a complete product-and-engineering organization as a plugin for Claude Code:

- **51 agents.** 12 C-level (strategy, product, engineering, marketing, operations, security, data, AI, finance, revenue, legal, chief of staff) and 39 operational agents that do the work.
- **4 skills.** 3 orchestration skills plus 1 agent shortcut. `/bigtech` assembles the constellation, `/proj_software` runs the software development life cycle (SDLC), `/tab_pendencias` plans the backlog by value and dependency; `/visual-design-director` is a shortcut that delegates to the visual-design-director agent for rendered high-fidelity design.
- **Governance and TDD hooks.** Test guard-rail (red, green, refactor), project-size reassessment, operating-mode reinforcement, and bootstrap of the manuals into the session.

The non-negotiable principle: **the process adapts to the size of the project, never the other way around.** A 200-line CLI does not summon the whole team. The Chief of Staff classifies the size and turns on only what is needed, preventing over-engineering.

### Installation

**Recommended companion: `superpowers`.** `bigtech` pairs very well with [`superpowers`](https://claude.com/plugins/superpowers), Anthropic's suite of engineering and process skills (brainstorming, writing-plans, TDD, debugging, and more). Installing it **before** `bigtech` is recommended for the best experience: the agents and skills lean on those flows when they are available.

```
/plugin install superpowers@claude-plugins-official
```

**Recommended skill for UI work: `frontend-design`.** When the constellation builds or reshapes interfaces (the `ux-ui-designer`, `visual-design-director`, `art-director`, `frontend-engineer`, and `accessibility-specialist` agents), Anthropic's [`frontend-design`](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) skill helps produce distinctive, intentional visual design instead of templated defaults. It ships in the `example-skills` plugin of the `anthropic-agent-skills` marketplace:

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

Then install `bigtech` itself:

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech@petrinhu
```

The first command registers the `petrinhu` marketplace. The second installs the `bigtech` plugin from it. The `bigtech@petrinhu` form disambiguates the source; if the environment has only this marketplace, `/plugin install bigtech` also resolves.

#### Prerequisites per OS

The only hard prerequisite is **`python3` resolvable on your PATH** (the plugin's hooks are spawned as `python3`). Check it with `python3 --version`:

- **Linux:** almost always already present. If missing: `sudo apt install python3` (or `dnf`/`pacman`/`zypper`).
- **macOS:** install via `xcode-select --install` or `brew install python`.
- **Windows (native):** the **Microsoft Store** Python registers the `python3` alias automatically (recommended). The python.org installer gives `python`/`py` but not `python3`; if `python3 --version` fails, the plugin ships a `bin/python3.cmd` shim you can place on your PATH, or just use **WSL**.

The companion dependencies (`superpowers`, `playwright`, `frontend-design`) are installed through Claude Code itself, the same on every OS. The agents' runtime tools are handled automatically (each one is offered or installed per your OS when a task needs it; nothing runs silently). Step-by-step per OS, including verification, in the [Installation wiki page](https://codeberg.org/petrinhu/bigtech_plugin/wiki/Installation).

If you are an AI agent installing this plugin on behalf of a user, see [AGENTS.md](AGENTS.md).

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

**Platform.** Works on Linux, macOS, and Windows (native or WSL). The hooks are pure Python and run cross-platform; the one prerequisite is `python3` resolvable on the PATH (see [Prerequisites per OS](#prerequisites-per-os), notably the Windows note). When the `tab_pendencias` skill plans tests or audits that need external tools, each tool is offered for installation with your confirmation, using the command that fits your OS (apt/dnf/brew/winget/choco/scoop) and preferring cross-platform managers (pip/uv, cargo, npm). Nothing is installed silently.

**Built for Claude Code (Anthropic).** The plugin uses Claude Code's own features: life-cycle hooks, skills, the subagent protocol, and the plugin/marketplace format. There is no guarantee it works on other AI assistants or code CLIs (for example, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, or Aider); porting to other platforms may require adaptation and is not officially supported.

**Incompatible with the `caveman` plugin.** `caveman` compresses communication and conflicts with this plugin's mode reinforcement. Disable `caveman` before using `bigtech`; the session hook warns you if it detects both active at the same time.

**Suggested dependencies:** `playwright` and `superpowers`. They are not required, but they enable the full experience (browser automation and advanced flows). Install them to get the most out of the plugin; the session hook suggests installing them when they are absent.

### Orchestration model

By default, the agents use the **`opus`** model (always the latest Opus: the `model` field does not pin a version), and the **orchestration** (the Chief of Staff and the C-level assembling and coordinating the constellation) runs at **maximum effort**, for the deepest reasoning on the decisions that cut across the team. This is the recommended default.

You can change it manually: edit the `model` field in the header of any agent in `agents/<slug>.md` (accepted values: `opus`, `sonnet`, `haiku`) and adjust your session's effort level with `/effort`.

### Documentation

**Wiki (beginner-friendly, didactic):** the [project Wiki](https://codeberg.org/petrinhu/bigtech_plugin/wiki) has one page per agent, hook, and skill, plus a glossary, an installation guide, and a step-by-step usage guide.

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

> Estruture qualquer projeto como uma empresa de produto digital: uma constelação de 51 agents (12 C-level + 39 operacionais), 4 skills e hooks de governança e TDD. Dimensionável do solo founder à bigtech.

### Bem-vindo, líder supremo

Você, que instala e opera este plugin, é o **líder supremo desta organização: o CEO da sua bigtech.** A constelação C-level (Celso/CEO inclusive) propõe e executa, mas **a palavra final é sempre sua.**

Decisões de altíssimo valor (arquitetura macro, escopo, stack, go/no-go, deploy irreversível, gasto, qualquer escolha difícil de reverter) são suas. Diante de dúvida ou de mais de uma opção viável, os agents não decidem sozinhos: eles perguntam (a opção recomendada vem primeiro). O time trabalha para você.

### O que é

`bigtech` empacota uma organização completa de produto e engenharia em forma de plugin para o Claude Code:

- **51 agents.** 12 C-level (estratégia, produto, engenharia, marketing, operações, segurança, dados, IA, finanças, receita, jurídico, chief of staff) e 39 operacionais que executam o trabalho.
- **4 skills.** 3 de orquestração mais 1 atalho de agent. `/bigtech` monta a constelação, `/proj_software` toca o ciclo de vida de software (SDLC), `/tab_pendencias` planeja o backlog por valor e dependência; `/visual-design-director` é um atalho que delega ao agent visual-design-director para design de alta fidelidade renderizado.
- **Hooks de governança e TDD.** Guard-rail de testes (red, green, refactor), reavaliação de porte do projeto, reforço do modo de operação e bootstrap dos manuais na sessão.

O princípio inegociável: **o processo se adapta ao porte do projeto, nunca o contrário.** Um CLI de 200 linhas não chama o time inteiro. O Chief of Staff classifica o porte e liga só o necessário, prevenindo over-engineering.

### Instalação

**Companion recomendado: `superpowers`.** O `bigtech` integra-se muito bem com o [`superpowers`](https://claude.com/plugins/superpowers), a suíte de skills de engenharia e processo da Anthropic (brainstorming, writing-plans, TDD, debugging e outras). É recomendável instalá-lo **antes** do `bigtech` para a melhor experiência: os agents e as skills se apoiam nesses fluxos quando estão disponíveis.

```
/plugin install superpowers@claude-plugins-official
```

**Skill recomendada para trabalho de UI: `frontend-design`.** Quando a constelação constrói ou reformula interfaces (os agents `ux-ui-designer`, `visual-design-director`, `art-director`, `frontend-engineer` e `accessibility-specialist`), a skill [`frontend-design`](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) da Anthropic ajuda a produzir um design visual distintivo e intencional, em vez de padrões genéricos de template. Ela é distribuída no plugin `example-skills` do marketplace `anthropic-agent-skills`:

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

Em seguida, instale o `bigtech`:

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech@petrinhu
```

O primeiro comando registra o marketplace `petrinhu`. O segundo instala o plugin `bigtech` a partir dele. A forma `bigtech@petrinhu` desambigua a origem; se o ambiente só tiver esse marketplace, `/plugin install bigtech` também resolve.

#### Pré-requisitos por SO

O único pré-requisito rígido é **`python3` resolvível no seu PATH** (os hooks do plugin são chamados como `python3`). Confira com `python3 --version`:

- **Linux:** quase sempre já presente. Se faltar: `sudo apt install python3` (ou `dnf`/`pacman`/`zypper`).
- **macOS:** instale via `xcode-select --install` ou `brew install python`.
- **Windows (nativo):** o Python da **Microsoft Store** registra o alias `python3` automaticamente (recomendado). O instalador do python.org dá `python`/`py`, mas não o `python3`; se `python3 --version` falhar, o plugin traz um shim `bin/python3.cmd` que você pode colocar no PATH, ou então use **WSL**.

As dependências companion (`superpowers`, `playwright`, `frontend-design`) são instaladas pelo próprio Claude Code, iguais em todo SO. As ferramentas de runtime dos agents são tratadas automaticamente (cada uma é oferecida ou instalada conforme o seu SO quando uma tarefa precisa; nada roda em silêncio). Passo a passo por SO, com verificação, na [página de Instalação da wiki](https://codeberg.org/petrinhu/bigtech_plugin/wiki/Instalacao).

Se você é um agente de IA instalando este plugin a pedido de um usuário, veja [AGENTS.md](AGENTS.md).

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

**Plataforma.** Funciona em Linux, macOS e Windows (nativo ou WSL). Os hooks são Python puro e rodam de forma cross-platform; o único pré-requisito é `python3` resolvível no PATH (veja [Pré-requisitos por SO](#pré-requisitos-por-so), em especial a nota de Windows). Quando a skill `tab_pendencias` planeja testes ou auditorias que precisam de ferramentas externas, cada ferramenta é oferecida para instalação com a sua confirmação, no comando adequado ao seu SO (apt/dnf/brew/winget/choco/scoop) e preferindo gerenciadores cross-platform (pip/uv, cargo, npm). Nada é instalado em silêncio.

**Feito para o Claude Code (Anthropic).** O plugin usa recursos próprios do Claude Code: hooks de ciclo de vida, skills, o protocolo de subagents e o formato de plugin/marketplace. Não há garantia de funcionamento em outros assistentes de IA ou CLIs de código (por exemplo, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider); portar para outras plataformas pode exigir adaptação e não é suportado oficialmente.

**Incompatível com o plugin `caveman`.** O `caveman` comprime a comunicação e conflita com o reforço de modo deste plugin. Desative o `caveman` antes de usar o `bigtech`; o hook de sessão avisa caso detecte os dois ativos ao mesmo tempo.

**Dependências sugeridas:** `playwright` e `superpowers`. Não são obrigatórias, mas habilitam a experiência completa (automação de navegador e fluxos avançados). Instale-as para tirar o máximo do plugin; o hook de sessão sugere a instalação quando estão ausentes.

### Modelo de orquestração

Por padrão, os agents usam o modelo **`opus`** (sempre o Opus mais recente: o campo `model` não fixa versão), e a **orquestração** (o Chief of Staff e os C-level montando e coordenando a constelação) roda em **effort máximo**, para o raciocínio mais profundo nas decisões que cruzam o time. Esse é o default recomendado.

Você pode mudar manualmente: edite o campo `model` no cabeçalho de qualquer agent em `agents/<slug>.md` (valores aceitos: `opus`, `sonnet`, `haiku`) e ajuste o nível de esforço da sua sessão com `/effort`.

### Documentação

**Wiki (didática, para iniciantes):** a [Wiki do projeto](https://codeberg.org/petrinhu/bigtech_plugin/wiki) tem uma página por agente, hook e skill, além de glossário, guia de instalação e de uso passo a passo.

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
