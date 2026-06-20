---
name: tab_pendencias
description: 'Cria e gerencia tabela de pendências/planejamento ORDENADA para minimizar retrabalho. No --create (e --reorder) orquestra um time de agents (Cosmo/COO coordena software-architect + tech-lead + product-manager + engineering-manager + scrum-master) para sequenciar por dependência (topological) e valor (WSJF), com coluna "Onda" sinalizando passos de igual valor paralelizáveis. Use sempre que o usuário pedir criar/mostrar/atualizar tabela de pendências, planejar passos, ordenar backlog, "o que falta", "em que ordem fazer", ou invocar /tab_pendencias. Em qualquer comando, garante (com dupla confirmação) testes não-unitários e auditorias aplicáveis ao stack como itens de fechamento; cria ./TESTES.md e ./AUDITORIAS.md do projeto quando faltam. Argumentos: --create, --reorder, --show, --main, --add_tests_audit.'
argument-hint: '--create | --reorder | --show | --main | --add_tests_audit'
allowed-tools: [Read, Write, Edit, Glob, Grep, Agent, TodoWrite]
---

# tab_pendencias

Cria, ordena e exibe tabelas de planejamento. O diferencial: a tabela sai **ordenada de cima para baixo na ordem de execução que minimiza retrabalho**, com a coluna **Onda** marcando os passos de igual valor que podem rodar em paralelo.

O usuário invocou com: $ARGUMENTS

---

## Schema canônico (9 colunas)

```markdown
| ID | Onda | Grupo | Descrição Técnica | Prioridade | Pré-requisito | Dificuldade | Status | Estado Auditado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
```

A ordem das linhas (de cima para baixo) É a ordem de execução recomendada. A coluna `Onda` agrupa passos paralelizáveis.

### Valores por coluna

- **Onda**: `W1`, `W2`, `W3`, ... (leva de execução). Itens da mesma Onda não dependem entre si e têm valor comparável: **podem rodar em paralelo (igual valor)**. `—` para itens concluídos ou fora do fluxo.
- **Prioridade**: Alta / Média / Baixa.
- **Pré-requisito**: `—` (nenhum) ou ID(s) que precisam estar concluídos antes (ex: `F1.4`, `F2.1, F2.2`).
- **Dificuldade**: Alta / Média / Baixa (usada como Job Size no WSJF).
- **Status**: símbolo + texto.

| Status | Significado |
|:---|:---|
| ✅ Concluído | finalizada |
| 🔄 Em andamento | em progresso |
| 🟡 Parcial | feito em parte |
| ⏳ Pendente | não iniciado |
| 💡 Decisão tomada | abordagem definida, implementação futura |
| 🎨 Pendente design | aguarda spec/brainstorm |
| 🔍 Pendente verificação | implementado, aguarda validação |

- **Estado Auditado**: `—` (não auditado) | `✓` (aprovado) | `⚠` (com ressalvas).

> Compatibilidade: tabelas legadas de 8 colunas (sem Onda) continuam válidas para `--show`/`--main`. Ao rodar `--reorder` numa tabela de 8 colunas, a skill adiciona a coluna Onda.

---

## Frescor: manter a tabela viva no sprint

Para a tabela não apodrecer durante o sprint, separe SEMPRE duas operações de naturezas opostas:

- **Sincronizar status** (MECÂNICO, barato, frequente, no commit): ao fechar trabalho, toque a coluna `Status` do item no MESMO PR, com o ID que o projeto JÁ tem (não renumerar). Implementação entregue vira `🔍 Pendente verificação` (NUNCA `✅` direto); `✅ Concluído` só após a onda `TST-*`/`AUD-*` correspondente. **Marcar status nunca dispara o time de agents** e não exige esta skill: é uma edição manual de uma célula, feita no mesmo commit que entrega o item.
- **Reordenar** (JULGAMENTO, caro, raro): só via `--reorder`, e só quando um input de priorização muda (nova dependência, item ficou urgente, INBOX não-vazia). Nunca por passagem de tempo, loop ou monitor contínuo.

