# Privacy Policy

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

**Effective date:** 2026-11-20

This Privacy Policy describes how the **bigtech** plugin for Claude Code handles
data. The summary in one sentence: **the plugin does not collect, store on any
server, or transmit personal data to its author; its hooks run locally and make
no network calls, and the only feature that talks to the network is an opt-in
GitHub channel that you register yourself.**

### What the plugin is

`bigtech` is a local plugin for Claude Code, made up of Markdown files (agents,
skills, and documentation), seven Python hook scripts (registered nine times in
`hooks/hooks.json`), and a few optional skills. It has no server and no backend
operated by the author. It does not create an account and does not require a
login.

### No data collection by the author

The plugin does not send data to its author. It runs no telemetry, no
analytics, and no usage tracking. Nothing you do in a session is reported to
the maintainer.

### What the hooks do

The hooks run locally on your machine, under your own user account, in response
to Claude Code session events (SessionStart, UserPromptSubmit, PreToolUse, and
PostToolUse). They read the local session context: the files of the project you
have open, the `.bigtech-porte` marker that records the project size, and the
Claude Code settings files of your machine. **None of the hooks makes a network
connection.**

The hooks are fail-safe: an internal error is caught and the session continues
normally. The only intentional exception is the TDD guard, an opt-in test
guard-rail that may decline a code edit when the test cycle requires it. The TDD
feature acts only in projects that include a `.claude/tdd-guard.json` file; with
that file present, the test runner executes the test command declared by that
project. This is the same kind of trust as running `make test` or `npm test` in
a repository. For the full trust model and how to disable it, see
[SECURITY.md](./SECURITY.md).

### Local state written by the plugin

The plugin writes local state only on your own machine, under your home
directory or the runtime directory of your user. No path is hard-coded; each is
resolved at run time from your environment:

- TDD cycle results: `$HOME/.claude/state/tdd-guard/`.
- Pendências hook: a per-session file in `$XDG_RUNTIME_DIR` or `$HOME/.cache`.
  The copy of that hook inside `hooks/` writes its session timestamp to the
  system temporary directory instead; this is a known limitation, recorded in
  [SECURITY.md](./SECURITY.md).
- Optional skills (`watchcode`, `manter_ligado`): state under
  the runtime directory, `$HOME/.cache`, and `$HOME/.config/bigtech/`.

### Scope and responsibility

This policy covers the **bigtech plugin only.** The plugin operates inside Claude
Code, which is a product of Anthropic. Your use of Claude Code itself, and of any
artificial-intelligence model it relies on, is governed by Anthropic's own
policies, not by this policy. The optional plugins listed as dependencies of the
`bigtech-completo` bundle, and the third-party services named above, have their
own policies. This document does not control, and cannot speak for, how
Anthropic, GitHub, Cloudflare, or any third party handles your data.

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
Code lida com dados. O resumo em uma frase: **o plugin não envia dados pessoais
ao seu autor; os hooks rodam localmente e não fazem chamada de rede; a única
função que usa a rede é um canal opcional do GitHub, que você registra por conta
própria.**

### O que é o plugin

O `bigtech` é um plugin local do Claude Code, composto por arquivos Markdown
(agents, skills e documentação), sete scripts Python de hook (registrados nove
vezes em `hooks/hooks.json`) e alguns skills opcionais. Ele não tem servidor
nem backend operado pelo autor. Ele não cria conta e não exige login.

### Nenhuma coleta de dados pelo autor

O plugin não envia dados ao seu autor. Ele não roda telemetria, não roda
analytics e não faz rastreamento de uso. Nada do que você faz numa sessão é
reportado ao mantenedor.

### O que os hooks fazem

Os hooks são executados localmente na sua máquina, sob o seu próprio usuário,
em resposta a eventos de sessão do Claude Code (SessionStart,
UserPromptSubmit, PreToolUse e PostToolUse). Eles leem o contexto local da
sessão: os arquivos do projeto que você abriu, o marcador `.bigtech-porte`, que
registra o porte do projeto, e os arquivos de configuração do Claude Code da sua
máquina. **Nenhum dos hooks faz conexão de rede.**

Os hooks são fail-safe: um erro interno é capturado e a sessão segue
normalmente. A única exceção intencional é o guard de TDD, um guard-rail de
testes opt-in que pode recusar uma edição de código quando o ciclo de testes
exige. O recurso de TDD só atua em projetos que contêm um arquivo
`.claude/tdd-guard.json`; com esse arquivo presente, o executor de testes roda o
comando de teste declarado por aquele projeto. Isso tem a mesma natureza de
confiança de rodar `make test` ou `npm test` em um repositório. Para o modelo de
confiança completo e como desativar, consulte o [SECURITY.md](./SECURITY.md).

### Estado local gravado pelo plugin

O plugin grava estado local apenas na sua máquina, sob o seu diretório pessoal
ou o diretório de execução do seu usuário. Nenhum caminho é fixado no código;
cada um é resolvido em tempo de execução a partir do seu ambiente:

- Resultados do ciclo de TDD: `$HOME/.claude/state/tdd-guard/`.
- Hook de pendências: um arquivo por sessão em `$XDG_RUNTIME_DIR` ou
  `$HOME/.cache`. A cópia desse hook dentro de `hooks/` grava o carimbo de
  sessão no diretório temporário do sistema; essa é uma limitação conhecida,
  registrada no [SECURITY.md](./SECURITY.md).
- Skills opcionais (`watchcode`, `manter_ligado`): estado no
  diretório de execução, em `$HOME/.cache` e em `$HOME/.config/bigtech/`.

### Escopo e responsabilidade

Esta política cobre **apenas o plugin bigtech.** O plugin opera dentro do Claude
Code, que é um produto da Anthropic. O uso do próprio Claude Code, e de qualquer
modelo de inteligência artificial do qual ele dependa, é regido pelas políticas
da própria Anthropic, e não por esta política. Os plugins opcionais listados
como dependências do bundle `bigtech-completo` e os serviços de terceiros
citados acima têm políticas próprias. Este documento não controla, e não pode
responder por, como a Anthropic, o GitHub, a Cloudflare ou qualquer terceiro
lida com os seus dados.

### Mudanças nesta política

Qualquer mudança nesta Política de Privacidade é publicada no repositório do
projeto. A data de vigência acima é atualizada quando a política muda.

### Contato

Dúvidas sobre esta política podem ser registradas pelas issues do repositório
público:

- GitHub: https://github.com/petrinhu/bigtech_plugin

Handle do mantenedor: `petrinhu`.
