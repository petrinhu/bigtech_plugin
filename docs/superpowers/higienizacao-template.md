# Template de higienização — plugin público `bigtech`

- **Tipo (Diátaxis):** How-to guide (procedimento reutilizável).
- **Audiência:** technical-writers (e ux-writer) que higienizam docs/agents/skills em paralelo (D1b, D1c, D2, A1, A2a-e, S1, S2, S3).
- **Owner:** technical-writer.
- **Last-reviewed:** 2026-06-13.
- **Fonte de verdade do escopo:** `specs/2026-06-13-bigtech-plugin-design.md` (§4 + Apêndice A). Em conflito, a spec vence.
- **Status:** validado nas tarefas-piloto de doc (`docs/TOOLING.md`, item D1a) e de agent (`agents/celso-ceo.md`, item A1 — fixou o padrão da §4.3, seção "Instrução imperativa de leitura para AGENTS").

> Este é o **contrato** que padroniza a higienização. Aplique as 6 regras na ordem,
> rode o bloco de validação no fim e só então marque o item como "Pendente verificação".
> Não simplifique conteúdo técnico: despersonalizar ≠ empobrecer.

---

## Quando usar

Sempre que transformar um doc/agent/skill do vault de origem em arquivo empacotado no plugin público. O plugin é **distribuível e público**: não pode conter wikilink do vault, path local, nem identidade/infra pessoal.

## Pré-requisitos

1. Saber o **destino** do arquivo (tabela §1 abaixo) — define a profundidade dos links relativos.
2. Ter lido a spec §4 e o Apêndice A.
3. Trabalhar dentro de `Projects/plugin_bigtech/`. **Nunca** commitar (o git é responsabilidade do orquestrador / item R4).

---

## Regra 1 — Zero `[[ ]]`, zero órfãos

Cada `[[X]]` é **eliminado** por uma de duas vias; **nunca** vira ponteiro pendurado ("ver [[X]]" apontando para o vazio).

- **Alvo empacotado** (um dos 13 docs) → **link Markdown relativo**.
- **Alvo não empacotado** (PARA do vault, projeto pessoal, memória não incluída, link quebrado) → **reescrever a frase como texto autossuficiente** que explica o conceito sem citar o alvo.
- **Exceção:** `[[nodiscard]]`, `[[likely]]`, `[[maybe_unused]]` e outros **atributos C++** dentro de blocos/trechos de código são preservados (não são wikilinks).

### 1.1 Profundidade do link relativo (calcule a partir do diretório do arquivo de origem)

| Arquivo de origem está em… | Prefixo para `docs/X.md` | Prefixo para `docs/manuals/X.md` | Prefixo para `docs/principles/X.md` |
|---|---|---|---|
| `docs/` (ex.: TOOLING, ORG) | `X.md` | `manuals/X.md` | `principles/X.md` |
| `docs/manuals/` | `../X.md` | `X.md` (irmão) | `../principles/X.md` |
| `docs/principles/` | `../X.md` | `../manuals/X.md` | `X.md` (irmão) |
| `agents/` | `../docs/X.md` | `../docs/manuals/X.md` | `../docs/principles/X.md` |
| `skills/<nome>/` (SKILL.md) | `../../docs/X.md` | `../../docs/manuals/X.md` | `../../docs/principles/X.md` |

> Nos **agents**, a spec §4.3 pede instrução **imperativa autocontida** (não apenas um link passivo): "Os manuais (ORG, CONTRACT, …) acompanham o plugin; o caminho absoluto vem no contexto de sessão (docs-bootstrap). **Leia o manual citado antes de decidir.** Se o caminho não estiver no contexto, localize via Glob `**/bigtech/docs/**/<NOME>.md`." Use o link relativo como complemento, não como única referência.

### 1.2 Tabela canônica `[[X]]` → destino (todos os alvos conhecidos do Apêndice A)

Coluna "Ação": **REL** = link relativo (alvo empacotado); **TEXTO** = reescrever autossuficiente; **REMOVER** = apagar a referência; **MANTER** = preservar como está.

