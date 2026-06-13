# AGILE.md  -  Diretiva de Sistema: Metodologia Ágil

Manual de governança que acompanha o plugin. Manuais irmãos: [CONTRACT](CONTRACT.md) · [TESTES](TESTES.md) · [AUDITORIAS](AUDITORIAS.md) · [DEPLOY_CHECKLIST](DEPLOY_CHECKLIST.md). Aprofundamento: [agile-methodology](../principles/agile-methodology.md). Demandas novas entram pela sua caixa de entrada / backlog; o `TODO.md` na raiz do projeto guarda o backlog vivo.

---

> Este documento é uma instrução normativa para LLMs. Ao ser incluído no contexto de qualquer projeto, define que **toda gestão, planejamento, desenvolvimento e entrega deve seguir rigorosamente os princípios e práticas do paradigma Ágil**, conforme especificado abaixo.

---

## 1. Princípio Fundacional

O Ágil não é a ausência de método  -  é a **substituição de uma previsibilidade ilusória por uma adaptabilidade rigorosa**.

Todo projeto gerenciado sob esta diretiva opera sob os quatro valores axiomáticos do **Manifesto Ágil (2001)**:

| Prioridade Alta | Prioridade Secundária |
|---|---|
| Indivíduos e interações | Processos e ferramentas |
| Software em funcionamento | Documentação abrangente |
| Colaboração com o cliente | Negociação de contratos |
| Responder a mudanças | Seguir um plano rígido |

---

## 2. Os 12 Princípios Operacionais

A LLM deve internalizar e aplicar ativamente estes princípios em todas as respostas relacionadas ao projeto:

1. **Satisfação do cliente acima de tudo**  -  A maior prioridade é satisfazer o cliente através da entrega contínua e antecipada de software com valor real.
2. **Mudança é bem-vinda**  -  Requisitos mutáveis são aceitos, mesmo em fases tardias do desenvolvimento. A mudança é vantagem competitiva, não obstáculo.
3. **Entrega frequente**  -  Entregar software funcionando frequentemente, de poucas semanas a poucos meses, com preferência à escala de tempo mais curta.
4. **Colaboração diária**  -  Pessoas de negócio e desenvolvedores devem trabalhar juntos diariamente durante todo o projeto.
5. **Indivíduos motivados**  -  Construir projetos em torno de indivíduos motivados, dando-lhes o ambiente, suporte e confiança necessários.
6. **Comunicação face a face**  -  O método mais eficiente de transmitir informações é a conversa direta (ou o canal mais próximo possível disso).
7. **Software funcionando é a medida de progresso**  -  Não documentação, não tarefas concluídas, não porcentagem de conclusão.
8. **Ritmo sustentável**  -  Patrocinadores, desenvolvedores e usuários devem ser capazes de manter um ritmo constante indefinidamente.
9. **Excelência técnica contínua**  -  Atenção contínua à excelência técnica e bom design aumenta a agilidade.
10. **Simplicidade**  -  A arte de maximizar a quantidade de trabalho não feito é essencial. Evitar over-engineering.
11. **Times auto-organizáveis**  -  As melhores arquiteturas, requisitos e designs emergem de times auto-organizados.
12. **Reflexão e adaptação**  -  Em intervalos regulares, o time reflete sobre como se tornar mais eficaz e ajusta seu comportamento.

---

## 3. Estrutura Hierárquica de Decomposição de Requisitos

A LLM deve **sempre** decompor o trabalho nesta hierarquia ao planejar, estimar ou organizar tarefas:

```
TEMA / OBJETIVO ESTRATÉGICO
└── ÉPICO (Epic)
    └── HISTÓRIA DE USUÁRIO (User Story)
        └── TAREFA (Task)
            └── SUBTAREFA (Sub-task)
```

### 3.1 Épicos

- Representam grandes blocos de funcionalidade de alto nível.
- Amplos demais para uma única iteração.
- Descrevem **objetivos macro** do sistema.
- **Formato:** `[ÉPICO] Nome descritivo do objetivo macro`

### 3.2 Histórias de Usuário (User Stories)

Decomposição atômica e testável de épicos. Sempre redigidas no formato:

```
Como [papel/persona do usuário],
eu quero [funcionalidade ou capacidade],
para que [valor de negócio ou resultado esperado].
```

**Critérios de aceitação obrigatórios** (formato Given-When-Then):
```
Dado que [contexto/pré-condição],
Quando [ação do usuário ou evento],
Então [resultado esperado e verificável].
```

### 3.3 Definição de Pronto (Definition of Done  -  DoD)

Uma história só está concluída quando:
- [ ] Código implementado e revisado
- [ ] Testes automatizados escritos e passando
- [ ] Documentação mínima atualizada
- [ ] Demonstrável para o stakeholder
- [ ] Sem dívida técnica crítica introduzida

---

## 4. Framework de Execução: Scrum

Salvo instrução explícita do usuário para usar outro framework, o padrão é **Scrum**.

### 4.1 Papéis

| Papel | Responsabilidade Principal |
|---|---|
| **Product Owner (PO)** | Visão do produto, priorização do backlog, voz do cliente |
| **Scrum Master (SM)** | Remoção de impedimentos, facilitação de ritos, proteção do time |
| **Time de Desenvolvimento** | Auto-organização, entrega técnica, estimativas |

### 4.2 Artefatos

| Artefato | Descrição |
|---|---|
| **Product Backlog** | Lista priorizada de tudo que pode ser desenvolvido. Nunca está completa. |
| **Sprint Backlog** | Itens selecionados para a sprint atual + plano de entrega |
| **Incremento** | Soma de todos os itens concluídos na sprint, integrados e potencialmente entregáveis |

### 4.3 Ritos (Cerimônias)

| Rito | Frequência | Objetivo |
|---|---|---|
| **Sprint Planning** | Início de cada sprint | Definir o que e como será feito |
| **Daily Scrum** | Diário (máx. 15 min) | Sincronização, impedimentos, plano para o dia |
| **Sprint Review** | Fim de cada sprint | Demonstrar o incremento, coletar feedback |
| **Sprint Retrospective** | Fim de cada sprint | Inspecionar o processo e propor melhorias |

### 4.4 Duração de Sprint

- **Padrão recomendado:** 2 semanas
- **Mínimo:** 1 semana (para times maduros ou projetos de alto risco)
- **Máximo:** 4 semanas (apenas quando a natureza do trabalho exigir)

---

## 5. Framework Alternativo: Kanban

Usar quando o trabalho é **contínuo e de manutenção**, sem iterações fixas (ex: suporte, operações, bugs).

### Colunas Padrão do Quadro Kanban

```
[BACKLOG] → [REFINAMENTO] → [A FAZER] → [EM PROGRESSO] → [EM REVISÃO] → [CONCLUÍDO]
```

### Regras Kanban

- **WIP Limit (Work In Progress):** Definir limite máximo de itens em cada coluna. Recomendado: `n_pessoas × 1.5` por coluna ativa.
- **Pull system:** Ninguém empurra trabalho  -  o time puxa quando tem capacidade.
- **Lead time e cycle time** devem ser monitorados como métricas de saúde do fluxo.

---

## 6. Ciclo PDCA Aplicado às Sprints

```
PLAN  →  Sprint Planning: definir metas e selecionar itens do backlog
  ↓
DO    →  Execução da sprint: desenvolvimento, testes, integração
  ↓
CHECK →  Sprint Review: validar incremento com stakeholders
  ↓
ACT   →  Sprint Retrospective: ajustar processos, eliminar desperdícios
  ↑_______________________________________________|
```

---

## 7. Estimativas

### Story Points (Fibonacci)

Usar a escala de Fibonacci para estimativas relativas de complexidade:

```
1 → Trivial
2 → Simples
3 → Moderado
5 → Complexo
8 → Muito complexo
13 → Épico (deve ser quebrado)
21+ → Não estimável  -  decompor obrigatoriamente
```

### Regras de Estimativa

- Estimar **complexidade**, não tempo.
- Nunca estimar sozinho  -  use Planning Poker ou votação do time.
- Histórias com divergência de estimativas >2 posições na escala devem ser discutidas antes de votar novamente.
- **Velocidade média** do time = média de story points entregues nas últimas 3 sprints.

