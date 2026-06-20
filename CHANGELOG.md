# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.15] - 2026-06-20

Release de frescor da tabela de pendências. **Não há novo agent nem nova skill: as contagens seguem em 51 agents e 4 skills** (badges inalterados). O frescor entra como **convenção** (status mecânico no commit, reordenar à parte), não como ferramenta: **o toolkit de git hooks de sincronização não foi incluído nesta release**.

### Added

- **Convenção "Frescor da TODO.md em commits" embarcada nos 12 agents de implementação.** Os agents `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `software-architect`, `tech-lead`, `devops-sre`, `data-engineer`, `ml-engineer`, `applied-ai-engineer` e `qa-engineer` passam a declarar a regra: ao commitar trabalho que fecha ou avança um item da tabela de pendências (`TODO.md`), citar o ID do item (ex.: `V-12`, `F1.4`) na mensagem do commit (corpo ou footer do Conventional Commit) e tocar a coluna `Status` no mesmo commit (implementação entregue vira `🔍 Pendente verificação`, NUNCA `✅` direto; `✅` só após a onda de teste/auditoria). Marcar status é edição manual de uma célula e nunca dispara o time de agents.
- **Seção "Frescor" e INBOX na skill `tab_pendencias`.** A `SKILL.md` ganhou a seção "Frescor: manter a tabela viva no sprint", que separa as duas operações de naturezas opostas - sincronizar status (mecânico, barato, frequente, no commit) e reordenar (julgamento, caro, raro, só via `--reorder` quando um input de priorização muda) - mais a subseção INBOX (captura imediata de trabalho novo em 1 linha, drenada pelo `--create`/`--reorder`; arquivo-por-descoberta em `inbox/` sob worktrees paralelos; conflito resolvido sempre por união). Reforça que a convenção vale no `TODO.md` de projeto, não no hub agregador.
- **Documento `docs/tabela-pendencias-frescor.md`.** Novo doc de governança (Diátaxis: explanation + reference) que registra a causa-raiz da defasagem, a distinção status (mecânico) vs prioridade (julgamento), o Definition of Done de status (implementação entregue → `🔍 Pendente verificação`; `✅` só pós-teste/auditoria), a INBOX e uma escada de escalonamento opcional apresentada de forma genérica (aviso de frescor no CI, rotina agendada determinística, fonte-da-verdade em issues do repositório), cada camada condicional a evidência de que o mínimo falhou. README e `AGENTS.md` (EN e PT) passam a citar a convenção de frescor onde documentam a skill `/tab_pendencias`, com link para o novo doc.

### Changed

- **Fiação do `visual-design-director` nas tabelas de delegação de Capitolino/CPO e Caetano/CTO.** O agent de design visual (introduzido na 0.1.14) passa a constar explicitamente nas tabelas de delegação dos dois C-level que o acionam: Capitolino (CPO) para o design da Fase 3 e Caetano (CTO) para o handoff de implementação. Ajuste de consistência entre o catálogo e o roteamento dos C-level; nenhuma contagem muda.
- **Mensagens do hook `tab_pendencias_reminder` refinadas.** Os avisos passam a distinguir com clareza as duas ações: **atualizar o `Status`** (mecânico, barato, faça você mesmo no commit que fecha o item) versus **reordenar a tabela** (julgamento do time, só com input de priorização novo). O comportamento do hook não muda - continua somente-leitura e fail-open, só lembra, nunca bloqueia nem reordena -, apenas o texto fica alinhado à convenção de frescor.

## [0.1.14] - 2026-06-20

### Added

- **Novo agent `visual-design-director` (Diretor de Design Visual).** Operacional (cor azul), na família Produto/UX e Design. Conduz design visual de **alta fidelidade renderizado**: pesquisa tendências do domínio, faz brainstorm dirigido (uma pergunta por vez, opções A/B/C), escreve mockups HTML/CSS com conteúdo real do produto e os **abre no navegador do usuário**, itera por seção via screenshot (paleta, navegação, componentes, tabelas, gráficos, estados, tela a tela) e entrega spec versionada em `docs/` (tokens light+dark com hex, decisões e por tela) mais o handoff. Reporta a Capitolino/CPO (design, Fase 3) e a Caetano/CTO (handoff). Distinto do `ux-ui-designer` (jornada, IA, wireframe, design-system textual) e do `art-director` (identidade visual, mood board, style guide); aqui é pixel renderizado e validado no browser. Complementa ux-writer, ux-researcher e accessibility-specialist; delega a implementação ao `frontend-engineer`. Acionável pela skill `/bigtech` quando o porte do projeto pede design dedicado.
- **Nova skill `/visual-design-director`.** Atalho que delega ao subagent homônimo para design visual de alta fidelidade renderizado.
- **A constelação passa a ter 51 agents e 4 skills.** Os operacionais sobem de 38 para 39 (a família Produto/UX e Design vai de 7 para 8) e as skills de 3 para 4. Os badges do README (`agents-51`, `skills-4`), o catálogo de agents (README), o `AGENTS.md` (EN e PT) e a constelação no `docs/ORG.md` foram atualizados. As 3 skills de orquestração (`/bigtech`, `/proj_software`, `/tab_pendencias`) seguem como pontos de entrada principais; `/visual-design-director` é a 4ª skill, no formato de atalho de agent.

## [0.1.13] - 2026-06-17

### Changed

- **`tab_pendencias_reminder` vira detector de defasagem da tabela.** Antes o hook só lembrava de criar o `TODO.md` (via `/tab_pendencias --create`) num projeto classificado (`.bigtech-porte`) mas sem a tabela. Agora, com a tabela presente, ele mede a defasagem real rodando `git` em modo somente-leitura: conta quantos commits e quantos dias se passaram desde o último toque no `TODO.md` e avisa quando os limiares são ultrapassados. O lembrete histórico de criar a tabela continua igual. O hook nunca reordena a tabela sozinho (reordenar exige o time de agents da skill `/tab_pendencias`); tudo é fail-open (qualquer erro não avisa e nunca bloqueia). O número de hooks não muda (continuam 6; o badge `hooks-6` permanece).
- **Wiring do hook em `UserPromptSubmit`.** Além do `SessionStart`, o `tab_pendencias_reminder` passa a disparar também em `UserPromptSubmit` para dar, após uma sessão longa com `TODO.md` presente, um nudge único de higiene (revisar e reordenar a tabela).

### Added

- **Config opcional `.tab-staleness.json` na raiz do projeto.** Ajusta os limiares do detector de defasagem (defaults embutidos): `commits` e `dias` para o gatilho de staleness, `modo` (`"e"` exige os dois limiares, `"ou"` basta um), `horas_sessao` para o nudge de sessão longa e `off: true` para desligar os gatilhos de staleness e de sessão (o lembrete de criar a tabela continua ativo).
- **Testes da nova lógica do hook.** A suíte de testes do `tab_pendencias_reminder` foi reescrita para cobrir os três gatilhos (criar, staleness por `git`, nudge de sessão longa), a leitura da config `.tab-staleness.json` e os caminhos fail-open. A suíte total passou a ter 141 testes (os testes do hook antigo foram substituídos pelos 15 da reforma).

## [0.1.12] - 2026-06-17

### Fixed

- **Fail-open dos três reminders de sessão quando o `stdin` não é um dicionário.** Os hooks `bigtech_porte_reminder.py`, `tab_pendencias_reminder.py` e `bigtech_session_init.py` tratavam um payload de `stdin` não-dict (lista, número ou JSON malformado) como erro e saíam com código 1, gerando ruído de "hook error" no terminal; agora absorvem o caso e seguem o turno sem interromper. Achado da auditoria de corretude dos hooks.
- **`conftest.py` aninhado classificado como código de produção.** A heurística que distingue arquivo de teste de arquivo de produção marcava um `conftest.py` fora da raiz de testes (em subdiretório aninhado) como produção, fazendo o `tdd_guard` bloquear indevidamente a edição no modo TDD; a classificação passa a reconhecê-lo como suporte de teste.
- **Falso-bloqueio do `tdd_guard` por erro de I/O.** Uma falha ao ler ou gravar o estado do TDD (arquivo de estado inacessível, permissão negada) podia ser interpretada como ausência de teste vermelho e barrar a escrita de produção; o guard passa a fazer fail-open diante de erro de I/O, permitindo a edição em vez de travar o trabalho.
- **Falsos positivos do regex de roteamento do `bigtech_reinforce`.** O padrão que detecta ativação por linguagem natural para `/bigtech` casava trechos que apenas continham a substring (por exemplo dentro de outra palavra), roteando pedidos que não eram de ativação; o regex foi ancorado para casar só a intenção real. Achado da mesma auditoria.

### Added

- **Testes para os caminhos de falha antes sem cobertura.** A suíte ganhou casos para o fail-open dos reminders com `stdin` não-dict, a classificação do `conftest.py` aninhado, o fail-open do `tdd_guard` por erro de I/O e os limites do regex de roteamento, fechando as lacunas apontadas pela auditoria de corretude dos hooks.
- **Aviso de segurança no README (EN+PT) sobre o `tdd_runner`.** A seção de Segurança/Security explicita que o modo TDD é opt-in (só liga com `.claude/tdd-guard.json` presente) e que, quando ligado, o `fast_command`/`test_command` do projeto é executado como comando de shell após cada edição; orienta a tratar esse arquivo como código confiável e a não ativar o modo TDD em repositório de terceiro não-confiável. Linha equivalente espelhada no `SECURITY.md`.

## [0.1.11] - 2026-06-17

### Added

- **Campos `$schema` e `displayName` no `.claude-plugin/plugin.json`.** O `$schema` (`https://json.schemastore.org/claude-code-plugin-manifest.json`) habilita autocomplete e validação do manifesto no editor; o `displayName` (`"Bigtech"`) é o nome legível exibido no seletor `/plugin`. Ambos os campos são opcionais e não afetam o carregamento do plugin.

