# Privacy Policy

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

**Effective date:** 2026-11-20

This Privacy Policy describes how the **bigtech** plugin for Claude Code handles
data. The summary in one sentence: **the plugin does not collect personal data,
does not store it on any server, and does not send it to its author; its hooks
run locally and open no network connection themselves.**

### What the plugin is

`bigtech` is a local plugin for Claude Code, made up of Markdown files (agents,
skills, and documentation), seven Python hook scripts (registered nine times in
`hooks/hooks.json`), and the scripts of a few skills, which run only when you
invoke those skills. It has no server and no backend operated by the author. It
does not create an account and does not require a login.

### No data collection by the author

The plugin does not send data to its author. It runs no telemetry, no
analytics, and no usage tracking. Nothing you do in a session is reported to
the maintainer.

### What the hooks do

The hooks run locally on your machine, under your own user account, in response
to Claude Code session events (SessionStart, UserPromptSubmit, PreToolUse, and
PostToolUse). They read the local session context: the files of the project you
have open, the `.bigtech-porte` marker that records the project size, the
Claude Code settings files of your machine, and, for the backlog-table
reminders, the `git` history of the project, read-only. **None of the hooks
opens a network connection itself.**

The hooks are fail-safe: an internal error is caught and the session continues
normally. The only intentional exception is the TDD guard, an opt-in test
guard-rail that may decline a code edit when the test cycle requires it. The TDD
feature acts only in projects that include a `.claude/tdd-guard.json` file; with
that file present, the test runner executes the test command declared by that
project. That command can do anything the project's test suite does when you
run it by hand, network access included. This is the same kind of trust as
running `make test` or `npm test` in a repository. For the full trust model and
how to disable it, see [SECURITY.md](./SECURITY.md).

### What can leave your machine

The code of the hooks sends nothing off your machine; the project's test
command, which the TDD hook runs, is covered above. Outside the hooks, these
are the only paths, and each one depends on a feature you turn on or a command
you run:

- **`manter_ligado` skill.** At 20% and at 5% battery, it sends a short battery
  notice to a phone already paired with your computer through KDE Connect, if
  there is one. Without a paired phone, it shows a desktop notification.
- **`manter_ligado` with `MEMO_HEADLESS=1`.** At 5% battery, it also starts a
  headless Claude Code session (`claude -p`) for each registered session, to
  save its memories. That session talks to Anthropic like any other Claude Code
  session. It asks for the `/memo_persistente` skill, which does not ship with
  the plugin and only works if it exists in your configuration; the output and
  errors of that call are discarded.
- **`tab_pendencias` skill, `--audit` command.** To check claims in the table
  such as "not pushed yet" or "on branch X", it queries the git remote of your
  project with `git ls-remote`, which only reads the remote and changes nothing,
  locally or remotely.
- **Dependencies of the `bigtech-completo` bundle.** They are third-party
  plugins with their own behavior. For example, `playwright` downloads the
  `@playwright/mcp` package from the internet every time its server starts.

Agents and skills can also ask Claude Code to use its own tools during a
session, such as web search. Those tools are part of Claude Code and follow
Anthropic's policies.

### Local state written by the plugin

The plugin writes local state only on your own machine, under your home
directory, the runtime directory of your user, or the project you open. No path
is hard-coded; each is resolved at run time from your environment:

- TDD cycle results: `$HOME/.claude/state/tdd-guard/`, one folder per project.
- Backlog-table hooks: the hook in `hooks/` keeps the session start time in
  `bigtech_tab_sessao`, and the hook of the `tab_pendencias` skill keeps, per
  session, the notices it has already shown in `tab_pendencias_hook_state`.
  Both folders live in `$XDG_RUNTIME_DIR`, or in `$HOME/.cache` when that
  variable is not set, are created with mode `0700`, and are pruned by age.
  Neither hook writes to the shared temporary directory (`/tmp`). See
  [SECURITY.md](./SECURITY.md).
- `bigtech` skill: once the project size is classified, the `.bigtech-porte`
  marker at the root of the project.
- `tab_pendencias` skill: when you run it, it writes `TODO.md` in your project,
  the project's `TESTES.md` and `AUDITORIAS.md` when they are missing, and,
  when it needs them, an `inbox/` folder next to `TODO.md` and, inside the
  `.git` folder of the repository, an intake journal and a write lock (outside
  a git repository, the lock sits next to `TODO.md`).
