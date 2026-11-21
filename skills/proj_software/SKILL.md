---
name: proj_software
description: "Orquestra ciclo de vida de software (SDLC estendido) em 5 macrofases, alocando os agentes corretos por etapa, com proteção anti-over-engineering em projetos pequenos e trilha de escalonamento (S0 protótipo → S1/S2 early → S3 scale → S4 enterprise). Aplica DevSecOps / Shift-Left (security transversal).  Para projeto de jogo, a rota é /bigtech:proj_jogo; para Linux, /bigtech:suporte-linux; para pendências, /bigtech:tab_pendencias; para pessoas, bigtech:engineering-coach. Use IMEDIATAMENTE quando o usuário disser \"vou criar um software\", \"começar projeto\", \"criar app\", \"novo sistema\", \"construir [feature/produto]\", \"estruturar projeto\", \"como fazer X em produção\", \"qual fluxo seguir\", ou invocar /bigtech:proj_software. Use também quando a conversa começa um projeto novo de software sem mencionar skill."
---

# proj_software: orquestração SDLC com squad de engenharia

Aplica o **macrofluxo de engenharia em 5 fases** delegando aos agentes corretos. Inclui **gatekeeper anti-over-engineering**, **shift-left de segurança**, e **trilha de escalonamento** quando o projeto cresce.

> **Regra de ouro:** projeto pequeno usa poucos agentes em fases simples. Não invocar o squad inteiro pra um CLI de 200 linhas. Calibrar SEMPRE pela matriz de tamanho.

> **Piso de testes.** Teste só para lógica de produto. O CI é o único portão. Nada de teste de mutação, sabotagem, auditoria, reauditoria, varredura de gêmeos, checklist de perguntas do revisor, script de verificação extra nem portão local novo. Exceção: segurança, privacidade e deploy irreversível. Os gates de fase abaixo seguem este piso.

## Leitura obrigatória antes de alocar o squad

**Antes de definir o nível (S0-S4) e disparar qualquer agente, leia os manuais que acompanham o plugin.** O caminho absoluto de `docs/` é injetado no contexto da sessão pelo docs-bootstrap (hook `SessionStart`) e, como esta skill é carregada de diretório conhecido, o Read relativo também funciona. Se o caminho não estiver no contexto, localize os arquivos via Glob `**/bigtech:bigtech/docs/**/<NOME>.md`. Leia o manual relevante ao tipo de decisão **antes** de fechá-la:

- **Padrão de código** (estrutura, SOLID, convenções de commit): `CONTRACT` (`${CLAUDE_PLUGIN_ROOT}/docs/house/CONTRACT.md`).
- **Qualidade e testes** (piso de testes, TDD): `TESTES` (`${CLAUDE_PLUGIN_ROOT}/docs/house/TESTES.md`).
- **Cadência ágil** (sprint, INVEST, métricas de fluxo): `AGILE` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AGILE.md`).
- **Deploy e rollback** (gates da Fase 5): `DEPLOY_CHECKLIST` (`${CLAUDE_PLUGIN_ROOT}/docs/house/DEPLOY_CHECKLIST.md`).
- **Auditoria** (só segurança, privacidade e deploy irreversível): `AUDITORIAS` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AUDITORIAS.md`).
- **Princípios de arquitetura** (4 camadas, anti-over-engineering): [`arquitetura-principios`](../../docs/principles/arquitetura-principios.md).
- **Métodos ágeis** (Scrum + Kanban + escalonamento): [`agile-methodology`](../../docs/principles/agile-methodology.md).
- **Anti-padrões proibidos** (commit publicado, force-push, etc.): [`anti-patterns`](../../docs/principles/anti-patterns.md).
- **Ferramentas FOSS por agent**: `TOOLING` (`${CLAUDE_PLUGIN_ROOT}/docs/house/TOOLING.md`).

> **Ao despachar um agent via Agent tool, inclua o caminho absoluto de `docs/` no prompt da task.** Subagents não herdam o contexto da sessão (o docs-bootstrap só alcança a thread principal e as skills); sem o caminho no prompt, o agent não consegue abrir o manual citado.

---

## 0. Calibragem inicial (obrigatório)

Antes de invocar qualquer agente, identifique:

| Dimensão | Pergunta |
|---|---|
| Capacity / tamanho eng (nota, não porte bigtech) | Protótipo 1 pessoa / Pequeno (1-3) / Médio (4-10) / Grande (10-50) / Enterprise (50+): mapeia a S0-S4; porte arquitetural (`early|scale|bigtech`) vem de `/bigtech:bigtech` |
| Stake | Pessoal / Interno / Cliente externo / Crítico (financeiro, saúde, segurança de vida) |
| Time-to-live | Dias / semanas / meses / anos |
| Compliance | Nenhuma / leve (LGPD básico) / regulada (PCI, HIPAA, SOX) |
| Performance / escala | Baixa / média / alta / extrema |
| Distribuição | Self-host pessoal / SaaS B2C / B2B / on-prem cliente / multi-tenant / multi-region |
| Tipo | CLI / script / web app / mobile / desktop / serviço / lib / firmware integrado |
| Compartilhamento | Privado / open source / produto comercial |

Se o usuário não disse: **pergunte 1-3 itens críticos**, não mais. Maioria das decisões deriva dessas respostas.

---

## 1. Matriz tamanho → agentes a invocar

Use o **mínimo viável**. Cada agente adiciona overhead de comunicação e processo.

### Nível S0: Script / Prototype (1 pessoa, sem deploy)
**Agentes:** um único agente especialista (o mais próximo do stack, ex. `bigtech:backend-engineer`) implementa. A thread principal só confere: lê, mede, verifica, despacha e reporta; nunca produz. Esta regra vale sem exceção de tamanho, inclusive em S0. Time enxuto continua sendo o objetivo (1 agente, não uma constelação); só não é a thread principal quem digita.
- Sem PRD, sem ADR, sem RFC, sem CI elaborada.
- Sem `bigtech:software-architect`: overkill.
- Apenas: leia o problema, escreva o teste que falha, escreva o código, use.
- **Guardrails:** `superpowers:brainstorming` se requirements ambíguos; `superpowers:test-driven-development` em todo código de comportamento (exceção declarada: protótipo descartável, script avulso).
- Doc: README mínimo é suficiente.

### Nível S1: App pessoal / MVP interno (1-2 pessoas, deploy simples)
**Agentes ativos:** 1 agente implementador (o mais próximo do stack) + 2-3 especialistas sob demanda. A thread principal só confere: lê, mede, verifica, despacha e reporta; nunca produz (sem exceção de tamanho).
- `bigtech:product-manager` opcional (só se requirements ambíguos)
- `bigtech:software-architect` **apenas** quando trade-off real existe (escolha de banco, sync × async)
- `bigtech:qa-engineer` sob demanda (test plan curto, não pirâmide completa)
- `bigtech:security-engineer` sob demanda para checklist OWASP top 10
- Sem `bigtech:engineering-manager` / `bigtech:scrum-master` / `bigtech:tech-lead` formal
- Sem `bigtech:data-engineer` separado se não há analytics
- Sem `bigtech:devops-sre` separado: o agente implementador do nível cuida do deploy sob despacho (a thread principal não executa deploy)
- Doc: README + 1-2 ADRs em decisões one-way door

### Nível S2: Produto pequeno / startup early-stage (3-8 devs)
**Agentes ativos comuns:**
- `bigtech:product-manager` (visão/escopo)
- `bigtech:software-architect` (decisões one-way door)
- `bigtech:ux-ui-designer` se há interface
- `bigtech:frontend-engineer` + `bigtech:backend-engineer` (implementação)
- `bigtech:qa-engineer` (teste da lógica de produto)
- `bigtech:devops-sre` (CI/CD básico, monitoring básico)
- `bigtech:security-engineer` (threat model leve + SAST/SCA em CI + checklist OWASP)
- `bigtech:technical-writer` opcional (README + docs API)
- Doc: PRD curto, ADRs em decisões importantes, README + getting-started

### Nível S3: Produto médio / scale-up (8-30 devs, múltiplos times)
**Adicionar a S2:**
- `bigtech:tech-lead` por squad
- `bigtech:engineering-manager` por área
- `bigtech:scrum-master` ou ágil distribuído nos times
- `bigtech:ux-writer` separado
- `bigtech:accessibility-specialist` se cliente-facing
- `bigtech:i18n-l10n-specialist` se multi-locale
- `bigtech:data-engineer` + `bigtech:data-scientist` se há analytics / ML
- `bigtech:mobile-engineer` se há app
- `bigtech:compliance-legal` se regulado
- `bigtech:engineering-manager` cuida do growth e da mentoria do time

