# Frescor da tabela de pendências (TODO.md) no sprint

> **Tipo (Diátaxis):** Explanation + Reference (convenção). **Audiência:** quem opera o plugin (o líder) e os agents de implementação.
> **Escopo:** convenção do plugin para manter o `TODO.md` de projeto fresco durante um sprint. Complementa a skill `/tab_pendencias`.
> **Last-reviewed:** 2026-06-20 · **Owner:** mantenedor do projeto · **Aplica a:** todo projeto com `TODO.md` (skill `/tab_pendencias`).

Este documento registra a **convenção de frescor** (Camadas 0+1, já adotadas pelo plugin) e descreve, de forma genérica, uma **escada de escalonamento** opcional (Camadas 2-4) para quem mais tarde precisar de mais automação. O foco é a convenção: marcar status é barato e manual; reordenar é caro e raro.

---

## Causa-raiz

A `TODO.md` apodrece porque um único verbo informal - "atualizar a tabela" - **acopla duas operações de naturezas opostas**:

1. **Sincronizar status** (marcar um item como concluído): operação **determinística, barata, frequente** e **derivável do git** (o commit que fecha o trabalho já existe). Não exige julgamento.
2. **Re-planejar** (adicionar trabalho novo + reordenar por dependência topológica + WSJF + ondas): operação de **julgamento do time de agents**, **cara** e **rara**. Exige contexto, priorização e decisão.

O custo alto de (2) **contamina** (1): por estarem sob o mesmo verbo, "marcar um item" passa a *parecer* que exige convocar o time de agents. Como convocar é caro, ninguém marca. O resultado é que a maior parte da defasagem observada é da categoria **"feito mas não marcado"** - trabalho concluído cujo status nunca foi tocado, não trabalho novo a planejar.

**A cura é desacoplar status de prioridade.** Marcar status vira um ato barato, mecânico e local; re-planejar vira um ato consciente, raro e disparado por mudança real de input de priorização.

---

## Status (mecânico) vs prioridade (julgamento)

A distinção é a ideia central deste documento:

| Eixo | O que é | Custo | Frequência | Quem faz |
|---|---|---|---|---|
| **Status** | Em que ponto o item está (`🔍`, `✅`, etc.) | Barato | Frequente (a cada item fechado) | Quem abre o PR, à mão, no mesmo commit |
| **Prioridade** | Em que ordem fazer (dependência + WSJF + ondas) | Caro | Rara (só com input novo) | O time de agents, via `/tab_pendencias --reorder` |

Status é higiene barata e local. Prioridade é decisão cara e soberana. **Nunca tratá-las com o mesmo verbo.**

---

## Por que NÃO monitor, loop nem agente sempre-ativo

Vigilância contínua (um daemon, loop ou agente que vigia a tabela o tempo todo) **reordena o que não mudou** - queima recurso e reintroduz o anti-padrão clássico do Scrum Master que vira micromanager, repriorizando backlog estável sem sinal novo.

O sinal certo para agir é:

- **Event-driven** - no commit/PR que fecha trabalho (sincronizar status); e
- **Periódico** - por cadência (review de sprint, INBOX não-vazia) para re-planejar.

**Nunca contínuo.** Frequência alta sem mudança de input não produz frescor; produz ruído e desperdício.

---

## Camada 0 - Definition of Done de status (sempre)

Ao fechar trabalho, **toque a coluna `Status` do item no MESMO commit/PR** que entrega o trabalho. Regras:

- **Cite o ID do item na mensagem do commit** (corpo ou footer do Conventional Commit). Use o ID que o projeto **já tem** (`V-NN`, `ORG-NN`, `Fx.y`, etc.). Não inventar esquema novo, não renumerar.
- **Use o glyph correto** do vocabulário da skill `/tab_pendencias`:
  - Implementação entregue → `🔍 Pendente verificação`. **NUNCA `✅` direto.**
  - `✅ Concluído` **só** após rodar a onda de teste/auditoria correspondente (`TST-*` / `AUD-*`).
