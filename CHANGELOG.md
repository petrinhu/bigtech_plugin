# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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

[0.1.1]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/v0.1.1
[0.1.0]: https://codeberg.org/petrinhu/bigtech_plugin/releases/tag/v0.1.0
