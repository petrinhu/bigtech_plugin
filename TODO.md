# TODO — Plugin `bigtech` (planejamento e pendências)

> Tabela ordenada **de cima para baixo na ordem de execução** que minimiza retrabalho.
> A coluna **Onda** marca passos paralelizáveis (igual valor, sem dependência mútua).
> Fonte de verdade do escopo: `docs/superpowers/specs/2026-06-13-bigtech-plugin-design.md`.
> Método: topological sort (Pré-requisito) + WSJF. Reorder campanha 2026-08-16:
> Cosimo → thread direta (anti-OE; 10 ativos BT-*, grafo linear). Tabela 1.0 histórica
> foi consolidada por Cosmo/COO a partir de 4 lentes.
>
> **Estado atual:** Release 1.0 fechado (ondas W1-W8 + W-WIKI ✅). Campanha ativa **2026-08-16** =
> IDs **`BT-*`** no topo (ondas **W1..W5**); fechamento **`TST-BT-1` (W6) → `AUD-BT-1` (W7)** fica no
> **fim da tabela** (não executar agora; só após BT-*) + plano
> `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`. Legados **N9**, **OS-1..5** e **TOOL-1..4**
> cancelados 2026-08-16 (legacy/OE). Catálogo genérico T5/T12/AUD-DISC|ARCH|COV|DEPS|LANG: **skip**
> (cobertos por suite 1.0 ✅ ou anti-OE; ver nota add_tests_audit).

- **Caminho crítico (1.0, concluído):** `F1 → H3 → A2* → S1 → TST-ORFAOS → AUD-PRIV → R4`.
- **Caminho crítico (pós-1.0 histórico):** `N8` ✅; `N9` cancelado 2026-08-16 (legacy/OE, fora da campanha BT-*).
- **Caminho crítico (campanha BT-\*, ativo):** `BT-0` (W1) → `BT-3`/`BT-1`/`BT-2` (W2) → `BT-5`/`BT-6`/`BT-4` (W3) → `BT-7`/`BT-8` (W4) → `BT-9` (W5) → `TST-BT-1` (W6) → `AUD-BT-1` (W7). Fundação restante = `BT-1` (bloqueia BT-5/BT-6). `BT-9` gated pelo líder; fechamento = revalidação + auditoria de campanha. Reorder 16/08/26: Cosimo → thread direta; 🔍 não bloqueia dependentes de fatia já entregue.
- **WIP de paralelização:** campanha BT-\* (main despacha ≤2 agents/rodada). WIP pós-1.0 em N9 **encerrado** com o cancelamento legacy/OE. Era 3 durante o 1.0 (gargalo = 1 revisor humano), 4 só em janelas pontuais (W2, fatiamento de A2\*).
- **One-way-doors (decisão do líder supremo):** `F1` (nome/layout/`source` do marketplace = contrato público), `R4` (primeira publicação pública — host legado da época; canônico agora GitHub). `N9` (marketplace comunitário) permanece one-way-door **se reaberto**, mas está **cancelado** na tabela até go/no-go pós-campanha.
- **Abreviações de pré-requisito:** `D1* = D1a,D1b,D1c`; `A2* = A2a,A2b,A2c,A2d,A2e`.

| Status | Significado |
|:---|:---|
| ✅ Concluído | finalizada |
| 🔄 Em andamento | em progresso |
| ⏳ Pendente | não iniciado |
| 🔍 Pendente verificação | implementado, aguarda validação |
| 💡 Decisão tomada | abordagem definida / cancelado (legacy-OE) sem emoji próprio |

## Tabela de pendências