### Changed

- **Campo `$schema` do `.claude-plugin/marketplace.json` corrigido.** Antes apontava para `https://anthropic.com/claude-code/marketplace.schema.json`, uma URL que não resolvia; agora usa o schema canônico do SchemaStore (`https://json.schemastore.org/claude-code-marketplace.json`). O Claude Code ignora esse campo em runtime; o ganho é autocomplete e validação no editor. Ajuste cosmético e não-breaking, fruto da auditoria de conformidade contra os parâmetros oficiais da Anthropic (o validador `claude plugin validate --strict` já passava).

## [0.1.10] - 2026-06-16

### Added

- **Seção "Direção de design distintivo" no agent `frontend-engineer`.** Os princípios da skill `frontend-design` da Anthropic (pensar tom, tipografia, cor, motion, composição e fundos antes de codar; recusar o look genérico de IA) passam a estar embarcados no corpo do agent, porque um subagent não invoca skill nativamente. Aplicam-se sempre que a tarefa cria ou redesenha interface visível, em conjunto com os cuidados de performance, acessibilidade e responsividade (não como troca).

### Changed

- **README (EN+PT) passa a recomendar a skill `frontend-design` da Anthropic para trabalho de UI.** Quando a constelação constrói ou reformula interface (`ux-ui-designer`, `art-director`, `frontend-engineer`, `accessibility-specialist`), a skill ajuda a produzir design visual distintivo em vez de padrões genéricos de template. Recomendação bilíngue (inglês internacional e pt-br), com link canônico para `https://github.com/anthropics/skills` e os comandos `/plugin marketplace add anthropics/skills` + `/plugin install example-skills@anthropic-agent-skills`.
- **`AGENTS.md` e a wiki (Instalação) passam a recomendar a skill `frontend-design`.** A recomendação "instale se ainda não estiver instalada" entra junto das dependências sugeridas, em inglês e português, com os comandos de instalação a partir do plugin `example-skills` do marketplace `anthropic-agent-skills`. A página de wiki do agent `frontend-engineer` ganha o resumo didático da nova seção.

