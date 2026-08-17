# Plano de melhoria do /bigtech para Claude Code e atualização do repositório

**Data da auditoria:** 2026-08-16  
**Repositório distribuível:** `petrinhu/bigtech_plugin`  
**Vault/instalação viva auditada:** `petrinhu/claude-memory` como espelho não-secreto de `~/.claude/`  
**Objetivo:** tornar o `/bigtech` uma camada de orquestração confiável para projetos predominantemente de um único mantenedor humano, sem confundir headcount com complexidade, e eliminar divergência entre a instalação viva e o plugin publicado.

> Este arquivo é um **runbook para Claude Code**. Não é uma coleção de sugestões. Cada fase possui pré-condições, medição, Definition of Done e gates de publicação.

---

## Regra de interpretação dos modelos (Claude **e** Grok — sem versão hardcoded)

**Proibição:** não gravar slugs de versão de modelo no plano, nos prompts, nem em prosa operacional (ex.: “4.5”, “4.6”, “Sonnet 4”, “Opus 5”). Sempre o **papel relativo** ao catálogo **atual** do host.

### Notação canônica em prosa

| Papel | Claude (host Claude Code) | Grok (host Grok Build) | Uso típico |
|---|---|---|---|
| Implementação / fatia delimitada | **[sonnet][mais recente]** | **[grok][modelo anterior ao mais recente]** | código, testes, docs mecânicas, migração local |
| Orquestração / arquitetura / auditoria cotidiana | **[opus][mais recente]** | **[grok][modelo anterior ao mais recente]** | main, C-level planejando, review adversarial rotina |
| Teto (gates FABLE-*, redesign global, auditoria final de campanha) | **[fable][mais recente]** | **[grok][mais recente]** | só gates explicitamente `FABLE-*` ou ordem do líder |

Mapa de equivalência (ordem do líder 2026-08-16, campanha bigtech dual-host):

- Onde o plano disser **[fable][mais recente]** → no Grok usar **[grok][mais recente]**.
- Onde o plano disser **[opus][mais recente]** ou **[sonnet][mais recente]** → no Grok usar **[grok][modelo anterior ao mais recente]**.
- Resolver o ID concreto só na hora do spawn, consultando o catálogo vivo do host (nunca pin de versão no texto do plano).

Frontmatter/YAML do Claude Code pode continuar com literais de máquina (`model: opus`, `model: sonnet`) quando a plataforma exigir; isso **não** autoriza hardcode de geração (“5”, “4.6”) na prosa humana nem nos briefs dual-host.

Sinônimos legados neste arquivo (“[sonnet][mais recente]”, etc.) leem-se pela tabela acima.

---

## Manuais canônicos do vault (obrigatórios em **todos** os projetos da campanha)

**Ordem do líder (2026-08-16):** o bigtech e **qualquer** projeto sob esta campanha **sempre** devem aplicar as orientações dos manuais da raiz do vault claudebrain (fonte de verdade da casa), não só o que estiver dentro do plugin:

| Manual | Path canônico no vault do líder |
|---|---|
| Contrato / DoD | `/home/petrus/IDrive/Documentos/projetos_claudebrain/CONTRACT.md` |
| Testes | `.../TESTES.md` |
| Tooling por papel | `.../TOOLING.md` |
| Pipeline de release | `.../pipeline_release_1.0.md` |
| Deploy | `.../DEPLOY_CHECKLIST.md` |
| Liderança do pipeline | `.../lideranca_pipeline_release.md` |
| Organização / constelação | `.../ORG.md` |
| Standards | `.../Standards.md` |
| Ágil | `.../AGILE.md` |
| Auditorias | `.../AUDITORIAS.md` |

### Distribuição para quem não tem o vault

Estes arquivos **podem e devem** ser **commitados e pushados** no repositório do produto (ex.: `docs/house/` ou `docs/canon/` no `bigtech_plugin` / consumidor), com:

- cópia **sem segredos**;
- nota de origem e data de sincronização;
- instrução de que, se o usuário tiver o vault, o vault prevalece em conflito; se não tiver, usa a cópia versionada no repo.

Fase 0 / docs da campanha inclui: inventariar, copiar (se ainda não estiver no repo), e referenciar no README/AGENTS do plugin.

Conflito vault × cópia no repo: **não** “resolver no silêncio” — classificar e elevar ao líder se a divergência for material.

---

# Mandato da campanha

1. O main/orquestrador da campanha roda em **[opus][mais recente]** (Claude) / **[grok][modelo anterior ao mais recente]** (Grok).
2. O main pode delegar trabalho delimitado a **[sonnet][mais recente]** (Claude) / **[grok][modelo anterior ao mais recente]** (Grok).
3. **[fable][mais recente]** (Claude) / **[grok][mais recente]** (Grok) só entra em gates explicitamente marcados `FABLE-*` (ou ordem do líder).
4. Subagents podem inspecionar, editar em worktrees isolados e devolver diffs/relatórios.
5. Subagents **não fazem push, merge, tag ou release**.
6. O main relê o diff, reroda as medições e testes relevantes e só então publica.
7. Nenhuma alegação “sincronizado”, “atualizado”, “sem conflito”, “modelo corrigido” ou “plugin ativo” é aceita sem medição direta.
8. Não modificar a instalação viva de `~/.claude/` (nem `~/.grok/` de forma destrutiva) antes do canário do plugin atualizado.
9. Não apagar diferenças do vault só para fazer os dois lados parecerem iguais: primeiro classificar cada diferença como `CORE-GENERIC`, `PERSONAL-OVERLAY`, `STALE` ou `INTENTIONAL-EXCLUSION`.
10. Aplicar em **todo** projeto da campanha os manuais canônicos (CONTRACT, TESTES, TOOLING, pipeline_release, DEPLOY_CHECKLIST, lideranca_pipeline_release, ORG, Standards, AGILE, AUDITORIAS) — ver seção acima; copiar para o repo quando o usuário não tiver o vault.
11. Dual-host: prosa e briefs usam a notação **[claude][papel][mais recente]** e **[grok][mais recente|modelo anterior ao mais recente]**; **nunca** hardcode de versão de modelo.

---

# Pré-requisitos de DESBLOQUEIO desta campanha (Gate tab_pendencias → bigtech)

**Ordem do líder (2026-08-16):** a campanha de melhoria do `/bigtech` **só desbloqueia** (execução de fases deste plano, “AGORA É HORA DE bigtech”) quando **todos** os critérios abaixo estiverem **checked** (medidos no disco, não alegados). Isto reforça e estreita o Gate 1 do briefing de reorganização do ecossistema.

## Checklist de desbloqueio (tudo obrigatório)

### 1. Pendências de campanha do `tab_pendencias` — checked

- Toda pendência **desta campanha/projeto** (`TAB-*`, `FIX-RISCO*`, `AUD-FUP*`, decisões 16/08 da campanha, `BUS-1`, `INTAKE-*`, e demais IDs da campanha de melhoria) está em estado terminal aceitável: **não há ⏳/🔄 de campanha**.
- **Exceção explícita: legados não bloqueiam.** Itens legados (ex.: ADR-1, SCAF-1, CI-* antigos, BUG-5 histórico, WIKI-1 de backlog antigo, dezenas de 🔍 pré-campanha) **não** entram neste checklist e **não** impedem o desbloqueio.
- `classifiable_inbox_count == 0` no `todo_health` do `tab_pendencias`.
- Working tree do `tab_pendencias` sem fatia crítica de campanha só dirty/untracked.

### 2. Ligação global Claude **e** Grok — checked

A instalação do produto `tab_pendencias` deve estar **corretamente linkada** nos dois hosts globais:

| Host | Exigência mínima |
|---|---|
| **Grok** (`~/.grok`) | Skill `tab_pendencias` resolve para o **produto** (symlink ou path vivo), sem stub YOLO, sem link quebrado; hooks/reminder de sessão resolvem arquivo real. |
| **Claude** (`~/.claude`) | Skill `tab_pendencias` instalada e legível (submódulo/pin ou path documentado); hooks em `settings` apontam para path **vivo** da skill/hooks; sem path morto. |
| **Ambos** | Auditoria de wiring com veredito **`LIGADO_OK`** (não basta “descobre no catálogo”). Gaps **P0 e P1** da auditoria de wiring (ex.: `core.hooksPath` apontando para árvore de **dev** em vez da instalação publicada — HOOKSRC-1; pin Claude irremediavelmente divergente se quebrar runtime) devem estar **fechados** antes do desbloqueio. |
| **Prova** | Relatório versionado no control plane `reorg_gus_ecosystem/reports/tab_pendencias_global_wiring_*.md` (ou re-medição equivalente no mesmo dia do unlock) com `gaps_p0=0` e P1 de ligação tratados. |

### 3. CI multi-OS do `tab_pendencias` — checked (mesma matriz, mesmo rigor)

Antes de desbloquear bigtech, o **CI do `tab_pendencias` no GitHub** deve estar **verde** na **mesma matriz multi-OS** que o projeto já roda (referência: `.github/workflows/ci.yml` do `tab_pendencias`), **mesmo que** parte do gate de campanha anterior não tivesse exigido isso explicitamente:

| Superfície (referência tab_pendencias) | Obrigatório no desbloqueio |
|---|---|
| **Ubuntu nativo** (`ubuntu-latest`) + versões Python da matrix | hard gate verde |
| **Windows nativo** (`windows-latest`) + Python da matrix | hard gate verde |
| **Debian** (container, ex. `debian:12-slim`) | hard gate verde |
| **Fedora** (container, ex. release estável numerada) | hard gate verde |
| **Arch** (container `archlinux`) | hard gate verde |
| Jobs auxiliares do mesmo workflow (lint/shellcheck/etc. se hard no projeto) | conforme o workflow canônico do tab_pendencias |

Prova: SHA do commit do `tab_pendencias` sob teste + URL/run id do GitHub Actions **verde** na matrix completa (não só job local ou só Ubuntu).

### 4. Registro no control plane

- `ORCHESTRATION_STATE.md` grava o unlock com: `bigtech_liberated: true` **somente** após os itens 1–3; cita SHA tab, veredito wiring, e run de CI multi-OS.
- Até lá: **AINDA NÃO É HORA DE** bigtech; **AGORA É HORA DE** fechar o que faltar em tab_pendencias / wiring / CI.

## O que isto NÃO é

- Não exige zerar ✅ em todo o backlog legado do `TODO.md`.
- Não autoriza push/tag sem ordem do líder.
- Não substitui os gates **internos** deste plano (fases 0–N, FABLE-*, cutover do plugin).