| ID | Onda | Grupo | Descrição Técnica | Prioridade | Pré-requisito | Dificuldade | Status | Estado Auditado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BT-0 | W1 | Campanha | PHASE 0 freeze/baseline/inventario campanha 2026-08-16: medir e fechar DoD (SHA repos + agents/skills/hooks + modelos) <!-- intake:cand-BT-0-2026-08-16 --> | Alta | — | Média | 🔍 Pendente verificação | — |
| BT-3 | W2 | Distribuição | Remote GitHub canônico + purgar CI/host legado (`.forgejo`) e refs operacionais; oficial `github.com/petrinhu/bigtech_plugin` (sem apagar histórico git) <!-- intake:cand-BT-3-2026-08-16 --> | Alta | BT-0 | Média | 🔍 Pendente verificação | — |
| BT-1 | W2 | Arquitetura | FABLE-ORG-ARCH: ADR source-of-truth dual-authority vault×plugin (PHASE 1) <!-- intake:cand-BT-1-2026-08-16 --> | Alta | BT-0 | Alta | 🔍 Pendente verificação | — |
| BT-2 | W2 | Docs | docs/house: sync 10 manuais vault + README de navegação (cópia produto) <!-- intake:cand-BT-2-2026-08-16 --> | Alta | BT-0 | Média | 🔍 Pendente verificação | — |
| BT-5 | W3 | Porte | Eliminar solo/headcount como porte (skill /bigtech + hooks + Cosimo alinhados; piso early) <!-- intake:cand-BT-5-2026-08-16 --> | Alta | BT-1 | Média | ⏳ Pendente | — |
| BT-6 | W3 | Governança | Inventário dual-authority agents: classificar CORE/OVERLAY/STALE/EXCLUSION + plano cutover <!-- intake:cand-BT-6-2026-08-16 --> | Alta | BT-1 | Alta | ⏳ Pendente | — |
| BT-4 | W3 | CI | CI multi-OS GitHub Actions (matrix espelho tab_pendencias: Ubuntu/Windows + containers) <!-- intake:cand-BT-4-2026-08-16 --> | Alta | BT-3 | Alta | 🔍 Pendente verificação | — |
| BT-7 | W4 | Qualidade | Drift gate semântico registry/agents/skills (CI/hook; PHASE posterior) <!-- intake:cand-BT-7-2026-08-16 --> | Média | BT-6 | Alta | ⏳ Pendente | — |
| BT-8 | W4 | Evals | Evals de roteamento da skill /bigtech (constelação + porte) <!-- intake:cand-BT-8-2026-08-16 --> | Média | BT-5 | Alta | ⏳ Pendente | — |
| BT-9 | W5 | Release | Proteção de main + release gates (go/no-go do líder) (protecao remota GitHub, tag/PR) <!-- intake:cand-BT-9-2026-08-16 --> | Alta | BT-4 | Média | ⏳ Pendente | — |
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
| TST-T14 | W5 | Testes | Smoke test de instalação: marketplace local → `/plugin install` → carregar 50 agents + 3 skills + hooks; agent resolve e lê um manual. | Alta | H4, A1, A2*, S1, S2, S3, R1 | Média | ✅ Concluído | — |
| R2 | W5 | Release | `README.md` (instalação via marketplace, ritual de boas-vindas/CEO, compat caveman, deps playwright/superpowers, lista de agents/skills). | Alta | D4, H3, S1 | Média | ✅ Concluído | — |
| R3 | W5 | Release | `CHANGELOG.md` v0.1.0. | Baixa | F1 | Baixa | ✅ Concluído | — |
| AUD-SEC | W6 | Auditoria | Segurança dos hooks Python (silent-fail, sem exec inseguro/path traversal, não bloqueia) + secrets. | Alta | H4, TST-T2, TST-T8 | Alta | ✅ Concluído | ✓ |
| AUD-PRIV | W6 | Auditoria | Privacidade/despersonalização: zero dados pessoais (nome/títulos/infra/specs de máquina). **Gate de publicação.** | Alta | TST-ORFAOS | Média | ✅ Concluído | ✓ |
| AUD-LICENSE | W6 | Auditoria | Licença/atribuição: Apache-2.0 correta + `NOTICE` + compatibilidade da origem dos docs. | Alta | R1, D1* | Baixa | ✅ Concluído | ✓ |
| AUD-QUALITY | W6 | Auditoria | Qualidade/consistência de docs/agents/skills (sem god-doc, refs coerentes, terminologia única CEO). | Média | D1*, A1, A2*, S1 | Média | ✅ Concluído | ✓ |
| TST-T15 | W7 | Testes | Pré-CI: rodar a suíte local (estática + pytest dos hooks + zero-órfãos) antes do push. | Média | TST-T2, TST-ORFAOS, TST-T14 | Baixa | ✅ Concluído | — |
| AUD-REPORT | W7 | Auditoria | Relatório final consolidado (score, sumário de achados, remediação) antes do gate. | Alta | AUD-SEC, AUD-PRIV, AUD-LICENSE, AUD-QUALITY | Média | ✅ Concluído | ✓ |
| R4 | W8 | Release | `git init` + primeira publicação pública (host legado da época; canônico agora `github.com/petrinhu/bigtech_plugin`). **Gate de publicação / one-way-door — go/no-go do líder supremo.** | Alta | TST-T14, TST-T15, TST-ORFAOS, AUD-REPORT | Baixa | ✅ Concluído | — |
| W-WIKI | W8 | Release | Wiki do repo (GitHub wiki-native) + doc `.md` extensa em registro didático para INICIANTE (explica jargão, passo-a-passo). Deriva de `docs/` (linka, não duplica). Execução via `technical-writer`/`ux-writer`. | Baixa | R4 | Média | ✅ Concluído | ✓ |
| N1 | W9 | Manutenção | Conformidade 100% (`validate --strict` + `tag`): marketplace description + migração `CLAUDE.md` → `DEVELOPMENT.md`. *(release 0.1.2)* | Alta | R4 | Baixa | ✅ Concluído | — |
| N2 | W9 | Manutenção | Badges no `README` + badge de release dinâmico (endpoint shields do host da época; canônico agora GitHub). *(releases 0.1.2/0.1.3/0.1.5)* | Média | R4 | Baixa | ✅ Concluído | — |
| N3 | W9 | Manutenção | Aviso de compatibilidade só-Claude (`README` + `AGENTS.md` + os 50 agents). *(release 0.1.3)* | Média | R4 | Baixa | ✅ Concluído | — |
| N4 | W9 | Manutenção | `AskUserQuestion` no campo `tools` dos 50 agents (alinhamento com a autoridade do líder supremo). *(release 0.1.4)* | Média | R4 | Média | ✅ Concluído | — |
| N5 | W9 | Manutenção | Integração `tab_pendencias`: hook `tab_pendencias_reminder` + pre-flight de `TODO.md` nos 50 agents + coluna Ferramentas no catálogo. *(release 0.1.6)* | Alta | R4, N4 | Média | ✅ Concluído | — |
| N6 | W9 | Distribuição | Higienização de distribuição: `docs/superpowers` + `TODO`/`TESTES`/`AUDITORIAS` fora do pacote (gitignored); zero PII/wikilinks no tracked. *(release 0.1.6)* | Alta | R4 | Média | ✅ Concluído | — |
| N7 | W9 | Manutenção | CI resiliente no runner lazy do host anterior (legado, removido; pipeline tolerante a flaky). *(releases 0.1.5/0.1.6)* | Média | R4 | Média | ✅ Concluído | — |
| N8 | W10 | Release | Fechar 0.1.6: CI verde + tag `bigtech--v0.1.6` (imutável) + Release formal. **One-way-door técnico (tag); destravou N9 e N10.** Concluído: CI verde no lazy (1m4s), tag e Release publicadas. | Alta | N1, N5, N6, N7 | Baixa | ✅ Concluído | — |
| N10 | W12 | Release | Releases formais retroativas 0.1.0 / 0.1.1 (mecânica de Release repetida x2). **Two-way-door; paralelizável com W11. Opcional: dropar com razão registrada se não for puxado.** | Baixa | N8 | Baixa | ✅ Concluído | — |
| N11 | W13 | Sincronização | Portar dos fontes a regra "porte nunca rebaixa para solo" (piso early; anti-OE calibrado por complexidade): no `cosimo-chief-of-staff` remover a faixa Solo da tabela de porte e renomear o Pipeline-Sprint para early minimalista; nos ~19 agents trocar "projeto solo" por "projeto pequeno". Espelha o commit `a2d68212`. | Média | — | Média | ✅ Concluído | — |
| N12 | W13 | Sincronização | Confirmar fallback de modelo para `opus` e zero resíduo indevido de `fable` (espelha `e9056515`). Os orquestradores do plugin já usam `opus`; a única menção a `fable` é histórica no `CHANGELOG`. Verificação. | Baixa | — | Baixa | ✅ Concluído | — |
| N13 | W13 | Sincronização | Portar a atualização da skill `tab_pendencias` (gate por complexidade + determinação de agente; espelha `e68cc7e3` do submodule) para `skills/tab_pendencias/`. | Média | — | Baixa | ✅ Concluído | — |
| N14 | W14 | Auditoria | **Re-higienização de PII e wikilinks pós-sincronização (DoD recorrente).** Rodar o gate zero-órfãos (`validate_plugin.py`) + verificação de PII/wikilinks no conteúdo tracked, garantindo que os portes N11-N13 não reintroduziram nome do autor, paths locais, wikilinks `[[ ]]` nem links órfãos no distribuível. | Alta | N11, N12, N13 | Baixa | ✅ Concluído | — |
| AUD-R1 | W15 | Auditoria | 🔴 Remediar críticos de conteúdo (via technical-writer): SECURITY.md para 6 hooks (F01); acentuação pt-br completa de `hooks/README-tdd.md`, `skills/tab_pendencias/SKILL.md` e `references/catalogo-testes-auditorias.md` (F02-F04); reparar os índices dos manuais distribuídos `AUDITORIAS.md` e `TESTES.md` (âncoras mortas + salto de heading) (F05-F06). | Alta | — | Alta | ✅ Concluído | ✓ |
| AUD-R2 | W15 | Auditoria | 🔴 Cobertura de testes dos hooks (via qa-engineer): criar testes de `tab_pendencias_reminder` + `bigtech_session_init`/`porte_reminder`/`reinforce`; exercitá-los no smoke; desfixar "52 testes" nos comentários (F07, F08, F20). | Alta | — | Média | ✅ Concluído | ✓ |
| AUD-R3 | W16 | Auditoria | 🟠 Conteúdo/acentuação pontual (secao/ate/criterios), em-dash de prosa (10 ocorrências) e comando de instalação consistente entre README e AGENTS (F09-F17). | Média | AUD-D01, AUD-D03 | Média | ✅ Concluído | ✓ |
| AUD-R4 | W16 | Auditoria | 🟠 Acessibilidade (via accessibility-specialist): alt descritivo do badge de CI + alternativa textual dos diagramas Mermaid em ORG/lideranca/pipeline (F18, F19). | Média | — | Baixa | ✅ Concluído | ✓ |
| AUD-R5 | W17 | Auditoria | 🟢 Cosméticos de conteúdo (via technical-writer): AGENTS.md versão para 0.1.6 (F21), ORG inclui CAIO na lista histórica (F22), naming "OpenAI Codex" uniforme (F28), over-engineering hifenizado (F29), travessão em heading do cosimo (F30), a11y menores (F31). | Baixa | AUD-D03 | Baixa | ✅ Concluído | ✓ |
| AUD-R6 | W17 | Auditoria | 🟢 Cosméticos de CI/build (via devops-sre): comentário do CI cita o smoke (F23), `claude plugin validate --strict` oficial no preci/CI (F24), trava de sync de versão entre os 2 manifestos (F25), remover `.gitkeep` redundantes (F26), faixa de ano no NOTICE (F27). | Baixa | — | Baixa | ✅ Concluído | ✓ |
| I18N-1 | W18 | i18n | **Tradução bilíngue (1-eng-intl + 2-pt-br no MESMO arquivo)** de README, wiki e demais docs user-facing (AGENTS, docs/), via i18n-l10n-specialist: inglês internacional primeiro, pt-br em seguida, no mesmo arquivo. Habilita alcance internacional no marketplace oficial. | Média | AUD-R1, AUD-R3, AUD-R5 | Alta | ✅ Concluído | — |
| AUD-R7 | W19 | Auditoria | **Re-auditoria final pós-remediação** (internal-auditor): rodar N14 (re-higienização PII/wikilinks) + re-testar os achados; virar Estado Auditado para ✓; gate final antes da submissão ao marketplace. | Alta | AUD-R1, AUD-R2, AUD-R3, AUD-R4, AUD-R5, AUD-R6, I18N-1 | Média | ✅ Concluído | ✓ |
| DIST-1 | W20 | Distribuição | Estabelecer GitHub público (`github.com/petrinhu/bigtech_plugin`) para submissão ao marketplace oficial (AUD-D02; resolve AUD-U01). Host legado deixou de ser origem. | Alta | AUD-R7 | Média | ✅ Concluído | — |
| SUB-1 | W21 | Distribuição | Preparar o material de submissão ao marketplace oficial `claude-plugins-community` (via product-marketing-manager + technical-writer): descrição de loja em inglês internacional, keywords/categoria, checklist de prontidão (`validate --strict`, repo público GitHub, LICENSE/SECURITY/README bilíngue), link do repo GitHub e dossiê de revisão para o líder aprovar antes do envio. | Alta | DIST-1, AUD-R7 | Baixa | ✅ Concluído | — |
| N9 | W22 | Distribuição | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; marketplace community = one-way-door externo W22 pós-1.0, não fase BT-0..9. Reabrir só com go/no-go do líder pós-campanha.] Submissão a `claude-plugins-community` (PR); canal canônico GitHub + community (AUD-D01). | Alta | SUB-1, AUD-R7, DIST-1 | Alta | 💡 Decisão tomada | — |
| OS-1 | W23 | OS-Agnóstico | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; dívida de verificação legada jun/2026; núcleo coberto por `bin/python3.cmd` + CI multi-OS BT-4.] Auditoria OS: `hooks.json`/`python3` no Windows. Decisão 2026-06-20: Windows nativo. | Alta | — | Média | 💡 Decisão tomada | — |
| OS-2 | W23 | OS-Agnóstico | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; verificação legada TDD Windows; núcleo globs/separadores + CI multi-OS BT-4.] TDD no Windows: shell/glob/preset php. | Média | OS-1 | Média | 💡 Decisão tomada | — |
| OS-3 | W23 | OS-Agnóstico | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; residual cosmético visual-design-director Linux-only = OE se forçado agora.] Gêmeos macOS/Windows para open/screenshot. | Média | — | Baixa | 💡 Decisão tomada | — |
| OS-4 | W23 | OS-Agnóstico | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; residual cosmético docs portabilidade = OE se forçado agora.] Notas OS em hardware-resource-limits/CONTRACT/TOOLING. | Média | — | Média | 💡 Decisão tomada | — |
| OS-5 | W23 | OS-Agnóstico | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; residual cosmético hooks (ValueError/exit/encoding) = OE se forçado agora.] Robustez cross-OS fail-open. | Baixa | — | Baixa | 💡 Decisão tomada | — |
| TOOL-1 | W24 | Política-Tools | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; doutrina híbrida já decidida 2026-06-20; verification aging legado, não fase BT.] Conflito TOOLING vs TESTES/AUDITORIAS (auto-instalar vs AskUserQuestion). | Alta | — | Média | 💡 Decisão tomada | — |
| TOOL-2 | W24 | Política-Tools | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; `docs/principles/missing-tool-policy.md` já existe; aging de verificação legado.] Promover missing-tool-policy cross-cutting. | Alta | TOOL-1 | Média | 💡 Decisão tomada | — |
| TOOL-3 | W24 | Política-Tools | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; propagação residual agents = verification aging legado.] Propagar missing-tool-policy aos agents. | Média | TOOL-2 | Média | 💡 Decisão tomada | — |
| TOOL-4 | W24 | Política-Tools | [CANCELADO 2026-08-16: legacy/OE — fora da campanha BT-*; alinhamento TOOLING/TESTES residual = OE se forçado agora.] Install OS-aware no TOOLING.md. | Baixa | TOOL-2 | Baixa | 💡 Decisão tomada | — |
| TST-BT-1 | W6 | Testes | Revalidar suite campanha: `preci.sh` + pytest hooks + validate_plugin + smoke + CI multi-OS verde no SHA final (pós BT-5..BT-8; espelha T15/T14 no escopo da campanha). Ver `TESTES.md` § Campanha 2026-08-16. | Alta | BT-5,BT-6,BT-7,BT-8 | Média | ⏳ Pendente | — |
| AUD-BT-1 | W7 | Auditoria | Auditoria de campanha bigtech 2026-08-16: dual-authority, porte solo/headcount, source-of-truth, CI matrix, zero host legado operacional. Consolida no espírito de AUD-REPORT (sem recriar REPORT). Ver `AUDITORIAS.md` § Campanha 2026-08-16. | Alta | TST-BT-1, BT-1, BT-5, BT-6 | Alta | ⏳ Pendente | — |