## [0.1.9] - 2026-06-14

### Added

- **Política "ferramenta ausente" canonizada.** Os manuais `TESTES.md` e `AUDITORIAS.md`, o catálogo da skill `tab_pendencias` (e os templates que ela gera) e a `SKILL.md` passam a declarar a regra: ao executar um teste (TST-*) ou auditoria (AUD-*) cuja ferramenta requerida não está instalada, o agente oferece instalá-la com a confirmação do usuário (via AskUserQuestion), nunca em silêncio e nunca pulando o item sem avisar.

### Changed

- **Portabilidade agnóstica de sistema operacional (Linux, macOS, Windows nativo ou WSL).** Os manuais e o `docs/TOOLING.md` passam a tratar detecção e instalação adequadas ao SO (apt/dnf/brew/winget/choco/scoop), preferindo gerenciadores cross-platform (pip/uv, cargo, npm/pnpm). O `README.md` e a wiki (Instalação, Uso) ganham nota de Plataforma e da política, em inglês e português.

## [0.1.8] - 2026-06-14

### Changed

- **README.md passa a recomendar o plugin companheiro `superpowers`.** A suíte de skills de engenharia da Anthropic é apresentada como complemento que se integra bem ao bigtech, com instrução de instalá-la antes do bigtech. A recomendação é bilíngue (inglês internacional e pt-br), com link canônico `https://claude.com/plugins/superpowers` e o comando `/plugin install superpowers@claude-plugins-official`.

