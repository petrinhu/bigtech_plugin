# Testes do Projeto — Plugin `bigtech`

> Tipos de teste aplicáveis a este projeto. Stack: **Python** (hooks) + **Markdown** (agents/skills/docs) + **JSON** (plugin/marketplace).
> Não-aplicáveis (podados): binário compilado (T3/T4/T7/T11), DB SQL (T10), rede/API (T6/T9).
> T1 (unitário) fica sob o **hook de TDD** (`tdd_guard`/`tdd_runner`) — não vira item na tabela.
> Cada tipo abaixo é um item `TST-*` no `TODO.md`, nas ondas após a implementação.

## TST-T2 — Análise Estática
Detecta bugs e más práticas sem executar.
**Ferramentas:** `ruff` + `mypy` (hooks Python); `markdownlint` (docs/agents/skills); validação de schema dos `plugin.json` / `marketplace.json` / `hooks.json`.

## TST-DEPS (T5 + T12) — Dependências e CVEs
Dependências vulneráveis/desatualizadas e CVEs conhecidas. Os hooks devem ficar em stdlib sempre que possível; este teste confirma.
**Ferramentas:** `pip-audit`, `trivy`, OSV/NVD.

## TST-T8 — Verificação de Secrets
Garante que nenhuma credencial, token ou caminho/identidade pessoal foi commitado.
**Ferramentas:** `gitleaks`, `trufflehog`. Crítico **antes** de `R4` (publicação irreversível).

## TST-ORFAOS — Validação ZERO-ÓRFÃOS (específico do projeto)
Critério de aceitação da §4.1 do spec. Fora de blocos de código:
- `grep -rn '\[\['` = **0** (nenhum wikilink Obsidian; atributos C++ `[[nodiscard]]` em código são exceção);
- `grep -rn '/home/petrus\|~/\.claude'` = **0** (sem paths locais);
- **0** menções aos 20 agents/skills excluídos (jogo, perícia, `engineering-coach`, `product-marketing-manager`, `proj_jogo`, `pericia-medica`);
- **0** termos pessoais (nome do autor como soberano, infra pessoal, specs de máquina);
- **0** links Markdown relativos apontando para arquivo inexistente (checagem ativa de órfãos).
**Ferramentas:** script `grep`/`ripgrep` + resolvedor de links relativos. Rodar **incremental** (DoD de cada item de texto), não só ao fim.

## TST-T14 — Integração / Smoke de Instalação
Sistema integrado contra a fonte de verdade (o Claude Code real).
**Procedimento:** adicionar o marketplace local → `/plugin install bigtech` → verificar que os 50 agents, as 3 skills e os hooks carregam; e que um agent consegue **resolver e ler** um manual de `docs/` em runtime (valida o §4.3).

## TST-T15 — Pré-CI (espelhar CI local)
Rodar a suíte do CI localmente antes do push: estática (T2) + pytest dos hooks + ZERO-ÓRFÃOS.
**Ferramentas:** `scripts/preci.sh`.