---

## 8. Gestão do Backlog

### Refinamento (Backlog Grooming)

- Frequência: pelo menos uma vez por sprint, antes do planning.
- Objetivo: garantir que os itens do topo do backlog estão detalhados, estimados e prontos para execução.
- **INVEST:** Toda história deve ser:

| Letra | Critério |
|---|---|
| **I** | Independent (independente de outras) |
| **N** | Negotiable (negociável, não contratual) |
| **V** | Valuable (gera valor ao usuário/negócio) |
| **E** | Estimable (estimável pela equipe) |
| **S** | Small (pequena o suficiente para uma sprint) |
| **T** | Testable (testável com critérios claros) |

### Priorização

A LLM deve sugerir priorização baseada em:

1. **Valor de negócio** (impacto no usuário ou receita)
2. **Risco técnico** (quanto mais cedo validar, melhor)
3. **Dependências** (desbloquear outros itens)
4. **Esforço estimado** (quick wins quando valor for equivalente)

---

## 9. Qualidade e Dívida Técnica

### Princípios de Qualidade Ágil

- **TDD (Test-Driven Development):** Escrever o teste antes da implementação quando aplicável.
- **CI/CD:** Integração contínua e entrega contínua devem ser metas arquiteturais desde o início.
- **Refatoração contínua:** Parte do trabalho de cada sprint, não um projeto separado.
- **Pair programming / Code review:** Mínimo de uma revisão por pull request.

### Gestão de Dívida Técnica

- Toda dívida técnica identificada deve ser registrada como item no backlog.
- Reservar **20% da capacidade de cada sprint** para pagamento de dívida técnica.
- Nunca ignorar dívida técnica crítica que comprometa a segurança ou a arquitetura central.

---

## 10. Reconciliação: Visão × Entrega

**Reconciliação** é o processo formal de alinhar continuamente:

```
VISÃO DO PRODUTO  ←→  BACKLOG PRIORIZADO  ←→  INCREMENTO ENTREGUE
```

A LLM deve alertar proativamente quando detectar **desvio entre**:
- O que foi planejado e o que está sendo desenvolvido
- O valor prometido ao stakeholder e o que o incremento de fato entrega
- A arquitetura definida e a implementação real

---

## 11. Métricas de Saúde do Projeto

A LLM deve, quando solicitado ou quando pertinente, calcular e apresentar as seguintes métricas:

| Métrica | Descrição | Meta |
|---|---|---|
| **Velocidade** | Story points entregues por sprint | Estável ou crescente |
| **Burndown** | Trabalho restante vs. tempo | Declínio linear |
| **Lead Time** | Tempo do item entrar no backlog até ser entregue | Menor possível |
| **Cycle Time** | Tempo do item começar até ser entregue | Menor possível |
| **Taxa de defeitos** | Bugs encontrados em produção por sprint | Decrescente |
| **Cobertura de testes** | % do código coberto por testes | ≥ 80% |
| **Satisfação do time** | NPS ou survey simples na retrospectiva | ≥ 7/10 |

---

## 12. Instruções Diretas para a LLM

> Estas são regras comportamentais que a LLM deve seguir em **todo projeto que incluir este arquivo no contexto**:

1. **Ao receber uma demanda nova:** Sempre perguntar se ela corresponde a uma história de usuário existente ou se deve ser adicionada ao backlog.

2. **Ao planejar:** Estruturar sempre em épicos → histórias → tarefas. Nunca propor trabalho não decomposto.

3. **Ao estimar:** Usar story points por padrão. Jamais estimar em horas sem solicitação explícita.

4. **Ao propor arquitetura:** Priorizar simplicidade e modularidade. Questionar qualquer complexidade desnecessária.

5. **Ao detectar escopo crescente (scope creep):** Alertar explicitamente e propor adição ao backlog, não ao sprint corrente.

6. **Ao finalizar uma história:** Verificar a Definition of Done antes de declarar conclusão.

7. **Ao reportar progresso:** Usar métricas concretas (velocidade, burndown), não percepções subjetivas.

