# Metodologia ágil obrigatória

**Diretiva sempre ativa**: este documento é normativo em **todo projeto que use a constelação bigtech**, sem necessidade de cópia local. Define o paradigma Ágil (Manifesto 2001 + Scrum Guide 2020 + Kanban) **e seu escalonamento via SAFe 6.0** como contrato de gestão, planejamento e entrega.

Princípios relacionados: [arquitetura e princípios](arquitetura-principios.md) · [anti-patterns](anti-patterns.md). O manual [AGILE](../manuals/AGILE.md) detalha os rituais e artefatos; a priorização WSJF é operada pela skill `/tab_pendencias`.

Conteúdo coberto pela diretiva:

**Micro-Agile (time, §1-14):**

- 4 valores do Manifesto e 12 princípios operacionais (priorizar indivíduos, software funcionando, colaboração, resposta a mudanças).
- Decomposição obrigatória em Tema, Épico, História de Usuário, Tarefa, Subtarefa.
- Histórias no formato "Como X, eu quero Y, para Z" + critérios Given-When-Then.
- Definition of Done (DoD): código revisado, testes passando, doc mínima atualizada, demonstrável, sem dívida crítica nova.
- Scrum como framework default (sprints 2 semanas, ritos: Planning, Daily, Review, Retrospective). Kanban quando o trabalho for contínuo (suporte, ops, bugs).
- Estimativas em story points (Fibonacci 1, 2, 3, 5, 8, 13, 21+).
- INVEST para refinamento, PDCA por sprint, dívida técnica reservando 20% da capacidade.
- Anti-padrões: waterfall disfarçado, mini-waterfall, backlog não priorizado, velocity gaming, sprint sem DoD, ausência de retrospectiva, **Water-Scrum-Fall**.
- 10 instruções comportamentais diretas (perguntar se cabe em história existente, planejar épico-história-tarefa, estimar em SP, alertar scope creep, escalar impedimentos, priorizar qualidade sobre velocidade).

**Macro-Agile / SAFe (§15-21, ativado sob critério de escala):**

- **Postura LLM:** antidoutrinação (recusar clichê corporativo), resolução de escala (Micro vs Macro), detecção de patologias (Water-Scrum-Fall).
- **Ontologia SAFe:** Agile Release Train (ART, 50-125 pessoas), Planning Interval (PI, 8-12 semanas), Iteração IP (buffer rígido - **não colonizar com escopo remanescente**).
- **WSJF (Weighted Shortest Job First):** `WSJF = CoD / Job Size` onde `CoD = Valor + Criticidade Temporal + Redução de Risco/Habilitação`. Pesos via Fibonacci modificada `(1,2,3,5,8,13,20)`. Tabela de saída obrigatória ao priorizar Program Backlog.
- **Rituais SAFe:** PI Planning com matriz de dependências cross-team (bloqueio crítico se Time A depende do Time B na mesma iteração); System Demo só aceita software integrado real em ambiente homólogo.
- **Flow Metrics (Lei de Little, Reinertsen):** Flow Velocity, Flow Efficiency (touch_time/lead_time, meta >40%), Flow Time, Flow Load (WIP), Flow Distribution. Minimizar WIP ativamente.
- **Architectural Runway + Enablers:** alocar 15-30% da capacidade do ART para Enablers (Exploration / Architecture / Infrastructure / Compliance). Alertar se `<10%` ou `>35%`.
- **Critério de adoção SAFe:** time único ou ≤4 times com dependência ocasional → recusar SAFe (cerimônia parasitária). 5+ times com dependências estruturais ou produto regulado → SAFe justificável.
- **Output formatting SAFe-aware:** exaustividade analítica, rastreabilidade operacional (citar §X.Y), precisão terminológica formal, honestidade de escala.

## Adaptações universais (precedência sobre o paradigma base em caso de conflito)

1. **Auto mode + pedidos cirúrgicos**: a regra "Ao receber demanda nova, perguntar se cabe em história existente" não se aplica a edits pontuais óbvios (correção de bug, typo, ajuste de uma linha). Auto mode tem precedência. Apenas demanda **nova de feature ou épico** exige confirmação ou adição explícita ao backlog.
2. **TDD sobre cobertura**: o paradigma base define meta "≥ 80% cobertura" como métrica de saúde. A regra TDD red/green prevalece (ver [arquitetura e princípios](arquitetura-principios.md)): cobertura é consequência de TDD, não objetivo. Não inflar testes só para bater o número.
3. **`TODO.md` tabular como backlog**: o backlog do projeto vive no `TODO.md` da raiz (formato da skill `/tab_pendencias`). Mapeamento: coluna `Grupo` corresponde a Épico, cada linha é uma História ou Tarefa, `Dificuldade` mapeia para story points (Baixa = 1-2, Média = 3-5, Alta = 8). Não criar `BACKLOG.md` paralelo. Itens novos seguem formato User Story na descrição quando aplicável; itens legados não precisam ser reescritos.
4. **Time solo**: em projeto com um único desenvolvedor, ritos com time (Daily, Planning, Review, Retro) viram self-review/self-retro implícitas via commits/changelog/`TODO.md`. Papéis (PO, SM, Dev) são acumulados pela mesma pessoa, mas cada decisão deve ser tomada com a mentalidade do papel correspondente.
5. **Definition of Done estendida** para projetos com hooks/CI: além dos 5 itens do paradigma base, adicionar "smoke automatizado verde" e "pre-commit/pre-push limpos".
6. **Conventional Commits são DoD implícita**: commit `feat:`/`fix:`/`refactor:` etc. é evidência mínima de que a história está pronta para Review. Histórias sem commit não passam pela DoD.

## Ver também

- Rituais, artefatos e detalhamento operacional: [AGILE](../manuals/AGILE.md).
- Arquitetura, SOLID, DRY e TDD: [arquitetura e princípios](arquitetura-principios.md).
- Anti-patterns universais a evitar: [anti-patterns](anti-patterns.md).