---

# CI multi-OS obrigatório **deste** repositório (`bigtech_plugin`) — mesmo que não estivesse previsto

**Ordem do líder (2026-08-16):** o plugin/repositório bigtech **deve** adotar e manter CI no GitHub com a **mesma filosofia de matrix multi-OS** do `tab_pendencias`, **mesmo que** a métrica antiga (“>=1 workflow”) ou a Fase 9 abaixo tenham previsto apenas um job único.

### Matrix mínima obrigatória (espelho tab_pendencias)

1. **Job nativo:** `ubuntu-latest` + `windows-latest` (e Python pinado como no produto).
2. **Job em container no Ubuntu runner:** **Debian**, **Fedora**, **Arch** (imagens pinadas por digest quando o tab_pendencias o fizer; root vs user comum se o tab_pendencias tiver essa disciplina).
3. Hard gates sem `|| true` / skip silencioso que transforme falha em verde.
4. Scripts locais (`preci`/equivalente) e Actions chamando a **mesma** base de checks, na medida do possível.

Isto **entra no Definition of Done de publicação** (Fase 9 / release): release candidata **não** sobe com matrix incompleta ou só-Ubuntu. Se a fase 9.2 listar checks sem matrix, a matrix acima **prevalece** como requisito adicional do líder.

Métrica da campanha (atualização):

| Métrica | Alvo antigo | Alvo com ordem 16/08 |
|---|---|---|
| GitHub Actions multi-OS (ubuntu+windows+debian+fedora+arch) | não exigido de forma explícita | **obrigatório e verde** antes de release e como padrão permanente |

---

# Métricas primárias da campanha

A campanha não mede sucesso por commits, linhas alteradas ou versão publicada. Mede:

| Métrica | Baseline auditado | Alvo |
|---|---:|---:|
| Fontes de verdade ativas para o núcleo bigtech | pelo menos 2 | 1 |
| Agentes core duplicados em escopo de usuário e plugin | existência confirmada; contagem exata deve ser medida localmente | 0 |
| Hooks bigtech/TDD/tab do plugin duplicados por registro global | globais existentes; plugin ainda não habilitado no snapshot auditado | 0 após migração |
| `solo` usado como porte/classificação arquitetural | presente | 0 |
| Headcount usado para determinar perfil arquitetural | presente | 0 |
| Referências operacionais a host legado (não-GitHub) | presentes | 0 |
| GitHub Actions para o repo | 0 workflow verificado / só CI do host anterior no baseline | matrix multi-OS espelho tab_pendencias (ubuntu+windows nativos + debian+fedora+arch em container) **verde** + gates semânticos |
| Proteção de `main` | desativada | ativada com gate obrigatório |
| Uso inválido de override `model=fable` por Agent tool | presente no vault | 0 |
| Drift semântico detectável automaticamente entre registry/agents/skills/docs | não existe gate específico | gate obrigatório |
| Evals de roteamento `/bigtech` | não medidos | suite versionada e verde |

A cada fase, imprimir **antes → depois** destas métricas quando a fase puder alterá-las.

---

# I. FALHAS HISTÓRICAS

## I.1. A publicação e a instalação viva viraram duas linhas evolutivas

### Evidência medida

- `bigtech_plugin/main` auditado em `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6`, release `0.2.0`, de 2026-06-21.
- `claude-memory/main` auditado em `627e507fbee06b6ed4d8940526a43f76ffc1ddb1`, com snapshots até 2026-08-16.
- O vault possui cópias próprias de `agents/`, `skills/bigtech/` e hooks bigtech.
- Arquivos amostrados com o mesmo papel têm SHA e conteúdo diferentes entre os dois repositórios.

### Mecanismo do erro

O produto distribuível não foi tornado a fonte canônica da instalação pessoal. Melhorias continuaram surgindo em `~/.claude/`, enquanto o plugin ficou parado. Isto gera **dual authority**: editar um lado não atualiza o outro.

### Consequência

Uma release nova do plugin pode estar correta e ainda assim não alterar o comportamento da máquina do mantenedor.

---

## I.2. Agentes globais podem sombrear agentes do plugin

### Evidência de plataforma

A documentação atual do Claude Code define a precedência de subagents homônimos:

1. managed;
2. CLI `--agents`;
3. project `.claude/agents`;
4. user `~/.claude/agents`;
5. plugin `agents/`.

Logo, um agent core mantido simultaneamente no vault e no plugin faz a cópia do usuário vencer a do plugin.

### Mecanismo do erro

A própria estratégia de backup preservou como configuração ativa o que deveria ter virado overlay ou dependência versionada.

### Consequência

“Atualizar `bigtech_plugin`” não implica “Claude passou a usar o agent atualizado”.

---

## I.3. Skills não têm a mesma semântica de colisão que agents

### Evidência de plataforma

Skills de plugin são namespaced. Uma skill `bigtech` do plugin aparece como `bigtech:bigtech`; uma skill pessoal `~/.claude/skills/bigtech` continua sendo `/bigtech`.

### Falha histórica

Documentação do plugin trata agentes, skills e hooks como se todos sofressem o mesmo tipo de conflito de nomes.

### Correção conceitual

- **Agent duplicado:** há precedência/sombreamento real.
- **Skill pessoal x plugin:** coexistem por namespace; o risco é **dupla implementação semântica**, não colisão do identificador.
- **Hook global + hook de plugin:** ambos podem executar e produzir efeito duplicado.

---

## I.4. A classificação ainda confunde headcount com porte em parte da stack

### Evidência medida

`skills/bigtech/SKILL.md` ainda pergunta:

- `Headcount | Solo / Early / Scale / Bigtech`;
- aceita `--porte solo|early|scale|bigtech`;
- mapeia `solo / pessoal → Pipeline-Sprint → S0/S1`.

Ao mesmo tempo, `cosimo-chief-of-staff` do plugin já contém a regra “NUNCA classificar como solo” e manda dimensionar por complexidade, criticidade e escala, não por uma única pessoa humana.

### Mecanismo do erro

A política nova foi aplicada no agente Cósimo, mas não propagada à skill, hooks, marcador e documentação.

### Consequência

A classificação depende de qual componente está falando. Um ecossistema multi-repo crítico mantido por uma pessoa pode ser rebaixado por um componente e promovido por outro.

---

## I.5. `porte` virou um nome ruim para a variável realmente necessária

O usuário é primariamente o único mantenedor humano dos projetos. Portanto headcount quase nunca discrimina risco arquitetural. A variável útil é **perfil operacional/complexidade**, não tamanho de empresa.

Um projeto de uma pessoa pode ter:

- múltiplos repositórios e contratos cruzados;
- dados sensíveis;
- consumidores reais;
- build multiplataforma;
- migrações irreversíveis;
- cadeia de dependências longa;
- blast radius alto.

Tratar tudo isso como “pequeno porque solo” é erro de modelo de domínio.

---

## I.6. O reforço por turno combate drift criando outro tipo de drift

### Evidência medida

`bigtech_reinforce.py` injeta, a cada `UserPromptSubmit` de projeto classificado, uma mensagem relativamente longa sobre constelação, C-levels, gerenciamento, anti-over-engineering e autoridade.

### Mecanismo do erro

O hook foi projetado para impedir que Claude esqueça o modo bigtech. Mas a política é injetada independentemente de o pedido atual ser estratégico ou uma edição técnica trivial.

### Risco

- consumo repetitivo de contexto;
- indução a cerimônia em tarefas locais;
- ativação mental de papéis gerenciais que não agregam à ação corrente;
- aumento de conflito com outras skills/hooks.

A correção não é remover governança. É tornar o reforço **state-aware e intent-aware**.

---

## I.7. Política de modelo existe, mas não fecha com a API atual

### Evidência medida no vault

`session_models_apply.py` e `/modelos_sessao`:

- ainda rotulam o tier principal antigo;
- aceitam `fable` como se fosse alias válido do parâmetro `model` da Agent tool;
- instruem o main a passar esse valor em cada invocação.

### Evidência da plataforma atual

A Agent tool aceita override por invocação para aliases suportados; o full model ID é aceito na **definição do subagent**, mas o schema atual de `AgentInput.model` não oferece o alias `fable`.

### Mecanismo do erro

Uma capability de produto evoluiu depois da automação local, mas o hook não possui contract test contra o schema atual.

### Consequência

O tier mais caro/forte pode estar configurado no estado sem ser aplicável da forma prometida.

---

## I.8. A amostra de agents mostra sobrealocação de modelo

### Medição direta da amostra

Na auditoria, os seguintes agentes publicados declaravam `model: opus`:

- `cosimo-chief-of-staff`;
- `caetano-cto`;
- `software-architect`;
- `tech-lead`;
- `backend-engineer`;
- `qa-engineer`;
- `engineering-manager`;
- `scrum-master`;
- `product-manager`;
- `internal-auditor`.

**Não declarar que os 51 estão em `opus` sem medir todos.** A campanha deve calcular a distribuição completa via parser local.

### Mecanismo provável

O frontmatter cresceu de forma uniforme, sem tiering por natureza da tarefa.

### Efeito

- custo e latência maiores;
- pouco incentivo para decompor tarefas;
- modelo mais forte gasto em execução mecânica;
- `effortLevel=xhigh` global do vault amplifica o custo quando o agent herda esforço.

---

## I.9. Regras cross-cutting foram copiadas para dezenas de prompts

Amostras de agents repetem blocos sobre:

- compatibilidade Claude Code;
- localização de `docs/`;
- leitura obrigatória;
- autoridade do usuário;
- TODO pre-flight;
- missing-tool policy;
- hardware limits.

### Mecanismo do erro

Faltou uma camada de contexto comum injetada de forma confiável no subagent.

### Consequência

- prompts maiores;
- mudanças globais exigem N edições;
- versões ficam divergentes;
- um agent pode carregar regra antiga enquanto outro já recebeu a nova.

---

## I.10. O docs-bootstrap depende de repasse manual que hoje pode ser automatizado melhor

`bigtech_session_init.py` injeta o path de `docs/` na thread principal e manda o main repetir esse path em todo prompt de subagent.

Claude Code atual expõe `SubagentStart` com `additionalContext`. Portanto existe hoje uma seam melhor: um hook pode injetar o path e o contrato mínimo diretamente em cada subagent da constelação.

A implementação antiga não era necessariamente errada quando criada; ela ficou inferior às capabilities atuais da plataforma.

---

## I.11. Correção de uma afirmação errada feita durante esta auditoria

