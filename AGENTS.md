# AGENTS.md

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

> Installation manual aimed at an AI agent (Claude). If you are a human, start with the [README.md](README.md).

### You are an AI agent

You are an AI agent (Claude). If the user pointed you at this repository and asked something like "install the bigtech plugin from codeberg.org/petrinhu/bigtech_plugin", this file is your script. Follow the steps below in order, **stop before installing** if the conflict check (the "Name conflicts" section) finds a collision, and report to the user what you did.

General rule: prefer the main path (remote marketplace). Use the local-clone alternative only if the user asked for it, if the environment has no network, or if the remote registry fails.

### What this plugin is

`bigtech` is a plugin for Claude Code that packages a product-and-engineering organization:

- **50 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO, and Chief of Staff) and 38 operational agents that do the work.
- **3 orchestration skills.** `/bigtech` assembles the constellation and classifies the project size, `/proj_software` runs the software development life cycle (SDLC), `/tab_pendencias` plans the backlog by value and dependency.
- **Governance and TDD hooks.** Bootstrap of the manuals into the session, size reassessment, operating-mode reinforcement, TDD guard-rail (red, green, refactor), and a test runner.

Package identity (confirmed in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`):

| Field | Value |
|---|---|
| Marketplace | `petrinhu` |
| Plugin | `bigtech` |
| Version | `0.1.9` |
| License | `Apache-2.0` |
| Repository | `https://codeberg.org/petrinhu/bigtech_plugin` |
| Author | `petrinhu` |

### Installation in Claude Code (main path)

Run these slash commands in Claude Code, in order:

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech@petrinhu
```

The first command registers the `petrinhu` marketplace. The second installs the `bigtech` plugin from that marketplace. The `bigtech@petrinhu` form disambiguates the source; if the environment has only this marketplace, `/plugin install bigtech` also resolves.

After installing, **ask the user to restart the session** (or restart it once you have authorization). The `bigtech_session_init` hook runs on the `SessionStart` event: it is what loads the docs-bootstrap and injects the path of the manuals in `docs/` into the context. Without restarting, the manuals do not enter the context and the mode reinforcement is not active.

### Alternative: local clone

Use this when the user asked to install from a local copy, when there is no network, or when the remote registry failed.

```bash
git clone https://codeberg.org/petrinhu/bigtech_plugin
```

Then, in Claude Code, register the marketplace from the cloned path and install:

```
/plugin marketplace add <local-clone-path>
/plugin install bigtech
```

Replace `<local-clone-path>` with the absolute path of the directory where you cloned the repository (the one that contains `.claude-plugin/marketplace.json`).

### Post-installation verification

Confirm the three signals. If any of them fails, report it to the user before moving on.

1. **The 50 agents show up.** List the available agents and check for the C-level ones (`celso-ceo`, `capitolino-cpo`, `caetano-cto`, `camilo-cmo`, `cosmo-coo`, `narciso-ciso`, `candido-cdo`, `caio-caio`, `confucio-cfo`, `cicero-cro`, `claudio-clo`, `cosimo-chief-of-staff`) and a sample of the operational ones (`software-architect`, `backend-engineer`, `qa-engineer`, `technical-writer`).
2. **The 3 skills exist.** `/bigtech`, `/proj_software`, and `/tab_pendencias` must be listed and invokable.
3. **The hooks run.** When starting a new session, `bigtech_session_init` should inject the path of the manuals into the context. On a code project not yet classified, `bigtech_porte_reminder` reassesses the size. Use `/plugin` to confirm that the plugin is active and that the hooks are registered.

### ⚠️ Name conflicts (check BEFORE installing)

This is the most important point for you, agent. **Check it before running `/plugin install`.**

If the user's environment already has **global** agents, skills, or hooks (defined in `~/.claude/`, outside the plugin) with the **same names** as the ones this plugin ships, installing the plugin causes duplication and conflict. Examples of a likely collision: homonymous agents such as `celso-ceo`; homonymous skills such as `/bigtech` and `/tab_pendencias`; and, most seriously, **homonymous TDD hooks would run twice** (the global version plus the plugin's), which can block or run the test suite twice over.

Run this check before installing:

1. Inspect `~/.claude/agents/` for files with the same names as the agents in the "What this plugin is" section.
2. Inspect `~/.claude/skills/` (or `~/.claude/commands/`) for `/bigtech`, `/proj_software`, `/tab_pendencias`.
3. Inspect `~/.claude/hooks/` for homonymous TDD or governance hooks (`tdd_guard`, `tdd_runner`, `bigtech_*`).

If there is a collision, **do not install over it.** Present to the user, as a question, the two safe ways out (recommend the first):

- **Isolated profile (recommended).** Install the plugin in a clean environment, pointing Claude Code at another configuration directory with `CLAUDE_CONFIG_DIR` (for example, export `CLAUDE_CONFIG_DIR=/path/to/clean-profile` before starting the session). That way the plugin does not contend for names with the global config.
- **Remove the homonymous globals.** With explicit authorization from the user, remove or rename the global agents, skills, and hooks that collide before installing the plugin. Treat this as a destructive change: confirm each item.

With no collision, proceed with the installation normally.

### Compatibility

- **Built for Claude Code (Anthropic).** No guarantee it works on other assistants or code CLIs (for example, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, or Aider). Hooks, skills, and the subagent protocol depend on Claude Code; porting requires adaptation and is not officially supported.
- **Incompatible with the `caveman` plugin.** `caveman` compresses communication and conflicts with `bigtech`'s mode reinforcement. If `caveman` is active, **disable it** before using `bigtech`. The `bigtech_session_init` hook warns on `SessionStart` when it detects both active at the same time.
- **Suggested dependencies:** `playwright` and `superpowers`. They are not required, but they enable the full experience (browser automation and advanced flows). Install them for full use; `bigtech_session_init` suggests installing them when they are absent. For UI/design work, also install Anthropic's `frontend-design` skill if it is not already installed (it ships in the `example-skills` plugin: `/plugin marketplace add anthropics/skills` then `/plugin install example-skills@anthropic-agent-skills`). The `frontend-engineer` agent embeds its principles directly, so the skill is optional but recommended for richer, non-generic interfaces.

### Security

This plugin's hooks **run code on the user's machine**, as that user. Before installing, read and consider [SECURITY.md](SECURITY.md). Summary of what you need to know:

- The `tdd_runner` hook runs the test command declared by the **project the user opens** (`fast_command`/`test_command` field in `.claude/tdd-guard.json`). This has the same trust parity as running `make test` or `npm test` in the repository: the command comes from the project's versioned file.
- TDD (guard and runner) is **opt-in**: it only acts on projects that contain `.claude/tdd-guard.json`. Without that file, both hooks stay inert.
- When working in an unaudited third-party repository, inspect the `test_command`/`fast_command` in `.claude/tdd-guard.json` before editing files. To turn TDD off for the session, export `TDD_GUARD=off`.

### How to use it after installing

The entry points are the 3 skills. To get started, invoke `/bigtech` pointing at the project: the Chief of Staff classifies the size (avoiding over-engineering) and returns the activation map, that is, which C-levels and operational agents to turn on and in which phases.

```
/bigtech ./my-project
```

From there, `/proj_software` runs the software cycle and `/tab_pendencias` plans the backlog. For the detail of each skill, the agents, and the governance manuals, see the [README.md](README.md) and the `docs/` directory.

---

## Português

> Manual de instalação dirigido a um agente de IA (Claude). Se você é humano, comece pelo [README.md](README.md).

### Você é um agente de IA

Você é um agente de IA (Claude). Se o usuário apontou você para este repositório e pediu algo como "instala o plugin bigtech de codeberg.org/petrinhu/bigtech_plugin", este arquivo é o seu roteiro. Siga os passos abaixo na ordem, **pare antes de instalar** se a verificação de conflito (seção "Conflito de nomes") acusar colisão, e relate ao usuário o que você fez.

Regra geral: prefira o caminho principal (marketplace remoto). Use a alternativa de clone local só se o usuário pediu, se o ambiente não tem rede, ou se o registro remoto falhar.

### O que é este plugin

`bigtech` é um plugin para o Claude Code que empacota uma organização de produto e engenharia:

- **50 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO e Chief of Staff) e 38 operacionais que executam o trabalho.
- **3 skills de orquestração.** `/bigtech` monta a constelação e classifica o porte do projeto, `/proj_software` toca o ciclo de vida de software (SDLC), `/tab_pendencias` planeja o backlog por valor e dependência.
- **Hooks de governança e TDD.** Bootstrap dos manuais na sessão, reavaliação de porte, reforço do modo de operação, guard-rail de TDD (red, green, refactor) e runner de testes.

Identidade do pacote (confirmada em `.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`):

| Campo | Valor |
|---|---|
| Marketplace | `petrinhu` |
| Plugin | `bigtech` |
| Versão | `0.1.9` |
| Licença | `Apache-2.0` |
| Repositório | `https://codeberg.org/petrinhu/bigtech_plugin` |
| Autor | `petrinhu` |

### Instalação no Claude Code (caminho principal)

Execute estes comandos de barra no Claude Code, na ordem:

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech@petrinhu
```

O primeiro comando registra o marketplace `petrinhu`. O segundo instala o plugin `bigtech` a partir desse marketplace. A forma `bigtech@petrinhu` desambigua a origem; se o ambiente só tiver esse marketplace, `/plugin install bigtech` também resolve.

Depois de instalar, **peça ao usuário para reiniciar a sessão** (ou reinicie quando tiver autorização). O hook `bigtech_session_init` roda no evento `SessionStart`: é ele que carrega o docs-bootstrap e injeta no contexto o caminho dos manuais em `docs/`. Sem reiniciar, os manuais não entram em contexto e o reforço de modo não fica ativo.

### Alternativa: clone local

Use quando o usuário pediu instalação a partir de uma cópia local, quando não há rede, ou quando o registro remoto falhou.

```bash
git clone https://codeberg.org/petrinhu/bigtech_plugin
```

Em seguida, no Claude Code, registre o marketplace a partir do caminho clonado e instale:

```
/plugin marketplace add <caminho-local-do-clone>
/plugin install bigtech
```

Substitua `<caminho-local-do-clone>` pelo caminho absoluto do diretório onde você clonou o repositório (o que contém `.claude-plugin/marketplace.json`).

### Verificação pós-instalação

Confirme os três sinais. Se algum falhar, relate ao usuário antes de seguir.

1. **Os 50 agents aparecem.** Liste os agents disponíveis e confira a presença dos C-level (`celso-ceo`, `capitolino-cpo`, `caetano-cto`, `camilo-cmo`, `cosmo-coo`, `narciso-ciso`, `candido-cdo`, `caio-caio`, `confucio-cfo`, `cicero-cro`, `claudio-clo`, `cosimo-chief-of-staff`) e de uma amostra dos operacionais (`software-architect`, `backend-engineer`, `qa-engineer`, `technical-writer`).
2. **As 3 skills existem.** `/bigtech`, `/proj_software` e `/tab_pendencias` devem estar listadas e invocáveis.
3. **Os hooks rodam.** Ao iniciar uma nova sessão, o `bigtech_session_init` deve injetar o caminho dos manuais no contexto. Em projeto de código ainda não classificado, o `bigtech_porte_reminder` reavalia o porte. Use `/plugin` para confirmar que o plugin está ativo e que os hooks estão registrados.

### ⚠️ Conflito de nomes (verifique ANTES de instalar)

Este é o ponto mais importante para você, agente. **Verifique antes de rodar `/plugin install`.**

Se o ambiente do usuário já tiver agents, skills ou hooks **globais** (definidos em `~/.claude/`, fora do plugin) com os **mesmos nomes** dos que este plugin traz, instalar o plugin causa duplicação e conflito. Exemplos de colisão provável: agents homônimos como `celso-ceo`; skills homônimas como `/bigtech` e `/tab_pendencias`; e, o mais grave, **hooks de TDD homônimos rodariam duas vezes** (a versão global mais a do plugin), o que pode bloquear ou rodar a suíte de testes em duplicidade.

Faça esta checagem antes de instalar:

1. Inspecione `~/.claude/agents/` em busca de arquivos com os mesmos nomes dos agents da seção "O que é este plugin".
2. Inspecione `~/.claude/skills/` (ou `~/.claude/commands/`) em busca de `/bigtech`, `/proj_software`, `/tab_pendencias`.
3. Inspecione `~/.claude/hooks/` em busca de hooks de TDD ou de governança homônimos (`tdd_guard`, `tdd_runner`, `bigtech_*`).

Se houver colisão, **não instale por cima.** Apresente ao usuário, via pergunta, as duas saídas seguras (recomende a primeira):

- **Perfil isolado (recomendado).** Instale o plugin em um ambiente limpo, apontando o Claude Code para outro diretório de configuração com `CLAUDE_CONFIG_DIR` (por exemplo, exportar `CLAUDE_CONFIG_DIR=/caminho/para/perfil-limpo` antes de iniciar a sessão). Assim o plugin não disputa nomes com a config global.
- **Remover os globais homônimos.** Com autorização explícita do usuário, remova ou renomeie os agents, skills e hooks globais que colidem antes de instalar o plugin. Trate isso como mudança destrutiva: confirme cada item.

Sem colisão, siga a instalação normalmente.

### Compatibilidade

- **Feito para o Claude Code (Anthropic).** Sem garantia de funcionamento em outros assistentes ou CLIs de código (por exemplo, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider). Hooks, skills e o protocolo de subagents dependem do Claude Code; portar exige adaptação e não é suportado oficialmente.
- **Incompatível com o plugin `caveman`.** O `caveman` comprime a comunicação e conflita com o reforço de modo do `bigtech`. Se o `caveman` estiver ativo, **desative-o** antes de usar o `bigtech`. O hook `bigtech_session_init` avisa no `SessionStart` quando detecta os dois ativos ao mesmo tempo.
- **Dependências sugeridas:** `playwright` e `superpowers`. Não são obrigatórias, mas habilitam a experiência completa (automação de navegador e fluxos avançados). Instale-as para o uso pleno; o `bigtech_session_init` sugere a instalação quando estão ausentes. Para trabalho de UI/design, instale também a skill `frontend-design` da Anthropic, se ainda não estiver instalada (ela vem no plugin `example-skills`: `/plugin marketplace add anthropics/skills` e depois `/plugin install example-skills@anthropic-agent-skills`). O agent `frontend-engineer` já embarca os princípios dela, então a skill é opcional, mas recomendada para interfaces mais ricas e não genéricas.

### Segurança

Os hooks deste plugin **executam código na máquina do usuário**, com o usuário dele. Antes de instalar, leia e considere [SECURITY.md](SECURITY.md). Resumo do que você precisa saber:

- O hook `tdd_runner` roda o comando de teste declarado pelo **projeto que o usuário abrir** (campo `fast_command`/`test_command` em `.claude/tdd-guard.json`). Isso tem a mesma paridade de confiança de rodar `make test` ou `npm test` no repositório: o comando vem do arquivo versionado do projeto.
- O TDD (guard e runner) é **opt-in**: só atua em projetos que contêm `.claude/tdd-guard.json`. Sem esse arquivo, os dois hooks ficam inertes.
- Ao trabalhar em repositório de terceiros não auditado, inspecione o `test_command`/`fast_command` em `.claude/tdd-guard.json` antes de editar arquivos. Para desligar o TDD na sessão, exporte `TDD_GUARD=off`.

### Como usar depois de instalar

Os pontos de entrada são as 3 skills. Para começar, invoque `/bigtech` apontando para o projeto: o Chief of Staff classifica o porte (evitando over-engineering) e devolve o mapa de ativação, ou seja, quais C-levels e operacionais ligar e em quais fases.

```
/bigtech ./meu-projeto
```

A partir daí, `/proj_software` toca o ciclo de software e `/tab_pendencias` planeja o backlog. Para o detalhe de cada skill, dos agents e dos manuais de governança, consulte o [README.md](README.md) e o diretório `docs/`.