### Nível S4: Enterprise / regulado / multi-time (30+ devs)
**Squad completa.** Incluir:
- `bigtech:ml-engineer` se ML em produção
- `bigtech:engineering-manager` formal por área, com trilha de mentoria/coaching do time
- `bigtech:embedded-firmware-engineer` se HW envolvido
- `bigtech:hardware-engineer` se HW envolvido
- Process completo, docs robustas, compliance ativa, observability matura

---

## 2. As 5 Macrofases

### Fase 1: Concepção, Design de Sistemas, Especificação

**S0:** pular ou brainstorming pessoal curto.
**S1:** PRD-em-1-página + 1-2 ADRs.
**S2+:** pleno.

**Agentes** (escalonado por nível):
- `bigtech:product-manager`: visão, escopo, roadmap, MVP
- `bigtech:ux-ui-designer`: jornada e interface (se há UI)
- `bigtech:ux-writer`: microcópia e voice/tone (S2+)
- `bigtech:accessibility-specialist`: validação WCAG (S2+ cliente-facing)
- `bigtech:software-architect`: estrutura, stack, padrões integração
- `bigtech:security-engineer` (**Shift-Left**): threat model + crypto primitives + classificação de dado

**Gates de fase:**
- Problema validado (não inventado)
- Pillars / outcome definidos
- Não-funcionais declarados (latência, throughput, disponibilidade) **se houver SLO real**
- Decisões one-way door registradas em ADR
- Threat model proporcional ao stake

### Fase 2: Implementação

**Agentes:**
- `bigtech:engineering-manager` (S3+): gestão de pessoas, mentoria e growth do time
- `bigtech:engineering-coach` (S3+): IDP e prática deliberada do engenheiro, sem autoridade hierárquica; promoção e performance formal seguem com `bigtech:engineering-manager`
- `bigtech:scrum-master` (S2+): facilitação ágil
- `bigtech:tech-lead` (S3+): liderança técnica por squad
- `bigtech:backend-engineer`: server-side
- `bigtech:frontend-engineer`: UI (desktop/web)
- `bigtech:mobile-engineer`: clients iOS/Android (se aplicável)
- `bigtech:embedded-firmware-engineer`: firmware/IoT (se aplicável)
- `bigtech:security-engineer` (**transversal**): SAST/SCA em CI, code review crítico em autenticação/sessão/crypto

**Gates:**
- Branch protection com o CI como portão de merge; review aponta só o que quebra o critério de pronto
- SAST/SCA limpos
- Teste da lógica de produto passando no CI (TDD), conforme `TESTES` (`${CLAUDE_PLUGIN_ROOT}/docs/house/TESTES.md`)

### Fase 3: Dados, IA, MLOps

**S0/S1:** geralmente vazia.
**S2+:** ativa se há analytics/ML.

**Agentes:**
- `bigtech:data-engineer`: pipelines, warehouse, lineage
- `bigtech:data-scientist`: modelos, stats, responsible AI
- `bigtech:ml-engineer`: MLOps em produção
- `bigtech:applied-ai-engineer`: integração de LLM/IA aplicada ao produto
- `bigtech:security-engineer` (**transversal**): governança PII no pipeline, model supply chain, prompt injection se LLM

### Fase 4: Qualidade, Segurança, Compliance, Docs

**Agentes:**
- `bigtech:qa-engineer`: teste da lógica de produto (piso de testes)
- `bigtech:security-engineer` (**gatekeeper formal**): DAST + pentest controlado + relatório
- `bigtech:compliance-legal`: LGPD/GDPR/app store/OSS license (proporcional)
- `bigtech:technical-writer`: docs API + how-to + reference

**Gates:**
- CI do ramo verde com o teste da lógica de produto
- Pentest report zerado de critical/high
- Compliance: política privacidade publicada, OSS licenses limpas
- Docs mínimas: README + getting-started + reference

### Fase 5: Integração Contínua, Operação, Sustentação

**Agentes:**
- `bigtech:devops-sre`: CI/CD, infra, SLO, IR
- `bigtech:i18n-l10n-specialist`: locale/RTL/ICU/CLDR (se multi-locale)
- `bigtech:security-engineer` (**transversal**): SecOps, WAF, IDS/IPS, secrets, IR playbook
- `bigtech:product-manager`: métricas pós-launch, próximo ciclo