Foi dito inicialmente que a frase “subagent não dispara subagent” estaria obsoleta. **Isso estava errado.** A documentação atual do Claude Code continua explícita: subagents não podem spawnar outros subagents; workflows aninhados devem ser encadeados pela main conversation, por skills ou por outros mecanismos de agentes paralelos.

Regra para o relatório final: não remover esta limitação dos prompts. Remover apenas ferramentas `Agent` inúteis de subagents quando elas não tiverem finalidade como main-agent via `--agent`.

---

## I.12. Migração de hospedagem ficou incompleta

### Evidência medida (baseline `61c3ea4`, pré-BT-3)

O vault já registrou saída do host legado (fora de escopo; GitHub único) em agosto de 2026. No baseline do plugin ainda havia (passado; alvo BT-3 = purgar):

- `homepage`/`repository` apontando para o host legado;
- instruções de instalação e clone pelo host legado;
- CI legado sob path do host anterior;
- nenhuma `.github/workflows/` encontrada na auditoria da época.

### Mecanismo do erro

A migração foi aplicada ao vault e a outros artefatos, mas não fechou o ciclo de distribuição deste plugin. **Ordem do líder 2026-08-16:** GitHub único (`github.com/petrinhu/bigtech_plugin`); zero refs operacionais a host legado / só GitHub (BT-3).

---

## I.13. Há CI de sanitização, mas falta CI semântico de orquestração

`scripts/validate_plugin.py` verifica bem:

- wikilinks;
- paths locais;
- termos pessoais;
- referências excluídas;
- links relativos órfãos.

Isto protege distribuição. Não verifica, porém:

- `solo` proibido em um arquivo e aceito em outro;
- agent referenciado mas inexistente;
- agent existente mas sem rota;
- modelo inadequado ao papel;
- ferramenta deprecada;
- docs que contradizem a skill;
- hook que injeta schema antigo;
- distribuição de modelos e effort;
- duplicação entre registry e frontmatter.

O próximo gate precisa testar **semântica**, não só higiene textual.

---

# II. ESTADO ATUAL, MEDIDO AGORA

## II.1. Repositório distribuível

Baseline auditado (`61c3ea4`, passado — estado pré-BT-3):

- repo: `petrinhu/bigtech_plugin`;
- `main`: `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6`;
- release declarada: `0.2.0`;
- último commit medido: 2026-06-21;
- 51 agents e 4 skills declarados no próprio release/AGENTS;
- `main` **não protegida**;
- required status checks: nenhum;
- CI encontrada no baseline: path do host anterior (legado a purgar em BT-3/BT-4);
- GitHub Actions no baseline: nenhum workflow encontrado;
- metadados do plugin no baseline ainda apontavam para o host legado.
- **Alvo pós-BT-3 (ordem 2026-08-16):** host canônico `https://github.com/petrinhu/bigtech_plugin`; zero refs operacionais ao host legado.

---

## II.2. Instalação/vault

Baseline auditado:

- `claude-memory/main`: `627e507fbee06b6ed4d8940526a43f76ffc1ddb1`;
- README declara 71 agents e 46 skills;
- o validador do plugin enumera 20 agents pessoais/excluídos do produto, número coerente com um núcleo de 51, mas a interseção completa deve ser recalculada localmente antes de qualquer remoção;
- `settings.sanitized.json` registra hooks globais bigtech, TDD e tab;
- `enabledPlugins` do snapshot **não inclui `bigtech`**;
- `effortLevel` global está em `xhigh`;
- Agent Teams experimental está habilitado;
- Agent View está desabilitado.

Conclusão: a máquina auditada está operando **principalmente o bigtech standalone do vault**, não o plugin publicado.

---

## II.3. Divergência concreta entre vault e plugin

Exemplos medidos:

- `skills/bigtech/SKILL.md` possui SHAs diferentes e regras diferentes;
- `cosimo-chief-of-staff.md` difere;
- `caetano-cto.md` difere;
- `bigtech_reinforce.py` difere;
- o vault contém extensões pessoais/game-dev que o validador do plugin deliberadamente exclui do produto público.

Portanto **nem toda divergência é staleness**. Parte é overlay pessoal legítimo.

---

## II.4. Semântica de porte está inconsistente

Hoje coexistem:

- skill: `solo` é uma categoria de porte;
- Cósimo publicado: `solo` não deve ser categoria de porte;
- hooks: mensagens ainda falam em `solo/early/scale/bigtech` e “calibrar headcount pelo porte”.

Estado atual: **inconsistente**.

---

## II.5. Modelo e effort

Estado medido:

- todos os 10 agents amostrados acima usam `model: opus`;
- o vault força `effortLevel=xhigh` global;
- existe override por sessão;
- esse override está com rotulagem antiga e caminho inválido para o tier **[fable][mais recente]** via parâmetro por invocação.

A distribuição total dos 51 modelos não foi reproduzida pela API de busca do GitHub nesta auditoria. **Medição obrigatória local na Fase 0.**

---

## II.6. Claude Code atual oferece primitives que o plugin ainda não explora

A plataforma atual suporta em custom/plugin agents:

- `skills` preload;
- `memory`;
- `effort`;
- `maxTurns`;
- `background`;
- `isolation: worktree`;
- `disallowedTools`;
- full model ID no frontmatter;
- `SubagentStart` para injeção de contexto;
- precedence explícita de agent scopes;
- skills de plugin namespaced;
- dependências entre plugins com constraints;
- `/reload-plugins`;
- worktrees e agent teams como mecanismos distintos de paralelismo.

O desenho atual usa apenas parte desse conjunto.

---

# III. PLANO DE MELHORIA E PREVENÇÃO

# Estado-alvo arquitetural

```text
                         +------------------------+
                         |     usuário / main     |
                         | [opus][mais recente]|
                         +-----------+------------+
                                     |
                             /bigtech wrapper
                                     |
                         bigtech:bigtech (plugin)
                                     |
                           Cósimo / classificador
                                     |
                   +-----------------+------------------+
                   |                                    |
          decisão estratégica                  execução delimitada
     [opus][mais recente]             [sonnet][mais recente]
                   |                                    |
        C-level / architect                      specialists / QA
                   |                                    |
                   +---------------+--------------------+
                                   |
                             evidência / gates
                                   |
                       auditoria final excepcional
                       [fable][mais recente]
```

Fonte de verdade:

```text
bigtech_plugin
  ├── agents/             <- CORE distribuível canônico
  ├── skills/             <- workflows canônicos
  ├── hooks/              <- hooks do produto
  ├── docs/               <- governança canônica
  ├── config/agent-registry.json
  ├── scripts/audit_agents.py
  ├── evals/
  └── .github/workflows/

claude-memory
  ├── CLAUDE.md           <- preferências pessoais
  ├── memory/             <- memória pessoal/cross-project
  ├── agents/             <- SOMENTE agents pessoais que não pertencem ao core
  ├── skills/             <- wrappers/skills pessoais, sem duplicar lógica core
  ├── hooks/              <- SOMENTE hooks pessoais não pertencentes ao plugin
  └── settings.*          <- instala/habilita bigtech como plugin user-scope
```

---

# PHASE 0 — Freeze, backup e baseline reproduzível

**Modelo:** main em **[opus][mais recente]**; coleta mecânica pode ser delegada a **[sonnet][mais recente]**.

## 0.1. Não alterar ainda o vault vivo

Antes de instalar/desinstalar plugin ou remover cópias:

```bash
git -C ~/.claude status --short
git -C ~/.claude rev-parse HEAD
```

Guardar baseline e confirmar que `settings.json` real continua fora do git.

## 0.2. Clonar/abrir ambos os repos localmente

Trabalhar com:

- checkout de `bigtech_plugin`;
- checkout/árvore de `claude-memory`;
- checkout do `tab_pendencias` standalone se ele continuar dependência da constelação.

## 0.3. Medir interseção real de agents

Gerar listas por `name:` do frontmatter, não pelo filename.

Saídas obrigatórias:

```text
CORE_ONLY=
VAULT_ONLY=
INTERSECTION=
DUPLICATE_NAME_WITHIN_SCOPE=
```

Para cada item da interseção:

```text
name | sha/product | sha/vault | identical? | classification
```

Classificação:

- `CORE-GENERIC`: melhoria que deve ir para o plugin;
- `PERSONAL-OVERLAY`: informação específica do usuário/vault;
- `STALE`: versão antiga sem razão de existir;
- `INTENTIONAL-EXCLUSION`: papel deliberadamente fora do produto.

## 0.4. Medir modelos, tools e tamanho dos prompts

Criar relatório automático:

```text
agent | bytes | model | effort | maxTurns | tools | disallowedTools | skills | memory | isolation
```

Contadores:

- quantos `model: opus`;
- quantos `model: sonnet`;
- quantos herdam;
- quantos não possuem `effort`;
- quantos não possuem `maxTurns`;
- quantos têm Bash sem necessidade evidente;
- quantos têm `Agent` embora operem apenas como subagent;
- top 10 prompts por bytes;
- blocos boilerplate repetidos.

## 0.5. Medir hooks ativos reais

No `settings.json` vivo + plugins instalados:

```text
event | hook global | hook plugin | executa quantas vezes
```

Não assumir pelo backup sanitizado que o runtime é idêntico.

### DoD Phase 0

- [ ] baseline SHA dos três repos relevantes;
- [ ] inventário exato de agents;
- [ ] inventário exato de skills;
- [ ] inventário exato de hooks;
- [ ] distribuição de modelos medida;
- [ ] nenhum arquivo vivo removido.

---

# PHASE 1 — FABLE-ORG-ARCH: arquitetura de fonte de verdade

**Modelo:** **[fable][mais recente]**.

Objetivo: revisar adversarialmente a separação `produto core` x `overlay pessoal` antes de mover arquivos.

Entregável: `docs/adr/ADR-source-of-truth.md` com decisão explícita:

1. `bigtech_plugin` é autoridade para o conjunto distribuível de agents medido na Fase 0 (baseline publicado hoje declara 51), skills core, hooks core e docs core.
2. `claude-memory` não mantém cópia ativa homônima de agent core.
3. Personalização fica em `CLAUDE.md`, memória, hooks pessoais ou agentes exclusivos.
4. Uma skill pessoal curta pode existir como **compatibility wrapper** para preservar `/bigtech`, mas não pode reimplementar o workflow.
5. Componentes externos, como `tab_pendencias`, têm um único owner e entram por dependência versionada quando tecnicamente viável.

### DoD Phase 1