## Tabela de scoring WSJF (itens-pai funcionais)

`CoD = Valor + Criticidade + Redução de Risco`; `WSJF = CoD / Job Size`. Rank = ordem decrescente de WSJF (justifica a prioridade *dentro* de cada nível topológico). `D1` e `A2` aparecem como item-pai (fatiados em D1a-c / A2a-e na execução; sub-lotes herdam o WSJF do pai).

| ID | Item | Valor | Criticidade | Red. Risco | CoD | Job Size | WSJF | Rank |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| R1 | LICENSE + NOTICE | 13 | 14 | 19 | 46 | 1 | 46.0 | 1 |
| F1 | Estrutura + plugin.json + marketplace.json | 18 | 18 | 20 | 56 | 2 | 28.0 | 2 |
| R3 | CHANGELOG | 8 | 9 | 7 | 24 | 1 | 24.0 | 3 |
| H4 | hooks.json | 13 | 14 | 18 | 45 | 2 | 22.5 | 4 |
| R4 | Publicar (gate; host legado→GitHub canônico) | 17 | 13 | 9 | 39 | 2 | 19.5 | 5 |
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

### Scoring WSJF — pós-1.0 (histórico; N8/N10 ✅; N9 cancelado)

Os itens N1-N7, N8 e N10 já foram entregues. **N9 foi cancelado 2026-08-16 (legacy/OE)** e não pontua na campanha BT-\*. O ranking abaixo é **histórico** da faixa pós-1.0 (não é o backlog ativo).

