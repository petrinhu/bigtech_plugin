# TODO — Plugin `bigtech` (planejamento e pendências)

> Tabela ordenada **de cima para baixo na ordem de execução** que minimiza retrabalho.
> A coluna **Onda** marca passos paralelizáveis (igual valor, sem dependência mútua).
> Fonte de verdade do escopo: `docs/superpowers/specs/2026-06-13-bigtech-plugin-design.md`.
> Método: topological sort (Pré-requisito) + WSJF, consolidado por Cosmo/COO a partir de 4 lentes
> (software-architect, product-manager, engineering-manager, scrum-master).

- **Caminho crítico:** `F1 → H3 → A2* → S1 → TST-ORFAOS → AUD-PRIV → R4`.
- **WIP de paralelização:** 3 (gargalo = 1 revisor humano). 4 só em janelas pontuais (W2, fatiamento de A2*).
- **One-way-doors (decisão do líder supremo):** `F1` (nome/layout/`source` do marketplace = contrato público) e `R4` (publicação irreversível no Codeberg).
- **Abreviações de pré-requisito:** `D1* = D1a,D1b,D1c`; `A2* = A2a,A2b,A2c,A2d,A2e`.

| Status | Significado |
|:---|:---|
| ✅ Concluído | finalizada |
| 🔄 Em andamento | em progresso |
| ⏳ Pendente | não iniciado |
| 🔍 Pendente verificação | implementado, aguarda validação |

## Tabela de pendências