**Gates:**
- Pipeline CI/CD operante (no provedor de CI do projeto)
- Observability (logs estruturados + métricas + traces)
- Backup + restore drill testado
- Runbook por alerta crítico
- Postmortem template pronto
- Antes do go, rode os checks de `DEPLOY_CHECKLIST` (`${CLAUDE_PLUGIN_ROOT}/docs/house/DEPLOY_CHECKLIST.md`)

---

## 3. Shift-Left de segurança (security-engineer transversal)

`bigtech:security-engineer` opera em **todas as 5 fases**, não só na 4:

| Fase | Atuação |
|---|---|
| 1. Concepção | Threat modeling (STRIDE/PASTA) + escolha de primitives criptográficas + classificação de dado |
| 2. Implementação | SAST/SCA em CI bloqueando PR; code review crítico em auth/sessão/IO externo |
| 3. Dados/IA | Governança PII, anonimização, model supply chain, prompt injection |
| 4. QA | DAST + fuzzing + pentest controlado + report formal |
| 5. Operação | WAF, IDS/IPS, secrets vault, IR playbook compartilhado com `bigtech:devops-sre` |

**Calibre por nível:** S0 = não precisa; S1 = checklist OWASP top 10; S2 = threat model leve + SAST; S3+ = pleno DevSecOps.

---

## 4. Anti-over-engineering (gatekeeper obrigatório)

**Antes de invocar um agente, pergunte:**

1. **Existe trade-off real ou é decisão óbvia?** Decisão óbvia não precisa agente. Trade-off real chama o specialist.
2. **O custo de errar excede o custo de chamar o agente?** Threat model num CLI offline pessoal = overkill. Threat model em API pública = obrigatório.
3. **O artefato gerado vai ser usado?** PRD de 30 páginas pra MVP early/pequeno nunca lido. README curto sempre lido. Otimizar pra leitor.
4. **Há evidência empírica do problema?** "Vai escalar" sem dado = não-requisito.

### Smell de over-engineering

| Smell | Correção |
|---|---|
| Microsserviços antes de monolito modular | Voltar a monolito modular bem-fatorado |
| Event-driven sem necessidade de desacoplamento real | Síncrono + função |
| Cache antes de medir latência | Remover; medir; só adicionar quando dor real |
| Abstração genérica pra UMA implementação | Manter o código concreto; extrair só na 3ª ocorrência do mesmo padrão |
| Feature flag pra mudança one-shot reversível por re-deploy | Sem flag |
| Kubernetes pra app de 100 usuários | systemd + Caddy + Postgres num VPS |
| 3 camadas de DI / factories sem polimorfismo real | Construtor direto |
| Custom DSL antes de YAML/TOML resolver | Config padrão |
| ORM completo pra 4 tabelas simples | SQL direto + 1 query builder leve |
| 8 categorias de log estruturado num CLI | `print` ou logger simples |

### Princípios anti-over-engineering

- **Tudo o que não foi pedido é over-engineering.** Validar com o usuário antes de adicionar.
- **3 linhas similares > abstração prematura.** Esperar 3ª ocorrência.
- **Sem otimização sem profile.** Hot path real raramente é onde se imagina.
- **Sem `for the future`.** Construir pra hoje; refatorar quando o futuro chegar.
- **Sem feature flag pra mudança simples.** Flag tem custo de manutenção.
- **README + 1-2 ADRs > wiki de 50 páginas.**

---

## 5. Trilha de escalonamento (pequeno → grande)

Projetos crescem. Reconheça **sinais** e migre **incrementalmente**, não big-bang.

### Sinais que indicam migração de nível

**S0 → S1:**
- Vai usar em produção / outras pessoas vão usar
- Precisa de update / deploy regular
- Custo de bug ficou não-trivial

**Ações:** introduzir CI básica, testes do crítico, README adequado, monitoramento mínimo.

**S1 → S2:**
- 3+ pessoas codificando
- Múltiplos componentes (front + back)
- Compliance entra (LGPD básico)
- SLA com cliente

**Ações:** introduzir PRD-curto, ADRs, threat model leve, SAST/SCA em CI, observability básica (logs + healthcheck).

**S2 → S3:**
- 8+ devs em squads
- Releases coordenadas entre times
- Múltiplas regiões / multi-locale
- Analytics / ML em produção

**Ações:** introduzir tech leads, `bigtech:engineering-manager` por área (gestão e mentoria), scrum master, data engineering, design system formal, runbooks, SLO formal, capacity planning.

**S3 → S4:**
- 30+ devs
- Compliance regulada (PCI, HIPAA, SOX)
- Crítico (financeiro, saúde, vida)
- Multi-tenant grande