- **Marcar status NUNCA dispara o time de agents.** É edição mecânica de uma célula, feita à mão no commit que fecha o item. Não exige a skill `/tab_pendencias`.

Isso evita o **"falso-done"**: o board dizer `✅ Concluído` enquanto o teste ou a auditoria ainda não rodou. O estado intermediário `🔍 Pendente verificação` torna visível o trabalho entregue-mas-não-validado.

> **Por que citar o ID importa.** Como os commits do projeto saem quase sempre pela própria IA (thread principal ou agents, via `git commit`), citar o ID no commit que fecha ou avança um item é o que torna a defasagem rastreável: liga o trabalho entregue à linha da tabela. Por isso a convenção está embarcada nos agents de implementação.

---

## Camada 1 - INBOX (captura agora, prioriza depois) + lembrete (sempre)

Trabalho novo descoberto durante o sprint vai para a **INBOX imediatamente** - 1 linha, **sem ordenar**. Captura barata agora; priorização cara depois.

- **Local padrão:** seção `## INBOX (descobertas não priorizadas)` no fim do `TODO.md` de projeto.
- **Quando há worktrees / PRs paralelos:** trocar a seção por **um arquivo-por-descoberta** em `inbox/` (ex.: `inbox/2026-06-20-cache-stale.md`), para não gerar conflito de merge na mesma linha do `TODO.md`.
- **Regra de conflito da INBOX:** em merge, sempre **UNIÃO**, **NUNCA descartar linha**. Toda descoberta sobrevive.
- **Drenagem:** a skill `/tab_pendencias` **drena a INBOX** no `--create` / `--reorder` - integra cada item na ordenação (dependência + WSJF + ondas) e **esvazia** a INBOX. **INBOX não-vazia é o gatilho natural de reordenar.**

O hook `tab_pendencias_reminder.py` (incluído no plugin) continua lembrando:

- **`SessionStart`** - por defasagem detectada no git (commits que fecharam trabalho sem status tocado);
- **`UserPromptSubmit`** - por tempo de sessão decorrido.

A mensagem do hook **distingue as duas ações**: a barata (sincronizar status - faça você mesmo no commit) versus a cara (reordenar - ato consciente do time, só com input novo). O hook só lembra; nunca bloqueia nem reordena.

---

## Dois tipos de TODO.md

A convenção acima **só se aplica a um dos tipos**. Não confundir:

- **De projeto** - itens editáveis, a relação item↔commit faz sentido. **Aqui** valem Camada 0 (DoD de status), Camada 1 (INBOX) e a regra de ouro.
- **Hub agregador** - contagens derivadas de vários projetos (ex.: painel cross-project). **NÃO** marcar à mão, **NÃO** usar INBOX. **Regenerar por script** a partir das fontes. Não aplicar a convenção de projeto ao hub - ali a fonte da verdade são os `TODO.md` de projeto, e o hub é uma *view*.

---

## Regra de ouro

> **Marcar status nunca dispara o time de agents.**
>
> **Reordenar só quando um input de priorização muda** - nova dependência, item ficou urgente, ou INBOX não-vazia - sempre como **ato consciente na thread principal** (ou via PR que o usuário aprova), respeitando a **autoridade do usuário sobre prioridade**.

Status é higiene barata e local. Prioridade é decisão cara e soberana. Nunca tratá-las com o mesmo verbo.

---

## Escada de escalonamento (opcional, só com gatilho)

As camadas abaixo **não fazem parte do plugin** e **não estão adotadas**. Cada uma só deve ser adotada com **evidência concreta de que o mínimo (Camadas 0+1) falhou** - caso contrário, o aparato custa mais do que cura. Estão descritas de forma genérica; a escolha de ferramenta é sua.

