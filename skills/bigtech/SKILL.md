---
name: bigtech
description: "Monta o time de agents C-level (constelação) para um projeto como se fosse uma bigtech. Invoca Cósimo (Chief of Staff), classifica o PORTE do projeto, seleciona a VARIANTE de pipeline (anti over-engineering), e devolve o MAPA DE ATIVAÇÃO (quais C-levels e agents operacionais ligar, em quais das 12 fases). Opcionalmente dispara os C-levels ativos. Camada de NEGÓCIO e LIDERANÇA (produto, marketing, vendas, legal, finanças, release); delega a execução de engenharia ao /proj_software. Use quando o usuário disser \"montar o time\", \"organizar como bigtech\", \"qual pipeline e quais agents\", \"quem lidera isso\", \"classificar o porte\", \"estruturar a empresa do projeto\", ou invocar /bigtech. Para SDLC puro de engenharia sem camada de negócio, usar /proj_software."
argument-hint: "[caminho ou descrição do projeto] [--porte early|scale|bigtech] [--dispatch]"
allowed-tools: [Read, Grep, Glob, Bash, Agent, TodoWrite]
---

# bigtech: montar a constelação C-level via Cósimo

Materializa a organização descrita nos manuais de governança e liderança do plugin (`ORG`, `pipeline_release_1.0`, `lideranca_pipeline_release`). Esta skill opera na **camada de empresa** (C-levels + pipeline de produto de 12 fases). A execução de engenharia (fases 4 a 9) é delegada ao `/proj_software`, que aloca os agents operacionais de engenharia por nível S0-S4.

> **Acesso aos manuais.** O caminho absoluto de `docs/` é injetado no contexto da sessão pelo docs-bootstrap (hook `SessionStart`). Esta skill é carregada de um diretório conhecido, então também pode ler os manuais por caminho relativo (a partir de `skills/bigtech/`): governança em [`ORG`](../../docs/ORG.md), pipeline em [`pipeline_release_1.0`](../../docs/pipeline_release_1.0.md), liderança em [`lideranca_pipeline_release`](../../docs/lideranca_pipeline_release.md). Se o caminho não estiver no contexto, localize via Glob `**/bigtech/docs/**/<NOME>.md`.

> **Regra de ouro (anti-OE):** quem decide o tamanho do time é Cósimo. Porte arquitetural = `early | scale | bigtech` (piso **early**). Headcount/capacity humana **não** define porte. Em early, a maioria dos C-levels fica dormente. Calibrar por complexidade, criticidade e escala.

Argumentos recebidos: $ARGUMENTS

> **Alias deprecado:** `--porte solo` é aceito e normalizado para `early` (com aviso ao usuário). Não grave `porte=solo` em marcadores novos.

---

## 0. Coleta de sinais (obrigatório antes de Cósimo)

Reúna o contexto. Se faltar, pergunte no máximo 1 a 3 itens críticos.

| Dimensão | Pergunta |
|---|---|
| Complexidade / criticidade | Baixa (escopo pequeno, uso próprio) / Média (PMF, primeiros usuários) / Alta (multi-produto, compliance, escala): **isto** orienta o porte, não o número de pessoas |
| Capacity humana (nota, não porte) | 1 pessoa / time pequeno / time médio / org grande: só capacity; **não** vira valor de `--porte` |
| Stake | Pessoal / Interno / Cliente externo / Crítico (financeiro, saúde, vida) |
| Compliance | Nenhuma / LGPD básico / Regulada (PCI, HIPAA, ANVISA, BACEN) |
| Dado pessoal/PII | Não / Sim (sobe a régua de Narciso e Cláudio) |
| Modelo de negócio | Sem receita / B2C / B2B / open source / interno |
| Tipo | CLI / web / mobile / desktop / serviço / lib / firmware |

Se há projeto em CWD, leia `CLAUDE.md`, `TODO.md` e `README` do projeto para inferir sinais antes de perguntar.

---

## 1. Invocar Cósimo (Chief of Staff)

Dispare o agent `cosimo-chief-of-staff` (tool Agent, subagent_type `cosimo-chief-of-staff`) passando os sinais coletados. Peça que devolva o **mapa de ativação** no formato:

```
PORTE: <early | scale | bigtech>
VARIANTE: <Pipeline-Early | Pipeline-Lean | Pipeline-Padrão | Pipeline-Completo>
C-LEVELS ATIVOS: [...]
C-LEVELS DORMENTES: [...]
AGENTS OPERACIONAIS: [...]
FASES APLICÁVEIS: [0..12 ou colapsadas]
CERIMÔNIA: <nenhuma | kanban | scrum>
GATILHO DE RE-ROTEAMENTO: <quando re-avaliar o porte>
JUSTIFICATIVA ANTI-OE: <por que esse nível e não mais>
```

> **Repasse o caminho absoluto de `docs/` no prompt da task de Cósimo.** Subagents não herdam o contexto da sessão (o docs-bootstrap só alcança a thread principal e as skills); sem o caminho no prompt, Cósimo não consegue abrir os manuais de governança (`ORG`, `pipeline_release_1.0`, `lideranca_pipeline_release`) que sustentam a classificação de porte. Use o caminho injetado no contexto da sessão; se ele não estiver disponível, resolva via Glob `**/bigtech/docs/` e inclua o resultado no prompt.