| `[[X]]` de origem | Categoria (Apêndice A) | Ação | Destino / texto sugerido |
|---|---|---|---|
| `[[ORG]]` | 1 — doc canônico | REL | `ORG.md` (ajuste a profundidade pela §1.1) |
| `[[pipeline_release_1.0]]` | 1 | REL | `pipeline_release_1.0.md` |
| `[[lideranca_pipeline_release]]` | 1 | REL | `lideranca_pipeline_release.md` |
| `[[TOOLING]]` | 1 | REL | `TOOLING.md` |
| `[[CONTRACT]]` | 1 | REL | `manuals/CONTRACT.md` |
| `[[TESTES]]` | 1 | REL | `manuals/TESTES.md` |
| `[[AGILE]]` | 1 | REL | `manuals/AGILE.md` |
| `[[DEPLOY_CHECKLIST]]` | 1 | REL | `manuals/DEPLOY_CHECKLIST.md` |
| `[[AUDITORIAS]]` | 1 | REL | `manuals/AUDITORIAS.md` |
| `[[arquitetura-principios]]` | 1 | REL | `principles/arquitetura-principios.md` |
| `[[agile-methodology]]` | 1 | REL | `principles/agile-methodology.md` |
| `[[anti-patterns]]` | 1 | REL | `principles/anti-patterns.md` |
| `[[nodiscard]]` e atributos C++ | 2 — atributo C++ | MANTER | preservar dentro do bloco de código |
| `[[feedback_hardware_resource_limits]]` / "limites de hardware" | 3 — memória transversal empacotada | REL | `principles/hardware-resource-limits.md` (versão generalizada, sem specs da máquina) |
| `[[feedback_mcp_priority]]` / "prioridade MCP" | 4 — memória absorvida | TEXTO | "quando houver um servidor MCP que cubra a tarefa, prefira-o ao shell cru" |
| `[[feedback-tests-real-db]]` | 4 | TEXTO | "prefira testar contra um banco real/efêmero em vez de mock quando a fidelidade importar" |
| `[[user-lider-supremo]]` / "líder supremo" | 4 — ver Regra 2 | TEXTO | transferir o conceito ao usuário/operador (Regra 2) |
| `[[Standards]]` | 5 — PARA do vault | TEXTO | "seus padrões/manuais de engenharia" (é o hub do vault; não existe no plugin) |
| `[[Journal]]` | 5 | TEXTO | "seu changelog / diário de projeto" |
| `[[Inbox]]`, `[[Areas]]`, `[[Resources]]`, `[[Resources/Standards/*]]` | 5 | TEXTO | reescrever para o conceito ("suas anotações", "suas áreas", "seus recursos") |
| `[[Projects/site_consultorio]]`, `rag_maker`, `PokemonTCGViewer`, `transcritor`, `my_comp`, `astrometrica`, `orcamento-pessoal`, `driver_brother_hl_l1222`, `ESP32`, `bcklight`, `*/reports`, `*/TODO` | 6 — projetos pessoais | TEXTO/REMOVER | substituir por exemplo genérico ("um projeto de API", "um app desktop") ou remover o exemplo |
| `[[CLAUDE]]` | 7 — genérico contextual | TEXTO | "o `CLAUDE.md` do projeto" |
| `[[TODO]]` | 7 | TEXTO | "o `TODO.md` do projeto" |
| `[[SEGURANCA]]` | 8 — link já quebrado | REMOVER | apagar (não existe nem no vault original) |
| `[[tab_pendencias]]` (skill incluída) | 11 — ref interna válida | MANTER | menção textual à skill `/tab_pendencias` (não é doc; não vira link relativo) |

> **Regra de ouro contra órfãos:** valide os links relativos contra o **mapa de destino**
> da §2.5 da spec (a tabela §1.2 acima), **não** contra o filesystem atual — os 13 docs são
> criados em paralelo (W2/W3) e podem ainda não existir quando você higieniza o seu. O gate
> final de órfãos (`TST-ORFAOS`, W5) roda quando todos estiverem no lugar.

---

## Instrução imperativa de leitura para AGENTS (§4.3)