- [ ] um owner por componente;
- [ ] política de overlay escrita;
- [ ] política de rollback escrita;
- [ ] nenhum “sync bidirecional” permanente.

**Proibido:** criar daemon que copie alterações nos dois sentidos. Isto apenas automatizaria dual authority.

---

## 1.1. Fronteira público × privado antes de sincronizar

A reconciliação não significa copiar `claude-memory` para o repositório público. Classifique cada diferença antes de qualquer port:

| Classe | Destino | Regra |
|---|---|---|
| `CORE-GENERIC` | `bigtech_plugin` | comportamento reutilizável por qualquer usuário do plugin |
| `PERSONAL-OVERLAY` | `claude-memory` | preferência, vocabulário, projeto, agente ou integração específica do mantenedor |
| `STALE` | remover do lado defasado | regra superseded, ferramenta/API antiga ou duplicação sem autoridade |
| `INTENTIONAL-EXCLUSION` | somente vault | capability deliberadamente fora do produto público |

**Proibido:** publicar paths locais, nomes internos de projetos privados, conteúdo do bus, dados de sessão, credenciais, PII, preferências pessoais ou detalhes do vault que não sejam necessários para explicar uma interface pública.

Manter dois artefatos durante a campanha:

1. **Runbook privado completo** — este arquivo, contendo evidência sobre `claude-memory`, reconciliação e cutover pessoal.
2. **Roadmap público sanitizado** — derivado deste runbook, contendo apenas arquitetura genérica, mudanças do plugin, testes e critérios de release.

O roadmap público deve passar `scripts/validate_plugin.py` e gitleaks antes de entrar no branch remoto.

## 1.2. Rollback da reconciliação

Antes de remover qualquer cópia global que sombreie o plugin:

- registrar SHA do plugin canário;
- registrar SHA do `claude-memory`;
- exportar inventário de agents/skills/hooks que serão retirados do escopo ativo;
- preservar o conteúdo removido no histórico git, sem `rm` destrutivo fora de controle;
- testar restauração da configuração anterior em perfil isolado;
- definir `LAST_KNOWN_GOOD_PLUGIN_SHA`;
- se o canário falhar, reativar o overlay anterior e registrar qual gate falhou.

**DoD da fronteira:** nenhuma diferença do vault é publicada sem classificação; nenhum core removido do vault antes de existir equivalente testado no plugin; o rollback para o último estado verde é executável e documentado.

# PHASE 2 — Redesenhar classificação: headcount não define o perfil

**Modelo de planejamento:** **[opus][mais recente]**.  
**Implementação:** **[sonnet][mais recente]**.

## 2.1. Separar PERFIL de CAPACIDADE

Novo domínio:

```text
PERFIL = risco/complexidade/governança necessários
CAPACIDADE = quantos humanos/agentes podem executar em paralelo
```

`capacity=solo` é normal no ambiente do usuário e **não reduz PERFIL**.

## 2.2. Inputs de perfil

Pontuar/avaliar no mínimo:

1. **Criticidade / custo da falha**
   - experimento pessoal reversível;
   - perda de tempo/dados locais;
   - indisponibilidade de consumidor real;
   - dinheiro, saúde, segurança, reputação.

2. **Blast radius**
   - arquivo/módulo;
   - repo único;
   - múltiplos módulos;
   - múltiplos repositórios/consumidores.

3. **Acoplamento/ecossistema**
   - standalone;
   - API interna;
   - dependentes diretos;
   - contratos cross-project/versionamento.

4. **Reversibilidade**
   - revert simples;
   - migração com rollback;
   - dados/formatos públicos;
   - one-way door.

5. **Compliance/dado sensível**
   - nenhum;
   - PII básica;
   - saúde/financeiro;
   - regulação/compliance forte.

6. **Complexidade técnica real**
   - simples/síncrono;
   - concorrência;
   - distribuição;
   - realtime/performance/hardware/multiplataforma.

7. **Distribuição e suporte**
   - uso só local;
   - terceiros ocasionais;
   - usuários reais;
   - biblioteca/framework consumido por outros projetos.

8. **Horizonte de manutenção**
   - descartável;
   - semanas;
   - longo prazo;
   - compatibilidade histórica necessária.

## 2.3. Perfis-alvo

Substituir a semântica de “tamanho de empresa” por:

| Perfil | Significado |
|---|---|
| `lean` | baixo risco, reversível, escopo limitado |
| `standard` | produto/repo real com integração e manutenção |
| `critical` | alto custo de erro, dados sensíveis, multi-repo, contratos ou one-way doors |
| `enterprise` | múltiplos produtos/consumidores, governança/compliance/escala muito alta |

O nome histórico `porte` pode continuar no arquivo de compatibilidade durante uma release, mas não deve mais controlar o comportamento.

## 2.4. Rubrica determinística de classificação

Não produzir o perfil por impressão subjetiva. Para cada dimensão, registrar um nível `0..3` com evidência:

| Dimensão | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| criticidade | descartável | perda local recuperável | usuário/serviço real | saúde, dinheiro, segurança ou dano reputacional relevante |
| blast radius | arquivo | módulo/repo | vários módulos | vários repos/consumidores |
| acoplamento | standalone | integração local | contrato versionado | ecossistema com dependentes independentes |
| reversibilidade | revert trivial | rollback simples | migração coordenada | one-way door / formato público / dado difícil de reverter |
| compliance/dados | nenhum | PII baixa | dado sensível | regulado/saúde/financeiro |
| complexidade técnica | direta | múltiplas camadas | concorrência/realtime/multiplataforma | distribuído/hardware/performance crítica |
| distribuição | local | uso próprio durável | terceiros/consumidor real | framework/lib/produto com múltiplos consumidores |
| manutenção | descartável | curto prazo | produto durável | compatibilidade histórica/longa cauda |

**Headcount/capacidade não entra nesta soma. Peso = zero para o perfil.**

Regra inicial, que deve ser calibrada por evals e não tratada como dogma eterno:

```text
max_dimension == 3 em saúde/segurança/compliance/one-way-door -> critical no eixo correspondente
soma 0..5   -> lean
soma 6..11  -> standard
soma 12..18 -> critical
soma 19+    -> enterprise-candidate, sujeito a confirmação de sinais realmente sistêmicos
```

Não aplicar `enterprise` apenas porque a soma cruzou um número: exigir pelo menos dois sinais sistêmicos nível 3, por exemplo multi-produto + múltiplos consumidores, ou compliance pesado + escala operacional alta.

### Perfis dimensionais

O resultado não precisa inflar toda a organização por causa de um único eixo. Registrar também `risk_axes`, por exemplo:

```json
{
  "profile": "standard",
  "risk_axes": {
    "security": "critical",
    "compliance": "critical",
    "delivery": "lean",
    "architecture": "standard"
  }
}
```

Assim, um software médico solo pode ativar Narciso/Cláudio e gates fortes de segurança/compliance sem introduzir Scrum, CFO, CRO ou cerimônia enterprise desnecessária.

### Histerese anti-thrashing

- escalada por novo sinal nível 3: imediata;
- escalada por score agregado: confirmar em um marco ou segunda medição;
- redução de perfil: só após dois marcos consecutivos sem o sinal que justificou a faixa superior, salvo erro de classificação comprovado;
- trabalho já iniciado não é replanejado por variação marginal de score;
- toda mudança de perfil registra **qual input mudou**.

### Capacidade solo

`capacity=solo` controla somente:

- WIP humano;
- quantidade de decisões simultâneas;
- número de subagents paralelos;
- necessidade de cerimônias humanas;
- tamanho de lotes e frequência de checkpoints.

Não reduz QA, segurança, auditoria ou arquitetura exigidos pelo risco real.

## 2.5. Marker schema v2

Preferir migrar para:

```json
{
  "schema": 2,
  "profile": "critical",
  "capacity": "solo",
  "pipeline": "standard",
  "signals": {
    "criticality": "high",
    "blast_radius": "multi-repo",
    "compliance": "none",
    "reversibility": "medium"
  },
  "classified_at": "YYYY-MM-DD",
  "recheck_on": ["release", "new-consumer", "schema-change"]
}
```

Pode ser `.bigtech.json`. Manter leitura do `.bigtech-porte` legado durante migração.

## 2.6. Evals obrigatórios de classificação

### CASE-A — trivial solo

Um script pessoal de 200 linhas, local, descartável.

Esperado: `lean`.

### CASE-B — ecossistema solo multi-repo

Um mantenedor, 6 repos, dependências cruzadas, framework consumido por dois apps.

Esperado: no mínimo `standard`; pode subir a `critical` conforme blast radius/one-way doors.

### CASE-C — saúde solo

Um mantenedor, app pequeno, mas com dado médico/PII.

Esperado: `critical` em segurança/compliance sem virar cerimônia enterprise em todas as dimensões.

### CASE-D — time grande, produto simples

Muitos colaboradores fazendo um site estático sem dado crítico.

Esperado: headcount não promove sozinho a `enterprise`.

### DoD Phase 2

- [ ] `solo` não aparece como perfil/porte arquitetural;
- [ ] headcount não altera score de perfil;
- [ ] capacidade é campo separado;
- [ ] CASE-A..D passam;
- [ ] Cósimo, skill, hooks e docs usam a mesma taxonomia.

---

# PHASE 3 — Redesenhar `/bigtech` como orquestrador state-aware

**Planejamento:** **[opus][mais recente]**.  
**Implementação:** **[sonnet][mais recente]**.

## 3.1. `/bigtech` deixa de “montar empresa” em toda chamada

Ele passa a executar quatro funções:

```text
CLASSIFY -> ROUTE -> EXECUTE -> RECHECK
```

### CLASSIFY

Só recalcula profile quando:

- não existe estado;
- requisito altera blast radius;
- entra novo consumidor;
- muda compliance/dado;
- há migração one-way;
- usuário pede explicitamente;
- gate/release exige rechecagem.

### ROUTE

Seleciona **capabilities necessárias para o pedido atual**, não “todos os cargos adequados ao projeto”.

### EXECUTE

Main chama só os agentes cuja decisão/trabalho é necessário.

### RECHECK

Após mudança estrutural, recalcula profile e activation map.

## 3.2. Output mínimo de Cósimo

```text
PROFILE: <lean|standard|critical|enterprise>
CAPACITY: <solo|small-team|...>
TASK_CLASS: <local|cross-cutting|release|incident|product|...>
ACTIVE_CAPABILITIES: [...]
AGENTS_TO_RUN_NOW: [...]
AGENTS_NOT_NEEDED: [...]
DEPENDENCY_ORDER: [...]
PARALLEL_SAFE: [...]
USER_DECISIONS_REQUIRED: [...]
RECHECK_TRIGGER: [...]
ANTI-OE_JUSTIFICATION: ...
```

