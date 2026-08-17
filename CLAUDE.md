# CLAUDE.md - plugin_bigtech (sessão local)

> Preferências e contexto **deste repositório**. Preferências universais da casa vivem em `~/.claude/CLAUDE.md` / `~/.grok/rules/`.  
> **Não** reescreve o [AGENTS.md](AGENTS.md) (roteiro de instalação do plugin).

## Identidade

| | |
|---|---|
| Produto | Plugin **bigtech** para Claude Code |
| Versão package | **0.2.0** (sem bump semver; `main` = post-0.2.0 até próxima release) |
| Campanha 2026-08-16 | **FECHADA** - tag `campanha/2026-08-16-fechada` |
| Pacote | 51 agents (12 C-level + 39 operacionais), 4 skills, hooks TDD + governança |
| Licença | Apache-2.0 |
| Autor | petrinhu |

**HEAD de fechamento da campanha:** `6a7b212757b92b01328f0aa1e19ad652ae41eaa7` (tag `campanha/2026-08-16-fechada`; AUD-BT-1 APROVADO 96/100).  
**Baseline de release package:** tag `bigtech--v0.2.0` (`61c3ea4…`) - ainda a versão em `plugin.json` / marketplace.  
Se `git rev-parse HEAD` divergir do que você alega, **re-medir** inventários e atualizar memórias/snapshot.

Release GitHub: https://github.com/petrinhu/bigtech_plugin/releases/tag/campanha/2026-08-16-fechada  
Índice de relatórios: [docs/campanha/README.md](docs/campanha/README.md)

## Status pós-campanha

- Campanha de melhoria dual-host Claude+Grok **não está** em “PHASE 0 in progress”.
- Entregas BT-0..BT-9 + TST-BT-1 + AUD-BT-1 fechadas no repo (GitHub-only, CI multi-OS, ADR SoT, porte early, dual-authority inventário/plano, drift gate, evals, branch protection, house manuals).
- **Próximo (opcional, não automático):** canário de cutover de `~/.claude` conforme [docs/campanha/2026-08-16-dual-authority-cutover-plan.md](docs/campanha/2026-08-16-dual-authority-cutover-plan.md) - só com ordem explícita do líder.
- **Não cutover** destrutivo de agents/skills/hooks/settings globais sem canário + autorização no contexto.

## Modo sessão (orquestração)

Quando a main/orquestrador está em modo campanha ou release:

1. **Só** interage com o líder, **despacha ≤2 agents** por rodada e **verifica** entregas.
2. **Não implementa produto** (código, docs de campanha, inventário mecânico, patches) na thread principal.
3. Implementação, inventário e artefatos = **sempre subagent** especialista (papel resolvido no spawn).

Ver também memória de feedback: `feedback_main_orquestrador_only` (Grok project memory / espelho Claude project memory).

## Modelos dual-host (sem hardcode de geração)

**Proibido** gravar slugs de versão de modelo (“4.5”, “4.6”, “Sonnet 4”, “Opus 5”) em prosa operacional. Use **papel relativo** ao catálogo **atual** do host:

| Papel | Claude Code | Grok Build | Uso |
|---|---|---|---|
| Implementação / fatia | **[sonnet][mais recente]** | **[grok][modelo anterior ao mais recente]** | código, testes, docs mecânicas |
| Orquestração / auditoria cotidiana | **[opus][mais recente]** | **[grok][modelo anterior ao mais recente]** | main, C-level planejando, review rotina |
| Teto (gates `FABLE-*`, redesign global) | **[fable][mais recente]** | **[grok][mais recente]** | só gates FABLE ou ordem do líder |

Frontmatter YAML do Claude (`model: opus` / `model: sonnet`) é literal de plataforma - **não** autoriza pin de geração na prosa nem nos briefs dual-host. Resolver o ID concreto só na hora do spawn.

## Runbook da campanha (arquivo histórico)

**Canônico da leva 2026-08-16:** [PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md](PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md)  
PHASE 0 e ondas BT-* estão **fechadas**; o plano permanece como registro, não como “em execução”.