- `watchcode` skill: state in `${XDG_RUNTIME_DIR:-$HOME/.cache}/watchcode`, and
  an optional baseline that you create in
  `$HOME/.config/bigtech/watchcode_baseline.txt`.
- `manter_ligado` skill: state in `${XDG_RUNTIME_DIR:-$HOME/.cache}/manter_ligado`.
  At 5% battery, it copies the transcripts of the registered sessions to
  `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/manter_ligado_snapshots` and keeps only
  the latest copy. Its `limpar` command deletes these copies.
- `olhe_agentes` skill: the monitor deadline, the stop order you gave (if any),
  and the last work it announced as done, in
  `$HOME/.config/olhe_agentes/<project folder>/`.

### Scope and responsibility

This policy covers the **bigtech plugin only.** The plugin operates inside Claude
Code, which is a product of Anthropic. Your use of Claude Code itself, and of any
artificial-intelligence model it relies on, is governed by Anthropic's own
policies, not by this policy. The optional plugins listed as dependencies of the
`bigtech-completo` bundle, and tools such as KDE Connect, have their own
policies. This document does not control, and cannot speak for, how Anthropic,
GitHub (where the repository and its issues live), or any third party handles
your data.

### Changes to this policy

Any change to this Privacy Policy is published in the project repository. The
effective date above is updated when the policy changes.

### Contact

Questions about this policy can be raised through the public repository issues:

- GitHub: https://github.com/petrinhu/bigtech_plugin

Maintainer handle: `petrinhu`.

---

## Português

**Data de vigência:** 2026-11-20

Esta Política de Privacidade descreve como o plugin **bigtech** para o Claude
Code lida com dados. O resumo em uma frase: **o plugin não coleta dados
pessoais, não os guarda em servidor nenhum e não os envia ao seu autor; os
hooks rodam localmente e não abrem conexão de rede por conta própria.**

### O que é o plugin

O `bigtech` é um plugin local do Claude Code, composto por arquivos Markdown
(agents, skills e documentação), sete scripts Python de hook (registrados nove
vezes em `hooks/hooks.json`) e os scripts de algumas skills, que só rodam
quando você invoca essas skills. Ele não tem servidor nem backend operado pelo
autor. Ele não cria conta e não exige login.

### Nenhuma coleta de dados pelo autor

O plugin não envia dados ao seu autor. Ele não roda telemetria, não roda
analytics e não faz rastreamento de uso. Nada do que você faz numa sessão é
reportado ao mantenedor.

### O que os hooks fazem

Os hooks são executados localmente na sua máquina, sob o seu próprio usuário,
em resposta a eventos de sessão do Claude Code (SessionStart,
UserPromptSubmit, PreToolUse e PostToolUse). Eles leem o contexto local da
sessão: os arquivos do projeto que você abriu, o marcador `.bigtech-porte`, que
registra o porte do projeto, os arquivos de configuração do Claude Code da sua
máquina e, nos lembretes da tabela de pendências, o histórico `git` do projeto,
só para leitura. **Nenhum dos hooks abre conexão de rede por conta própria.**

Os hooks são fail-safe: um erro interno é capturado e a sessão segue
normalmente. A única exceção intencional é o guard de TDD, um guard-rail de
testes opt-in que pode recusar uma edição de código quando o ciclo de testes
exige. O recurso de TDD só atua em projetos que contêm um arquivo
`.claude/tdd-guard.json`; com esse arquivo presente, o executor de testes roda o
comando de teste declarado por aquele projeto. Esse comando pode fazer tudo o
que a suíte de testes do projeto faz quando você a roda à mão, inclusive
acessar a rede. Isso tem a mesma natureza de confiança de rodar `make test` ou
`npm test` em um repositório. Para o modelo de confiança completo e como
desativar, consulte o [SECURITY.md](./SECURITY.md).

### O que pode sair da sua máquina

O código dos hooks não envia nada para fora da sua máquina; o comando de teste
do projeto, que o hook de TDD roda, está descrito acima. Fora dos hooks, estes
são os únicos caminhos, e cada um depende de um recurso que você liga ou de um
comando que você roda:

- **Skill `manter_ligado`.** Com 20% e com 5% de bateria, ela envia um aviso
  curto de bateria a um celular já pareado com o computador pelo KDE Connect,
  se houver um. Sem celular pareado, ela mostra uma notificação na área de
  trabalho.