| Camada | O que é | Comportamento | Gatilho para adotar | Saída |
|---|---|---|---|---|
| **2 - Aviso de frescor no CI (warning-only)** | Job de CI que sinaliza defasagem (por exemplo, abrindo uma issue persistente no repositório) | **Nunca bloqueia merge.** Só sinaliza. | Vários agents/worktrees fazem a tabela divergir mais rápido do que o humano acompanha | Issue de aviso |
| **3 - Rotina agendada determinística** | Tarefa agendada de **baixa frequência, condicional a atividade** | Faz **só a higiene mecânica** (sincronizar status, drenar INBOX, abrir PR). **NÃO reordena por WSJF** - uma rotina cega reordenaria com contexto *stale*. | Sprint formal + cadência de review estabelecida | Sempre **PR**, nunca auto-merge |
| **4 - Fonte-da-verdade → issues + milestones do repositório** | Status passa a viver em **issues** (fechamento nativo via palavra-chave do tipo `Closes #N`); `TODO.md` vira *view* gerada | Alto valor; **difícil de reverter** (one-way door) | `>30-40` itens vivos **ou** entrada de colaborador externo | Decisão do usuário via **AskUserQuestion** |

**Nota sobre a Camada 4:** mesmo migrando para issues, **reordenar por WSJF continua exigindo a skill** `/tab_pendencias`. Ou seja, mover o *status* para issues resolve o fechamento nativo, mas **não** elimina a necessidade do re-planejamento por julgamento. Além disso, nem todo servidor de issues move um card para "Done" de forma nativa; verifique antes de assumir essa migração.

### Mecânico vs julgamento, local vs externo

Há **dois eixos independentes**: *mecânico × julgamento* (o que se automatiza) e *local × externo* (onde roda). A escada acima descreve versões externas (servidor de CI, agendador na nuvem, servidor de issues), mas cada camada tem um equivalente **local, on-machine**, para quem prefere manter a execução sob controle e o dado fora da rede (relevante sob LGPD). Local resolve "onde", não "o quê": **mesmo uma automação local não deve reordenar** por WSJF, porque o contexto fica *stale*.

A metade **mecânica** do frescor (sincronizar status, drenar INBOX) é determinística e pode rodar offline; um **git hook local opcional** pode automatizar esse sync da parte mecânica - apenas marcando status a partir dos IDs citados nos commits, **nunca `✅` e nunca reordenando**. A metade de **julgamento** (reordenar) usa a skill `/tab_pendencias` e depende da inferência do modelo; é a única dependência externa irredutível.

---

## Riscos residuais

- **Falso-done residual** - se a onda de teste/auditoria nunca roda, o item fica eterno `🔍 Pendente verificação`. Mitigação: garantir que `TST-*`/`AUD-*` entrem no plano da onda.
- **Dependência de disciplina humana** - a DoD de status (Camada 0) ainda depende de quem abre o PR lembrar de tocar a célula e citar o ID. **Medir adesão** (quantos PRs que fecham trabalho também tocam status).
- **INBOX vira lixeira** - se não for drenada com regularidade, acumula. A drenagem no `--create`/`--reorder` é a válvula; INBOX gigante é sinal de re-planejamento atrasado.
- **Fadiga de alerta** - o hook pode incomodar. **Medir a taxa de disparo**; se subir, recuar a sensibilidade (config `.tab-staleness.json` na raiz do projeto).
- **Custo do próprio aparato** - manter CI/rotina/issues tem custo. Por isso **cada camada acima do mínimo é condicional a evidência** de falha, nunca preventiva.

---

## Ver também

- Skill `/tab_pendencias` (seção "Frescor: manter a tabela viva no sprint") - a convenção operacional resumida.
- [manuals/AGILE.md](manuals/AGILE.md) - WSJF, fluxo e WIP.
- [manuals/TESTES.md](manuals/TESTES.md) e [manuals/AUDITORIAS.md](manuals/AUDITORIAS.md) - as ondas `TST-*`/`AUD-*` que liberam o `✅`.

## Fontes

- https://arxiv.org/abs/2507.10753 - grooming com GenAI: fronteira entre o que é determinístico e o que exige julgamento.
- https://getnave.com/blog/aging-work-in-kanban/ - Work Item Age como gatilho de ação (envelhecimento, não vigilância contínua).
- https://dosu.dev/blog/score-documentation-freshness-in-ci - freshness gate em dois níveis (aviso vs bloqueio).
- https://github.com/alstr/todo-to-issue-action - sync mecânico de TODOs via diff.
