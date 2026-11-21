# LLM.md

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

> Installation manual aimed at an AI agent (Claude). If you are a human, start with the [README.md](README.md).

### You are an AI agent

You are an AI agent (Claude). If the user pointed you at this repository and asked something like "install the bigtech plugin from github.com/petrinhu/bigtech_plugin", this file is your script. Follow the steps below in order, **stop before installing** if the conflict check (the "Name conflicts" section) finds a collision, and report to the user what you did.

General rule: prefer the main path (remote marketplace). Use the local-clone alternative only if the user asked for it, if the environment has no network, or if the remote registry fails.

### What this plugin is

`bigtech` is a plugin for Claude Code that packages a product-and-engineering organization:

- **71 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO, and Chief of Staff) and 59 operational agents that do the work, including `visual-design-director`, the game-development squad, and the medical-expert agents.
- **15 skills.** Orchestration skills (`/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo`, `/bigtech:tab_pendencias`), agent shortcuts (`/bigtech:visual-design-director`, `/bigtech:dr-advogado`, `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-psiquiatra`, `/bigtech:dr-medico-trabalho`, `/bigtech:learning-designer`, `/bigtech:suporte-linux`), the case orchestrator `/bigtech:pericia-medica`, and three new operational skills: `/bigtech:watchcode`, `/bigtech:manter_ligado` and `/bigtech:olhe_agentes`. `github-gossips` left the plugin and stays available outside it.
- **Governance and TDD hooks.** Bootstrap of the manuals into the session, a reminder to classify the size, operating-mode reinforcement, TDD guard-rail (red, green, refactor), and a test runner.