> **Aplica-se apenas aos 50 agents** (`agents/*.md`). Nos docs e skills a referência passiva
> vira link relativo simples (Regra 1); nos **agents** ela vira uma **ordem de LER** o manual
> antes de decidir, com o caminho resolvido em runtime. Validado na tarefa-piloto
> (`agents/celso-ceo.md`, item A1).

**Problema que esta regra resolve (spec §4.3).** A referência original do agent é passiva
(`"Manuais: [[CONTRACT]], [[TESTES]]…"`) e depende do resolvedor de wikilinks do vault, que
**não viaja com o plugin**. Pior: `${CLAUDE_PLUGIN_ROOT}` só expande no `hooks.json` (não no
corpo do agent), e **subagents não herdam o `additionalContext`** injetado na thread principal.
A correção tem duas partes obrigatórias: (1) trocar a citação passiva por uma **ordem de
leitura** com caminho resolvido em runtime; (2) instruir o agent a **repassar o caminho absoluto
no prompt** quando ele despachar um subagent.

### Bloco-modelo (copie e adapte ao texto do agent)

Substitua a antiga seção de "Referências canônicas" por uma seção própria (sugestão de título:
**"Leitura obrigatória antes de decidir"**), com este esqueleto. Liste **apenas os manuais que o
agent original citava** (não acrescente manuais que não eram dele).

```markdown
## Leitura obrigatória antes de decidir

**Antes de [a ação central do agent: arbitrar / aprovar arquitetura / fechar o sprint / …], leia os manuais que acompanham o plugin.** O caminho absoluto de `docs/` é injetado no contexto da sessão pelo docs-bootstrap (hook `SessionStart`); se ele não estiver no contexto, localize os arquivos via Glob `**/bigtech/docs/**/<NOME>.md`. Leia o manual relevante ao tipo de decisão **antes** de fechá-la, nunca depois:

- **Pipeline de release**: [`pipeline_release_1.0`](../docs/pipeline_release_1.0.md).
- **Liderança C-level**: [`lideranca_pipeline_release`](../docs/lideranca_pipeline_release.md).
- **Governança e RACI**: [`ORG`](../docs/ORG.md).
- **Manuais de execução**, em `docs/manuals/`: [`CONTRACT`](../docs/manuals/CONTRACT.md) (código), [`TESTES`](../docs/manuals/TESTES.md) (qualidade), [`AGILE`](../docs/manuals/AGILE.md) (cadência), [`DEPLOY_CHECKLIST`](../docs/manuals/DEPLOY_CHECKLIST.md) (deploy/rollback), [`AUDITORIAS`](../docs/manuals/AUDITORIAS.md) (checklists de gate).

> **Ao despachar um subagent, inclua o caminho absoluto de `docs/` no prompt da task.** Subagents não herdam o contexto da sessão (o docs-bootstrap só alcança a thread principal e as skills); sem o caminho no prompt, o subagent não consegue abrir o manual.
```

### Como adaptar (4 ajustes obrigatórios)

1. **A ação central muda por agent.** No CEO é "arbitrar trade-off ou bater go/no-go"; num
   `software-architect` é "aprovar a arquitetura"; num `scrum-master` é "fechar o sprint".
   Use o verbo do mandato do próprio agent.
2. **Liste só os manuais do agent.** Reaproveite exatamente os `[[X]]` que o original citava
   (na seção "Referências canônicas" e ao longo do corpo). Não infle a lista.
3. **Profundidade do link = `../docs/`** (todo agent vive em `agents/`; ver §1.1). Atributo C++
   em código é exceção e fica intocado.
4. **A nota do subagent é obrigatória** sempre que o agent tiver a tool `Agent` (orquestradores
   e C-levels). Em agent puramente executor, sem `Agent` na lista de tools, a nota pode ser
   omitida, mas mantê-la não faz mal e padroniza.

### Refs imperativas no corpo (além da seção dedicada)