## 3.3. Não chamar C-level como cerimônia

Um C-level é ativado quando existe **decisão do domínio** correspondente.

Exemplos:

- bug local com contrato definido -> specialist + QA; nenhum CEO/CFO/CMO;
- mudança de arquitetura multi-repo -> CTO + architect;
- mudança de escopo/feature -> CPO + PM;
- dado médico -> CISO/CLO quando decisão de segurança/legal existe;
- release comercial -> COO/CMO/CFO/CRO conforme aplicável.

## 3.4. Engenharia

`/bigtech` não deve fazer engenharia duas vezes.

```text
/bigtech
  -> decide contexto/risco/capabilities
  -> quando execução técnica for necessária
       -> /proj_software
```

Caetano/CTO entra quando há decisão técnica macro, não como proxy obrigatório para toda edição de código.

### DoD Phase 3

- [ ] bug local não dispara C-suite;
- [ ] arquitetura multi-repo dispara cadeia correta;
- [ ] perfis não recalculam sem motivo;
- [ ] chamadas de agents registram por que cada agent foi necessário.

---

# PHASE 4 — Hooks: de reforço constante para contexto mínimo e eventos

**Implementação:** **[sonnet][mais recente]**.  
**Revisão:** **[opus][mais recente]**.

## 4.1. `SessionStart`

Injetar somente:

```text
[bigtech] profile=<...> capacity=<...> state=<path> docs=<path>
Use /bigtech:bigtech quando o pedido exigir coordenação cross-domain.
```

Não despejar mapa gerencial completo.

## 4.2. `UserPromptSubmit`

Com estado existente:

- classificar intenção por regex/heurística determinística barata;
- se pedido local de engenharia, não injetar C-suite;
- se pedido cross-domain/estratégico, injetar ponteiro para `/bigtech:bigtech`;
- se existe gate pendente no state, lembrar somente esse gate.

## 4.3. Novo `SubagentStart`

Criar hook `bigtech_subagent_context.py`.

Entrada:

- `agent_type`;
- `cwd`;
- plugin root.

Se `agent_type` pertence ao registry bigtech:

- injeta path absoluto de `docs/`;
- injeta profile/capacity atuais;
- injeta regra de autoridade mínima;
- injeta caminho do state;
- não carrega manuais inteiros.

O agent lê somente os docs relevantes.

**Resultado:** retirar de dezenas de prompts a obrigação repetida de localizar manual e repassar path manualmente.

## 4.4. Hook duplication gate

Criar script que detecta se nomes/paths de hooks core estão registrados simultaneamente em:

- settings user;
- settings project;
- plugin ativo.

Se duplicado, warning forte; nunca deletar sozinho.

## 4.5. Memória, estado e compactação

Claude Code já oferece `memory` para subagents e carrega a hierarquia de `CLAUDE.md`/memória aplicável no contexto de subagents. **Não habilitar `memory:` indiscriminadamente nos 51 agents nesta campanha.** Isso criaria um segundo mecanismo de aprendizado persistente antes de definir a relação dele com o vault existente.

Política inicial:

- conhecimento estático/reutilizável do plugin -> `docs/`/skills versionados;
- preferência pessoal/cross-project -> overlay do vault;
- estado operacional da orquestração -> arquivo pequeno do projeto;
- memória persistente nativa de agent -> experimento separado, só depois de provar ausência de dual authority.

### Estado operacional

Criar, se necessário, `.bigtech/state.json` ou equivalente gitignored para runtime, distinto de `.bigtech.json` versionável de classificação. Campos mínimos:

```json
{
  "schema": 1,
  "profile_sha": "...",
  "active_capabilities": [],
  "current_checkpoint": "...",
  "last_green_sha": "...",
  "open_handoffs": [],
  "updated_at": "..."
}
```

Regras:

- escrita atômica `temp -> fsync quando aplicável -> rename`;
- schema versionado;
- JSON inválido/corrompido nunca é aceito silenciosamente como estado válido;
- recuperação deve poder reconstruir o estado a partir de `.bigtech.json`, git e TODO/artefatos canônicos;
- runtime state nunca vira fonte de verdade de decisão estratégica.

### Compactação/handoff

Usar `PreCompact`/`PostCompact` somente para preservar **estado operacional mínimo**, não transcript inteiro como nova memória canônica. Antes de compactar uma campanha longa:

1. persistir checkpoint atual;
2. itens/IDs ativos;
3. SHA do último estado verde;
4. decisões pendentes do usuário;
5. agentes em andamento/handoffs;
6. próximo passo reproduzível.

Após compactação, validar que o checkpoint ainda referencia arquivos/SHAs existentes antes de continuar.

### Subagent handoff

Todo subagent recebe explicitamente:

- objetivo da fatia;
- profile/risk_axes relevantes;
- docs/skills necessários;
- arquivos permitidos;
- estado inicial/last-green quando necessário;
- Definition of Done.

O resultado devolve evidência e não depende de "lembrar" conversa anterior.

### DoD Phase 4

- [ ] hook per-turn não injeta C-suite em tarefa trivial;
- [ ] SubagentStart prova que agent recebe docs path sem prompt manual;
- [ ] cada hook tem teste unitário;
- [ ] zero execução duplicada no canário;
- [ ] nenhum segundo sistema de memória persistente introduzido sem ADR;
- [ ] estado runtime tem schema, escrita atômica e recovery testado;
- [ ] compactação preserva checkpoint mínimo e retoma de forma reproduzível.

---

# PHASE 5 — Governança dos 51 agents

## 5.1. Criar registry canônico

Adicionar `config/agent-registry.json` ou YAML com:

```text
name
family
role
capabilities
routes
model_tier
effort
max_turns
write_mode
requires_bash
requires_web
can_be_main_agent
docs_required
high_value_decisions
```

O registry não gera decisões; ele elimina duplicação estrutural de metadados.

## 5.2. Criar `scripts/audit_agents.py`

Gates:

1. nomes únicos;
2. todos os agents do registry existem;
3. nenhum agent extra sem registro;
4. refs de agents em skills/docs resolvem;
5. model/effort/maxTurns batem com policy;
6. tools batem com classe;
7. nenhum tool depreciado;
8. nenhum `Agent` em subagent que não é suportado como main-agent intencional;
9. tamanho de prompt acima de limiar gera warning;
10. agent sem rota explícita gera warning/fail conforme categoria;
11. agent route aponta para capability existente;
12. C-level e operational não têm responsabilidades impossíveis/duplicadas.

## 5.3. Reduzir boilerplate

Cada agent deve conter principalmente:

```text
IDENTIDADE
MANDATO
NÃO-MANDATO
INPUTS
DECISÕES QUE PODE TOMAR
DECISÕES QUE SOBEM AO USUÁRIO
TOOLS/CAPABILITIES
HANDOFF
DEFINITION OF DONE
ANTI-PATTERNS ESPECÍFICOS
```

Mover regras globais para:

- hook SubagentStart;
- docs canônicos;
- registry/validator.

## 5.4. Least privilege

Categorias sugeridas:

### Read/advisory

C-levels de negócio e papéis que não implementam código:

- Read/Grep/Glob/Web quando necessário;
- Write/Edit somente para artefatos que realmente produzem;
- Bash removido se não houver caso operacional concreto.

### Implementation

- Read/Edit/Write/Grep/Glob/Bash;
- Web apenas quando necessário;
- Task tracking conforme workflow.

### Audit

- leitura ampla;
- Bash para ferramentas de inspeção;
- Write apenas para dossiê/relatório;
- nenhuma alteração de produção durante auditoria sem mandato explícito.

## 5.5. Reachability

Todo agent deve ser:

- roteado explicitamente por `/bigtech`, `/proj_software` ou skill dedicada; **ou**
- marcado `auto-discovery-only` com description suficientemente precisa.

Agent sem rota e sem auto-discovery justificado = órfão.

## 5.6. Matriz de ownership e sobreposição

Criar `config/routing-matrix.json` derivado do registry. Cada classe de decisão tem **um owner primário** e zero ou mais consultados/verificadores.

Exemplo mínimo:

| Decisão/tarefa | Owner primário | Consultados/verificador | Não-owner |
|---|---|---|---|
| profile/capacity | Cósimo | CEO, especialistas de risco quando necessário | EM/Scrum |
| visão/go-no-go | CEO | CPO/CTO/CFO conforme caso | engineer operacional |
| escopo/roadmap | CPO | PM, CTO | CEO não micromaneja backlog |
| arquitetura cross-system | CTO → software-architect | CISO/tech-lead | PM/EM |
| design local de módulo | tech-lead | software-architect se one-way door | CTO não reimplementa |
| implementação | engineer especializado | tech-lead/QA | C-level |
| estratégia de testes | QA | tech-lead/security conforme risco | auditor não substitui QA |
| auditoria | internal-auditor | especialistas por capítulo | implementer do mesmo slice não atesta sozinho |
| fluxo/cadência | scrum-master/flow owner quando realmente necessário | COO/EM | não ativa por default em capacity=solo |
| capacidade humana/people management | EM somente quando existir problema humano real | COO | não usar para simular empresa num mantenedor solo |

O arquivo deve permitir exceções explícitas por `risk_axes`, mas nunca dois owners primários silenciosos.

### Taxonomia determinística de routing

Toda solicitação é classificada em uma ou mais capabilities, por exemplo:

```text
strategy
product
architecture
implementation.backend
implementation.frontend
quality
security
legal-compliance
data
ai
release
operations
audit
design
flow
```

Cósimo seleciona pelo registry, não por uma lista hardcoded duplicada no prompt.

### Escalation chain

Se o owner primário não consegue fechar a tarefa:

1. retorna `BLOCKED` com evidência e a capability faltante;
2. main resolve a capability pelo registry;
3. ativa especialista consultado;
4. decisões one-way-door/alto valor sobem ao usuário;
5. ausência de rota é erro de configuração, não motivo para inventar outro papel.

### Gate de órfãos e sobreposição

`audit_agents.py` deve emitir:

- `UNREACHABLE_AGENT`;
- `MISSING_ROUTE_TARGET`;
- `MULTIPLE_PRIMARY_OWNERS`;
- `ROLE_OVERLAP_WARNING`;
- `UNUSED_CAPABILITY`;
- `ROUTE_CYCLE`.

