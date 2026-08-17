# Campanha 2026-08-16 - índice

Melhoria dual-host **Claude Code + Grok Build** do plugin `bigtech`.  
**Status: FECHADA.**

| | |
|---|---|
| Tag de marco | [`campanha/2026-08-16-fechada`](https://github.com/petrinhu/bigtech_plugin/releases/tag/campanha/2026-08-16-fechada) |
| Release GitHub | https://github.com/petrinhu/bigtech_plugin/releases/tag/campanha/2026-08-16-fechada |
| HEAD de fechamento (AUD-BT-1) | `6a7b212` |
| Versão package | **0.2.0** (sem bump; trabalho em `main` = post-0.2.0) |
| Cutover `~/.claude` | **não** executado; plano de canário opcional abaixo |

Runbook histórico da leva: [PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md](../../PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md) (raiz do repo).

## O que entrou

- Host **só GitHub** (sem Forgejo/Codeberg operacional)
- CI multi-OS (ubuntu/windows + debian/fedora/arch + gitleaks)
- ADR de fonte da verdade (SoT)
- Porte canônico `early | scale | bigtech` (alias `solo` → `early`)
- Inventário dual-authority + plano de cutover (canário futuro)
- Gate de drift semântico registry/agents/skills
- Evals offline de roteamento `/bigtech`
- Branch protection em `main`
- Sync dos manuais da casa em `docs/house/`
- TST-BT-1 PASS + AUD-BT-1 APROVADO (96/100)

## PHASE 0

| Artefato | Descrição |
|---|---|
| [2026-08-16-phase0-baseline.md](2026-08-16-phase0-baseline.md) | Baseline / freeze |
| [2026-08-16-phase0-house-plan.md](2026-08-16-phase0-house-plan.md) | Plano de sync house |
| [2026-08-16-phase0-todo-intake.md](2026-08-16-phase0-todo-intake.md) | Intake BT-* no TODO |
| [phase0-metrics-before.json](phase0-metrics-before.json) | Métricas before |
| [phase0-metrics-after-bt3.json](phase0-metrics-after-bt3.json) | Métricas after BT-3 |
| [phase0-agents-inventory.csv](phase0-agents-inventory.csv) | Inventário de agents |

## Itens BT-* (verificação)

| Item | Relatório |
|---|---|
| BT-0 PHASE 0 | [2026-08-16-w1-bt0-verification.md](2026-08-16-w1-bt0-verification.md) |
| BT-1 ADR SoT | (ADR no repo; sanitize em histórico git) |
| BT-2 house manuals | [2026-08-16-w2-bt2-verification.md](2026-08-16-w2-bt2-verification.md) |
| BT-3 GitHub-only | [2026-08-16-w2-bt3-verification.md](2026-08-16-w2-bt3-verification.md) |
| BT-4 CI multi-OS | [2026-08-16-bt4-ci-multi-os.md](2026-08-16-bt4-ci-multi-os.md) · [2026-08-16-w3-bt4-verification.md](2026-08-16-w3-bt4-verification.md) |
| BT-5 porte early | [2026-08-16-verify-bt5.md](2026-08-16-verify-bt5.md) |
| BT-6 dual-authority | [2026-08-16-dual-authority-inventory.md](2026-08-16-dual-authority-inventory.md) · [2026-08-16-dual-authority-inventory.csv](2026-08-16-dual-authority-inventory.csv) · [2026-08-16-dual-authority-cutover-plan.md](2026-08-16-dual-authority-cutover-plan.md) · [2026-08-16-verify-bt6.md](2026-08-16-verify-bt6.md) |
| BT-7 drift gate | [2026-08-16-verify-bt7.md](2026-08-16-verify-bt7.md) |
| BT-8 routing evals | [2026-08-16-verify-bt8.md](2026-08-16-verify-bt8.md) |
| BT-9 branch protection | [2026-08-16-w5-bt9-branch-protection.md](2026-08-16-w5-bt9-branch-protection.md) |

## Teste e auditoria de campanha

| Item | Relatório | Resultado |
|---|---|---|
| TST-BT-1 | [2026-08-16-tst-bt1-revalidation.md](2026-08-16-tst-bt1-revalidation.md) | PASS |
| AUD-BT-1 | [2026-08-16-aud-bt1-campaign-audit.md](2026-08-16-aud-bt1-campaign-audit.md) | APROVADO 96/100 |

## Outros

| Artefato | Descrição |
|---|---|
| [2026-08-16-cancel-legacy-open.md](2026-08-16-cancel-legacy-open.md) | Cancelamento de itens legados OS/TOOL abertos |

## Próximo (opcional)

Canário de cutover de `~/.claude` segundo o [plano dual-authority](2026-08-16-dual-authority-cutover-plan.md) - **somente** com autorização explícita do líder. Não faz parte do fechamento da campanha.