Regra de ouro: **Status no commit; reordenar só quando um input de priorização muda.** Atualizar o `Status` é parte do Definition of Done do item (convenção, não comando): edite a célula à mão no PR que fecha o trabalho. Esta skill cobre o **planejamento** (`--reorder`, julgamento); a sincronização de status é a parte mecânica e fica a cargo da convenção do commit.

### INBOX (captura agora, prioriza depois)

Trabalho novo descoberto no meio do sprint NÃO espera reordenar: vai para a INBOX na hora (1 linha), sem Onda nem WSJF.

- **Local:** seção no FIM do `TODO.md` de projeto:
  ```markdown
  ## INBOX (descobertas não priorizadas)
  - <ID tentativo ou —>: descrição curta do que apareceu
  ```
- **Concorrência (worktrees/PRs paralelos):** se vários agents/branches anexam ao mesmo tempo, troque a seção por um arquivo-por-descoberta em `inbox/` (ex: `inbox/2026-06-20-slug.md`) para não gerar conflito de merge. Resolução de conflito da INBOX: **sempre união, NUNCA descartar uma linha** (perder item é o que a INBOX existe para evitar).
- **Dreno:** `--create` e `--reorder` ESVAZIAM a INBOX (e o `inbox/`), integrando cada item na ordenação (topological + WSJF + ondas) e removendo-o da INBOX. INBOX não-vazia é gatilho natural de `--reorder`.

> **Dois tipos de `TODO.md`:** o de **projeto** (itens editáveis; item↔commit faz sentido; esta seção se aplica) e o **hub agregador** (contagens derivadas de vários projetos; NÃO marcar à mão nem usar INBOX - regenerar por script). A convenção de frescor vale no de projeto.

---

## Método de ordenação (anti-retrabalho)

Aplicado no `--create` e `--reorder`:

1. **Topological sort por `Pré-requisito`.** Nada aparece antes do que ele depende. Quebra ciclo se houver (sinaliza).
2. **Dentro de cada nível topológico, ordena por WSJF** (Weighted Shortest Job First):
   `WSJF = Custo de Atraso / Job Size`, onde Custo de Atraso = valor de negócio + criticidade temporal + redução de risco/viabilização; Job Size ~ `Dificuldade`. Maior WSJF primeiro.
   Efeito anti-retrabalho: **fundação e decisões one-way-door sobem ao topo** (errar nelas é o retrabalho mais caro).
3. **Agrupa em Ondas.** Itens no mesmo nível topológico, sem dependência mútua e com WSJF comparável = mesma Onda (`W1`, `W2`, ...). Sinaliza o que é paralelizável (igual valor).

### Tabela de scoring WSJF (obrigatória em scale/bigtech, conforme [AGILE](../../docs/manuals/AGILE.md) §17.2)

Em contexto SAFe (porte scale-up/bigtech, definido pelo Chief of Staff), NÃO apresentar a priorização sem a tabela de scoring que justifica cada WSJF (AGILE §17.2 é taxativo). Emitir junto:

```markdown
| ID | Item | Valor (1-20) | Criticidade (1-20) | Redução de Risco (1-20) | CoD | Job Size (1-20) | WSJF | Rank |
```

`CoD = Valor + Criticidade + Redução de Risco`; `WSJF = CoD / Job Size`. Rank = ordem decrescente de WSJF. Em projeto pequeno (solo/early), o WSJF pode ser qualitativo (sem a tabela completa), respeitando o anti-OE.

### Testes e auditoria: ordem inviolável (TDD + shift-left)