| ID | Onda | Grupo | Descrição Técnica | Prioridade | Pré-requisito | Dificuldade | Status | Estado Auditado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| F1 | W1 | Fundação | Estrutura de diretórios + `.claude-plugin/plugin.json` (name=bigtech, Apache-2.0) + `marketplace.json` (name=petrinhu, 1 plugin, `source: "./"`). **One-way-door.** | Alta | — | Baixa | ✅ Concluído | — |
| R1 | W2 | Release | `LICENSE` Apache-2.0 + `NOTICE` (pull-early: desbloqueia AUD-LICENSE). | Alta | F1 | Baixa | ✅ Concluído | — |
| D3 | W2 | Docs | Gerar `docs/principles/hardware-resource-limits.md` **generalizado** (sem specs da máquina); ~20 agents dependem. | Média | F1 | Média | ✅ Concluído | — |
| D1a | W2 | Docs | Higienizar `TOOLING.md` (40 wikilinks — o doc mais pesado). **Piloto: gerou `docs/superpowers/higienizacao-template.md`.** | Alta | F1 | Alta | ✅ Concluído | — |
| D1b | W2 | Docs | Higienizar `ORG` + `pipeline_release_1.0` + `lideranca_pipeline_release` (core da constelação). | Alta | F1 | Alta | ✅ Concluído | — |
| D1c | W2 | Docs | Higienizar manuais: `DEPLOY_CHECKLIST`, `CONTRACT`, `TESTES`, `AGILE`, `AUDITORIAS`. | Média | F1 | Média | ✅ Concluído | — |
| D2 | W2 | Docs | Higienizar 3 docs de princípios (`arquitetura-principios`, `agile-methodology`, `anti-patterns`). | Média | F1 | Média | ✅ Concluído | — |
| H1 | W2 | Hooks | Portar hooks TDD (`tdd_guard`+`tdd_common`+`tdd_runner`+`tests/`); paths → `${CLAUDE_PLUGIN_ROOT}`. **51 testes passando.** | Média | F1 | Alta | ✅ Concluído | — |
| H2 | W2 | Hooks | Portar `bigtech_porte_reminder` + `bigtech_reinforce` (paths/marcador `.bigtech-porte`). | Média | F1 | Média | ✅ Concluído | — |
| H3 | W2 | Hooks | Criar `bigtech_session_init.py` (SessionStart: docs-bootstrap + aviso caveman via settings.json + sugestão deps). **Caminho crítico (§4.3).** | Alta | F1, D3 | Alta | ✅ Concluído | — |
| D4 | W3 | Docs | Reescrever ORG §0 — transferência do título de líder supremo/CEO ao usuário que instala. *(feito junto do D1b)* | Média | D1b | Média | ✅ Concluído | — |
| H4 | W3 | Hooks | `hooks/hooks.json` — registro central de todos os hooks (eventos + `${CLAUDE_PLUGIN_ROOT}`). *(antecipado para W2)* | Média | H1, H2, H3 | Baixa | ✅ Concluído | — |
| A1 | W3 | Agents | Higienizar 12 agents C-level (zero-wikilink→links relativos, instrução imperativa de leitura, refs só aos 50, despersonalizar). | Alta | D1*, D2, D3 | Média | ✅ Concluído | — |
| A2a | W3 | Agents | Higienizar 14 agents de Engenharia (architect, tech-lead, back/front/mobile/embedded/hardware, devops, perf, network, net-sec, security, qa, release). | Alta | D1*, D2, D3 | Alta | ✅ Concluído | — |
| A2b | W3 | Agents | Higienizar 4 agents de Dados/IA (data-engineer, data-scientist, ml-engineer, applied-ai-engineer). | Média | D1*, D2, D3 | Baixa | ✅ Concluído | — |
| A2c | W3 | Agents | Higienizar 7 agents de Produto/UX/Design (PM, BA, ux-researcher, ux-ui, ux-writer, a11y, art-director). | Média | D1*, D2, D3 | Média | ✅ Concluído | — |
| A2d | W3 | Agents | Higienizar 8 agents de Gestão+Marketing (eng-manager, scrum-master, content-seo, pr-comms, growth, community, customer-success, revenue-ops). | Média | D1*, D2, D3 | Média | ✅ Concluído | — |
| A2e | W3 | Agents | Higienizar 5 agents de Suporte/Docs/Legal/i18n (support, technical-writer, compliance-legal, internal-auditor, i18n-l10n). | Média | D1*, D2, D3 | Média | ✅ Concluído | — |
| S3 | W4 | Skills | Higienizar `/tab_pendencias` (zero-wikilink, `references/`). | Média | D1*, D2 | Média | ✅ Concluído | — |
| S1 | W4 | Skills | Higienizar `/bigtech` (listar só os 50, remover `/proj_jogo`, orquestração repassa path de docs aos subagents). | Alta | A1, A2*, D1* | Alta | ✅ Concluído | — |
| S2 | W4 | Skills | Higienizar `/proj_software` (refs só aos incluídos, zero-wikilink). | Média | A1, A2*, D1* | Média | ✅ Concluído | — |
| TST-T2 | W4 | Testes | Análise estática (ruff/mypy nos hooks + markdownlint + validação de schema JSON). | Média | H3, A2* | Baixa | ✅ Concluído | — |
| TST-T8 | W4 | Testes | Verificação de secrets (gitleaks/trufflehog) em todo o repo. | Alta | H4, A2*, D1* | Baixa | ✅ Concluído | — |
| TST-ORFAOS | W5 | Testes | **Validação ZERO-ÓRFÃOS** (gate §4.1): wikilinks=0 fora de código, paths locais=0, refs aos 20 excluídos=0, termos pessoais=0, links Markdown órfãos=0. | Alta | D1*, D2, D3, D4, A1, A2*, S1, S2, S3 | Alta | ✅ Concluído | — |
| TST-DEPS | W5 | Testes | Scanning de dependências + CVEs (pip-audit / trivy / OSV) dos hooks. | Baixa | H1, H4 | Baixa | ✅ Concluído | — |
| TST-T14 | W5 | Testes | Smoke test de instalação: marketplace local → `/plugin install` → carregar 50 agents + 3 skills + hooks; agent resolve e lê um manual. | Alta | H4, A1, A2*, S1, S2, S3, R1 | Média | ⏳ Pendente | — |
| R2 | W5 | Release | `README.md` (instalação via marketplace, ritual de boas-vindas/CEO, compat caveman, deps playwright/superpowers, lista de agents/skills). | Alta | D4, H3, S1 | Média | ✅ Concluído | — |
| R3 | W5 | Release | `CHANGELOG.md` v0.1.0. | Baixa | F1 | Baixa | ✅ Concluído | — |
| AUD-SEC | W6 | Auditoria | Segurança dos hooks Python (silent-fail, sem exec inseguro/path traversal, não bloqueia) + secrets. | Alta | H4, TST-T2, TST-T8 | Alta | ✅ Concluído | ✓ |
| AUD-PRIV | W6 | Auditoria | Privacidade/despersonalização: zero dados pessoais (nome/títulos/infra/specs de máquina). **Gate de publicação.** | Alta | TST-ORFAOS | Média | ✅ Concluído | ✓ |
| AUD-LICENSE | W6 | Auditoria | Licença/atribuição: Apache-2.0 correta + `NOTICE` + compatibilidade da origem dos docs. | Alta | R1, D1* | Baixa | ✅ Concluído | ✓ |
| AUD-QUALITY | W6 | Auditoria | Qualidade/consistência de docs/agents/skills (sem god-doc, refs coerentes, terminologia única CEO). | Média | D1*, A1, A2*, S1 | Média | ✅ Concluído | ✓ |
| TST-T15 | W7 | Testes | Pré-CI: rodar a suíte local (estática + pytest dos hooks + zero-órfãos) antes do push. | Média | TST-T2, TST-ORFAOS, TST-T14 | Baixa | ⏳ Pendente | — |
| AUD-REPORT | W7 | Auditoria | Relatório final consolidado (score, sumário de achados, remediação) antes do gate. | Alta | AUD-SEC, AUD-PRIV, AUD-LICENSE, AUD-QUALITY | Média | ⏳ Pendente | — |
| R4 | W8 | Release | `git init` + publicar no Codeberg (`codeberg.org/petrinhu/bigtech_plugin`). **Gate de publicação / one-way-door — go/no-go do líder supremo.** | Alta | TST-T14, TST-T15, TST-ORFAOS, AUD-REPORT | Baixa | ⏳ Pendente | — |
| W-WIKI | W8 | Release | Wiki do repo (Codeberg/Forgejo wiki-native) + doc `.md` extensa em registro didático para INICIANTE (explica jargão, passo-a-passo). Deriva de `docs/` (linka, não duplica). Execução via `technical-writer`/`ux-writer`. | Baixa | R4 | Média | ⏳ Pendente | — |