Se o usuário passou `--porte`, normalize alias deprecado (`solo` → `early` + aviso) e informe a Cósimo como hint; deixe ele validar contra os sinais (criticidade e complexidade sobrepõem headcount/capacity).

---

## 2. Apresentar o mapa ao usuário

Mostre o mapa de ativação de forma legível: tabela fase x C-level ativo, lista de agents operacionais, cerimônia, e a justificativa anti-OE. **Não dispare nada ainda** sem aprovação, salvo se `--dispatch` foi passado.

Mapeamento de porte entre as duas camadas (mantenha coerência):

| Porte (Cósimo / bigtech) | Variante de pipeline | Nível SDLC (/proj_software) |
|---|---|---|
| early (minimalista / projeto pequeno) | Pipeline-Early | S0 / S1 |
| early (early-stage / PMF) | Pipeline-Lean | S2 |
| scale | Pipeline-Padrão | S3 |
| bigtech | Pipeline-Completo | S4 |

---

## 3. Despachar (sob aprovação ou com --dispatch)

Para cada **C-level ativo**, dispare o agent correspondente (tool Agent) para liderar suas fases, em paralelo quando independentes:

| Fase do pipeline | C-level (agent) |
|---|---|
| 0 Ideação, 11 coordenação | `celso-ceo` |
| 1-3 Discovery/Definição/Design, 12 Pós | `capitolino-cpo` |
| 4-9 Arquitetura a Beta (engenharia) | `caetano-cto` -> **delega ao /proj_software** |
| 8 Segurança | `narciso-ciso` |
| 8 Jurídico | `claudio-clo` |
| 2 e 6-12 Dados (se ativo) | `candido-cdo` |
| 10 GTM | `camilo-cmo` |
| 10 Pricing/orçamento (se ativo) | `confucio-cfo` |
| 10-11 Receita (se ativo) | `cicero-cro` |
| 6-11 Execução cross-func | `cosmo-coo` |

> **Ao disparar cada C-level via Agent tool, inclua o caminho absoluto de `docs/` no prompt da task.** O subagent não herda o contexto da sessão; sem o caminho ele não abre os manuais que precisa para decidir (governança, manuais de execução em `docs/manuals/`). Repasse o caminho de `docs/` vindo do contexto da sessão (ou resolvido via Glob `**/bigtech/docs/`) em toda task de C-level.

Cada C-level devolve decisões + mapa de delegação aos seus operacionais; a thread principal dispara os operacionais (repassando o mesmo caminho de `docs/` no prompt de cada um). Para as fases de engenharia, **invoque `/proj_software`** em vez de re-listar os eng agents aqui (DRY).

**Invariante de ordem (testes x auditoria):** testes são enabler/DoD (TDD, shift-left): rodam COM a implementação nas Fases 6-7, nunca depois. Auditoria (Fase 8 e 12.6, `internal-auditor`) é downstream: depende de código já testado. Ao gerar plano/tabela via `/tab_pendencias`, a auditoria sempre tem como `Pré-requisito` os itens de código+teste. Nunca sequenciar teste após auditoria. Leia [`TESTES`](../../docs/manuals/TESTES.md), [`AUDITORIAS`](../../docs/manuals/AUDITORIAS.md) e [`AGILE`](../../docs/manuals/AGILE.md) (TDD/DoD) antes de fechar a ordem.

---

## 4. Gravar o marcador de porte

Após classificar, grave o marcador `.bigtech-porte` na raiz do projeto (uma linha: `porte=<early|scale|bigtech>` + data + variante). **Nunca** grave `porte=solo` (alias deprecado; se um marcador legado tiver `solo`, os hooks normalizam a leitura para `early`). Isso silencia o lembrete do hook SessionStart (`bigtech_porte_reminder.py`). Reescreva o marcador quando o porte mudar no re-roteamento.

## 5. Re-roteamento

Registre o porte escolhido e o gatilho de re-avaliação. A cada marco (fim de fase, release, mudança de complexidade/criticidade, capacity humana só como sinal auxiliar, novo requisito regulatório), reinvoque `/bigtech` ou Cósimo para checar se o projeto subiu ou desceu de porte, e ajustar a constelação. Documente a transição no changelog/diário do projeto e atualize [`ORG`](../../docs/ORG.md) se a estrutura mudar.

---

## Integração com ecossistema

- Agent `cosimo-chief-of-staff`: o roteador que esta skill invoca.
- Skill `/proj_software`: execução SDLC de engenharia (fases 4-9); esta skill delega a ela.
- Skill `/tab_pendencias`: tabela canônica de pendências (formato de [`ORG`](../../docs/ORG.md)).
- Docs canônicos: [`ORG`](../../docs/ORG.md), [`pipeline_release_1.0`](../../docs/pipeline_release_1.0.md), [`lideranca_pipeline_release`](../../docs/lideranca_pipeline_release.md), e os 5 manuais em `docs/manuals/`: [`CONTRACT`](../../docs/manuals/CONTRACT.md), [`TESTES`](../../docs/manuals/TESTES.md), [`AGILE`](../../docs/manuals/AGILE.md), [`DEPLOY_CHECKLIST`](../../docs/manuals/DEPLOY_CHECKLIST.md), [`AUDITORIAS`](../../docs/manuals/AUDITORIAS.md).
- Linguagem default: pt-br.