Package identity (confirmed in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`):

| Field | Value |
|---|---|
| Marketplace | `petrinhu` |
| Plugin | `bigtech` (core) and `bigtech-completo` (bundle with the recommended dependencies) |
| Version | `2.0.0` |
| License | `Apache-2.0` |
| Repository | `https://github.com/petrinhu/bigtech_plugin` |
| Author | `petrinhu` |

### Installation in Claude Code (main path)

Run these commands in a terminal, in order. Each step is a command, not a slash command.

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

After installing, **ask the user to restart the session** (or restart it once you have authorization). The `bigtech_session_init` hook runs on the `SessionStart` event: it is what loads the docs-bootstrap and injects the path of the manuals in `docs/house/` into the context. Without restarting, the manuals do not enter the context and the mode reinforcement is not active.

### Dependencies and installation per OS

What you need to know to make the plugin work on the user's operating system. Two layers: a hard prerequisite (`python3`) and a runtime convention you already follow.

**Hard prerequisite: `python3` resolvable on the PATH.** The plugin's hooks are declared in `hooks/hooks.json` with `"command": "python3"`, so Claude Code spawns the interpreter by that exact name. If `python3` does not resolve, the hooks fail silently and the plugin is inert (no docs-bootstrap, no mode reinforcement). Verify with `python3 --version`, then per OS:

- **Linux:** `python3` is almost always present. If missing, offer to install it via the system manager (`sudo apt install python3` / `dnf` / `pacman` / `zypper`); this is a privileged system action, so ask first.
- **macOS:** ships via the Xcode Command Line Tools (`xcode-select --install`) or Homebrew (`brew install python`). Confirm `python3 --version` resolves.
- **Windows (native):** the hooks call `python3`. (a) **Microsoft Store Python** (recommended) registers the `python3` and `python` aliases automatically. (b) The **python.org installer** provides `python` and the `py` launcher but does **not** guarantee `python3`; the fix is to put the plugin's `bin/python3.cmd` shim (it forwards to `py -3` or `python`) on a PATH directory such as `%LOCALAPPDATA%\Microsoft\WindowsApps`, or create an alias. (c) **WSL** is the simplest alternative: inside WSL the Linux instructions apply verbatim. Always verify `python3 --version`.

**Linux with systemd only (`manter_ligado`).** The skill keeps the connection alive with the lid closed and depends on systemd. Do not enable it on other systems.

**Agent runtime tools follow the missing-tool-policy automatically.** When an agent needs an external FOSS tool (linter, scanner, diagram, profiler) that is not installed, it detects the OS, then either auto-installs userland command-line tools without privilege (`pip`/`uv`, `cargo`, `npm`, `$HOME` binary) or asks for privileged installs or libraries, models, extensions and browsers, which always need the user's permission. It never refuses a task for a missing tool. Manager map: `apt`/`dnf`/`pacman`/`zypper` (Linux), `brew` (macOS), `winget`/`scoop`/`choco` (Windows), and cross-platform (`pip`/`uv`, `cargo`, `npm`). Full doctrine in [docs/principles/missing-tool-policy.md](docs/principles/missing-tool-policy.md); per-tool install commands in [docs/house/TOOLING.md](docs/house/TOOLING.md).

### Alternative: local clone

Use this when the user asked to install from a local copy, when there is no network, or when the remote registry failed.

```bash
git clone https://github.com/petrinhu/bigtech_plugin
```

Then register the marketplace from the cloned path and install:

```
claude plugin marketplace add /absolute/path/to/bigtech_plugin
claude plugin install bigtech@petrinhu
```

Replace `/absolute/path/to/bigtech_plugin` with the absolute path of the directory where you cloned the repository (the one that contains `.claude-plugin/marketplace.json`). The local clone does not add the dependency marketplaces: for the bundle, add them first, as in the section above.

### Post-installation verification

Confirm the three signals. If any of them fails, report it to the user before moving on.

1. **The 71 agents show up.** List the available agents and check for the C-level ones (`celso-ceo`, `capitolino-cpo`, `caetano-cto`, `camilo-cmo`, `cosmo-coo`, `narciso-ciso`, `candido-cdo`, `caio-caio`, `confucio-cfo`, `cicero-cro`, `claudio-clo`, `cosimo-chief-of-staff`) and a sample of the operational ones (`software-architect`, `backend-engineer`, `qa-engineer`, `visual-design-director`, `technical-writer`).
2. **The 15 skills exist.** `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:tab_pendencias` and `/bigtech:visual-design-director` must be listed and invokable.
3. **The hooks run.** When starting a new session, `bigtech_session_init` should inject the path of the manuals into the context. On a code project without the `.bigtech-porte` marker, `bigtech_porte_reminder` reminds you to classify the size; with the marker, it anchors the operating mode and cites the recorded size. Use `/plugin` to confirm that the plugin is active and that the hooks are registered.

### ⚠️ Name conflicts (check BEFORE installing)

This is the most important point for you, agent. **Check it before running the install commands.**

If the user's environment already has **global** agents, skills, or hooks (defined in `~/.claude/`, outside the plugin) with the **same names** as the ones this plugin ships, installing the plugin causes duplication and conflict. Examples of a likely collision: homonymous agents such as `celso-ceo`; homonymous skills such as a global `bigtech` or `tab_pendencias`, which the plugin ships as `/bigtech:bigtech` and `/bigtech:tab_pendencias`; and, most seriously, **homonymous TDD hooks would run twice** (the global version plus the plugin's), which can block or run the test suite twice over.

Run this check before installing:

1. Inspect the `agents` folder of your global Claude Code configuration for files named like any of the 71 agents of this plugin. "What this plugin is" gives only their count and roles; the names are listed in the Agents section of the [README.md](README.md) and are the file names of the plugin's `agents/` folder, without `.md` (for example `celso-ceo`).
2. Inspect `~/.claude/skills/` for folders, and `~/.claude/commands/` for `.md` files, named like the 15 skills listed in "What this plugin is", written without the slash and without the `bigtech:` prefix (for example `bigtech`, `proj_software`, `tab_pendencias`). Global skills have no plugin prefix, so search for the bare name: a global `tab_pendencias` folder is the homonym of the plugin's `/bigtech:tab_pendencias`.
3. Inspect `~/.claude/hooks/` for homonymous TDD or governance hooks (`tdd_guard`, `tdd_runner`, `bigtech_*`).

If there is a collision, **do not install over it.** Present to the user, as a question, the two safe ways out (recommend the first):