| ID | Item | CoD (qualitativo) | Job Size | WSJF (relativo) | Rank (histórico) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| N8 | Fechar 0.1.6 (CI + tag + Release) | Alto (fundação imutável; destrava N9/N10) | Baixo (fluxo já automatizado 4x) | **Alto** | 1 ✅ |
| N9 | Marketplace comunitário `claude-plugins-community` | Alto (alcance; gated por go/no-go) | Alto (gargalo externo Anthropic) | **Médio** | 2 💡 cancelado legacy/OE |
| N10 | Releases retroativas 0.1.0 / 0.1.1 | Baixo (cosmético/histórico) | Baixo (mecânica repetida x2) | **Baixo** | 3 ✅ |

> Leitura (histórico): N8 fechou a fundação imutável. N9 era folha one-way-door externa e foi
> **cancelado** para não competir com a campanha BT-\* (fonte-de-verdade/CI/porte). N10 ✅.
> Backlog ativo e WSJF da campanha: IDs **BT-0..BT-9** (plano 2026-08-16).

### Scoring WSJF — campanha BT-* (2026-08-16, `--reorder`)

Régua Fibonacci `(1,2,3,5,8,13,20)`. `CoD = Valor + Criticidade + Red. Risco`; `WSJF = CoD / Job Size`.
Job Size = rótulo `Dificuldade` (early: Baixa=2, Média=5, Alta=8). Rank = WSJF **dentro do nível topológico**
(dependência sempre vence). `BT-9` fica em W5 por julgamento (go/no-go do líder), não por WSJF global.