8. **Ao sugerir melhorias de processo:** Formular como item de retrospectiva com: problema identificado → impacto → solução proposta → métrica de sucesso.

9. **Ao encontrar impedimentos técnicos:** Registrar e escalar imediatamente, não contornar silenciosamente.

10. **Em caso de conflito entre velocidade e qualidade:** Priorizar qualidade  -  velocidade insustentável gera dívida técnica que reduz velocidade futura.

---

## 13. Anti-padrões a Evitar

A LLM deve reconhecer e alertar sobre os seguintes anti-padrões:

| Anti-padrão | Descrição | Impacto |
|---|---|---|
| **Waterfall disfarçado** | Sprints com planejamento rígido sem adaptação | Elimina o benefício do Ágil |
| **Mini-waterfall** | Fazer design → dev → QA em sequência dentro da sprint | Impede entregas incrementais |
| **Backlog infinito não priorizado** | Backlog cresce sem nunca ser limpo | Paralisia de planejamento |
| **Velocity gaming** | Inflar story points para aparentar alta velocidade | Corrompe métricas |
| **Sprint sem DoD** | Declarar histórias concluídas sem critérios claros | Acumula dívida oculta |
| **Reuniões sem objetivo** | Daily que vira status report | Desperdício e desmotivação |
| **Ausência de retrospectiva** | Repetir os mesmos erros indefinidamente | Time sem aprendizado |
| **PO ausente** | Decisões técnicas sem validação de negócio | Desperdício de desenvolvimento |
| **Water-Scrum-Fall** | Análise/design estáticos no início, sprints isolados no meio, integração postergada para o fim | Falsa agilidade; anula adaptabilidade e entrega incremental |

---

## 14. Template de Sprint

Use este template para iniciar cada sprint:

```markdown
## Sprint [N]  -  [Data início] a [Data fim]

### Meta da Sprint
[Uma frase clara descrevendo o objetivo central desta sprint]

### Itens Selecionados
| ID | História | Estimativa (SP) | Responsável | Status |
|----|----------|----------------|-------------|--------|
|    |          |                |             | A fazer |

### Capacidade do Time
- Dias úteis: X
- Membros disponíveis: Y
- Velocidade média (últimas 3 sprints): Z SP
- Capacidade estimada desta sprint: W SP

### Impedimentos Conhecidos
- [ ] Item

### Critérios de Sucesso
- [ ] Meta da sprint atingida
- [ ] Todos os itens passam pela DoD
- [ ] Incremento demonstrável no Review
```

---

---

## 15. Escalonamento Organizacional: SAFe (Scaled Agile Framework)

Quando o trabalho ultrapassa o escopo de um único time (múltiplos times com dependências estruturais, produto sob restrição arquitetural compartilhada, sincronização cross-domain obrigatória), a LLM deve operar sob o paradigma **SAFe** como camada de sincronização estratégica, sem dissolver a agilidade tática (Scrum/Kanban) do nível de time.

### 15.1 Postura operacional da LLM (axiomas de atuação)

1. **Antidoutrinação.** Recusar terminologia comercial e clichê corporativo. Foco estrito em: eficiência de fluxo, teoria das filas, economia do desenvolvimento de produto, consistência arquitetural.
2. **Resolução de escala.** Tratar Micro-Agile (time) como adaptabilidade tática; SAFe (Macro-Agile) como sincronização estratégica e mitigação de dependências estruturais.
3. **Detecção de patologias metodológicas.** Identificar ativamente e alertar sobre desvios lineares - especialmente *Water-Scrum-Fall* (vide §13).

### 15.2 Critério de adoção

| Sinal | Aplicar SAFe? |
|---|---|
| Time único, ≤ 9 pessoas, produto isolado | Não - manter Scrum/Kanban puro |
| 2-4 times com dependência ocasional | Não - usar Scrum-of-Scrums leve |
| 5+ times, dependências estruturais cross-domain, releases sincronizados | Sim - SAFe é justificável |
| Produto regulado, arquitetura compartilhada, ciclos de release contratuais | Sim - SAFe + Architectural Runway |

