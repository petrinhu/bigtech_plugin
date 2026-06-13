# tab_pendencias

![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Type](https://img.shields.io/badge/type-Claude%20Code%20Skill-blue)
![Status](https://img.shields.io/badge/status-stable-brightgreen)
![Language](https://img.shields.io/badge/lang-pt--br%20%2F%20en-lightgrey)
![File](https://img.shields.io/badge/canonical-TODO.md-yellow)

---

## Português (pt-br)

Skill do Claude Code que gerencia a tabela de pendências/planejamento de projetos no padrão `TODO.md` tabular: cabeçalho fixo, símbolos de status visuais, dependências por ID, auditoria opcional. A tabela sai **ordenada na ordem de execução que minimiza retrabalho** (topological sort + WSJF), com a coluna **Onda** marcando passos paralelizáveis.

### Instalação

Esta skill é distribuída como parte do plugin `bigtech`. Instale o plugin e a skill fica disponível automaticamente; não há passo de instalação manual separado.

Após instalar o plugin, a skill é auto-discovered pelo Claude Code. Trigger automático em frases como "criar tabela", "mostrar pendências", "mostrar tarefas", "o que falta", "em que ordem fazer", "histórico completo", "atualizar status".

Manual via tool `Skill`:
```
Skill: tab_pendencias
```

Ou comando slash: `/tab_pendencias [--create | --reorder | --show | --main | --add_tests_audit]`

### Estrutura padrão da tabela (9 colunas)

```markdown
| ID | Onda | Grupo | Descrição Técnica | Prioridade | Pré-requisito | Dificuldade | Status | Estado Auditado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
```

A ordem das linhas (de cima para baixo) é a ordem de execução recomendada. A coluna `Onda` agrupa passos de igual valor que podem rodar em paralelo.

### Valores válidos

| Coluna | Valores |
|---|---|
| **Onda** | `W1`, `W2`, `W3`, ... (leva de execução); traço para item concluído ou fora do fluxo |
| **Prioridade** | Alta / Média / Baixa |
| **Pré-requisito** | traço (nenhum) ou ID(s) (`F1.4`, `F2.1, F2.2`) |
| **Dificuldade** | Alta / Média / Baixa |
| **Estado Auditado** | traço (não auditado) / `✓` (aprovado) / `⚠` (com ressalvas) |

> Nota: onde a tabela mostra "traço", o valor literal da célula no `TODO.md` é o caractere de travessão. Veja o schema canônico em `SKILL.md`.

### Status (símbolo + texto)

| Valor | Significado |
|---|---|
| ✅ Concluído | Tarefa finalizada |
| 🔄 Em andamento | Trabalho em progresso |
| 🟡 Parcial | Feito em parte |
| ⏳ Pendente | Não iniciado |
| 💡 Decisão tomada | Abordagem definida, implementação futura |
| 🎨 Pendente design | Aguarda spec/brainstorm |
| 🔍 Pendente verificação | Implementado, aguarda validação |

### Argumentos

| Argumento | Comportamento |
|---|---|
| `--create` | Cria nova tabela em `TODO.md` na raiz do projeto, ordenada por execução |
| `--reorder` | Reordena uma tabela existente (preserva IDs, Status e Estado Auditado) |
| `--show` | Exibe tabela completa (incluindo `✅ Concluído`) |
| `--main` | Exibe só pendentes (filtra fora `✅`) |
| `--add_tests_audit` | Injeta testes e auditorias direto (sem perguntar) |

Sem argumento, usa linguagem natural: "mostrar pendências" vira `--main`, "tabela completa" vira `--show`, "criar tabela" vira `--create`, "reordenar" vira `--reorder`, "faltam testes" vira `--add_tests_audit`.

### Testes e auditorias automaticos

Em qualquer comando, a skill verifica se os testes nao-unitarios (T2-T15) e as
auditorias aplicaveis ao stack do projeto estao no planejamento. Se faltam, ela
pergunta (com recomendacao alta) se deve acrescentar; recusando duas vezes, segue
sem eles e lembra do comando `--add_tests_audit` para incluir depois.

- O teste unitario (TDD) NAO entra na tabela: fica a cargo do hook de TDD.
- Os manuais `./TESTES.md` e `./AUDITORIAS.md` sao criados na raiz do projeto
  (podados pro stack) quando faltam, e nunca sobrescritos se ja existem.
- Os itens entram como `TST-*` (testes, apos a implementacao) e `AUD-*` (auditorias,
  nas ondas finais), de forma idempotente.

Comando dedicado: `/tab_pendencias --add_tests_audit` injeta direto, sem perguntar.

### Arquivo canônico

**`TODO.md` na raiz do projeto** é a única localização válida. A skill nunca cria `PENDENCIAS.md`, `TAREFAS.md` ou `BACKLOG.md` paralelos.

### Integração com `CLAUDE.md`

No primeiro uso num projeto, a skill verifica se o `CLAUDE.md` da raiz já referencia `TODO.md`. Se não, acrescenta:

```markdown
## Pendências
A tabela de pendências e planejamento do projeto está em `TODO.md` na raiz.
```

### Licença

Esta skill faz parte do plugin `bigtech` e é distribuída sob a licença [Apache-2.0](../../LICENSE) da raiz do plugin.

---

## English (en-intl)

Claude Code skill that manages the project pendencies/planning table in `TODO.md` tabular standard: fixed header, visual status symbols, ID-based dependencies, optional audit column. The table is emitted **ordered by the execution sequence that minimizes rework** (topological sort + WSJF), with a **Wave** column marking parallelizable steps.

### Installation

This skill ships as part of the `bigtech` plugin. Install the plugin and the skill becomes available automatically; there is no separate manual installation step.

Once the plugin is installed, the skill is auto-discovered by Claude Code. Auto-triggers on phrases like "create table", "show pendencies", "show tasks", "what's left", "in what order", "full history", "update status".

Manual via `Skill` tool:
```
Skill: tab_pendencias
```

Or slash command: `/tab_pendencias [--create | --reorder | --show | --main | --add_tests_audit]`

### Standard table structure (9 columns)

```markdown
| ID | Wave | Group | Technical Description | Priority | Prerequisite | Difficulty | Status | Audit State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
```

Row order (top to bottom) is the recommended execution order. The `Wave` column groups equal-value steps that can run in parallel.

### Valid values

| Column | Values |
|---|---|
| **Wave** | `W1`, `W2`, `W3`, ... (execution wave); dash for done or out-of-flow items |
| **Priority** | High / Medium / Low (Alta / Média / Baixa) |
| **Prerequisite** | dash (none) or ID(s) (`F1.4`, `F2.1, F2.2`) |
| **Difficulty** | High / Medium / Low |
| **Audit State** | dash (not audited) / `✓` (approved) / `⚠` (with caveats) |

> Note: where the table reads "dash", the literal cell value in `TODO.md` is the em-dash glyph. See the canonical schema in `SKILL.md`.

### Status (symbol + text, in pt-br)

| Value | Meaning |
|---|---|
| ✅ Concluído | Task completed |
| 🔄 Em andamento | Work in progress |
| 🟡 Parcial | Partially done |
| ⏳ Pendente | Not started |
| 💡 Decisão tomada | Approach defined, implementation deferred |
| 🎨 Pendente design | Awaiting spec/brainstorm |
| 🔍 Pendente verificação | Implemented, awaiting validation |

### Arguments

| Argument | Behavior |
|---|---|
| `--create` | Creates table at `TODO.md` in project root, ordered by execution |
| `--reorder` | Reorders an existing table (preserves IDs, Status and Audit State) |
| `--show` | Displays full table (including `✅ Concluído`) |
| `--main` | Displays only pending items (filters out `✅`) |
| `--add_tests_audit` | Injects tests and audits directly (without asking) |

Without argument, uses natural language: "show pendencies" becomes `--main`, "full table" becomes `--show`, "create table" becomes `--create`, "reorder" becomes `--reorder`, "tests are missing" becomes `--add_tests_audit`.

### Automatic tests and audits

On any command, the skill checks whether non-unit tests (T2-T15) and stack-applicable
audits are in the plan. If missing, it asks (with a strong recommendation) whether to
add them; on a second refusal it proceeds without them and reminds you of the
`--add_tests_audit` command to add them later.

- The unit test (TDD) does NOT enter the table: it is handled by the TDD hook.
- The `./TESTES.md` and `./AUDITORIAS.md` manuals are created in the project root
  (pruned to the stack) when missing, and never overwritten if they already exist.
- Items enter as `TST-*` (tests, after implementation) and `AUD-*` (audits, in the
  final waves), idempotently.

Dedicated command: `/tab_pendencias --add_tests_audit` injects directly, without asking.

### Canonical file

**`TODO.md` in project root** is the only valid location. The skill never creates `PENDENCIAS.md`, `TAREFAS.md`, or `BACKLOG.md` parallels.

### `CLAUDE.md` integration

On first use in a project, the skill checks whether root `CLAUDE.md` already references `TODO.md`. If not, appends:

```markdown
## Pendências
A tabela de pendências e planejamento do projeto está em `TODO.md` na raiz.
```

### License

This skill is part of the `bigtech` plugin and is distributed under the plugin root's [Apache-2.0](../../LICENSE) license.
