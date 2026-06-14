# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