Falham CI: órfão core, target inexistente, owner primário duplicado e ciclo. Sobreposição intencional pode ser warning com justificativa versionada.

### DoD Phase 5

- [ ] registry completo;
- [ ] audit_agents PASS;
- [ ] zero nomes duplicados dentro do plugin;
- [ ] zero refs quebradas;
- [ ] distribuição de tools justificada;
- [ ] prompt-size report versionado como artefato de CI.

---

# PHASE 6 — Política de modelos e effort

## 6.1. Main/orquestrador

**[opus][mais recente]**.

Responsabilidades:

- ler contexto global;
- chamar Cósimo quando necessário;
- manter ordem de dependências;
- decidir paralelismo;
- validar outputs;
- rerodar gates;
- fazer commits/push/PR/release.

## 6.2. Estratégia/arquitetura/auditoria complexa

Default **[opus][mais recente]** para:

- Cósimo;
- CEO quando realmente ativado;
- CTO/CPO/CISO/CLO em decisões estratégicas;
- software-architect;
- internal-auditor;
- revisões cross-project de alto impacto.

Não significa que todo C-level roda em toda tarefa.

## 6.3. Execução

Default **[sonnet][mais recente]** para:

- backend/frontend/mobile;
- QA;
- DevOps/SRE operacional;
- data/ML implementation;
- technical writer;
- PM operacional;
- scrum/flow;
- EM operacional;
- implementação de design;
- refactors mecânicos.

Escalar uma fatia específica para **[opus][mais recente]** quando:

- falhou duas vezes com evidência;
- há concorrência/algoritmo particularmente difícil;
- contrato cross-project não está claro;
- bug exige raciocínio arquitetural.

## 6.4. Gates FABLE

Usar **[fable][mais recente]** apenas em:

- `FABLE-ORG-ARCH` — fonte de verdade + overlays;
- `FABLE-AGENT-GOVERNANCE` — revisão do registry e sobreposição de papéis;
- `FABLE-CLASSIFICATION` — revisão do novo modelo de profile;
- `FABLE-CUTOVER` — antes de remover cópias ativas do vault;
- `FABLE-FINAL-AUDIT` — antes da release que declara a campanha concluída.

Não usar como default de implementação.

## 6.5. Corrigir `/modelos_sessao`

O vault deve ser ajustado em campanha coordenada:

- atualizar labels;
- validar aliases aceitos pelo Agent tool;
- **não** instruir `model=fable` por invocação;
- para **[fable][mais recente]**, usar caminho suportado: main session apropriada ou agent dedicado cujo frontmatter use full model ID;
- adicionar contract test que compara os valores aceitos com a versão do Claude Code disponível.

## 6.6. Precedência e modelo efetivo

Claude Code resolve o modelo do subagent nesta ordem:

```text
CLAUDE_CODE_SUBAGENT_MODEL
    > override por invocação
    > frontmatter do agent
    > modelo da conversa principal
```

Logo, o sistema não pode declarar sucesso só porque o registry ou frontmatter foi alterado. Antes de cada eval de modelo:

1. registrar se `CLAUDE_CODE_SUBAGENT_MODEL` está definido;
2. registrar o `model` solicitado pelo router;
3. registrar a definição do agent;
4. observar, por mecanismo suportado pela CLI/logs/hooks, o modelo efetivamente utilizado;
5. comparar `requested_model` × `effective_model`;
6. falhar o eval quando divergir sem override intencional documentado.

Formato de evidência:

```json
{
  "agent": "backend-engineer",
  "requested_tier": "execution",
  "requested_model": "sonnet",
  "frontmatter_model": "sonnet",
  "env_override": null,
  "effective_model": "<observado>",
  "result": "PASS"
}
```

### Contract test de `/modelos_sessao`

O teste deve consultar a versão instalada do Claude Code e verificar:

- aliases válidos para override por Agent tool;
- suporte a full model ID no frontmatter/`--model`;
- precedência de `CLAUDE_CODE_SUBAGENT_MODEL`;
- opções de `effort` aceitas pelo modelo efetivo;
- comportamento quando um modelo pedido não existe.

Nunca hardcodar uma lista eterna sem conferir a CLI/documentação compatível com a versão instalada.

### Caminho para **[fable][mais recente]**

Enquanto o override por invocação não aceitar um alias específico, não fabricar `model=fable`. Use um caminho realmente suportado e testado:

- agent dedicado com full model ID válido no frontmatter; ou
- sessão/main iniciada com o modelo apropriado; ou
- outro mecanismo oficialmente suportado pela versão instalada.

O runbook registra **capability requerida**, não assume que um alias futuro exista.

## 6.7. `effort`

Não herdar `xhigh` indiscriminadamente.

Sugestão inicial a validar por eval:

- orchestration/architecture: `high` ou `xhigh`;
- routine implementation: `medium`/`high`;
- QA mecânico/documentação: `medium`;
- auditoria final: `xhigh`/`max` quando suportado.

Nunca inventar budget fixo sem medir qualidade/custo.

### DoD Phase 6

- [ ] model distribution medida e aprovada;
- [ ] nenhum caminho inválido para **[fable][mais recente]**;
- [ ] agents de rotina não usam tier estratégico sem justificativa;
- [ ] eval custo/qualidade registrado;
- [ ] eval registra requested_model × effective_model;
- [ ] ambiente não contém override global não contabilizado.

---

# PHASE 7 — Cósimo e C-levels: contratos de delegação claros

**Revisão arquitetural:** **[opus][mais recente]**.  
**FABLE-AGENT-GOVERNANCE:** **[fable][mais recente]** após primeira revisão.

## 7.1. Cósimo

É router, não implementer.

Deve:

- classificar profile;
- escolher capabilities;
- emitir dependency graph;
- dizer o que **não** ativar;
- apontar decisões do usuário;
- registrar recheck triggers.

Não deve:

- duplicar o trabalho do PM/CTO;
- produzir solução técnica detalhada;
- invocar uma “empresa inteira” por default.

## 7.2. C-levels

Cada C-level deve produzir:

```text
DECISION/RECOMMENDATION
EVIDENCE
TRADE-OFFS
HANDOFFS
BLOCKERS
USER_DECISION (se houver)
```

Sem textos longos de identidade corporativa quando não agregam.

## 7.3. Operational agents

Cada operacional recebe um task contract fechado:

```text
GOAL
FILES/SCOPE
READ-ONLY OR WRITE
INPUT CONTRACTS
OUTPUT CONTRACTS
TESTS
DO NOT TOUCH
DONE WHEN
```

## 7.4. Writer-verifier

Para trabalho importante:

- writer em **[sonnet][mais recente]**;
- verifier independente em **[opus][mais recente]** quando risco alto;
- main aceita/rejeita após evidência.

### DoD Phase 7

- [ ] nenhum agent devolve apenas “plano genérico” quando deveria implementar;
- [ ] nenhum agent implementa quando mandato é auditoria;
- [ ] handoff possui arquivos/contratos/testes mensuráveis.

---

# PHASE 8 — Integrar `/tab_pendencias` sem criar terceira fonte de verdade

A campanha própria de `tab_pendencias` deve ser respeitada.

## 8.1. Situação-alvo

`tab_pendencias` tem um único repo owner.

Preferência arquitetural quando o standalone estiver pronto como plugin:

```text
bigtech plugin
   dependencies:
      tab-pendencias >= versão testada
```

Claude Code atual suporta plugin dependencies versionadas. Isto é preferível a copiar o mesmo SKILL.md em três lugares.

## 8.2. Transição

Enquanto o standalone não estiver empacotado/validado:

- marcar a cópia vendorizada no bigtech como transitória;
- registrar upstream version/SHA;
- criar gate de drift;
- não editar a cópia em paralelo sem portar upstream.

## 8.3. Integração semântica

`/bigtech` não transforma toda descoberta em TODO manual.

Fluxo:

```text
agent descobre trabalho
  -> main entrega à tab_pendencias
  -> tab classifica local/scoped/full/inbox residual
  -> TODO recebe posição
```

Individual agents não precisam repetir o pre-flight TODO completo em seus prompts.

### DoD Phase 8

- [ ] um owner de tab_pendencias;
- [ ] versão/dependency explícita;
- [ ] nenhum copy-paste silencioso;
- [ ] agents não gerenciam backlog por conta própria.

---

# PHASE 9 — GitHub como distribuição real

**Implementação mecânica:** **[sonnet][mais recente]**.  
**Revisão:** **[opus][mais recente]**.

## 9.1. Atualizar metadados

Trocar links operacionais para GitHub em:

- `.claude-plugin/plugin.json`;
- `.claude-plugin/marketplace.json`;
- README;
- AGENTS;
- SECURITY/PRIVACY/docs onde aplicável.

Referências históricas em CHANGELOG podem permanecer se claramente históricas.

## 9.2. GitHub Actions

Criar `.github/workflows/ci.yml` executando pelo menos:

1. `validate_plugin.py`;
2. `audit_agents.py`;
3. pytest hooks;
4. JSON/YAML parse;
5. version parity;
6. ruff/lint;
7. gitleaks;
8. smoke offline;
9. `claude plugin validate --strict` quando disponível;
10. evals determinísticos/fixtures que não exigem modelo.

### Matrix multi-OS (obrigatória — ordem do líder 2026-08-16)

**Mesma cobertura de SO que o `tab_pendencias`**, mesmo que este plano tivesse previsto só “um workflow”. Implementar e manter:

| Job | Runner / ambiente |
|---|---|
| pytest/checks nativos | `ubuntu-latest` **e** `windows-latest` |
| pytest/checks em container | **Debian**, **Fedora**, **Arch** (via container no runner Ubuntu; imagens pinadas por digest quando aplicável) |

Referência de desenho: `tab_pendencias/.github/workflows/ci.yml` (matrix nativa + job container com `matrix.distro`). Não aceitar release com “só Ubuntu verde”. Hard gates da lista acima rodam **em cada célula da matrix** quando forem portáveis; o que for Linux-only (ex. shellcheck) documenta exceção por job, não omite a matrix.

Ferramenta ausente em gate essencial **não pode virar PASS falso**. Definir claramente quais gates são hard e quais são advisory.

### Classificação obrigatória dos gates

Definir no workflow e no runbook:

**Hard gates — falham fechado:**

- parse/schema de manifestos;
- `validate_plugin.py`;
- `audit_agents.py`;
- testes dos hooks;
- version parity;
- gitleaks/secret scan;
- smoke offline básico;
- evals determinísticos de classificação/routing;
- validação do plugin quando a CLI suportada é pré-requisito da release.

