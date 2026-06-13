# AGENTS.md

> Manual de instalação dirigido a um agente de IA (Claude). Se você é humano, comece pelo [README.md](README.md).

## Você é um agente de IA

Você é um agente de IA (Claude). Se o usuário apontou você para este repositório e pediu algo como "instala o plugin bigtech de codeberg.org/petrinhu/bigtech_plugin", este arquivo é o seu roteiro. Siga os passos abaixo na ordem, **pare antes de instalar** se a verificação de conflito (seção "Conflito de nomes") acusar colisão, e relate ao usuário o que você fez.

Regra geral: prefira o caminho principal (marketplace remoto). Use a alternativa de clone local só se o usuário pediu, se o ambiente não tem rede, ou se o registro remoto falhar.

## O que é este plugin

`bigtech` é um plugin para o Claude Code que empacota uma organização de produto e engenharia:

- **50 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO e Chief of Staff) e 38 operacionais que executam o trabalho.
- **3 skills de orquestração.** `/bigtech` monta a constelação e classifica o porte do projeto, `/proj_software` toca o ciclo de vida de software (SDLC), `/tab_pendencias` planeja o backlog por valor e dependência.
- **Hooks de governança e TDD.** Bootstrap dos manuais na sessão, reavaliação de porte, reforço do modo de operação, guard-rail de TDD (red, green, refactor) e runner de testes.

Identidade do pacote (confirmada em `.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`):

| Campo | Valor |
|---|---|
| Marketplace | `petrinhu` |
| Plugin | `bigtech` |
| Versão | `0.1.0` |
| Licença | `Apache-2.0` |
| Repositório | `https://codeberg.org/petrinhu/bigtech_plugin` |
| Autor | `petrinhu` |

## Instalação no Claude Code (caminho principal)

Execute estes comandos de barra no Claude Code, na ordem:

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech@petrinhu
```

O primeiro comando registra o marketplace `petrinhu`. O segundo instala o plugin `bigtech` a partir desse marketplace. A forma `bigtech@petrinhu` desambigua a origem; se o ambiente só tiver esse marketplace, `/plugin install bigtech` também resolve.

Depois de instalar, **peça ao usuário para reiniciar a sessão** (ou reinicie quando tiver autorização). O hook `bigtech_session_init` roda no evento `SessionStart`: é ele que carrega o docs-bootstrap e injeta no contexto o caminho dos manuais em `docs/`. Sem reiniciar, os manuais não entram em contexto e o reforço de modo não fica ativo.

## Alternativa: clone local

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

## Verificação pós-instalação

Confirme os três sinais. Se algum falhar, relate ao usuário antes de seguir.

1. **Os 50 agents aparecem.** Liste os agents disponíveis e confira a presença dos C-level (`celso-ceo`, `capitolino-cpo`, `caetano-cto`, `camilo-cmo`, `cosmo-coo`, `narciso-ciso`, `candido-cdo`, `caio-caio`, `confucio-cfo`, `cicero-cro`, `claudio-clo`, `cosimo-chief-of-staff`) e de uma amostra dos operacionais (`software-architect`, `backend-engineer`, `qa-engineer`, `technical-writer`).
2. **As 3 skills existem.** `/bigtech`, `/proj_software` e `/tab_pendencias` devem estar listadas e invocáveis.
3. **Os hooks rodam.** Ao iniciar uma nova sessão, o `bigtech_session_init` deve injetar o caminho dos manuais no contexto. Em projeto de código ainda não classificado, o `bigtech_porte_reminder` reavalia o porte. Use `/plugin` para confirmar que o plugin está ativo e que os hooks estão registrados.

## ⚠️ Conflito de nomes (verifique ANTES de instalar)

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

## Compatibilidade

- **Feito para o Claude Code (Anthropic).** Sem garantia de funcionamento em outros assistentes ou CLIs de código (por exemplo, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider). Hooks, skills e o protocolo de subagents dependem do Claude Code; portar exige adaptação e não é suportado oficialmente.
- **Incompatível com o plugin `caveman`.** O `caveman` comprime a comunicação e conflita com o reforço de modo do `bigtech`. Se o `caveman` estiver ativo, **desative-o** antes de usar o `bigtech`. O hook `bigtech_session_init` avisa no `SessionStart` quando detecta os dois ativos ao mesmo tempo.
- **Dependências sugeridas:** `playwright` e `superpowers`. Não são obrigatórias, mas habilitam a experiência completa (automação de navegador e fluxos avançados). Instale-as para o uso pleno; o `bigtech_session_init` sugere a instalação quando estão ausentes.

## Segurança

Os hooks deste plugin **executam código na máquina do usuário**, com o usuário dele. Antes de instalar, leia e considere [SECURITY.md](SECURITY.md). Resumo do que você precisa saber:

- O hook `tdd_runner` roda o comando de teste declarado pelo **projeto que o usuário abrir** (campo `fast_command`/`test_command` em `.claude/tdd-guard.json`). Isso tem a mesma paridade de confiança de rodar `make test` ou `npm test` no repositório: o comando vem do arquivo versionado do projeto.
- O TDD (guard e runner) é **opt-in**: só atua em projetos que contêm `.claude/tdd-guard.json`. Sem esse arquivo, os dois hooks ficam inertes.
- Ao trabalhar em repositório de terceiros não auditado, inspecione o `test_command`/`fast_command` em `.claude/tdd-guard.json` antes de editar arquivos. Para desligar o TDD na sessão, exporte `TDD_GUARD=off`.

## Como usar depois de instalar

Os pontos de entrada são as 3 skills. Para começar, invoque `/bigtech` apontando para o projeto: o Chief of Staff classifica o porte (evitando over-engineering) e devolve o mapa de ativação, ou seja, quais C-levels e operacionais ligar e em quais fases.

```
/bigtech ./meu-projeto
```

A partir daí, `/proj_software` toca o ciclo de software e `/tab_pendencias` planeja o backlog. Para o detalhe de cada skill, dos agents e dos manuais de governança, consulte o [README.md](README.md) e o diretório `docs/`.