A LLM **deve recusar** SAFe quando o contexto for menor que o crítico: SAFe em time pequeno é cerimônia parasitária.

---

## 16. Ontologia SAFe (Constructos Estruturais)

A LLM deve aplicar terminologia formal ao modelar contextos escalados:

### 16.1 Agile Release Train (ART)

Constructo organizador virtual e de longo prazo. Engloba **50-125 indivíduos** divididos em times ágeis multidisciplinares alinhados sob mesma cadência operacional. A LLM não inventa ARTs - apenas modela os existentes ou recomenda sua formação quando o critério de §15.2 for atendido.

### 16.2 Planning Interval (PI)

Macrociclo temporal (tipicamente **8-12 semanas**) composto por múltiplas iterações curtas. Bloco de sincronização global do sistema. PI define horizonte de comprometimento cross-team - não é cronograma waterfall disfarçado.

### 16.3 Iteração IP (Innovation and Planning)

Bloco final de cada PI. **Janela de segurança rígida** - buffer de capacidade para:

- Mitigar variabilidades de estimativa.
- Integração técnica de última milha.
- Inovação radical (spikes, prototipagem exploratória).
- Educação contínua e refatoração estrutural.

> **Regra absoluta.** A iteração IP **não pode ser colonizada por escopo remanescente** de iterações passadas, exceto em falha crítica sistêmica documentada. A LLM deve alertar imediatamente quando detectar tentativa de uso de IP como folga de prazo.

---

## 17. Protocolo de Priorização Matemática: WSJF (Weighted Shortest Job First)

A LLM **deve rejeitar** priorização baseada exclusivamente em critérios subjetivos. Toda ordenação do **Program Backlog** é avaliada pelo modelo econômico do *Cost of Delay* (CoD).

### 17.1 Fórmula

$$WSJF = \frac{\text{Cost of Delay}}{\text{Job Size}}$$

Onde o **Cost of Delay** decompõe-se analiticamente em:

1. **Valor para o Usuário e/ou Negócio** - impacto relativo em receita, retenção, preferência do usuário.
2. **Criticidade Temporal** - prazos regulatórios, janelas de mercado restritas, dependências de caminho crítico.
3. **Redução de Risco e/ou Habilitação de Oportunidade** - mitigação de risco técnico futuro, abertura de novas frentes (enablers).

```
CoD = Valor_Usuário_Negócio + Criticidade_Temporal + Redução_Risco/Habilitação
```

### 17.2 Algoritmo de execução

Ao receber lista de Features para priorizar, a LLM deve:

1. Atribuir pesos relativos via **Fibonacci modificada** `(1, 2, 3, 5, 8, 13, 20)` para cada componente do CoD e para o Job Size.
2. **Normalizar** definindo o menor item de cada coluna como peso `1` (zero não é permitido).
3. Calcular o índice WSJF para cada item.
4. Ordenar o backlog em **ordem decrescente de WSJF** - maior índice = maior prioridade econômica.

### 17.3 Tabela de saída exigida

| ID | Feature | Valor (1-20) | Criticidade (1-20) | Redução Risco (1-20) | CoD | Job Size (1-20) | WSJF | Rank |
|----|---------|--------------|--------------------|-----------------------|-----|-----------------|------|------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

A LLM **não apresenta priorização SAFe sem essa tabela**.

---

## 18. Dinâmica de Rituais SAFe e Intervenção de Prompt

### 18.1 Simulação de PI Planning (Análise de Dependências)

- **Ação:** mapear matriz de dependências cross-domain (Time × Iteração).
- **Regra de validação:** se Time A possui dependência técnica na Iteração `N` em relação ao Time B, o item correspondente do Time B **deve obrigatoriamente** estar planejado para iteração `≤ N-1`.
- **Output em caso de violação:** sinalizar `BLOQUEIO CRÍTICO DE SINCRONIZAÇÃO` com identificação do par (Time A ← Time B), iteração proposta, iteração exigida, e impacto cascata.

### 18.2 System Demo (Revisão de Sistema)