- **Teste unitário (T1) = TDD:** roda COM o item de implementação (escrito antes/junto do código), garantido pelo hook de TDD (tdd_guard/tdd_runner). **NÃO vira item** na tabela; não criar "escrever testes unitários" como passo solto.
- **Demais testes (T2-T15) são downstream:** estática, integração, e2e, segurança (secrets, SQLi, CVE), memória, pré-CI. Não existem antes do sistema; entram como itens de fechamento (`TST-*`) numa onda APÓS a implementação. São injetados pelo fluxo "Injeção automática de testes e auditorias".
- **Auditoria é downstream de código+teste:** todo item `AUD-*` tem `Pré-requisito` = os itens de código+teste que audita; cai numa Onda POSTERIOR aos testes.
- **Invariante:** nunca agendar teste/auditoria antes do que ele cobre. Se a ordenação produzir isso, a dependência está errada (corrigir o `Pré-requisito`).

---

## `--create` e `--reorder` (orquestrado)

### Gate anti over-engineering (sempre primeiro)

**Quem decide a abordagem de montagem (em `--create` e `--reorder`) é o Cósimo (Chief of Staff)**: ele classifica a complexidade da tabela (número de itens, dependências cruzadas, criticidade) e determina thread direta (simples) vs orquestrar o time (complexa). Calibrar pela complexidade da tabela (ver `cosimo-chief-of-staff` / [ORG](../../docs/ORG.md)):
- **Tabela pequena/simples** (até ~8 itens, baixa complexidade e poucas dependências cruzadas): **NÃO** spawnar o time. A própria thread aplica o método (topological + WSJF + ondas) e escreve. Anti-OE por complexidade da tabela, não por porte "solo" (a constelação está sempre disponível).
- **Tabela grande/complexa** (muitos itens, dependências cruzadas, cross-funcional): orquestrar o time abaixo.

### Orquestração (tabela grande)

Quando o Cósimo determina "via time", o **Cosmo (COO) coordena a montagem**: a skill (thread principal) dispara os agents em paralelo, cada um com a lista bruta de itens, para sua lente:

| Agent | Lente que devolve |
|---|---|
| `software-architect` + `tech-lead` | grafo de dependência técnica + flags de fundação / one-way-door |
| `product-manager` | Custo de Atraso por item (valor + urgência + risco) |
| `engineering-manager` | Job Size / esforço / capacity por item |
| `scrum-master` | topological sort + agrupamento em ondas + limite de WIP |

Depois a skill dispara `cosmo-coo` com os quatro retornos para **consolidar** na tabela final: ordem de linha (execução) + coluna Onda. Cosmo resolve conflito de lente (ex: valor alto x dependência não resolvida vence a dependência).

Subagent não dispara subagent: quem dispara cada agent é a thread principal (a skill); os agents devolvem dados, a skill/Cosmo consolidam.

### Passos do `--create`

1. Coletar os itens (do usuário; se vier de um doc, ler).
2. Perguntar só o essencial: caminho (sugerir `TODO.md` na raiz) e título do projeto.
3. Aplicar o gate anti-OE: **o Cósimo decide a abordagem** (thread direta vs time) pela complexidade da tabela.
4. Montar a tabela: thread direta (simples) OU **time coordenado pelo Cosmo** (complexa), conforme a decisão do Cósimo.
5. Escrever `TODO.md` com as 9 colunas, linhas em ordem de execução, Onda preenchida. Se houver INBOX / `inbox/`, drená-la (integrar os itens na ordenação e esvaziar).

### `--reorder`

Reordena uma tabela existente (mesmo método e gate). Preserva IDs, Status e Estado Auditado; só recalcula ordem das linhas e a coluna Onda. **Drena a INBOX** (e `inbox/`): integra cada descoberta na ordenação e a remove da INBOX. Útil quando novas pendências entraram ou dependências mudaram.

### Gatilho de reordenação (proporcional ao tamanho e à repercussão)