## [0.1.7] - 2026-06-14

### Changed

- **Remediação completa da auditoria de 9 dimensões (31 achados).** Acentuação pt-br restaurada nos hooks, no `README-tdd.md`, nas skills e no catálogo de auditorias; índices dos manuais `AUDITORIAS.md` e `TESTES.md` reparados; `SECURITY.md` passa a refletir os 6 hooks de fato; em-dash de prosa removido do conteúdo distribuído. Sincronização com os fontes: a regra de porte "nunca rebaixa para solo / piso early" agora consta no Chief of Staff e nos agents, e a skill `tab_pendencias` ganhou o gate por complexidade.

### Added

- **Cobertura de testes dos hooks de governança e do `tab_pendencias_reminder`.** A suíte de testes cresceu para 97. CI com 8 gates, incluindo o `claude plugin validate --strict` oficial e a paridade de versão entre os manifestos (`plugin.json` == `marketplace.json`).
- **README e AGENTS.md bilíngues.** Ambos passam a trazer inglês internacional e pt-br no mesmo arquivo.
- **Acessibilidade dos docs.** Texto alternativo (`alt`) no badge de CI e alternativa textual aos diagramas Mermaid.
- **Releases formais retroativas 0.1.0 e 0.1.1.** Publicadas para fechar o histórico de tags do projeto.

## [0.1.6] - 2026-06-14

### Added

- **Hook `tab_pendencias_reminder` (SessionStart).** Lembra de gerar a tabela de pendências (`TODO.md`) via `/tab_pendencias` quando o projeto já foi classificado pelo `/bigtech` (marcador `.bigtech-porte`) mas ainda não tem a tabela. Sempre sai sem bloquear (só lembra). Agora são 6 hooks (badge `hooks 6` no README).
- **Pre-flight de tabela de pendências nos 50 agents.** Ao serem acionados, os agents checam o `TODO.md` na raiz: os C-level o exigem como pré-condição no mapa de ativação; os operacionais sinalizam caso falte e seguem com a tarefa.
- **Coluna Ferramentas no catálogo de auditorias** da skill `tab_pendencias` (ex.: lcov/gcov em AUD-COV).

### Changed

- **Pacote enxuto para distribuição.** Artefatos de construção e processo saíram do pacote público (agora gitignored, mantidos só localmente): `docs/superpowers/` (spec, template de higienização e relatório de auditoria, que continham nome do autor e wikilinks de exemplo) e os artefatos de planejamento `TODO.md`, `TESTES.md` e `AUDITORIAS.md` da raiz. Os manuais de governança em `docs/manuals/` permanecem. O distribuível passa a ter zero PII e zero wikilinks.

## [0.1.5] - 2026-06-13

### Fixed

- **Badge de release no README.** O badge de versão apontava para `v0.1.2` (não fora atualizado nos lançamentos 0.1.3 e 0.1.4). Agora usa o endpoint dinâmico do shields.io para Codeberg (`gitea/v/release`), refletindo automaticamente a última release publicada, sem manutenção manual.

### Changed

- **CI no runner `codeberg-medium-lazy`.** O workflow Forgejo Actions passou a rodar no pool lazy da Codeberg (carga flexível, mais disponível) após o runner `codeberg-medium` standard ficar longos períodos em fila sem pegar o job.

## [0.1.4] - 2026-06-13

### Changed

- **`AskUserQuestion` no `tools` dos 50 agents.** Todos os agents passam a declarar a ferramenta `AskUserQuestion` no frontmatter, corrigindo a inconsistência de o corpo já instruir "pergunte via AskUserQuestion" (regra de autoridade do líder supremo) sem a ferramenta estar disponível. Em foreground o agent pode perguntar ao usuário diante de dúvida ou decisão de alto valor; em background é no-op.