Níveis topo: L0=`BT-0`; L1=`BT-1,BT-2,BT-3`; L2=`BT-4,BT-5,BT-6`; L3=`BT-7,BT-8,BT-9`.
Onda canônica (CHK-07: pré-req nunca na mesma onda): W1=L0; W2=L1; W3=L2; W4=`BT-7,BT-8`; W5=`BT-9`.

| ID | Item | Nível | Valor | Criticidade | Red. Risco | CoD | Job Size | WSJF | Rank no nível |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BT-0 | PHASE 0 freeze/baseline | L0 | 13 | 13 | 13 | 39 | 5 | 7.80 | 1 |
| BT-3 | GitHub canônico + purge host legado | L1 | 13 | 13 | 13 | 39 | 5 | 7.80 | 1 |
| BT-1 | FABLE ADR source-of-truth vault×plugin | L1 | 20 | 13 | 20 | 53 | 8 | 6.63 | 2 |
| BT-2 | docs/house sync 10 manuais | L1 | 8 | 8 | 8 | 24 | 5 | 4.80 | 3 |
| BT-5 | Eliminar solo/headcount (piso early) | L2 | 13 | 8 | 13 | 34 | 5 | 6.80 | 1 |
| BT-6 | Inventário dual-authority + cutover | L2 | 13 | 8 | 20 | 41 | 8 | 5.13 | 2 |
| BT-4 | CI multi-OS GitHub Actions | L2 | 13 | 8 | 13 | 34 | 8 | 4.25 | 3 |
| BT-9 | Proteção de main + release gates | L3 | 13 | 5 | 13 | 31 | 5 | 6.20 | 1* |
| BT-7 | Drift gate semântico registry | L3 | 8 | 5 | 13 | 26 | 8 | 3.25 | 2 |
| BT-8 | Evals de roteamento `/bigtech` | L3 | 8 | 5 | 8 | 21 | 8 | 2.63 | 3 |