- **Isolated profile (recommended).** Install the plugin in a clean environment, pointing Claude Code at another configuration directory with `CLAUDE_CONFIG_DIR` (for example, export `CLAUDE_CONFIG_DIR=/path/to/clean-profile` before starting the session). That way the plugin does not contend for names with the global config.
- **Remove the homonymous globals.** With explicit authorization from the user, remove or rename the global agents, skills, and hooks that collide before installing the plugin. Treat this as a destructive change: confirm each item.

With no collision, proceed with the installation normally.

### Compatibility

- **Built for Claude Code (Anthropic).** No guarantee it works on other assistants or code CLIs (for example, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor, or Aider). Hooks, skills, and the subagent protocol depend on Claude Code; porting requires adaptation and is not officially supported.
- **Possible conflict with the `caveman` plugin.** `caveman` compresses communication and can interfere with `bigtech`'s mode reinforcement and routing. If `caveman` is active, tell the user: keeping or disabling plugins is the user's decision, so do not disable it yourself. If the user keeps both, make sure requests for the constellation still reach the `bigtech` skill. The `bigtech_session_init` hook warns on `SessionStart` when it detects `caveman` active.
- **Dependencies:** the section "Installation in Claude Code" above lists them, with the install command for the bundle. `frontend-design` comes from the `claude-plugins-official` marketplace only.

### Security

This plugin's hooks **run code on the user's machine**, as that user. Before installing, read and consider [SECURITY.md](SECURITY.md). Summary of what you need to know:

- The `tdd_runner` hook runs the test command declared by the **project the user opens** (`fast_command`/`test_command` field in `.claude/tdd-guard.json`). This has the same trust parity as running `make test` or `npm test` in the repository: the command comes from the project's versioned file.
- TDD (guard and runner) is **opt-in**: it only acts on projects that contain `.claude/tdd-guard.json`. Without that file, both hooks stay inert.
- When working in an unaudited third-party repository, inspect the `test_command`/`fast_command` in `.claude/tdd-guard.json` before editing files.

### How to use it after installing

The main entry points are the 4 orchestration skills: `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo` and, for the backlog, `/bigtech:tab_pendencias`. Always invoke them with the `bigtech:` prefix: the name without the prefix only works while no other skill or command uses it. To get started, invoke `/bigtech:bigtech` pointing at the project: the Chief of Staff classifies the size (avoiding over-engineering) and returns the activation map, that is, which C-levels and operational agents to turn on and in which phases.

```
/bigtech:bigtech ./my-project
```

From there, `/bigtech:proj_software` runs the software cycle (`/bigtech:proj_jogo`, when the project is a game) and `/bigtech:tab_pendencias` plans the backlog. To keep that table fresh, follow one convention: when you commit work that closes or advances a `TODO.md` item, cite the item ID in the commit message and touch the `Status` column in the same commit (delivered implementation → `🔍 Pendente verificação`; `✅` only after the test/audit wave); reordering is separate and runs only through `/bigtech:tab_pendencias --reorder`. Detail in [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md). For the detail of each skill, the agents, and the governance manuals, see the [README.md](README.md) and the `docs/` directory.

---

## Português

> Manual de instalação dirigido a um agente de IA (Claude). Se você é humano, comece pelo [README.md](README.md).

### Você é um agente de IA

Você é um agente de IA (Claude). Se o usuário apontou você para este repositório e pediu algo como "instala o plugin bigtech de github.com/petrinhu/bigtech_plugin", este arquivo é o seu roteiro. Siga os passos abaixo na ordem, **pare antes de instalar** se a verificação de conflito (seção "Conflito de nomes") acusar colisão, e relate ao usuário o que você fez.

Regra geral: prefira o caminho principal (marketplace remoto). Use a alternativa de clone local só se o usuário pediu, se o ambiente não tem rede, ou se o registro remoto falhar.

### O que é este plugin

`bigtech` é um plugin para o Claude Code que empacota uma organização de produto e engenharia:

- **71 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO e Chief of Staff) e 59 operacionais que executam o trabalho, incluindo `visual-design-director`, o diretor de design visual, o time de desenvolvimento de jogos e os agents médico-periciais.
- **15 skills.** Skills de orquestração (`/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo`, `/bigtech:tab_pendencias`), atalhos de agent (`/bigtech:visual-design-director`, `/bigtech:dr-advogado`, `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-psiquiatra`, `/bigtech:dr-medico-trabalho`, `/bigtech:learning-designer`, `/bigtech:suporte-linux`), o orquestrador de caso `/bigtech:pericia-medica` e três skills operacionais novas: `/bigtech:watchcode`, `/bigtech:manter_ligado` e `/bigtech:olhe_agentes`. `github-gossips` saiu do plugin e continua disponível fora dele.
- **Hooks de governança e TDD.** Bootstrap dos manuais na sessão, lembrete de classificar o porte, reforço do modo de operação, guard-rail de TDD (red, green, refactor) e runner de testes.

Identidade do pacote (confirmada em `.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`):

| Campo | Valor |
|---|---|
| Marketplace | `petrinhu` |
| Plugin | `bigtech` (núcleo) e `bigtech-completo` (pacote com as dependências recomendadas) |
| Versão | `2.0.0` |
| Licença | `Apache-2.0` |
| Repositório | `https://github.com/petrinhu/bigtech_plugin` |
| Autor | `petrinhu` |

### Instalação no Claude Code (caminho principal)

Execute estes comandos em um terminal, na ordem. Cada passo é um comando de terminal, não um comando de barra.

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

Depois de instalar, **peça ao usuário para reiniciar a sessão** (ou reinicie quando tiver autorização). O hook `bigtech_session_init` roda no evento `SessionStart`: é ele que carrega o docs-bootstrap e injeta no contexto o caminho dos manuais em `docs/house/`. Sem reiniciar, os manuais não entram em contexto e o reforço de modo não fica ativo.

### Dependências e instalação por SO

O que você precisa saber para o plugin funcionar no sistema operacional do usuário. Duas camadas: um pré-requisito rígido (`python3`) e uma convenção de runtime que você já segue.

**Pré-requisito rígido: `python3` resolvível no PATH.** Os hooks do plugin estão declarados em `hooks/hooks.json` com `"command": "python3"`, então o Claude Code chama o interpretador por esse nome exato. Se `python3` não resolve, os hooks falham em silêncio e o plugin fica inerte (sem docs-bootstrap, sem reforço de modo). Verifique com `python3 --version` e, por SO:

- **Linux:** o `python3` quase sempre já está presente. Se faltar, ofereça instalar pelo gerenciador do sistema (`sudo apt install python3` / `dnf` / `pacman` / `zypper`); isso é ação com privilégio de sistema, então pergunte antes.
- **macOS:** vem via Xcode Command Line Tools (`xcode-select --install`) ou Homebrew (`brew install python`). Confirme que `python3 --version` resolve.
- **Windows (nativo):** os hooks chamam `python3`. (a) **Python da Microsoft Store** (recomendado) registra os aliases `python3` e `python` automaticamente. (b) O **instalador do python.org** dá `python` e o launcher `py`, mas **não** garante `python3`; a solução é colocar o shim `bin/python3.cmd` do plugin (ele encaminha para `py -3` ou `python`) num diretório do PATH, como `%LOCALAPPDATA%\Microsoft\WindowsApps`, ou criar um alias. (c) **WSL** é a alternativa mais simples: dentro do WSL valem as instruções de Linux na íntegra. Sempre verifique `python3 --version`.

**Só Linux com systemd (`manter_ligado`).** A skill mantém a conexão viva com a tampa fechada e depende do systemd. Não ative em outros sistemas.

**As ferramentas de runtime dos agents seguem a missing-tool-policy automaticamente.** Quando um agent precisa de uma ferramenta FOSS externa (linter, scanner, diagrama, profiler) que não está instalada, ele detecta o SO e então ou autoinstala ferramentas de linha de comando de uso geral sem privilégio (`pip`/`uv`, `cargo`, `npm`, binário no `$HOME`) ou pede permissão para bibliotecas, modelos, extensões e navegadores, e para instalações com privilégio. Nunca recusa a tarefa por falta de ferramenta. Mapa de gerenciador: `apt`/`dnf`/`pacman`/`zypper` (Linux), `brew` (macOS), `winget`/`scoop`/`choco` (Windows) e cross-platform (`pip`/`uv`, `cargo`, `npm`). Doutrina completa em [docs/principles/missing-tool-policy.md](docs/principles/missing-tool-policy.md); comandos de instalação por ferramenta em [docs/house/TOOLING.md](docs/house/TOOLING.md).