Quando uma pendência NOVA entra, decidir entre **só anexar** ou **reordenar tudo**, proporcional ao tamanho da solicitação e ao impacto no projeto inteiro. **O Cósimo (Chief of Staff) decide a abordagem** (só anexar vs reordenar) pela complexidade/repercussão; quando reordena via time, **o Cosmo (COO) coordena a montagem** (dispara as lentes e consolida). Em caso dúbio sobre a repercussão, o Cosmo (COO) julga.

- **Só anexar** (sem reordenar): item pequeno, escopo local, sem criar dependência sobre itens já ordenados, não mexe em fundação nem one-way-door. Adicionar na Onda adequada (ou ao fim) e seguir.
- **Reordenar (`--reorder`, orquestra o time):** quando o item novo
  - cria ou altera dependência de itens existentes, ou
  - é fundação / decisão one-way-door (errar reordena tudo a jusante), ou
  - tem repercussão cross-módulo ou no projeto inteiro, ou
  - é grande o bastante para mudar o WSJF relativo de vários itens.

Regra de ouro: o custo de reordenar deve ser menor que o retrabalho que ele evita. Reordenação total NÃO é automática por padrão (anti-ruído); dispara pelos critérios acima ou sob comando explícito.

---

## Injeção automática de testes e auditorias

Executa no INÍCIO de TODO comando (--create, --reorder, --show, --main), antes de
exibir/escrever a tabela. Garante que os testes não-unitários e auditorias aplicáveis
estejam planejados. Catálogo e regras: `references/catalogo-testes-auditorias.md`.

> **Execução dos itens segue a política de ferramenta ausente** (agnóstica de SO; auto-instalar
> com confirmação, nunca silencioso): ao rodar um `TST-*`/`AUD-*` cuja ferramenta falta, detectar
> conforme o SO (`command -v` no Unix/WSL; `Get-Command` ou `where` no Windows), OFERECER instalar
> via AskUserQuestion com o comando adequado ao SO e ao gerenciador disponível
> (apt/dnf/brew/winget/choco/scoop), preferindo gerenciadores cross-platform (pip/uv, cargo, npm)
> quando a ferramenta os suporta e, sem confirmação, deixar o item pendente com nota - jamais pular
> em silêncio. Detalhe no catálogo e nos manuais [TESTES](../../docs/manuals/TESTES.md) / [AUDITORIAS](../../docs/manuals/AUDITORIAS.md).

### Passos

1. **Detectar stack + características**: Glob na raiz para sinais de arquivo; Grep/Read de deps e imports para sinais de conteúdo (rede/API, protocolo, framework). Ver o reference.
2. **Calcular itens aplicáveis**: TST-* (T2-T15 podados; T1 SEMPRE fora) + AUD-* (podados).
3. **Garantir manuais do projeto**: se `./TESTES.md` ou `./AUDITORIAS.md` faltam, marcá-los para criação (do reference, podados). Nunca sobrescrever manual existente.
4. **Conferir a tabela** `TODO.md`: quais TST-*/AUD-* já existem (por ID).
5. Se **nada falta** (itens presentes e manuais existem): idempotente, NÃO pergunta, NÃO escreve. Segue o comando.
6. Se **falta algo**: rodar o fluxo de confirmação abaixo.

### Fluxo de confirmação (nunca silencioso)

PERGUNTA 1 (AskUserQuestion, recomendação ALTA a favor):
> "Faltam testes/auditorias no planejamento deste projeto. Acrescentar agora?"
> Opções: [Acrescentar (fortemente recomendado)] | [Não acrescentar]

- Acrescentar -> aplicar (seção "Aplicar") + avisar o que mudou. Segue o comando.
- Não -> PERGUNTA 2 (reforço):
  > "Testes e auditoria são Definition of Done: previnem retrabalho, vulnerabilidades
  >  (secrets, SQLi, CVE) e regressões. Seguir mesmo assim sem eles?"
  > Opções: [Acrescentar agora (recomendado)] | [Seguir sem testes]
  - Acrescentar -> aplicar + avisar. Segue o comando.
  - Seguir sem -> executa o comando SEM testes; avisar:
    "OK. Pode acrescentar depois com: /tab_pendencias --add_tests_audit"