> \* `BT-9` tem o maior WSJF do L3, mas a onda é **W5** (porta do líder no fim), não W4.
> `BT-1` sobe no L1 (fundação / one-way-door de SoT). Itens 🔍 (BT-0/2/3/4) não bloqueiam
> dependentes de *código* da fatia já entregue; Status permanece 🔍.

### Fechamento campanha (add_tests_audit 2026-08-16)

| ID | Item | Nível | Pré-requisito | Onda | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TST-BT-1 | Revalidar suite campanha (preci+CI) | L4 (após impl) | BT-5,BT-6,BT-7,BT-8 | W6 | ⏳ |
| AUD-BT-1 | Auditoria campanha (SoT/porte/CI/host) | L5 (após teste) | TST-BT-1, BT-1, BT-5, BT-6 | W7 | ⏳ |

**Skip catálogo (anti-OE / coberto 1.0):** `TST-T5`≈`TST-DEPS`✅; `TST-T12`≈`TST-DEPS`✅+CI/gitleaks;
`AUD-DISC`/`AUD-ARCH`/`AUD-COV`/`AUD-DEPS`/`AUD-LANG` — sem ⏳ cosmético (escopo campanha em `AUD-BT-1`);
`AUD-SEC`/`AUD-QUALITY`/`AUD-REPORT` já ✅; `W-WIKI` ✅ (CHK-14).