Quando um anti-padrão ou passo do corpo citava um manual de forma passiva ("ver
[[DEPLOY_CHECKLIST]]"), troque por uma **ordem curta com o link relativo**, ex.:
`leia [DEPLOY_CHECKLIST](../docs/manuals/DEPLOY_CHECKLIST.md) antes do go`. O link relativo é
complemento da ordem, nunca a única referência.

### Cuidado de estilo (anti-pattern do projeto)

Ao reescrever o bloco de **Autoridade** (transferência de título, Regra 2) e a seção de leitura,
**não use em-dash (`—`)**. Prefira parênteses, dois-pontos ou reestruture a frase. O em-dash é
proibido pelo projeto; o gate de validação não o pega, então é responsabilidade do writer.
Rode `grep -n '—' agents/<agent>.md` (esperado: 0) antes de entregar.

---

## Regra 2 — Despersonalização e transferência de título (spec §4.2)

Remover o que prende à **identidade** do autor; transferir o **conceito** de autoridade ao usuário que instala.

1. **Identidade pessoal** → generalizar para **"você, o usuário/operador"**. Termos a eliminar: `<nome-do-autor>` e qualquer apelido de soberania (ex.: títulos como rei/presidente/soberano atrelados nominalmente ao autor), "líder supremo" como pessoa específica, `<email-pessoal>`.
2. **Transferência de título (feature de produto, não remoção):** o conceito de autoridade suprema **passa para quem instala**. Padrão de reescrita:
   > "Você, que opera este plugin, é o **líder supremo** desta organização — o **CEO da sua bigtech**. A constelação C-level propõe e executa; a palavra final é sua. Diante de dúvida ou de mais de uma opção, os agents perguntam via AskUserQuestion (opção recomendada primeiro)."

   Onde aplicar com mais força: **ORG §0** e o **README** (ritual de boas-vindas). Nos demais arquivos, basta trocar "petrus/o líder supremo" por "você, o usuário".
3. **Stack imposta** (`C++/Qt`, `Breeze` como default obrigatório) → "stack do projeto (configurável)". Mantenha exemplos **como exemplos**, nunca como lei pessoal. (No TOOLING, "build C++/Qt" foi preservado por ser exemplo legítimo de uso da ferramenta `cmake`, não imposição de stack.)
4. **Infra pessoal** → genérica ou removida: `<infra-pessoal>` (provedor de hosting, instâncias de git pessoais, MCPs/tokens específicos, contas) → "seu provedor de git/hosting", "seu servidor MCP".
5. **Specs de máquina** → remover: modelo de CPU/GPU, quantidade de RAM/VRAM (ex.: "VRAM 4GB" → "a VRAM disponível"), distro como fato pessoal ("Fedora 44", "auditado no sistema em <data>").
6. **`anti-patterns.md`** recebe revisão item a item: manter as proibições **universais** (`--force`, `--no-verify`, amend de commit publicado), generalizar/remover as atreladas ao fluxo pessoal.

### Termos pessoais a remover (lista de varredura)

Use como filtro `grep -niE`. Qualquer ocorrência fora de exemplo neutro deve ser tratada:

```
<nome-do-autor> | presidente | \brei\b | soberano | líder supremo
<infra-pessoal> | /home/<usuário> | ~/\.claude | <email-pessoal>
<instância-de-git-pessoal> | <conta-de-git-pessoal>
<distro+versão> | auditado no sistema | instalado no sistema | <specs-de-máquina>
```

> Substitua cada placeholder pelos valores reais do seu ambiente ao montar o filtro. Cuidado
> com falsos positivos: o gerenciador de pacotes da distro (`dnf`, `apt`, `pacman`…) **não** é
> dado pessoal — preserve-o como exemplo e acrescente a nota de portabilidade (Regra 4). A
> plataforma de git só é proibida quando aponta para a **conta pessoal**; citar a plataforma
> de forma genérica é permitido.

---

## Regra 3 — Remover refs a agents/skills excluídos (20)

O produto reflete **só os 50 agents incluídos**. Remova menções, seções, linhas de tabela, delegações e itens de "Integração" que citem qualquer excluído.

### 20 agents/skills excluídos

| Grupo | Itens |
|---|---|
| Jogo (10 agents) | `3d-artist-rigger`, `audio-designer-composer`, `economy-designer`, `engine-graphics-programmer`, `game-animator`, `gameplay_engineer`, `game-producer`, `lead-game-designer`, `level-designer`, `narrative-designer` |
| Perícia/forense (4 agents) | `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho` |
| Pessoal/literário/pedagógico (4 agents) | `narrative-writer`, `revisor-textual`, `learning-designer`, `linux-diag` |
| Sobreposição (2 agents) | `engineering-coach` (→ `engineering-manager`), `product-marketing-manager` (→ `camilo-cmo` + `content-seo` + `pr-comms`) |
| Skills (2) | `/proj_jogo`, `/pericia-medica` |

### Como remover sem deixar buraco

- **Linha de tabela** (ex.: `linux-diag` no kit canônico) → apagar a linha inteira.
- **Item de coluna** (ex.: "performance, linux-diag" em col Agents) → apagar só o termo excluído, manter o resto ("performance").
- **Seção inteira** dedicada a um excluído → remover a seção.
- **Delegação/integração** ("delega para `dr-advogado`") → remover ou redirecionar ao incluído equivalente.
- **`art-director`** (incluído, zona cinzenta): remover as referências dele aos **colegas de jogo** (3d-artist, level-designer etc.), mantendo o agent.

> No TOOLING-piloto, `linux-diag` aparecia em 2 lugares (col Agents de `strace/ltrace` e
> linha própria no kit canônico §11). Ambos foram tratados: termo removido da coluna; linha
> do kit apagada.

---

## Regra 4 — Paths locais e portabilidade

1. `~/.claude`, `/home/<usuário>` e qualquer caminho absoluto da máquina do autor → **remover** ou generalizar. Em **hooks** (não neste escopo de docs), paths resolvem via `${CLAUDE_PLUGIN_ROOT}` — **e somente** no `hooks/hooks.json`.
2. Caminhos de runtime nos docs/agents → instrução de localização via contexto de sessão (docs-bootstrap) ou Glob `**/bigtech/docs/**/<NOME>.md` (spec §4.3).
3. **Comandos de instalação por distro:** `dnf` (Fedora/RHEL) é mantido como exemplo concreto **com nota de portabilidade** no topo do doc:
   > "Os comandos usam `dnf` (Fedora/RHEL) como exemplo; em outras distribuições adapte ao seu gerenciador de pacotes (`apt`, `pacman`, `zypper`, `brew`, `nix`)."

---

## Regra 5 — Preservar todo o conteúdo técnico

Despersonalizar **não** é empobrecer. Mantêm-se integralmente: o catálogo de ferramentas FOSS, os comandos de instalação, os kits por agent, tabelas de opções, exemplos de código, sintaxe, diagramas. O que sai é só o **vínculo ao ambiente/identidade local**, nunca o **valor técnico**.

---

## Regra 6 — Status pessoal → neutro

Marcadores de status que descrevem a **máquina do autor** ("temos/instalado no sistema") são generalizados, não jogados fora (preserva o sinal técnico útil).

**Decisão adotada na piloto (TOOLING) — ratificar com o líder supremo antes de propagar:**

- **Legenda neutralizada** (em vez de remover a coluna):
  - ✓ **comum** — costuma já estar no toolchain de uma estação de desenvolvimento.
  - ⬇ **instalar sob demanda** — instale com o comando da coluna quando a tarefa pedir.
  - ↺ **preferir** — alternativa moderna recomendada no lugar da legada.
- **Seção de "Resumo de status"** (inventário "já temos / baixar" da máquina) → reescrita como **"Tiers de adoção"** (preferir-ao-legado + tier-1 mais usado + sob-demanda), sem listar o que está instalado em nenhuma máquina específica.
- **Remover** das notas: distro/versão como fato pessoal ("Fedora 44"), "auditado no sistema em <data>", specs de hardware.

> Alternativas consideradas e por que a neutralização venceu na piloto: (a) **remover a
> coluna inteira** — mais enxuto, porém perde o sinal "preferir X ao legado" que é
> recomendação técnica universal; (b) **manter só ↺** — meio-termo. A neutralização preserva
> o máximo de conteúdo técnico (mandato da Regra 5) sem nenhum resíduo de máquina. Como isto
> vira padrão para os demais docs, **o orquestrador deve confirmar a escolha com o líder
> supremo** (decisão estrutural; AskUserQuestion não está disponível em subagent).

---

## Mapa de destino dos 13 docs (spec §2.5)

| Doc | Destino no plugin |
|---|---|
| ORG | `docs/ORG.md` |
| pipeline_release_1.0 | `docs/pipeline_release_1.0.md` |
| lideranca_pipeline_release | `docs/lideranca_pipeline_release.md` |
| TOOLING | `docs/TOOLING.md` |
| CONTRACT | `docs/manuals/CONTRACT.md` |
| TESTES | `docs/manuals/TESTES.md` |
| AGILE | `docs/manuals/AGILE.md` |
| DEPLOY_CHECKLIST | `docs/manuals/DEPLOY_CHECKLIST.md` |
| AUDITORIAS | `docs/manuals/AUDITORIAS.md` |
| arquitetura-principios | `docs/principles/arquitetura-principios.md` |
| agile-methodology | `docs/principles/agile-methodology.md` |
| anti-patterns | `docs/principles/anti-patterns.md` (higienização extra item a item) |
| hardware-resource-limits | `docs/principles/hardware-resource-limits.md` (generalizado, sem specs da máquina) |

---

## Bloco de validação (rodar antes de marcar "Pendente verificação")

Troque `<ARQUIVO>` pelo caminho do seu doc. Os três primeiros são **critério de aceitação**; os demais são higiene de qualidade.

```bash
F=<ARQUIVO>

# 1. Zero wikilinks (fora de blocos de código com atributos C++). Esperado: 0.
grep -n '\[\[' "$F"

# 2. Zero termos pessoais (troque os placeholders pelos valores reais do seu ambiente). Esperado: 0.
grep -niE '<nome-do-autor>|<infra-pessoal>|/home/<usuário>|~/\.claude' "$F"

# 3. Zero agents/skills excluídos. Esperado: 0.
grep -niE 'linux-diag|narrative-writer|revisor-textual|learning-designer|engineering-coach|product-marketing-manager|proj_jogo|pericia-medica|dr-advogado|dr-medico|3d-artist|audio-designer|economy-designer|engine-graphics|game-animator|gameplay_engineer|game-producer|lead-game-designer|level-designer|narrative-designer' "$F"

# 4. Links relativos: confira cada alvo contra o mapa de destino (§2.5), NÃO contra o filesystem.
grep -noE '\]\([^)]+\.md\)' "$F" | sort -u

# 5. Resíduos de infra/specs (revisar manualmente; gerenciador de pacotes da distro + nota de portabilidade é OK).
grep -niE '<instância-de-git-pessoal>|<conta-de-git-pessoal>|VRAM [0-9]|auditado no sistema|instalado no sistema' "$F"
```

> `exit=1` (nenhum match) é o resultado esperado de 1, 2 e 3. Em (4), todo alvo deve constar
> da tabela §1.2/§2.5. Em (5), avalie cada match: nota de portabilidade do `dnf` é permitida;
> conta pessoal de git, specs de hardware e "auditado no sistema" devem sair.

---

## Checklist de doc lifecycle (por arquivo higienizado)

- [ ] Regra 1 aplicada — `grep '\[\['` = 0; cada `[[X]]` virou REL ou TEXTO (sem órfão).
- [ ] Regra 2 aplicada — identidade pessoal generalizada; título transferido ao usuário onde cabe.
- [ ] Regra 3 aplicada — zero menção aos 20 excluídos; sem buraco sintático.
- [ ] Regra 4 aplicada — sem path local; nota de portabilidade onde há comando por distro.
- [ ] Regra 5 respeitada — conteúdo técnico preservado integralmente.
- [ ] Regra 6 aplicada — status/inventário pessoal neutralizado.
- [ ] Links relativos conferidos contra o mapa de destino (§2.5).
- [ ] Heading hierarchy sem skip (H1 único; H2 → H3 sem pular).
- [ ] Bloco de validação rodado; resultados anexados ao status do item.
- [ ] Não commitado (git é do orquestrador / item R4).