### Alternativa: clone local

Use quando o usuário pediu instalação a partir de uma cópia local, quando não há rede, ou quando o registro remoto falhou.

```bash
git clone https://github.com/petrinhu/bigtech_plugin
```

Em seguida, registre o marketplace a partir do caminho clonado e instale:

```
claude plugin marketplace add /caminho/absoluto/para/bigtech_plugin
claude plugin install bigtech@petrinhu
```

Substitua `/caminho/absoluto/para/bigtech_plugin` pelo caminho absoluto do diretório onde você clonou o repositório (o que contém `.claude-plugin/marketplace.json`). O clone local não adiciona os marketplaces das dependências: para o pacote, adicione-os antes, como na seção acima.

### Verificação pós-instalação

Confirme os três sinais. Se algum falhar, relate ao usuário antes de seguir.

1. **Os 71 agents aparecem.** Liste os agents disponíveis e confira a presença dos C-level (`celso-ceo`, `capitolino-cpo`, `caetano-cto`, `camilo-cmo`, `cosmo-coo`, `narciso-ciso`, `candido-cdo`, `caio-caio`, `confucio-cfo`, `cicero-cro`, `claudio-clo`, `cosimo-chief-of-staff`) e de uma amostra dos operacionais (`software-architect`, `backend-engineer`, `qa-engineer`, `visual-design-director`, `technical-writer`).
2. **As 15 skills existem.** `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:tab_pendencias` e `/bigtech:visual-design-director` devem estar listadas e invocáveis.
3. **Os hooks rodam.** Ao iniciar uma nova sessão, o `bigtech_session_init` deve injetar o caminho dos manuais no contexto. Em projeto de código sem o marcador `.bigtech-porte`, o `bigtech_porte_reminder` lembra de classificar o porte; com o marcador, ancora o modo de operação e cita o porte registrado. Use `/plugin` para confirmar que o plugin está ativo e que os hooks estão registrados.

### ⚠️ Conflito de nomes (verifique ANTES de instalar)

Este é o ponto mais importante para você, agente. **Verifique antes de rodar os comandos de instalação.**

Se o ambiente do usuário já tiver agents, skills ou hooks **globais** (definidos em `~/.claude/`, fora do plugin) com os **mesmos nomes** dos que este plugin traz, instalar o plugin causa duplicação e conflito. Exemplos de colisão provável: agents homônimos como `celso-ceo`; skills homônimas como uma `bigtech` ou uma `tab_pendencias` globais, que o plugin traz como `/bigtech:bigtech` e `/bigtech:tab_pendencias`; e, o mais grave, **hooks de TDD homônimos rodariam duas vezes** (a versão global mais a do plugin), o que pode bloquear ou rodar a suíte de testes em duplicidade.

Faça esta checagem antes de instalar:

1. Inspecione a pasta `agents` da sua configuração global do Claude Code em busca de arquivos com o nome de algum dos 71 agents deste plugin. A seção "O que é este plugin" dá só a contagem e os papéis; os nomes estão na seção Agents do [README.md](README.md) e são os nomes dos arquivos da pasta `agents/` do plugin, sem o `.md` (por exemplo `celso-ceo`).
2. Inspecione `~/.claude/skills/` em busca de pastas, e `~/.claude/commands/` em busca de arquivos `.md`, com o nome das 15 skills listadas em "O que é este plugin", escrito sem a barra e sem o prefixo `bigtech:` (por exemplo `bigtech`, `proj_software`, `tab_pendencias`). Skill global não tem prefixo de plugin, então procure o nome puro: uma pasta global `tab_pendencias` é a homônima da `/bigtech:tab_pendencias` do plugin.
3. Inspecione `~/.claude/hooks/` em busca de hooks de TDD ou de governança homônimos (`tdd_guard`, `tdd_runner`, `bigtech_*`).