## [0.1.3] - 2026-06-13

### Added

- **Badges no README.** Conjunto curado em estilo `for-the-badge`: Claude Code, Python, licença, release, status de CI (vivo, via Forgejo Actions) e contadores de agents, skills e PRs.
- **Aviso de compatibilidade.** O README, o `AGENTS.md` e os 50 agents passam a destacar que o plugin é feito para o Claude Code (Anthropic) e que não há garantia de funcionamento em outros assistentes ou CLIs de código (por exemplo, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider).

## [0.1.2] - 2026-06-13

### Fixed

- **Conformidade 100% com `claude plugin validate --strict` e `claude plugin tag`.** Resolvidos os dois únicos avisos restantes do empacotamento.
- **`description` do marketplace.** Adicionado o campo `description` no nível raiz do `marketplace.json` (o aviso "No marketplace description provided" reprovava o `--strict`).

### Changed

- **`CLAUDE.md` da raiz renomeado para `DEVELOPMENT.md`.** Um `CLAUDE.md` na raiz de um plugin não é carregado como contexto e poluía o pacote distribuído (aviso do `claude plugin tag`); o conteúdo é doc de desenvolvimento/contribuição e segue versionado com nome honesto. As menções a "CLAUDE.md" nos manuais e skills são ao conceito genérico (o CLAUDE.md do projeto onde o plugin roda) e permanecem inalteradas.

## [0.1.1] - 2026-06-13

### Changed

- **Modelo de orquestração padronizado em `opus`.** Os agents orquestradores (Chief of Staff e COO) migram de `fable` para `opus`; agora os 50 agents usam `opus` (sempre o Opus mais recente, sem versão fixa). A orquestração roda em effort máximo (recomendado). O campo `model` continua modificável manualmente no cabeçalho de cada agent. Documentado no README.

### Fixed

- **CI verde.** Corrigidos 6 avisos do `ruff` (E402, E702, F841) nos testes dos hooks que reprovavam o workflow Forgejo Actions no Codeberg.

### Added

- Seção "Modelo de orquestração" no README e link para a Wiki do projeto.

## [0.1.0] - 2026-06-13

### Added

- **Constelação de 50 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO e Chief of Staff) e 38 operacionais cobrindo engenharia, dados e IA, produto, UX e design, gestão e pessoas, marketing, crescimento e receita, e suporte, docs, legal e i18n.
- **3 skills de orquestração.** `/bigtech` monta a constelação via Chief of Staff (classifica porte, escolhe a variante de pipeline e devolve o mapa de ativação); `/proj_software` toca o ciclo de vida de software em 5 macrofases com gatekeeper anti-over-engineering; `/tab_pendencias` cria a tabela de planejamento ordenada por valor (WSJF) e dependência (topológica).
- **Hooks de TDD.** `tdd_guard` (PreToolUse) e `tdd_runner` (PostToolUse) implementam o guard-rail do ciclo red, green, refactor, com opt-in por projeto.
- **Hooks de governança bigtech.** `bigtech_porte_reminder` (SessionStart) reavalia o porte do projeto e `bigtech_reinforce` (UserPromptSubmit) reforça o modo de operação e roteia ativação por linguagem natural.
- **Docs-bootstrap.** Hook `bigtech_session_init` (SessionStart) injeta o caminho dos manuais no contexto da sessão, avisa sobre incompatibilidade com o plugin `caveman` e sugere as dependências `playwright` e `superpowers` quando ausentes.
- **13 documentos de governança.** Manuais de organização, pipeline de release, liderança, ferramentas, contrato de qualidade, testes, agile, checklist de deploy, auditorias e princípios de arquitetura, higienizados para distribuição pública.
- **Marketplace `petrinhu`.** Distribuição via `/plugin marketplace add` e `/plugin install bigtech`, sob a licença Apache-2.0.

[0.1.15]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.15
[0.1.14]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.14
[0.1.13]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.13
[0.1.12]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.12
[0.1.11]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.11
[0.1.10]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.10
[0.1.9]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.9
[0.1.8]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.8
[0.1.7]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.7
[0.1.6]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.6
[0.1.5]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.5
[0.1.4]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.4
[0.1.3]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.3
[0.1.2]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.2
[0.1.1]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.1
[0.1.0]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.0