## Pendências

- Tabela local (se existir): `TODO.md` (working file).
- Skill de planeamento: **`tab_pendencias`** (produto standalone).
  - **Grok:** symlink `~/.grok/skills/tab_pendencias` → produto.
  - **Claude:** skill pin/submódulo em `~/.claude/skills/tab_pendencias`.
- Health de referência da campanha tab (não reabrir sem re-medir): 59 ✅, 1 🔄 (N9), 9 🔍 legados OS/TOOL, INBOX 0; wiring **LIGADO_OK** em v1.2.x.

## Manuais e docs

1. **Vault claudebrain** (autoridade da casa, se presente nesta máquina): `CONTRACT.md`, `TESTES.md`, `AUDITORIAS.md`, `AGILE.md`, `DEPLOY_CHECKLIST.md`, `ORG.md`, `TOOLING.md`, `pipeline_release_1.0.md`, `lideranca_pipeline_release.md`, `Standards.md` na raiz do vault.
2. **Cópia no produto:** `docs/house/` (manuais syncados na campanha). Vault prevalece em conflito material; divergência material → classificar e elevar ao líder.
3. Docs do plugin: `docs/`, README, SECURITY, AGENTS.md (install), `docs/campanha/` (relatórios 2026-08-16).

## Proibições (permanentes de produto / cutover)

- **Sem push, merge, tag ou release** sem autorização explícita do líder no contexto (esta fatia de docs foi autorizada no brief).
- **Não cutover** destrutivo de `~/.claude` (agents/skills/hooks/settings) **antes do canário** e ordem do líder.
- **Dual authority / classificação** de diferença vault×plugin: `CORE-GENERIC` | `PERSONAL-OVERLAY` | `STALE` | `INTENTIONAL-EXCLUSION` - nunca apagar diferença só para “ficar igual”.
- Subagents **não** pusham salvo brief que autorize push/tag nesta fatia. Main re-verifica claims; relatório de agent ≠ prova.
- Não editar secrets (`settings.json` com tokens, credentials).

## Host git

- **GitHub único e oficial:** `https://github.com/petrinhu/bigtech_plugin` - `origin` aponta para este host.
- **BT-3 ✅** (`origin` GitHub; `.forgejo` ausente; 0 `codeberg.org` em product paths).
- **BT-4 ✅** (`.github/workflows/ci.yml` multi-OS: ubuntu/windows + debian/fedora/arch + gitleaks).
- **AUD-BT-1 ✅** (W7): `docs/campanha/2026-08-16-aud-bt1-campaign-audit.md` - APROVADO 96/100. Sem cutover de `~/.claude`.
- Snapshots PHASE 0 (`docs/campanha/phase0-metrics-before.json` e baseline md) preservam medição **before** como prova histórica; não são instrução operacional.

## Reopen (claude / grok -c)

Neste cwd:

1. Ler **este** `CLAUDE.md`.
2. Se precisar do histórico da leva: runbook `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` + [docs/campanha/README.md](docs/campanha/README.md).
3. Snapshot:  
   - Grok: `~/.grok/projects/-home-petrus-IDrive-Documentos-projetos-claudebrain-Projects-plugin-bigtech/memory/project_session_atual.md`  
   - Claude (se existir): `~/.claude/projects/-home-petrus-IDrive-Documentos-projetos-claudebrain-Projects-plugin-bigtech/memory/project_session_atual.md`
4. Confirmar `git rev-parse HEAD` e tags `campanha/*` / `bigtech--v0.2.0`.
5. Main em modo orquestrador only quando em execução multi-agent; despachar ≤2 agents; não implementar produto na main.

## Nota (não alterar AGENTS.md por campanha)

`AGENTS.md` permanece o **script de instalação** do plugin para um agente que instala o marketplace. Contexto de **campanha 2026-08-16 (fechada)**, dual-host e regras de orquestração ficam **aqui** e nas memórias de projeto - não no install script.
