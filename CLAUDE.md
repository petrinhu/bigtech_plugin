# CLAUDE.md — plugin_bigtech (sessão local)

> Preferências e contexto **deste repositório**. Preferências universais da casa vivem em `~/.claude/CLAUDE.md` / `~/.grok/rules/`.  
> **Não** reescreve o [AGENTS.md](AGENTS.md) (roteiro de instalação do plugin).

## Identidade

| | |
|---|---|
| Produto | Plugin **bigtech** para Claude Code |
| Versão baseline | **0.2.0** |
| Campanha | melhoria dual-host Claude+Grok — **2026-08-16** (PHASE 0+) |
| Pacote | 51 agents (12 C-level + 39 operacionais), 4 skills, hooks TDD + governança |
| Licença | Apache-2.0 |
| Autor | petrinhu |

**Baseline HEAD local conhecido:** `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` (tag `bigtech--v0.2.0`).  
Se `git rev-parse HEAD` divergir, **re-medir** inventários e atualizar memórias/snapshot antes de alegar baseline.

## Modo sessão de EXECUÇÃO (campanha)

Nesta campanha, a **main/orquestrador**:

1. **Só** interage com o líder, **despacha ≤2 agents** por rodada e **verifica** entregas.
2. **Não implementa produto** (código, docs de campanha, inventário mecânico, patches).
3. Implementação, inventário e artefatos = **sempre subagent** especialista (papel resolvido no spawn).

Ver também memória de feedback: `feedback_main_orquestrador_only` (Grok project memory / espelho Claude project memory).

## Modelos dual-host (sem hardcode de geração)

**Proibido** gravar slugs de versão de modelo (“4.5”, “4.6”, “Sonnet 4”, “Opus 5”) em prosa operacional. Use **papel relativo** ao catálogo **atual** do host:

| Papel | Claude Code | Grok Build | Uso |
|---|---|---|---|
| Implementação / fatia | **[sonnet][mais recente]** | **[grok][modelo anterior ao mais recente]** | código, testes, docs mecânicas |
| Orquestração / auditoria cotidiana | **[opus][mais recente]** | **[grok][modelo anterior ao mais recente]** | main, C-level planejando, review rotina |
| Teto (gates `FABLE-*`, redesign global) | **[fable][mais recente]** | **[grok][mais recente]** | só gates FABLE ou ordem do líder |

Frontmatter YAML do Claude (`model: opus` / `model: sonnet`) é literal de plataforma — **não** autoriza pin de geração na prosa nem nos briefs dual-host. Resolver o ID concreto só na hora do spawn.

## Runbook da campanha

**Canônico desta leva:** [PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md](PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md)

PHASE 0 DoD (freeze + baseline): SHA dos três repos relevantes; inventário exato de agents/skills/hooks; distribuição de modelos medida; nenhum arquivo vivo removido.

## Pendências

- Tabela local (se existir): `TODO.md` (working file; pode estar gitignored).
- Skill de planeamento: **`tab_pendencias`** (produto standalone).
  - **Grok:** symlink `~/.grok/skills/tab_pendencias` → produto.
  - **Claude:** skill pin/submódulo em `~/.claude/skills/tab_pendencias`.
- Health de referência da campanha tab (não reabrir sem re-medir): 59 ✅, 1 🔄 (N9), 9 🔍 legados OS/TOOL, INBOX 0; wiring **LIGADO_OK** em v1.2.x.

## Manuais e docs

1. **Vault claudebrain** (autoridade da casa, se presente nesta máquina): `CONTRACT.md`, `TESTES.md`, `AUDITORIAS.md`, `AGILE.md`, `DEPLOY_CHECKLIST.md`, `ORG.md`, `TOOLING.md`, `pipeline_release_1.0.md`, `lideranca_pipeline_release.md`, `Standards.md` na raiz do vault.
2. **Cópia no produto** para quem não tem vault: eventual `docs/house/` ou `docs/canon/` (inventário + sync na PHASE 0/docs). Vault prevalece em conflito material; divergência material → classificar e elevar ao líder.
3. Docs do plugin: `docs/`, README, SECURITY, AGENTS.md (install).

## Proibições (campanha)

- **Sem push, merge, tag ou release** sem autorização explícita do líder no contexto.
- **Não cutover** destrutivo de `~/.claude` (agents/skills/hooks/settings) **antes do canário** do plano.
- **Dual authority / classificação** de diferença vault×plugin: `CORE-GENERIC` | `PERSONAL-OVERLAY` | `STALE` | `INTENTIONAL-EXCLUSION` — nunca apagar diferença só para “ficar igual”.
- Subagents **não** pusham. Main re-verifica claims (build/diff/medição); relatório de agent ≠ prova.
- Não editar secrets (`settings.json` com tokens, credentials).

## Host git

- **GitHub único e oficial:** `https://github.com/petrinhu/bigtech_plugin` — `origin` aponta para este host.
- **BT-3 ✅** (`origin` GitHub; `.forgejo` ausente; 0 `codeberg.org` em product paths).
- **BT-4 ✅** (`.github/workflows/ci.yml` multi-OS: ubuntu/windows + debian/fedora/arch + gitleaks; CI #15 verde no SHA `914eb27`).
- **AUD-BT-1 ✅** (W7): `docs/campanha/2026-08-16-aud-bt1-campaign-audit.md` — APROVADO 96/100. Sem cutover de `~/.claude`.
- Snapshots PHASE 0 (`docs/campanha/phase0-metrics-before.json` e baseline md) preservam medição **before** como prova histórica; não são instrução operacional.

## Reopen (claude / grok -c)

Neste cwd:

1. Ler **este** `CLAUDE.md`.
2. Ler o runbook `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`.
3. Snapshot:  
   - Grok: `~/.grok/projects/-home-petrus-IDrive-Documentos-projetos-claudebrain-Projects-plugin-bigtech/memory/project_session_atual.md`  
   - Claude (se existir): `~/.claude/projects/-home-petrus-IDrive-Documentos-projetos-claudebrain-Projects-plugin-bigtech/memory/project_session_atual.md`
4. Confirmar `git rev-parse HEAD` vs baseline `61c3ea4…`.
5. Main em modo orquestrador only; despachar ≤2 agents; não implementar produto na main.

## Nota de campanha (não alterar AGENTS.md)

`AGENTS.md` permanece o **script de instalação** do plugin para um agente que instala o marketplace. Contexto de **execução da campanha 2026-08-16**, dual-host e regras de orquestração ficam **aqui** e nas memórias de projeto — não no install script.