## Tabela de scoring WSJF (itens-pai funcionais)

`CoD = Valor + Criticidade + Redução de Risco`; `WSJF = CoD / Job Size`. Rank = ordem decrescente de WSJF (justifica a prioridade *dentro* de cada nível topológico). `D1` e `A2` aparecem como item-pai (fatiados em D1a-c / A2a-e na execução; sub-lotes herdam o WSJF do pai).

| ID | Item | Valor | Criticidade | Red. Risco | CoD | Job Size | WSJF | Rank |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| R1 | LICENSE + NOTICE | 13 | 14 | 19 | 46 | 1 | 46.0 | 1 |
| F1 | Estrutura + plugin.json + marketplace.json | 18 | 18 | 20 | 56 | 2 | 28.0 | 2 |
| R3 | CHANGELOG | 8 | 9 | 7 | 24 | 1 | 24.0 | 3 |
| H4 | hooks.json | 13 | 14 | 18 | 45 | 2 | 22.5 | 4 |
| R4 | Publicar no Codeberg (gate) | 17 | 13 | 9 | 39 | 2 | 19.5 | 5 |
| H2 | porte_reminder + reinforce | 14 | 9 | 11 | 34 | 3 | 11.3 | 6 |
| D4 | ORG §0 (transferência de título) | 16 | 9 | 8 | 33 | 3 | 11.0 | 7 |
| S2 | Skill /proj_software | 13 | 9 | 11 | 33 | 3 | 11.0 | 8 |
| S3 | Skill /tab_pendencias | 11 | 8 | 10 | 29 | 3 | 9.7 | 9 |
| R2 | README | 16 | 13 | 15 | 44 | 5 | 8.8 | 10 |
| D3 | hardware-resource-limits | 9 | 7 | 10 | 26 | 3 | 8.7 | 11 |
| S1 | Skill /bigtech | 16 | 11 | 13 | 40 | 5 | 8.0 | 12 |
| D2 | 3 docs de princípios | 11 | 8 | 9 | 28 | 5 | 5.6 | 13 |
| H3 | bigtech_session_init (docs-bootstrap) | 17 | 12 | 16 | 45 | 8 | 5.6 | 14 |
| A1 | 12 agents C-level | 18 | 11 | 15 | 44 | 8 | 5.5 | 15 |
| H1 | hooks TDD | 12 | 8 | 10 | 30 | 8 | 3.8 | 16 |
| D1 | 9 docs canônicos *(→ D1a/b/c)* | 17 | 11 | 14 | 42 | 13 | 3.2 | 17 |
| A2 | 38 agents operacionais *(→ A2a–e)* | 17 | 11 | 15 | 43 | 20 | 2.2 | 18 |

> Leitura: F1 e R1 são "small bets de alta alavancagem" (baratos, desbloqueiam tudo) → topo.
> D1 e A2 têm WSJF baixo só por serem grandes — por isso foram **fatiados** e entram cedo
> (W2/W3), pois são pré-requisito de quase tudo. O fatiamento encurta o caminho crítico.

## Decisões one-way-door (go/no-go do líder supremo)

1. **`F1`** — congelar nome (`bigtech`), layout e `source` do marketplace antes de abrir a W2 (contrato público; mudar depois quebra quem já instalou).
2. **`R4`** — go/no-go da publicação no Codeberg (irreversível; usuários passam a executar os hooks Python na máquina deles).
