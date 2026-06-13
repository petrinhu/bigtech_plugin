# bigtech

> Estruture qualquer projeto como uma empresa de produto digital: uma constelação de 50 agents (12 C-level + 38 operacionais), 3 skills de orquestração e hooks de governança e TDD. Dimensionável do solo founder à bigtech.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

## Bem-vindo, líder supremo

Você, que instala e opera este plugin, é o **líder supremo desta organização: o CEO da sua bigtech.** A constelação C-level (Celso/CEO inclusive) propõe e executa, mas **a palavra final é sempre sua.**

Decisões de altíssimo valor (arquitetura macro, escopo, stack, go/no-go, deploy irreversível, gasto, qualquer escolha difícil de reverter) são suas. Diante de dúvida ou de mais de uma opção viável, os agents não decidem sozinhos: eles perguntam (a opção recomendada vem primeiro). O time trabalha para você.

## O que é

`bigtech` empacota uma organização completa de produto e engenharia em forma de plugin para o Claude Code:

- **50 agents.** 12 C-level (estratégia, produto, engenharia, marketing, operações, segurança, dados, IA, finanças, receita, jurídico, chief of staff) e 38 operacionais que executam o trabalho.
- **3 skills de orquestração.** `/bigtech` monta a constelação, `/proj_software` toca o ciclo de vida de software (SDLC), `/tab_pendencias` planeja o backlog por valor e dependência.
- **Hooks de governança e TDD.** Guard-rail de testes (red, green, refactor), reavaliação de porte do projeto, reforço do modo de operação e bootstrap dos manuais na sessão.

O princípio inegociável: **o processo se adapta ao porte do projeto, nunca o contrário.** Um CLI de 200 linhas não chama o time inteiro. O Chief of Staff classifica o porte e liga só o necessário, prevenindo over-engineering.

## Instalação

```
/plugin marketplace add codeberg.org/petrinhu/bigtech_plugin
/plugin install bigtech
```

O primeiro comando registra o marketplace `petrinhu`. O segundo instala o plugin `bigtech`.

Se você é um agente de IA instalando este plugin a pedido de um usuário, veja [AGENTS.md](AGENTS.md).

## Uso

As 3 skills são os pontos de entrada. Invoque por barra ou descreva a intenção em linguagem natural; o reforço de modo roteia o pedido para a skill certa.

### `/bigtech`: montar a constelação

Camada de negócio e liderança (produto, marketing, vendas, jurídico, finanças, release). Invoca o Chief of Staff (Cósimo), que classifica o porte, escolhe a variante de pipeline e devolve o mapa de ativação: quais C-levels e operacionais ligar, em quais das 12 fases.

```
/bigtech ./meu-projeto
/bigtech "app de agenda para clínicas" --porte early --dispatch
```

Use quando quiser "montar o time", "organizar como bigtech", "qual pipeline e quais agents", "quem lidera isso" ou "classificar o porte".

### `/proj_software`: motor de SDLC

Orquestra o ciclo de vida de software em 5 macrofases, alocando os agents de engenharia por nível, com gatekeeper anti-over-engineering e segurança transversal (shift-left). É para onde o `/bigtech` delega a execução de engenharia.

```
/proj_software
/proj_software "API de pagamentos com idempotência"
```

Use quando começar um projeto novo de software: "vou criar um software", "novo sistema", "construir feature", "qual fluxo seguir".

### `/tab_pendencias`: tabela de planejamento WSJF

Cria e mantém uma tabela de pendências ordenada de cima para baixo na sequência que minimiza retrabalho, combinando ordenação topológica (dependência) com WSJF (valor). A coluna "Onda" marca passos de igual valor que rodam em paralelo.

```
/tab_pendencias --create
/tab_pendencias --show
/tab_pendencias --reorder
```

Use para planejar passos, ordenar backlog, ou perguntar "o que falta" e "em que ordem fazer".

## Agents

### C-level (12)

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

### Operacionais (38)

**Engenharia (14):** `software-architect`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `devops-sre`, `performance-engineer`, `network-engineer`, `network-security-engineer`, `security-engineer`, `qa-engineer`, `release-manager`.

**Dados e IA (4):** `data-engineer`, `data-scientist`, `ml-engineer`, `applied-ai-engineer`.

**Produto, UX e Design (7):** `product-manager`, `business-analyst`, `ux-researcher`, `ux-ui-designer`, `ux-writer`, `accessibility-specialist`, `art-director`.

**Gestão e Pessoas (2):** `engineering-manager`, `scrum-master`.

**Marketing, Crescimento e Receita (6):** `content-seo`, `pr-comms`, `growth-engineer`, `community-manager`, `customer-success`, `revenue-ops`.

**Suporte, Docs, Legal e i18n (5):** `support-engineer`, `technical-writer`, `compliance-legal`, `internal-auditor`, `i18n-l10n-specialist`.

## Hooks

| Hook | Evento | Função |
|---|---|---|
| `tdd_guard.py` | PreToolUse (Write/Edit) | Guard-rail de TDD: bloqueia código fora do ciclo red, green, refactor. Opt-in por projeto. |
| `tdd_runner.py` | PostToolUse (Write/Edit) | Roda a suíte de testes após a edição e reporta o resultado ao ciclo TDD. |
| `bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto (docs-bootstrap), avisa se o `caveman` está ativo e sugere as dependências ausentes. |
| `bigtech_porte_reminder.py` | SessionStart | Reavalia o porte do projeto (escala para cima ou para baixo); só dispara em projeto de código ainda não classificado. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo bigtech (anti-drift) e roteia ativação por linguagem natural para `/bigtech`. Escopado por marcador, anti-ruído. |

## Compatibilidade

**Incompatível com o plugin `caveman`.** O `caveman` comprime a comunicação e conflita com o reforço de modo deste plugin. Desative o `caveman` antes de usar o `bigtech`; o hook de sessão avisa caso detecte os dois ativos ao mesmo tempo.

**Dependências sugeridas:** `playwright` e `superpowers`. Não são obrigatórias, mas habilitam a experiência completa (automação de navegador e fluxos avançados). Instale-as para tirar o máximo do plugin; o hook de sessão sugere a instalação quando estão ausentes.

## Documentação

Os manuais de governança acompanham o plugin em `docs/` e são injetados no contexto da sessão:

- `docs/ORG.md`: manual de governança da constelação (RACI, portes, roteamento de pipeline).
- `docs/pipeline_release_1.0.md`: pipeline de release em 12 fases, da ideia ao 1.0.
- `docs/lideranca_pipeline_release.md`: teoria de liderança C-level e a constelação nomeada.
- `docs/TOOLING.md`: catálogo de ferramentas livres (FOSS) por agent.
- `docs/manuals/`: contrato de qualidade, testes, agile, checklist de deploy e auditorias.
- `docs/principles/`: princípios de arquitetura, metodologia agile, anti-patterns e limites de hardware.

## Segurança

Os hooks executam código na sua máquina e o `tdd_runner` pode rodar o comando de teste declarado pelo projeto que você abrir (paridade de confiança com `make test`/`npm test`). Antes de usar com repositórios de terceiros, leia [SECURITY.md](./SECURITY.md): modelo de confiança, opt-in e como desativar.

## Licença

Distribuído sob a licença [Apache-2.0](./LICENSE).
