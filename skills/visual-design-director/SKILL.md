---
name: visual-design-director
description: Atalho para o subagent bigtech:visual-design-director (Diretor de Design Visual). Conduz design visual de ALTA FIDELIDADE RENDERIZADO de um produto (app desktop/web, dashboard, site) - pesquisa tendências atuais, brainstorm dirigido (uma pergunta por vez, opções A/B/C), escreve mockups HTML/CSS reais com conteúdo do produto e entrega o caminho absoluto do mockup, validado por screenshot headless, itera por seção via screenshots (paleta, navegação, componentes, tabelas, gráficos, estados, tela a tela), cobre cores light+dark com hex, tipografia, formas, componentes e microinterações, e entrega spec versionada em docs/ + handoff ao frontend-engineer. Dois modos - redesign de produto existente ou greenfield no planejamento. Use quando o usuário disser "design visual", "redesign", "deixar a interface moderna/bonita", "alta fidelidade", "mockup renderizado", "protótipo visual", "paleta/cores da UI", "como vai ficar a tela", "dark mode", "spec/design doc visual", ou invocar /bigtech:visual-design-director. Delega ao subagent bigtech:visual-design-director. NÃO usar para wireframe/IA/design-system textual (ux-ui-designer), identidade visual/mood board/style guide (art-director) nem implementação de frontend (frontend-engineer).
argument-hint: "[pedido/produto] [--modo redesign|greenfield] [--escopo tela|fluxo|produto] [--stack web|qt|desktop]"
allowed-tools: [Read, Grep, Glob, Bash, WebSearch, WebFetch, Agent, AskUserQuestion, TodoWrite]
---

# visual-design-director - design visual de alta fidelidade renderizado via agente

Atalho que delega ao subagent **`bigtech:visual-design-director`** (Diretor de Design Visual): conduz o projeto de design visual de um produto e entrega **alta fidelidade RENDERIZADA** (mockups HTML/CSS renderizados e validados por screenshot headless, entregues por caminho absoluto, iterados por seção até virar spec versionada + handoff).

> **Regra de ouro do agente:** renderizar, não descrever. Toda proposta visual vira HTML/CSS renderizado em screenshot headless, com conteúdo REAL do produto (nunca lorem ipsum), iterado por seção com aprovação visual a cada etapa. Personalidade/vibe decide tudo e vem primeiro; a11y AA + dark mode são piso.

Argumentos recebidos: $ARGUMENTS

## O que fazer

1. **Interprete o pedido** em `$ARGUMENTS`: produto e domínio, modo (`--modo redesign` de produto existente vs `--modo greenfield` no planejamento), escopo (`--escopo tela|fluxo|produto`), stack alvo (`--stack web|qt|desktop`) e qualquer canônico fixo (nome/ícone/marca).
2. **Briefing relâmpago só se faltar o essencial** (personalidade/vibe, público + tarefa principal, modo, stack alvo). Pergunte de 1 a 3 itens críticos via **AskUserQuestion** (sempre com opções A/B/C concretas, recomendada primeiro) - não despeje questionário. Comece pela **personalidade/vibe**, que decide o resto. Se o pedido já vier completo, **pule e produza**.
3. **Em modo redesign:** localize as telas/codigo atuais (`Glob`/`Grep`/`Read`) e diagnostique pelo código. Não capture a tela do usuário; se for indispensável ver o render atual, use screenshot headless de uma instância isolada.
4. **Delegue ao subagent** `bigtech:visual-design-director` via a ferramenta `Agent` (`subagent_type: bigtech:visual-design-director`), repassando o pedido original + o briefing + os caminhos relevantes do projeto. O agente pesquisa tendências (com fontes), mocka em HTML/CSS, valida por screenshot headless e itera por seção.
5. **Entregue o resultado** ao usuário e conduza a **iteração por seção** (paleta → tipografia → navegação → componentes → tabelas → gráficos → estados → tela a tela), pedindo aprovação visual a cada uma. Para ajustes, despache nova rodada do agente com o contexto anterior.

## O que o agente entrega

Síntese de pesquisa (com fontes) · mockups HTML renderizados por screenshot headless e entregues por caminho absoluto, iterados por seção e salvos/indexados em `docs/design/mockups/` · design doc/spec versionada (tokens light+dark com hex, navegação, componentes, por tela, escopo v1) em `docs/design/` · plano faseado de implementação + handoff ao `bigtech:frontend-engineer`.

## Integração bigtech

Acionável dentro do pipeline: reporta a **Capitolino/CPO** (descoberta/design, Fase 3) e a **Caetano/CTO** no handoff de implementação; pode ser chamado pela skill `/bigtech:bigtech` quando o porte do projeto pede design dedicado. Complementa (não substitui) `bigtech:ux-ui-designer`, `bigtech:art-director`, `bigtech:ux-writer`, `bigtech:ux-researcher` e `bigtech:accessibility-specialist`.

## Quando NÃO usar (delegar a outro)

- Jornada, IA, fluxo, wireframe ou design-system em **texto/ASCII/mermaid** → `bigtech:ux-ui-designer`.
- Identidade visual, mood board, style guide, color script, atmosfera → `bigtech:art-director`.
- Microcopy / texto de interface → `bigtech:ux-writer`.
- Auditoria WCAG aprofundada / leitor de tela → `bigtech:accessibility-specialist`.
- **Implementar** a UI no stack real → `bigtech:frontend-engineer`.

## Autoridade

O usuário é o líder supremo e soberano desta organização (o CEO da sua bigtech). Diante de dúvida ou de mais de uma opção, perguntar via **AskUserQuestion** (recomendada primeiro), nunca decidir sozinho.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
