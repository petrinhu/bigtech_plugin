# ADR-source-of-truth: Fonte de verdade do conjunto bigtech (vault × plugin)

**Status:** Aceito (decisão autônoma 2026-08-16; confirmar retroativamente)
**Data:** 2026-08-16
**Decisores:** líder (mantenedor) via FABLE-ORG-ARCH / `software-architect` (autor deste ADR)
**Item do TODO.md:** BT-1 (bloqueia BT-5 e BT-6; pré-req de AUD-BT-1)
**Fase do plano:** PHASE 1 de `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`
**Licença do artefato:** Apache-2.0. Sem segredos, sem credenciais, sem PII, sem paths de máquina.

Este ADR fixa **um owner por componente**, a **política de overlay**, a **política de rollback**
e a **proibição de sync bidirecional permanente**. Não executa cutover (PHASE 11) nem classifica
arquivo a arquivo (BT-6). Não redesenha porte/headcount (BT-5).

---

## Contexto

A publicação (`bigtech_plugin`) e a instalação viva do mantenedor (`claude-memory` como
espelho não-secreto do diretório de configuração Claude do usuário) tornaram-se duas linhas
evolutivas. A PHASE 0 mediu, no freeze `61c3ea4` do plugin (release 0.2.0):

| Superfície | Medição (antes) | Alvo da campanha |
|---|---|---|
| Fontes de verdade ativas do núcleo bigtech | ≥ 2 (plugin não habilitado + globais vivos) | 1 |
| Agents core na interseção plugin ∩ vault | 51 / 51, **0** idênticos byte a byte | 0 cópias ativas homônimas |
| Skills core amostradas (`bigtech`, `proj_software`) | divergentes | 1 owner |
| Hooks bigtech/TDD/tab no registro global | 6 entradas; plugin off | 0 duplicatas após cutover |
| Host git operacional | host legado no `origin` do freeze | só GitHub |

Inventário reproduzível (histórico, não instrução operacional):

- [`docs/campanha/2026-08-16-phase0-baseline.md`](../campanha/2026-08-16-phase0-baseline.md)
- [`docs/campanha/phase0-agents-inventory.csv`](../campanha/phase0-agents-inventory.csv)
- [`docs/campanha/phase0-metrics-before.json`](../campanha/phase0-metrics-before.json)

Mecanismo do erro: o produto distribuível **não** era a fonte canônica da instalação pessoal.
Melhorar um lado não atualiza o outro. Uma release nova do plugin pode estar correta e ainda
assim não alterar o comportamento da máquina do mantenedor. Instalar o plugin **com** os
globais homônimos ativos produz risco **ALTO** de execução dupla nos mesmos eventos
(`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`).

Forças em jogo agora (antes de mover arquivos):

1. O plugin é produto público Apache-2.0; o vault pessoal não é o pacote.
2. Personalização do mantenedor é legítima e **não** deve ser apagada para “ficar igual”.
3. `tab_pendencias` já é produto standalone com owner próprio; um fork divergente no plugin
   recria dual authority num terceiro eixo.
4. A campanha é dual-host (Claude Code e Grok Build). Slug de geração de modelo na prosa
   envelhece no dia seguinte e vira spec falsa.
5. Host git legado deixou de ser operacional (BT-3 local). Só GitHub é canônico.

Sem este ADR, BT-6 (classificar e planear cutover) e BT-5 (porte) não têm regra de
autoridade para decidir o que entra no plugin, o que fica no overlay e o que se apaga.

---

## Decisão

O conjunto **distribuível** (agents, skills, hooks e docs **core** medidos na PHASE 0) tem
**um único owner:** o repositório `bigtech_plugin`. A instalação pessoal **não** mantém cópia
ativa homônima de agent core. Personalização vive em overlay (CLAUDE.md, memória, hooks
pessoais, agents exclusivos, wrapper curto). `tab_pendencias` permanece produto à parte.
Não existe sync bidirecional permanente. Toda diferença vault × plugin é classificada antes
de qualquer port. Host git do produto: somente GitHub.

### D1. `bigtech_plugin` é a autoridade do conjunto distribuível