Se houver colisão, **não instale por cima.** Apresente ao usuário, via pergunta, as duas saídas seguras (recomende a primeira):

- **Perfil isolado (recomendado).** Instale o plugin em um ambiente limpo, apontando o Claude Code para outro diretório de configuração com `CLAUDE_CONFIG_DIR` (por exemplo, exportar `CLAUDE_CONFIG_DIR=/caminho/para/perfil-limpo` antes de iniciar a sessão). Assim o plugin não disputa nomes com a config global.
- **Remover os globais homônimos.** Com autorização explícita do usuário, remova ou renomeie os agents, skills e hooks globais que colidem antes de instalar o plugin. Trate isso como mudança destrutiva: confirme cada item.

Sem colisão, siga a instalação normalmente.

### Compatibilidade

- **Feito para o Claude Code (Anthropic).** Sem garantia de funcionamento em outros assistentes ou CLIs de código (por exemplo, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider). Hooks, skills e o protocolo de subagents dependem do Claude Code; portar exige adaptação e não é suportado oficialmente.
- **Possível conflito com o plugin `caveman`.** O `caveman` comprime a comunicação e pode interferir no reforço de modo e no roteamento do `bigtech`. Se o `caveman` estiver ativo, informe o usuário: manter ou desativar plugins é decisão dele, então não o desative por conta própria. Se o usuário mantiver os dois, garanta que os pedidos da constelação ainda cheguem à skill `bigtech`. O hook `bigtech_session_init` avisa no `SessionStart` quando detecta o `caveman` ativo.
- **Dependências:** a seção "Instalação no Claude Code" acima lista todas, com o comando de instalação do pacote. O `frontend-design` vem só do marketplace `claude-plugins-official`.

### Segurança

Os hooks deste plugin **executam código na máquina do usuário**, com o usuário dele. Antes de instalar, leia e considere [SECURITY.md](SECURITY.md). Resumo do que você precisa saber:

- O hook `tdd_runner` roda o comando de teste declarado pelo **projeto que o usuário abrir** (campo `fast_command`/`test_command` em `.claude/tdd-guard.json`). Isso tem a mesma paridade de confiança de rodar `make test` ou `npm test` no repositório: o comando vem do arquivo versionado do projeto.
- O TDD (guard e runner) é **opt-in**: só atua em projetos que contêm `.claude/tdd-guard.json`. Sem esse arquivo, os dois hooks ficam inertes.
- Ao trabalhar em repositório de terceiros não auditado, inspecione o `test_command`/`fast_command` em `.claude/tdd-guard.json` antes de editar arquivos.

### Como usar depois de instalar

Os pontos de entrada principais são as 4 skills de orquestração: `/bigtech:bigtech`, `/bigtech:proj_software`, `/bigtech:proj_jogo` e, para o backlog, `/bigtech:tab_pendencias`. Invoque sempre com o prefixo `bigtech:`: o nome sem o prefixo só funciona enquanto nenhuma outra skill ou comando o usa. Para começar, invoque `/bigtech:bigtech` apontando para o projeto: o Chief of Staff classifica o porte (evitando over-engineering) e devolve o mapa de ativação, ou seja, quais C-levels e operacionais ligar e em quais fases.

```
/bigtech:bigtech ./meu-projeto
```

A partir daí, `/bigtech:proj_software` toca o ciclo de software (`/bigtech:proj_jogo`, quando o projeto é um jogo) e `/bigtech:tab_pendencias` planeja o backlog. Para manter essa tabela fresca, siga uma convenção: ao commitar trabalho que fecha ou avança um item do `TODO.md`, cite o ID do item na mensagem do commit e toque a coluna `Status` no mesmo commit (implementação entregue → `🔍 Pendente verificação`; `✅` quando o CI do ramo fecha verde); reordenar é à parte e só roda pelo `/bigtech:tab_pendencias --reorder`. Detalhe em [docs/tabela-pendencias-frescor.md](docs/tabela-pendencias-frescor.md). Para o detalhe de cada skill, dos agents e dos manuais de governança, consulte o [README.md](README.md) e o diretório `docs/`.
