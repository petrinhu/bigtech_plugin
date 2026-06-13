# Auditorias do Projeto — Plugin `bigtech`

> Auditorias aplicáveis a este projeto (stack: Python + Markdown + JSON; produto distribuível público).
> Cada uma é um item `AUD-*` no `TODO.md`, nas ondas finais (downstream de código + teste).
> Podadas as não-aplicáveis (AUD-DB sem SQL, AUD-API sem rede, AUD-UI sem UI, AUD-FRAMEWORK sem framework).
> Severidade dos achados: 🔴 crítico · 🟡 importante · ⚪ cosmético. Nenhum 🔴 fica sem plano de remediação.

## AUD-SEC — Segurança
Os hooks Python executam na máquina de quem instala (SessionStart / PreToolUse / UserPromptSubmit) — superfície de risco real.
- Sem `exec`/`eval`/`os.system` inseguro, sem path traversal, sem injeção.
- **Silent-fail garantido** (hook nunca bloqueia o turno; `exit 0` em erro).
- Sem secrets/tokens embarcados. Entrada não-confiável tratada.

## AUD-PRIV — Privacidade / Despersonalização **(gate de publicação)**
Confirma que **nenhum dado pessoal** sobrevive ao empacotamento:
- Sem nome do autor como soberano, e-mail, títulos pessoais; conceito de "líder supremo/CEO" transferido ao usuário (ORG §0 / §4.2 do spec).
- Sem infra pessoal (Hostinger, instâncias Forgejo/Codeberg pessoais, MCPs/tokens).
- Sem specs da máquina (no `hardware-resource-limits.md` generalizado).
- Confirma o resultado do `TST-ORFAOS` na dimensão semântica (o que o grep não pega).

## AUD-LICENSE — Licença e Atribuição
- `LICENSE` Apache-2.0 íntegra + `NOTICE` quando aplicável.
- Atribuições de terceiros e da origem dos docs/skills compatíveis com Apache-2.0.
- `plugin.json` declara `license` coerente.

## AUD-QUALITY — Qualidade e Consistência
- Sem god-doc/agent inchado; descrições e `description:` (frontmatter) coerentes.
- Referências cruzadas íntegras (toda a constelação reflete os 50 incluídos).
- Terminologia única (ex.: "líder supremo/CEO") sem divergência entre ORG §0, README e skills.

## AUD-REPORT — Relatório Final Consolidado
Consolida AUD-SEC + AUD-PRIV + AUD-LICENSE + AUD-QUALITY num relatório: score 0–100, sumário de achados por severidade, e plano de remediação. **Pré-requisito do gate `R4`** (publicação).