- **`manter_ligado` com `MEMO_HEADLESS=1`.** Com 5% de bateria, ela também abre
  uma sessão do Claude Code sem interface (`claude -p`) para cada sessão
  registrada, para salvar as memórias dela. Essa sessão fala com a Anthropic
  como qualquer outra sessão do Claude Code. Ela pede a skill
  `/memo_persistente`, que não vem no plugin e só funciona se existir na sua
  configuração; a saída e o erro dessa chamada são descartados.
- **Skill `tab_pendencias`, comando `--audit`.** Para conferir afirmações da
  tabela como "não pushado" ou "na branch X", ela consulta o remoto git do seu
  projeto com `git ls-remote`, que só lê o remoto e não altera nada, nem local
  nem remoto.
- **Dependências do pacote `bigtech-completo`.** São plugins de terceiros, com
  comportamento próprio. Por exemplo, o `playwright` baixa o pacote
  `@playwright/mcp` da internet toda vez que o servidor dele inicia.

Agents e skills também podem pedir ao Claude Code que use as ferramentas dele
durante a sessão, como a busca na web. Essas ferramentas fazem parte do Claude
Code e seguem as políticas da Anthropic.

### Estado local gravado pelo plugin

O plugin grava estado local apenas na sua máquina, sob o seu diretório pessoal,
o diretório de execução do seu usuário ou o projeto que você abriu. Nenhum
caminho é fixado no código; cada um é resolvido em tempo de execução a partir
do seu ambiente:

- Resultados do ciclo de TDD: `$HOME/.claude/state/tdd-guard/`, uma pasta por
  projeto.
- Hooks da tabela de pendências: o hook em `hooks/` guarda a hora de início da
  sessão em `bigtech_tab_sessao`, e o hook da skill `tab_pendencias` guarda, por
  sessão, os avisos que já mostrou em `tab_pendencias_hook_state`. As duas
  pastas ficam em `$XDG_RUNTIME_DIR` ou, quando essa variável não existe, em
  `$HOME/.cache`, são criadas com permissão `0700` e são podadas por idade.
  Nenhum dos dois grava no diretório temporário compartilhado (`/tmp`). Veja o
  [SECURITY.md](./SECURITY.md).
- Skill `bigtech`: depois que o porte do projeto é classificado, o marcador
  `.bigtech-porte` na raiz do projeto.
- Skill `tab_pendencias`: quando você a roda, ela grava o `TODO.md` no seu
  projeto, o `TESTES.md` e o `AUDITORIAS.md` do projeto quando faltam e,
  quando precisa, uma pasta `inbox/` ao lado do `TODO.md` e, dentro da pasta
  `.git` do repositório, um journal de intake e uma trava de escrita (fora de
  repositório git, a trava fica ao lado do `TODO.md`).
- Skill `watchcode`: estado em `${XDG_RUNTIME_DIR:-$HOME/.cache}/watchcode` e
  uma baseline opcional, criada por você, em
  `$HOME/.config/bigtech/watchcode_baseline.txt`.
- Skill `manter_ligado`: estado em `${XDG_RUNTIME_DIR:-$HOME/.cache}/manter_ligado`.
  Com 5% de bateria, ela copia os transcripts das sessões registradas para
  `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/manter_ligado_snapshots` e guarda só a
  cópia mais recente. O comando `limpar` apaga essas cópias.
- Skill `olhe_agentes`: o prazo do monitor, a parada que você ordenou (se
  houver) e o último trabalho que ele anunciou como concluído, em
  `$HOME/.config/olhe_agentes/<pasta do projeto>/`.

### Escopo e responsabilidade

Esta política cobre **apenas o plugin bigtech.** O plugin opera dentro do Claude
Code, que é um produto da Anthropic. O uso do próprio Claude Code, e de qualquer
modelo de inteligência artificial do qual ele dependa, é regido pelas políticas
da própria Anthropic, e não por esta política. Os plugins opcionais listados
como dependências do pacote `bigtech-completo`, e ferramentas como o KDE
Connect, têm políticas próprias. Este documento não controla, e não pode
responder por, como a Anthropic, o GitHub (onde ficam o repositório e as
issues) ou qualquer terceiro lida com os seus dados.

### Mudanças nesta política

Qualquer mudança nesta Política de Privacidade é publicada no repositório do
projeto. A data de vigência acima é atualizada quando a política muda.

### Contato

Dúvidas sobre esta política podem ser registradas pelas issues do repositório
público:

- GitHub: https://github.com/petrinhu/bigtech_plugin

Handle do mantenedor: `petrinhu`.