**Advisory — podem warning apenas com justificativa:**

- métricas de tamanho de prompt;
- ferramentas opcionais que não definem corretude;
- checks exploratórios de custo/performance sem budget aprovado.

Não usar `|| true`, “tool missing -> PASS” ou skip silencioso em hard gate. Se uma ferramenta é indispensável ao gate, instale/pine no CI ou faça o gate por implementação stdlib equivalente.

### Reprodutibilidade do CI

- pinar versão de Python suportada;
- pinar ações por major/commit conforme política;
- registrar versões de ferramentas relevantes;
- manter `scripts/preci.sh` e GitHub Actions chamando os mesmos scripts-base para evitar duas implementações do gate;
- rodar pelo menos uma prova em ambiente limpo, sem cache local do mantenedor.

## 9.3. Remover CI legado só depois do GitHub CI verde

Sequência (BT-3/BT-4; host canônico = GitHub):

```text
add GitHub Actions (.github/workflows/)
-> run green
-> compare coverage with previous-host CI (if still present)
-> only then delete legacy CI dirs/workflows
```

## 9.4. Canary de instalação/upgrade no Claude Code

Antes de remover a distribuição operacional antiga ou promover release:

1. instalar o plugin a partir do branch/tag candidato em `CLAUDE_CONFIG_DIR` limpo;
2. abrir nova sessão;
3. confirmar descoberta de skills/agents;
4. confirmar hooks exatamente uma vez;
5. executar `/bigtech` nos evals E1-E9;
6. testar upgrade de `0.2.0`/última versão suportada para a candidata;
7. testar uninstall/reinstall;
8. testar ausência de globals homônimos no perfil limpo;
9. só então fazer cutover do perfil pessoal.

A prova deve registrar versão da CLI, SHA/tag do plugin e resultado dos sinais.

## 9.5. Proteção de branch

Após workflow estável:

- proteger `main`;
- exigir CI;
- bloquear force-push;
- preferir PR para mudança substancial.

## 9.6. Release/proveniência

- tag imutável após todos os hard gates;
- release notes ligadas ao SHA auditado;
- manifest/marketplace/changelog em paridade;
- não reutilizar tag;
- registrar checks executados e limitações conhecidas;
- não declarar “GitHub migrado” enquanto instalação/documentação ainda apontar operacionalmente para o host legado.

### DoD Phase 9

- [ ] zero refs a host legado / só GitHub;
- [ ] GitHub Actions verde;
- [ ] main protegida;
- [ ] release process usa GitHub;
- [ ] hard gates não degradam para PASS por ferramenta ausente;
- [ ] canário de install/upgrade/uninstall em perfil limpo passa;
- [ ] tag/release apontam para SHA efetivamente auditado.

---

# PHASE 10 — Evals de comportamento real

**Desenho:** **[opus][mais recente]**.  
**Execução ampla:** **[sonnet][mais recente]**.  
**Auditoria de rubrica:** **[fable][mais recente]** apenas no gate.

Criar `evals/` com prompts reais e rubricas.

## E1 — solo trivial

Esperado: nenhum C-level desnecessário.

## E2 — solo multi-repo

Esperado: profile sobe por blast radius/ecossistema, apesar de capacity solo.

## E3 — solo saúde/PII

Esperado: security/legal capabilities ativadas proporcionalmente.

## E4 — bug local em projeto critical

Esperado: não reacordar C-suite inteira; specialist + verifier basta.

## E5 — mudança de contrato cross-project

Esperado: architecture/CTO + consumers impact + backlog update.

## E6 — feature de produto

Esperado: CPO/PM antes de execução quando escopo realmente precisa decisão.

## E7 — release

Esperado: gates e roles coerentes com profile.

## E8 — conflito de sources

Ambiente com agent homônimo user + plugin.

Esperado: auditor detecta que user scope ganha e bloqueia declaração falsa de “plugin ativo”.

## E9 — model routing

Esperado: tarefa mecânica vai para **[sonnet][mais recente]**; decisão arquitetural para **[opus][mais recente]**.

## E10 — final principal review

Rodar rubrica com **[fable][mais recente]** e comparar contra critérios fixos, não contra “parece bom”.

### Métricas

- route accuracy;
- agents invocados por tarefa;
- custo/tokens;
- turns;
- decisões desnecessárias solicitadas ao usuário;
- falhas de contrato;
- churn no TODO;
- tempo até evidência final.

### DoD Phase 10

- [ ] E1-E10 versionados com input e expected outcome;
- [ ] profile não deriva de headcount;
- [ ] routing accuracy medida;
- [ ] `requested_model` × `effective_model` registrado nos evals relevantes;
- [ ] nenhum eval é aprovado apenas por autoavaliação do mesmo agent que produziu a resposta;
- [ ] regressões ficam como fixtures permanentes.

---

# PHASE 11 — Cutover da instalação pessoal

**Planejamento/revisão:** **[opus][mais recente]**.  
**FABLE-CUTOVER:** **[fable][mais recente]** antes das remoções.

## 11.1. Publicar plugin canário

Não remover globais ainda.

Instalar/testar o plugin em perfil limpo ou `--plugin-dir`.

Provar:

- agents aparecem;
- skills namespaced aparecem;
- hooks executam uma vez;
- docs chegam aos subagents;
- evals de classificação passam.

## 11.2. Portar diferenças genéricas do vault

Para cada agent core divergente:

- diff;
- classificar;
- portar `CORE-GENERIC` para plugin;
- mover `PERSONAL-OVERLAY` para CLAUDE/memory/policy pessoal;
- não publicar PII, nomes privados, paths ou infraestrutura pessoal.

## 11.3. Remover sombreamento de agents

Só após canário verde:

- retirar da árvore **ativa** `~/.claude/agents/` os agents core homônimos;
- preservar backup em local não escaneado ou via git history;
- manter somente os agents pessoais/excluídos.

Prova:

- `/agents` deve indicar versão ativa do plugin para os core;
- agent testado deve refletir uma mudança exclusiva da nova release.

## 11.4. Skills pessoais

Preservar ergonomia sem duplicar lógica.

Exemplo:

```text
/bigtech (wrapper pessoal mínimo)
   -> encaminha para /bigtech:bigtech
```

Mesmo para `/proj_software` se desejado.

Para `tab_pendencias`, seguir owner definido na Phase 8.

## 11.5. Hooks globais

Remover da configuração global os registrations que agora pertencem ao plugin:

- bigtech route/reinforce;
- TDD core, se ownership for transferido;
- tab reminder conforme ownership final.

Manter globais pessoais que não pertencem ao plugin.

### DoD Phase 11

- [ ] plugin habilitado em user scope;
- [ ] 0 core agents user-scope sombreando plugin;
- [ ] 0 hooks core duplicados;
- [ ] wrappers pessoais sem lógica duplicada;
- [ ] rollback documentado.

---

# PHASE 12 — Release e propagação

## Versionamento

Mudanças alteram comportamento de classificação, roteamento e instalação. Em série `0.x`, tratar como release minor significativa; decidir número após medir compatibilidade.

## Release checklist

- [ ] source-of-truth audit green;
- [ ] agent audit green;
- [ ] hook tests green;
- [ ] evals green;
- [ ] GitHub Actions green;
- [ ] manifest/marketplace parity;
- [ ] `claude plugin validate --strict` green;
- [ ] clean install canary;
- [ ] upgrade from previous release canary;
- [ ] vault cutover canary;
- [ ] CHANGELOG com breaking/migration notes;
- [ ] tag/release somente pelo main após revisão.

### DoD Phase 12

- [ ] release candidata instalada e atualizada em perfil limpo;
- [ ] SHA/tag/version parity comprovada;
- [ ] migration notes incluem mudança `porte -> profile/capacity`;
- [ ] rollback para last-known-good executado em teste;
- [ ] `claude-memory` atualizado somente após o core publicado provar equivalência.

---

# PHASE 13 — FABLE-FINAL-AUDIT

**Modelo:** **[fable][mais recente]**.

Mandato adversarial:

> Tente provar que a campanha está sendo declarada concluída cedo demais.

Perguntas obrigatórias:

1. Existe qualquer agent core homônimo ainda ativo em user scope?
2. Atualizar um agent no plugin muda o agent realmente usado no vault?
3. Existe qualquer hook executando duas vezes?
4. `solo` ainda influencia profile em algum código/doc/hook?
5. Um projeto solo multi-repo é classificado corretamente?
6. Um pedido trivial num projeto critical evita C-suite desnecessária?
7. Todos os agents têm route ou justificativa auto-discovery?
8. Modelo de execução está separado de modelo estratégico?
9. O tier **[fable][mais recente]** é chamado por caminho tecnicamente válido?
10. Há qualquer host legado (não-GitHub) operacional ainda ativo?
11. GitHub CI e branch protection estão efetivamente ativos?
12. `tab_pendencias` possui um owner único?
13. As diferenças pessoais foram preservadas sem vazar para repo público?
14. O repo pode ser instalado em perfil limpo e reproduzir a constelação?
15. O rollback foi testado?

Nenhum item é PASS por narrativa. Cada PASS exige comando, output, arquivo ou comportamento observável.

### DoD Phase 13

- [ ] 15 perguntas respondidas com evidência;
- [ ] zero claim crítico marcado apenas como "parece"/"provavelmente";
- [ ] métricas primárias do topo do runbook atingiram alvo ou exceção foi explicitamente recusada como conclusão;
- [ ] BIGTECH-REFRESH-COMPLETE só pode ser declarado após este gate.

---

# Política detalhada de agents por modelo

## Grupo A — Estratégia/orquestração

Default: **[opus][mais recente]**.

Inclui inicialmente:

- Cósimo;
- Celso;
- Caetano quando decisão macro;
- Capitolino quando decisão de produto;
- Narciso/Cláudio em risco alto;
- software-architect;
- internal-auditor.

A lista final deve ser medida contra uso real; não transformar este grupo em desculpa para pôr todos os 51 no mesmo tier.

## Grupo B — Execução especializada

Default: **[sonnet][mais recente]**.

Inclui a maioria dos implementers, QA, docs, operações, produto operacional e flow management.

## Grupo C — Principal review

Default: nenhum agent permanente até existir necessidade.

Uso sob gate: **[fable][mais recente]**.

Se for necessário automatizar como subagent, criar definição dedicada com full model ID suportado pela versão atual do Claude Code; não inventar alias de Agent tool.

---

# Política de paralelismo

## Subagents

Use para tarefas independentes que retornam resumo/diff.