**Owner:** repositório público
[`https://github.com/<owner>/bigtech_plugin`](https://github.com/<owner>/bigtech_plugin)
(plugin `bigtech`, marketplace do owner no GitHub; ver `.claude-plugin/marketplace.json`).

**Escopo de autoridade** (núcleo medido na PHASE 0, baseline publicado 0.2.0):

| Superfície | Contagem PHASE 0 | Nota |
|---|---:|---|
| Agents core | 51 | 12 C-level + 39 operacionais (inclui `visual-design-director`) |
| Skills core do plugin | 4 | `bigtech`, `proj_software`, `visual-design-director`; `tab_pendencias` ver D5 |
| Hooks core | 6 scripts + `hooks.json` | `bigtech_session_init`, `bigtech_porte_reminder`, `bigtech_reinforce`, `tdd_guard`, `tdd_runner`, `tdd_common` + reminder tab **embutido só como shim** (D5) |
| Docs core do produto | README, AGENTS.md (install), SECURITY, NOTICE, `docs/principles/`, `docs/adr/`, specs do plugin | o que explica e governa o pacote |

**Exceção documentada (não é dual authority do produto):** os **manuais da casa** em
`docs/house/` são **cópia de distribuição** dos manuais do vault claudebrain. Se o usuário
tiver o vault, **o vault prevalece** em conflito material desses dez arquivos. Se não tiver,
usa a cópia versionada. Divergência material → classificar e elevar; não “resolver no
silêncio”. Esta exceção **não** autoriza o vault a ser owner de agent, skill, hook ou doc
**de produto**.

Melhoria reutilizável por qualquer instalador entra no plugin (`CORE-GENERIC`). Edição no
overlay pessoal **não** atualiza o produto.

### D2. `claude-memory` / configuração Claude do usuário não mantém cópia ativa homônima de agent core

O repositório `claude-memory` (espelho não-secreto do diretório de configuração Claude do
usuário) e o diretório vivo equivalente:

- **podem** guardar overlay pessoal (D3), agents exclusivos e histórico git;
- **não** mantêm, após o cutover da PHASE 11, arquivo ativo em `agents/` com o **mesmo
  `name:`** de um agent core do plugin.

Até o canário verde, as cópias globais homônimas **permanecem** (proibido cutover destrutivo
antes do canário). Este ADR define o estado-alvo, não executa a remoção.

O mesmo princípio aplica-se a skills e hooks **core** homônimos: um registro ativo por
papel. Dois `tdd_runner` no mesmo evento é defeito, não redundância.

**Grok (configuração global do host Grok e adaptadores):** não é terceira fonte de
verdade do produto. É overlay de host (symlink, adapter de hook, mapa de modelo,
clone de persona). O pacote distribuível continua a ser `bigtech_plugin`. Adaptador
que reimplementa workflow core é `STALE` ou violação desta decisão.

### D3. Personalização fica no overlay, não no produto

Personalização do mantenedor (e de qualquer instalador) vive **fora** do conjunto
distribuível:

| Superfície de overlay | O que pode viver lá |
|---|---|
| `CLAUDE.md` de projeto / preferências universais do host | regras da sessão, autoridade do líder, ponteiros de runbook |
| Memória tipada do host | feedback, referências, snapshots de projeto (sem virar spec do plugin) |
| Hooks pessoais | som de alerta, lixo→trash, anti-mdash, integrações da casa |
| Agents exclusivos | papéis que o produto deliberadamente não envia (ver D8 `INTENTIONAL-EXCLUSION` e `PERSONAL-OVERLAY`) |
| Settings do host | plugins habilitados, MCP, credenciais (**nunca** no repo do plugin) |

**Proibido** publicar no `bigtech_plugin`: paths locais, nomes internos de projetos
privados, conteúdo de bus/sessão, credenciais, PII, preferências pessoais ou detalhe de
vault que não seja necessário para explicar uma interface pública.

### D4. Skill pessoal curta pode ser compatibility wrapper de `/bigtech`

É lícito existir no overlay uma skill pessoal **curta** com o nome `/bigtech` (ou
equivalente de host) **somente** como **compatibility wrapper**:

- encaminha para a skill do plugin (`/bigtech:bigtech` ou o namespace vigente do host);
- não reimplementa classificação, mapa de ativação, workflow, rubrica de porte nem lista
  de agents;
- não carrega uma segunda cópia do `SKILL.md` do produto.

Qualquer wrapper que volte a conter o workflow é `STALE` e deve ser reduzido a encaminhar
ou removido. A ergonomia do comando curto **não** justifica dual authority.

### D5. `tab_pendencias` tem owner único: o produto standalone

**Owner:** repositório do produto `tab_pendencias`
([`https://github.com/<owner>/tab_pendencias`](https://github.com/<owner>/tab_pendencias)).

O plugin **depende** desse produto por **pin** (submódulo / versão taggeada no host Claude)
ou **symlink** (host Grok), **não** por fork divergente.

A PHASE 0 mediu um risco já materializado: o plugin **embute** uma cópia da skill, enquanto
a instalação viva aponta para o produto. Essa cópia embutida **não** é fonte de verdade.
Deriva nela é `STALE`. Evolução de parser, health, hooks de reminder e contrato da tabela
acontece no produto; o plugin só atualiza o pin/symlink.

Não reabrir o desenho do produto `tab_pendencias` neste ADR.

### D6. Política de overlay e de rollback

#### Overlay (estado-alvo)

1. Um owner por componente (D1, D5).
2. Overlay pessoal **não sombreia** nome de agent/skill/hook **core**.
3. Wrapper (D4) é o único homônimo de skill core permitido, e só se for encaminhamento.
4. Cutover (PHASE 11) é que materializa o estado-alvo. Antes do canário: não remover
   globais vivos.
5. Diferença ainda não classificada **não** se apaga e **não** se publica.

#### Rollback (antes de retirar qualquer global que sombreie o plugin)

Checklist obrigatório, executável, versionado no runbook privado da campanha (não neste
ADR público além da regra):

1. Registrar `LAST_KNOWN_GOOD_PLUGIN_SHA` (SHA do plugin canário verde).
2. Registrar SHA de `claude-memory` (e, se o host Grok tiver árvore versionada afetada, o
   SHA correspondente).
3. Exportar inventário de agents/skills/hooks que saem do escopo **ativo** (nome, path,
   sha256).
4. Preservar o conteúdo no **histórico git**; sem `rm` destrutivo fora de controle e sem
   apagar o único blob conhecido.
5. Provar restauração da configuração anterior num **perfil isolado**
   (`CLAUDE_CONFIG_DIR` ou equivalente), não na sessão viva do líder.
6. Se o canário falhar: reativar o overlay anterior e registrar **qual gate** falhou.
7. Nenhum core sai do vault ativo antes de existir equivalente **testado** no plugin.

DoD da fronteira: nenhuma diferença do vault é publicada sem classificação; o rollback para
o último estado verde é executável e documentado.

### D7. Proibido sync bidirecional permanente / daemon

**Proibido:**

- daemon, timer, hook ou rotina que copie alterações **nos dois sentidos**
  (vault ↔ plugin, ou Grok ↔ plugin) de forma permanente;
- “espelho contínuo” que trate as duas árvores como a mesma autoridade.

Isto apenas **automatizaria dual authority**. Sync pontual, **unidirecional**, com
classificação prévia (vault → plugin só para `CORE-GENERIC`; plugin → overlay nunca como
substituto de produto) é operação de campanha, não um serviço.

### D8. Classificação dual-authority (obrigatória antes de portar)

Toda diferença entre vault/overlay e plugin recebe **uma** classe antes de qualquer
cópia, exclusão ou publicação. Referência de inventário: PHASE 0 (arquivos acima). A
aplicação arquivo a arquivo é BT-6; a taxonomia é deste ADR.

| Classe | Destino | Regra |
|---|---|---|
| `CORE-GENERIC` | `bigtech_plugin` | comportamento reutilizável por qualquer usuário do plugin |
| `PERSONAL-OVERLAY` | overlay (`claude-memory` / config do host) | preferência, vocabulário, projeto, agente ou integração do mantenedor |
| `STALE` | remover do lado defasado | regra superseded, API antiga, ou duplicação sem autoridade |
| `INTENTIONAL-EXCLUSION` | somente overlay/vault | capability deliberadamente fora do produto público |

Heurística PHASE 0 (não é cutover; BT-6 revalida):

- Interseção 51: sugerida `CORE-GENERIC`, **nenhuma** idêntica; **não** auto-`STALE`
  sem diff semântico.
- Só-vault (20), amostras já públicas no spec 2026-06-13: stack de jogo e afins →
  `INTENTIONAL-EXCLUSION`; papéis médicos/jurídicos da casa, utilitário de host,
  coach e PMM fora do core 0.2.0 → `PERSONAL-OVERLAY`.

**Proibido** apagar diferença só para os dois lados parecerem iguais.

### D9. Dual-host Claude / Grok: papéis, sem hardcode de versão de modelo

Prosa operacional, ADRs, briefs e o plano da campanha usam **papel relativo** ao catálogo
**atual** do host. É **proibido** gravar slug de geração (“4.5”, “4.6”, “Sonnet 4”,
“Opus 5”) em prosa.

| Papel | Claude Code | Grok Build | Uso |
|---|---|---|---|
| Implementação / fatia | **[sonnet][mais recente]** | **[grok][modelo anterior ao mais recente]** | código, testes, docs mecânicas |
| Orquestração / auditoria cotidiana | **[opus][mais recente]** | **[grok][modelo anterior ao mais recente]** | main, C-level planejando, review de rotina |
| Teto (`FABLE-*`, redesign global) | **[fable][mais recente]** | **[grok][mais recente]** | só gates `FABLE-*` ou ordem do líder |

Frontmatter YAML do Claude (`model: opus` / `model: sonnet`) é literal de **plataforma**.
Não autoriza pin de geração na prosa nem nos briefs dual-host. O ID concreto resolve-se
**só na hora do spawn**, consultando o catálogo vivo do host.

### D10. Host git: somente GitHub

Host oficial e único do produto:

`https://github.com/<owner>/bigtech_plugin`
(owner = mantenedor do marketplace no GitHub; identidade literal em `.claude-plugin/plugin.json`)

Sem remoto operacional para Forgejo/Codeberg ou outro host. Histórico git **não** se apaga
(BT-3). Snapshots PHASE 0 que citam o host legado são prova histórica, não instrução.
Push, merge em `main`, tag e release **continuam** a exigir autorização do líder no
contexto (este ADR não publica).

---

## Opções consideradas

1. **Vault / `claude-memory` como SoT; plugin é export periódico**
   - Prós: casa evolui rápido; zero fricção para o mantenedor.
   - Contras: o produto público fica para trás por construção; instalador terceiro nunca
     vê a linha viva; dual authority permanente.
   - **Rejeitada.**

2. **Dual-write (editar os dois lados em cada mudança) sem owner**
   - Prós: ilusão de sincronia imediata.
   - Contras: o primeiro commit que tocar só um lado reabre a deriva; não é testável;
     PHASE 0 já mediu 51/51 divergentes.
   - **Rejeitada.**

3. **Daemon / sync bidirecional permanente**
   - Prós: “nunca mais esquecer de copiar”.
   - Contras: automatiza dual authority (D7); propaga PII para o repo público e
     regressões do overlay para o produto; rollback opaco.
   - **Rejeitada.**

4. **União vault ∪ plugin como “o produto”**
   - Prós: não perde capability.
   - Contras: publica exclusões intencionais e overlay pessoal; viola Apache-friendly e
     o spec 2026-06-13 (produto distribuível, sem identidade/infra pessoal).
   - **Rejeitada.**

5. **Fork divergente de `tab_pendencias` dentro do plugin**
   - Prós: plugin autocontido.
   - Contras: terceira fonte de verdade; PHASE 0 já mostrou cópia embutida ≠ produto.
   - **Rejeitada** (D5).

6. **Manter cópias homônimas “até o drift diminuir”**
   - Prós: evita cutover agora.
   - Contras: o drift não diminui sozinho; instalar o plugin com globais = hooks duplos.
   - **Rejeitada** como estado-alvo. Transitório só até o canário (D2, D6).

7. **Multi-host git (GitHub + host legado)**
   - Prós: nenhum, após a política do host legado recusar código gerado por LLM.
   - Contras: remoto morto, badges mentirosos, CI partida.
   - **Rejeitada** (D10; BT-3 já alinhou o `origin`).

8. **Pin de versão de modelo na prosa (“usar o 4.6”, etc.)**
   - Prós: parece preciso na semana em que se escreve.
   - Contras: envelhece; vira spec falsa; quebra o mapa dual-host.
   - **Rejeitada** (D9).

---

## Consequências

**Positivas:**

- Uma fonte de verdade para o núcleo distribuível (métrica da campanha: 2 → 1).
- BT-6 ganha taxonomia e destino por classe; BT-5 não mistura porte com overlay.
- Overlay pessoal sobrevive sem contaminar o pacote público.
- Rollback é procedimento, não esperança.
- Host e notação de modelo deixam de ser fonte extra de deriva.

**Negativas / aceites como custo:**

- Cutover da instalação pessoal fica **bloqueado** até canário + inventário BT-6.
  Estado transitório com globais homônimos continua até lá.
- Wrapper `/bigtech` exige disciplina: qualquer “melhoria rápida” no wrapper é regressão.
- Manuais em `docs/house/` têm regra de prevalência distinta; quem syncar sem ler a
  exceção pode “corrigir” o produto com o vault ou o contrário.
- Pin/symlink de `tab_pendencias` implica coordenar releases (cadência consumidor-driven);
  o plugin deixa de “consertar” o produto por cópia local.

**Riscos / pontos de atenção:**

- Relatório de agent ≠ prova: cutover só após medição (`/agents`, hooks uma vez, sha
  do agent ativo = plugin).
- Verificação de vazamento é no **histórico** (`git log --all -p`), não só na árvore.
- Grok adapter que copiar agent core para a instalação viva do usuário no host Grok
  (`agents/` do overlay) recria dual authority no segundo host; o owner continua a
  ser o plugin.
- Este ADR está **Aceito em modo autônomo**. O líder confirma retroativamente; se
  recusar um D*, o estado-alvo muda **aqui** antes de BT-6 executar.

---

## Reversibilidade

**Híbrida.**

- A **atribuição de owner** (D1, D5, D10) é *one-way door* barata de reverter **antes**
  do cutover e cara **depois** (reintroduzir globais homônimos). Por isso o cutover é
  fase posterior com rollback documentado (D6).
- A **classificação de um arquivo** (D8) é *two-way door*: reclassificar não exige
  reescrever o produto inteiro.
- D7 (proibir daemon) é *two-way door* formal, mas reabrir sync bidirecional reabre o
  defeito que este ADR existe para fechar.

---

## Fora de escopo

- Implementar BT-5 (eliminar solo/headcount como porte).
- Implementar BT-6 (inventário classificado + plano de cutover).
- Remover globais vivos; editar a configuração global do Claude Code do usuário
  (`` `${CLAUDE_CONFIG_DIR}` `` / instalação viva) ou o overlay Grok equivalente;
  push, tag remota, release.
- Redesenhar o produto `tab_pendencias`.
- Alterar frontmatter `model:` dos 51 agents (literal de plataforma; outra fase).

---

## Referências

- Plano da campanha, PHASE 1 e §1.1–1.2: `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`
- Inventário PHASE 0: `docs/campanha/2026-08-16-phase0-baseline.md` e anexos
- Spec de produto 2026-06-13: `docs/superpowers/specs/2026-06-13-bigtech-plugin-design.md`
- Manuais de distribuição: `docs/house/` (vault prevalece se presente)
- Identidade do pacote: `.claude-plugin/plugin.json` (0.2.0, Apache-2.0)
- Template ADR da constelação: `agents/software-architect.md` (Nygard / MADR)