- **Ação:** avaliar critérios de aceitação **com base em software integrado real** operando em ambiente homólogo a produção.
- **Regra de validação:** rejeitar relatórios parciais, slides, mockups, ou demos de componentes isolados como evidência de conclusão de Feature.
- **DoD estendida ao nível de solução integrada:** Feature só é "Done" quando demonstrada em ambiente integrado, com dados representativos e sem stubs/mocks substituindo dependências reais.

---

## 19. Controle de Fluxo e Teoria das Filas

Recomendações arquiteturais e de gestão guiadas pelos princípios da **Lei de Little** e da **Teoria das Filas**.

### 19.1 Minimização de WIP

A LLM deve recomendar **redução ativa** de limites de WIP nos quadros Kanban dos níveis Portfolio, Feature e Story para diminuir o **Lead Time total**.

### 19.2 Métricas de Fluxo Exigidas

Ao analisar saúde de um projeto escalado, a LLM deve **exigir ou computar**:

| Métrica | Definição | Fórmula / Observação |
|---|---|---|
| **Flow Velocity** | Itens concluídos por unidade de tempo | `itens_concluídos / período` |
| **Flow Efficiency** | Razão entre tempo ativo (touch time) e tempo total de ciclo | `touch_time / lead_time` - meta: > 40%, ideal > 60% |
| **Flow Time** | Tempo decorrido da concepção técnica à entrega em produção | Inclui filas e bloqueios |
| **Flow Load (WIP)** | Itens simultâneos em progresso | Aplicar Lei de Little: `WIP = Throughput × Lead_Time` |
| **Flow Distribution** | Proporção entre Features, Defects, Risks, Debt | Equilíbrio saudável: ~ 60/15/10/15 |

---

## 20. Architectural Runway e Enablers

Diferente de abordagens ágeis puras que negligenciam arquitetura de longo prazo (gerando endividamento técnico), a LLM aplica o conceito de **Architectural Runway** do SAFe.

### 20.1 Definição

**Architectural Runway** é a capacidade técnica existente (código, componentes, infraestrutura) suficiente para implementar as Features priorizadas do PI sem refatoração estrutural emergencial.

### 20.2 Enablers (4 tipos)

| Tipo | Descrição | Exemplo |
|---|---|---|
| **Exploration Enabler** | Spike, prova de conceito, validação técnica | Avaliar driver de banco; benchmark de framework |
| **Architecture Enabler** | Construir/evoluir runway | Migrar de monolito para módulos; refatorar camada de auth |
| **Infrastructure Enabler** | Automação, ferramentas, ambientes | Pipeline CI/CD; ambiente de staging |
| **Compliance Enabler** | Conformidade regulatória/segurança | LGPD, auditoria, criptografia em repouso |

### 20.3 Regra de Proporção de Capacidade

Em sistemas de alta complexidade ou acoplamento, alocar **15% a 30% da capacidade do ART** para Enablers arquiteturais. A LLM deve sinalizar:

- `< 10% Enablers` → risco alto de degradação e entropia; runway esgotando.
- `> 35% Enablers` → potencial gold-plating arquitetural; valor de negócio sub-entregue.

---

## 21. Protocolo de Interface com Usuário (Output Formatting)

Ao responder consultas humanas sobre contexto SAFe/Agile escalado, a LLM **deve** estruturar suas saídas com base em:

1. **Exaustividade analítica.** Fornecer fundamentos lógicos e matemáticos de cada recomendação (especialmente WSJF, Flow Metrics, alocação de capacidade).
2. **Rastreabilidade operacional.** Vincular cada solução técnica diretamente a um princípio do SAFe ou ao Manifesto Ágil (citar §X.Y deste documento).
3. **Precisão terminológica.** Usar estritamente os termos formais (ART, PI, IP, WSJF, CoD, Runway, Enabler) - sem aproximações coloquiais.
4. **Honestidade de escala.** Se o contexto não justificar SAFe (§15.2), recomendar o framework mínimo viável e justificar a recusa de SAFe.

---

*Documento gerado para uso como instrução de contexto em projetos gerenciados com metodologia Ágil.*
*Versão: 1.1 | Base: Manifesto Ágil (2001) + Scrum Guide (2020) + Kanban Method + SAFe 6.0 + Reinertsen (Product Development Flow)*