## Worktrees

Use quando dois writers podem tocar arquivos simultaneamente.

Não aplicar `isolation: worktree` permanentemente a todo agent: alguns precisam enxergar alterações não commitadas do main. O orquestrador escolhe isolamento por fatia.

## Agent Teams

Como é experimental e os teammates precisam coordenação explícita, usar somente quando:

- tarefas precisam trocar mensagens;
- partição de arquivos é clara;
- o ganho supera custo/token;
- não há escrita concorrente no mesmo arquivo.

Não transformar “Agent Teams habilitado” em “sempre usar team”.

---

# Contrato de briefing de subagent

Toda task de implementação deve incluir:

```text
ROLE: <agent>
MODEL-TIER: <policy>
GOAL: <um resultado>
WHY NOW: <dependência>
READ: <arquivos/contratos>
SCOPE: <arquivos permitidos>
DO NOT TOUCH: <escopo proibido>
BASELINE: <métrica antes>
IMPLEMENT: <mudança>
VERIFY: <comandos/testes>
OUTPUT: <diff + métricas + riscos>
DONE WHEN: <critério binário>
NO PUSH / NO TAG / NO RELEASE
```

Auditor recebe briefing separado com `READ-ONLY` explícito.

---

# Contrato de resultado de subagent

```text
STATUS: DONE-CANDIDATE | BLOCKED | FAILED | NO-CHANGE
FILES_READ:
FILES_CHANGED:
BASELINE:
AFTER:
TESTS:
DIFF_SUMMARY:
RISKS:
UNVERIFIED_CLAIMS:
NEXT_DEPENDENCY:
```

Main não aceita `DONE-CANDIDATE` como “pronto”. Reroda a evidência.

---

# Prevenção de drift futuro

## 1. Um único core

Nunca editar primeiro a cópia ativa pessoal de um agent core. Editar o repo canônico, testar via `--plugin-dir`, publicar e atualizar plugin.

## 2. Overlay pessoal declarado

Personalização que não pode ser pública mora em arquivos explicitamente pessoais e não usa o mesmo nome de agent core.

## 3. Drift check semanal/CI

Script pode comparar:

- versão instalada;
- versão disponível;
- shared names em user scope;
- hooks duplicados;
- wrappers esperados.

Warning-only local; CI do produto não lê dados pessoais.

## 4. Sem release sem semantic gate

`validate_plugin.py` + `audit_agents.py` + hook tests + eval suite.

## 5. Docs e código mudam juntos

Mudança de taxonomy (`profile`, capability, agent name) deve falhar CI se referências antigas continuarem fora de changelog/migration docs.

## 6. Métrica de progresso

Todo relato desta campanha inclui:

```text
core duplicate agents: X -> Y
hook duplicates: X -> Y
headcount-dependent classifications: X -> Y
semantic gate failures: X -> Y
legacy-host live refs: X -> Y
GitHub required gates: X -> Y
```

Sem delta, não chamar atividade de progresso.

---

# Anti-padrões proibidos

1. Não sincronizar plugin e vault bidirecionalmente para sempre.
2. Não copiar 51 agents para `~/.claude/agents` após cada release.
3. Não classificar projeto pelo número de humanos.
4. Não invocar todos os C-levels “porque o perfil é critical”.
5. Não repetir docs-bootstrap completo em 51 prompts.
6. Não pôr `model: opus` em todo agent por conveniência.
7. Não usar **[fable][mais recente]** como default diário.
8. Não passar alias não suportado à Agent tool.
9. Não declarar plugin atualizado sem provar qual agent venceu a precedência.
10. Não manter CI legado como único gate de um repo hospedado no GitHub.
11. Não remover globais antes do canário.
12. Não publicar overlay pessoal no repo público.
13. Não deixar `tab_pendencias` virar terceira implementação divergente.
14. Não transformar todo prompt em reunião de diretoria.
15. Não deixar hooks de lembrete controlarem semântica que deveria estar em state/skill.

---

# Definition of Done global — BIGTECH-REFRESH-COMPLETE

A campanha só termina quando todos forem verdadeiros:

## Source of truth

- [ ] `bigtech_plugin` é o único core distribuível ativo.
- [ ] 0 agents core homônimos ativos em `~/.claude/agents`.
- [ ] wrappers pessoais são finos e não reimplementam workflow.
- [ ] `tab_pendencias` possui owner único.

## Classificação

- [ ] `solo` não existe como profile arquitetural.
- [ ] `capacity=solo` é suportado e esperado.
- [ ] profile usa risco/complexidade/ecossistema.
- [ ] eval solo multi-repo passa.
- [ ] eval solo health/PII passa.

## Agents

- [ ] registry completo.
- [ ] todos os agents alcançáveis ou explicitamente auto-discovery.
- [ ] tools least-privilege revisados.
- [ ] model/effort/maxTurns definidos por policy.
- [ ] boilerplate cross-cutting removido dos prompts.

## Model policy

- [ ] main/orchestration em **[opus][mais recente]**.
- [ ] execução default em **[sonnet][mais recente]**.
- [ ] gates principais podem usar **[fable][mais recente]** por caminho suportado.
- [ ] nenhum override inválido.

## Hooks

- [ ] SessionStart compacto.
- [ ] UserPromptSubmit intent-aware.
- [ ] SubagentStart injeta context path/state.
- [ ] zero hook core duplicado.

## Repo

- [ ] GitHub URLs atuais.
- [ ] GitHub Actions green.
- [ ] CI/host legado operacional removido após paridade com GitHub Actions.
- [ ] `main` protegida.
- [ ] manifest/marketplace/version parity.

## Runtime

- [ ] clean install green.
- [ ] upgrade green.
- [ ] plugin ativo no vault.
- [ ] uma mudança exclusiva de agent do plugin é observável no agent realmente invocado.
- [ ] rollback testado.

---

# Sequência obrigatória resumida

```text
S0  BASELINE
 -> S1  SOURCE-OF-TRUTH / FABLE-ORG-ARCH
 -> S2  PROFILE != HEADCOUNT
 -> S3  ORCHESTRATOR STATE MACHINE
 -> S4  HOOKS EVENT-AWARE
 -> S5  AGENT REGISTRY + AUDIT
 -> S6  MODEL/EFFORT POLICY
 -> S7  ROLE CONTRACTS
 -> S8  TAB_PENDENCIAS OWNERSHIP
 -> S9  GITHUB DISTRIBUTION + CI
 -> S10 EVALS
 -> S11 VAULT CUTOVER / FABLE-CUTOVER
 -> S12 RELEASE
 -> S13 FABLE-FINAL-AUDIT
 -> BIGTECH-REFRESH-COMPLETE
```

Não inverter S11 antes de S9/S10: retirar o core global antes do plugin estar provado cria downtime da própria orquestração.

---

# Comandos de auditoria que a implementação deve criar/usar

Exemplos de interface desejada; os scripts concretos podem variar:

```bash
python3 scripts/audit_agents.py --strict
python3 scripts/audit_routing.py --strict
python3 scripts/audit_hooks.py --strict
python3 scripts/validate_plugin.py --strict
python3 scripts/run_evals.py --deterministic
pytest -q
claude plugin validate --strict .
```

Para a instalação pessoal:

```bash
python3 scripts/audit_installation.py \
  --claude-config "$HOME/.claude" \
  --plugin bigtech
```

Saída esperada:

```text
ACTIVE_CORE_SOURCE=plugin
SHADOWED_CORE_AGENTS=0
DUPLICATE_CORE_HOOKS=0
PERSONAL_OVERLAY_AGENTS=<N>
PLUGIN_VERSION=<version>
PROFILE_SCHEMA=2
```

---

# Relatório obrigatório a cada checkpoint

```text
CHECKPOINT:
BASE_SHA:
HEAD_SHA:
METRICS BEFORE:
METRICS AFTER:
TESTS:
EVALS:
ACTIVE AGENT SOURCE PROOF:
RISKS:
UNVERIFIED:
NEXT:
```

---

# Registro dos 7 ticks revisionais

Cada tick aplicou a pergunta: **“devo acrescentar mais algum detalhe aqui?”**

1. **Tick 1 — fronteira público/privado e rollback.** Adicionada classificação `CORE-GENERIC` / `PERSONAL-OVERLAY` / `STALE` / `INTENTIONAL-EXCLUSION`, dois artefatos (privado completo + público sanitizado) e rollback antes de remover globals.
2. **Tick 2 — classificação reproduzível.** Adicionada rubrica `0..3`, regras de escalada, perfis dimensionais, histerese e definição explícita de que `capacity=solo` tem peso zero no profile.
3. **Tick 3 — governança dos agents.** Adicionada matriz de owner primário, taxonomia de capabilities, escalation chain e gates de órfão/sobreposição/ciclo.
4. **Tick 4 — contexto, memória e compactação.** Adicionada política para não criar segunda memória persistente, state runtime versionado/atômico, recovery e handoff reproduzível.
5. **Tick 5 — modelo efetivo.** Adicionada precedência de seleção, `requested_model` × `effective_model`, contract test da CLI e caminho tecnicamente suportado para **[fable][mais recente]**.
6. **Tick 6 — CI/release.** Hard vs advisory gates, proibição de soft-pass em gate essencial, prova clean-room, canário install/upgrade/uninstall e release ligada ao SHA auditado.
7. **Tick 7 — revisão adversarial final.** Verificada nomenclatura de modelos, uso de `solo`, correção da limitação de subagents, claims sobre os 51 agents, DoDs, referências de migração e integridade estrutural do Markdown.

## Checks estruturais executados no Tick 7

- fences Markdown balanceadas;
- nenhuma menção humana a versões dos três tiers fora da nomenclatura aprovada; literais como `model: opus`, `model: sonnet` e full IDs permanecem apenas como sintaxe/configuração;
- `solo` permanece apenas como evidência histórica, caso de teste ou `capacity=solo`, nunca como profile-alvo;
- a afirmação correta “subagents não podem spawnar outros subagents” permanece explícita;
- não há claim de que todos os 51 agents usam o mesmo modelo sem medição;
- Phase 0–13 possuem gate/DoD aplicável ou checklist de release explicitamente mensurável;
- atualização do GitHub, CI, branch protection e cutover da instalação viva estão no caminho crítico.

# Estado deste runbook

Este documento foi produzido a partir de inspeção do GitHub conectado, do `claude-memory` versionado e da documentação atual do Claude Code. Itens que dependem do filesystem vivo da máquina são deliberadamente marcados para **re-medição local antes de alteração**.