## Decisões one-way-door (go/no-go do líder supremo)

1. **`F1`** — congelar nome (`bigtech`), layout e `source` do marketplace antes de abrir a W2 (contrato público; mudar depois quebra quem já instalou). *(concluído)*
2. **`R4`** — go/no-go da primeira publicação pública (host legado na época; canônico agora GitHub; irreversível; usuários passam a executar os hooks Python na máquina deles). *(concluído)*
3. **`N9`** — go/no-go da submissão ao marketplace comunitário `claude-plugins-community` (3ª porta sem volta se reaberta). **Cancelado 2026-08-16 (legacy/OE)** — fora da campanha BT-\*; reabrir só com go/no-go explícito do líder **depois** da campanha.

## Decisões da auditoria (saída da auditoria de 9 dimensões)

- **AUD-D01 (canal de distribuição): DECIDIDO → GitHub único + community marketplace (ordem líder 2026-08-16 prevalece sobre “AMBOS” legado).** Submeter ao marketplace oficial `claude-plugins-community` (auto-update dinâmico); host de desenvolvimento e distribuição canônico = `github.com/petrinhu/bigtech_plugin`. Host legado (forja anterior + CI legada) **eliminados** do produto (BT-3).
- **AUD-D02 (GitHub canônico): DECIDIDO → GitHub é a origem.** Repo público GitHub para desenvolvimento, CI e submissão ao oficial (item `DIST-1` + BT-3). Resolve AUD-U01.
- **AUD-D03 (glifo de travessão em tabelas): DECIDIDO → MANTER (exceção documentada).** O travessão como valor de célula/estado nas tabelas é símbolo de dado, não prosa; documentar a exceção à regra "zero em-dash". Remediar apenas os 10 em-dash de PROSA real (em AUD-R3/AUD-R5).
- **AUD-D04 (empacotar testes): pendente** — default: manter `hooks/tests/` e `hooks/README-tdd.md` no pacote (úteis para CI/contribuição). Reavaliar se quiser pacote mínimo.
- **AUD-U01: RESOLVIDO por AUD-D02 + ordem 2026-08-16** — o GitHub é o único host canônico e o canal de submissão garantido.