**Ações:** introduzir compliance dedicado, security DevSecOps maduro, trilha de mentoria/coaching formal sob o `bigtech:engineering-manager`, processo de change management, capacity engineering, DR multi-region testado.

### Refactor pra suportar crescimento (não rewrite)

- **Monolito modular** bem fatorado escala muito mais do que se imagina. Extrair serviço só quando dor real aparece (escala independente, time independente, stack incompatível).
- **Postgres + extensões** (Citus, TimescaleDB) sustenta startup inteiro até centenas de GB.
- **Self-host VPS → managed cloud → k8s** é progressão natural; pular k8s pra app de 100 usuários é over.
- **Teste** cresce com a lógica de produto. Começa com unit de todo comportamento novo (TDD); adiciona integration; e2e por último, no caminho crítico.
- **Observability**: logs estruturados desde D1; métricas RED quando deploy frequente; traces quando distribuído.

---

## 6. Templates rápidos por nível

### S0/S1: PRD-1-página
```markdown
# [Produto]
## Problema (1 frase)
## Quem sente isso (1 frase)
## Solução em 3-5 bullets
## Não-objetivos (o que NÃO vai fazer)
## Métrica de sucesso (1 número)
## Riscos top-3
```

### S2+: PRD estruturado
[Invocar `bigtech:product-manager`: template completo embutido lá]

### S1+: ADR mínimo
```markdown
# ADR-NNN: Título
Status: Accepted | Date: YYYY-MM-DD
## Contexto (3-5 linhas)
## Decisão (1-2 linhas)
## Opções consideradas (bullets)
## Consequências (positivas + negativas)
## Reversibilidade: one-way | two-way
```

### S2+: threat model leve
```markdown
# Threat Model: [Sistema]
## Assets
## Atores (legítimo + adversário)
## STRIDE por componente principal
## Top 5 riscos + mitigação
```

---

## 7. Como usar esta skill

1. **Identifique o nível** (S0-S4) com 1-3 perguntas se necessário
2. **Mapeie quais agentes** invocar conforme matriz
3. **Execute as fases** com agentes apenas onde adicionam valor
4. **Aplique shift-left de segurança** proporcional
5. **Cheque smells de over-engineering** antes de cada novo agente / camada / abstração
6. **Reconheça sinais de escalonamento** e migre incrementalmente quando aparecerem
7. **Documente decisões one-way door** em ADR
8. **Sempre prefira o agente correto** ao codificar genericamente: esse é o ponto desta skill

## Integração com ecossistema

- Os agentes são acionados conforme a matriz (a constelação C-level completa é montada pela skill `/bigtech:bigtech`). **Ao despachar um agent, inclua no prompt o caminho absoluto de `docs/`**: subagents não herdam o contexto de sessão.
- Skill **`/bigtech:bigtech`**: camada de NEGÓCIO/liderança (C-levels, pipeline de produto de 12 fases, GTM, release). Quando um projeto precisa de produto/marketing/vendas/release além da engenharia, comece por `/bigtech:bigtech`; ela delega a execução de engenharia (fases 4-9) de volta a esta skill. Os níveis S0-S4 daqui mapeiam aos portes arquiteturais `early|scale|bigtech` de lá (S0/S1 ≈ early minimalista; S2 ≈ early Lean; S3 ≈ scale; S4 ≈ bigtech).
- Skill **`/bigtech:tab_pendencias`**: tabela canônica de pendências.
- Projeto de jogo: esta skill não conduz o ciclo de jogo; use **`/bigtech:proj_jogo`**, que aloca os agents de jogo (`bigtech:gameplay-engineer`, `bigtech:engine-graphics-programmer` etc.) por etapa.
- Diagnóstico Linux de máquina ou serviço: **`/bigtech:suporte-linux`** (coleta com `bigtech:linux-diag`, somente leitura).
- Ensino e capacitação: **`/bigtech:learning-designer`**; coaching de engenheiro: `bigtech:engineering-coach`.
- O pipeline de CI é configurado pelo `bigtech:devops-sre` no provedor de CI do projeto.
- Princípios transversais: 4 camadas, SOLID, TDD e convenções de commit estão em [`arquitetura-principios`](../../docs/principles/arquitetura-principios.md) e `CONTRACT` (`${CLAUDE_PLUGIN_ROOT}/docs/house/CONTRACT.md`).
- Linguagem default: **pt-br**.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