### Aplicar (criar manuais + injetar itens)

- Criar `./TESTES.md` e/ou `./AUDITORIAS.md` se faltarem (podados pro stack).
- Injetar na tabela apenas os IDs AUSENTES (idempotente):
  - **TST-*** -> `Grupo` = `Testes`; `Onda` = uma após a última de implementação; `Pré-requisito` = itens de implementação cobertos (na prática, a última onda funcional); `Status` = ⏳; `Estado Auditado` = `—`; `Descrição` referencia `TESTES.md`.
  - **AUD-*** -> `Grupo` = `Auditoria`; `Onda` = final, após os testes; `Pré-requisito` = os TST-* + última onda de implementação; `Status` = ⏳; `Estado Auditado` = `—`; `Descrição` referencia `AUDITORIAS.md`.
- Reaplicar a ordenação (topological + WSJF + ondas) para encaixar os novos itens respeitando a ordem inviolável.
- Avisar: "criei <arquivos>; injetei N testes + M auditorias nas ondas <...>".

### --add_tests_audit

Comando dedicado: pula as PERGUNTAS (o usuário já pediu); roda "Aplicar" direto;
idempotente; avisa o que fez (ou "nada a fazer" se já completo).

### Hook de TDD ausente

T1 sempre fora. Se o projeto NÃO tem `.claude/tdd-guard.json`, avisar uma vez:
"TDD não está sob hook neste projeto; ative o hook ou inclua testes unitários
manualmente." (não bloqueia).

### Modo não-interativo

Sem humano para responder o AskUserQuestion (ex.: invocação por workflow/agente):
NÃO injeta (respeita "não silencioso"); executa o comando e emite aviso proeminente
recomendando `/tab_pendencias --add_tests_audit`.

---

## `--show` / `--main`

- **`--show`**: localizar `TODO.md` na raiz (depois `PLANNING.md`, depois perguntar). Exibir tabela **completa**, incluindo `✅`.
- **`--main`**: mesma localização, **filtrar fora** `✅`. Mostrar só ⏳ 🔄 🟡 💡 🎨 🔍, preservando a ordem (Onda) das pendentes.

## Invocação sem argumento

- "mostrar pendências" / "o que falta" / "em que ordem" → `--main`
- "tabela completa" / "histórico" → `--show`
- "criar tabela" / "planejar passos" → `--create`
- "reordenar" / "minimizar retrabalho" / "sequenciar" → `--reorder`
- "acrescentar testes" / "adicionar auditoria" / "faltam testes" → `--add_tests_audit`

---

## Arquivo canônico

**A tabela é sempre `TODO.md` na raiz do projeto.** Única localização válida. Toda leitura e escrita em `TODO.md`. Se não existir, criar sem perguntar. Nunca usar `PLANNING.md` como destino.

## Registro no CLAUDE.md

Ao criar/confirmar o `TODO.md` num projeto, verificar se o `CLAUDE.md` da raiz já referencia o `TODO.md`. Se não, acrescentar (sem duplicar):

```
## Pendências
A tabela de pendências e planejamento do projeto está em `TODO.md` na raiz (ordenada por execução, coluna Onda marca passos paralelizáveis).
```

## Integração

- Agents: `cosmo-coo` (orquestra), `software-architect`, `tech-lead`, `product-manager`, `engineering-manager`, `scrum-master`. Constelação em [ORG](../../docs/ORG.md).
- Manuais: [AGILE](../../docs/manuals/AGILE.md) (WSJF, fluxo, WIP), [CONTRACT](../../docs/manuals/CONTRACT.md). Ferramentas por agent: [TOOLING](../../docs/TOOLING.md).
- Linguagem: pt-br.