## Notas de cadência (pós-1.0 → campanha BT-*)

- **Campanha ativa = BT-\*** no topo da tabela (ondas W1..W5; plano `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`). Main orquestra-only; ≤2 agents/rodada.
- **N8 ✅, N10 ✅.** **N9, OS-1..5, TOOL-1..4 cancelados 2026-08-16** como legacy/OE (ver seção Cancelamentos).
- **Não há caminho crítico `N8 → N9` aberto.** WIP de manutenção pós-1.0 em N9 encerrou com o cancelamento; não reabrir N9 durante a campanha sem ordem do líder.
- **N10** já concluído (não é mais opcional pendente).

## Cancelamentos 2026-08-16 (legacy / anti-OE)

| ID | Motivo |
| :--- | :--- |
| N9 | Marketplace `claude-plugins-community` (W22 pós-1.0). One-way-door externo; **fora** das fases BT-0..BT-9. Manter vivo = OE de distribuição paralela à campanha de fonte-de-verdade/CI/porte. Reabrir só com go/no-go explícito do líder **depois** da campanha. |
| OS-1..OS-5 | Auditoria OS-agnóstico jun/2026; v0.2.0 já marcou OS-agnosticismo; `bin/python3.cmd`, globs Windows, CI multi-OS (BT-4) cobrem o núcleo. Itens presos em 🔍 = **dívida de verificação legada**, não roadmap da campanha. Residual cosmético (OS-3/4/5 docs) = OE se forçado agora. |
| TOOL-1..TOOL-4 | Auditoria política-tools jun/2026; `docs/principles/missing-tool-policy.md` já existe; doutrina híbrida decidida. Presos em 🔍 = verification aging legado, **não** fase do plano BT. Reabrir só se campanha/auditoria nova exigir. |
