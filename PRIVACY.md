# Privacy Policy

**[English](#english)** (below) · **[Português](#português)** (abaixo)

---

## English

**Effective date:** 2026-06-14

This Privacy Policy describes how the **bigtech** plugin for Claude Code handles
data. The summary in one sentence: **the plugin does not collect, store, or
transmit any personal data; everything runs locally on your machine.**

### What the plugin is

`bigtech` is a local plugin for Claude Code, made up of Markdown files (agents,
skills, and documentation) and six hooks written in Python. It has no server and
no backend. It does not create an account, it does not require a login, and it
makes no network calls of its own.

### No data collection

The plugin does not collect, store, or transmit personal data. It runs no
telemetry, no analytics, and no usage tracking. It does not send any data off
your machine.

### What the hooks do

The hooks run locally on your machine, under your own user account, in response
to Claude Code session events (such as SessionStart, UserPromptSubmit,
PreToolUse, and PostToolUse). They read only the local session context, for
example the files of the project you have open and the `.bigtech-porte` marker
that records the project size. They make no network connections.

The hooks are fail-safe: an internal error is caught and the session continues
normally. The only intentional exception is the TDD guard, an opt-in test
guard-rail that may decline a code edit when the test cycle requires it. The TDD
feature acts only in projects that include a `.claude/tdd-guard.json` file; with
that file present, the test runner executes the test command declared by that
project. This is the same kind of trust as running `make test` or `npm test` in
a repository. For the full trust model and how to disable it, see
[SECURITY.md](./SECURITY.md).

The plugin writes only local state on your own machine, under your home
directory, to support the TDD cycle. No path is hard-coded; it is resolved at
run time from your environment.

### Scope and responsibility

This policy covers the **bigtech plugin only.** The plugin operates inside Claude
Code, which is a product of Anthropic. Your use of Claude Code itself, and of any
artificial-intelligence model it relies on, is governed by Anthropic's own
policies, not by this policy. This document does not control, and cannot speak
for, how Anthropic or any third party handles your data. Please review
Anthropic's policies for those terms.

### Changes to this policy

Any change to this Privacy Policy is published in the project repository. The
effective date above is updated when the policy changes.

### Contact

Questions about this policy can be raised through the public repository issues:

- Codeberg: https://codeberg.org/petrinhu/bigtech_plugin
- GitHub mirror: https://github.com/petrinhu/bigtech_plugin

Maintainer handle: `petrinhu`.

---

## Português

**Data de vigência:** 2026-06-14

Esta Política de Privacidade descreve como o plugin **bigtech** para o Claude
Code lida com dados. O resumo em uma frase: **o plugin não coleta, não armazena
e não transmite nenhum dado pessoal; tudo é executado localmente na sua
máquina.**

### O que é o plugin

O `bigtech` é um plugin local do Claude Code, composto por arquivos Markdown
(agents, skills e documentação) e seis hooks escritos em Python. Ele não tem
servidor e não tem backend. Ele não cria conta, não exige login e não faz
chamadas de rede próprias.

### Nenhuma coleta de dados

O plugin não coleta, não armazena e não transmite dados pessoais. Ele não roda
telemetria, não roda analytics e não faz rastreamento de uso. Ele não envia
nenhum dado para fora da sua máquina.

### O que os hooks fazem

Os hooks são executados localmente na sua máquina, sob o seu próprio usuário, em
resposta a eventos de sessão do Claude Code (como SessionStart, UserPromptSubmit,
PreToolUse e PostToolUse). Eles leem apenas o contexto local da sessão, por
exemplo os arquivos do projeto que você abriu e o marcador `.bigtech-porte`, que
registra o porte do projeto. Eles não realizam nenhuma conexão de rede.

Os hooks são fail-safe: um erro interno é capturado e a sessão segue
normalmente. A única exceção intencional é o guard de TDD, um guard-rail de
testes opt-in que pode recusar uma edição de código quando o ciclo de testes
exige. O recurso de TDD só atua em projetos que contêm um arquivo
`.claude/tdd-guard.json`; com esse arquivo presente, o executor de testes roda o
comando de teste declarado por aquele projeto. Isso tem a mesma natureza de
confiança de rodar `make test` ou `npm test` em um repositório. Para o modelo de
confiança completo e como desativar, consulte o [SECURITY.md](./SECURITY.md).

O plugin grava apenas estado local na sua própria máquina, sob o seu diretório
pessoal, para apoiar o ciclo de TDD. Nenhum caminho é fixado no código; ele é
resolvido em tempo de execução a partir do seu ambiente.

### Escopo e responsabilidade

Esta política cobre **apenas o plugin bigtech.** O plugin opera dentro do Claude
Code, que é um produto da Anthropic. O uso do próprio Claude Code, e de qualquer
modelo de inteligência artificial do qual ele dependa, é regido pelas políticas
da própria Anthropic, e não por esta política. Este documento não controla, e
não pode responder por, como a Anthropic ou qualquer terceiro lida com os seus
dados. Consulte as políticas da Anthropic para esses termos.

### Mudanças nesta política

Qualquer mudança nesta Política de Privacidade é publicada no repositório do
projeto. A data de vigência acima é atualizada quando a política muda.

### Contato

Dúvidas sobre esta política podem ser registradas pelas issues dos repositórios
públicos:

- Codeberg: https://codeberg.org/petrinhu/bigtech_plugin
- Espelho no GitHub: https://github.com/petrinhu/bigtech_plugin

Handle do mantenedor: `petrinhu`.
