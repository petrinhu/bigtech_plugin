# CLAUDE.md — Projeto plugin `bigtech`

Construção de um **plugin Claude Code distribuível** que empacota a organização "bigtech"
(constelação de agents C-level + operacionais, sem jogo nem perícia) com skills de orquestração,
hooks e docs. Destino: `https://codeberg.org/petrinhu/bigtech_plugin.git`. Licença: Apache-2.0.

## Documentos canônicos do projeto

- **Spec (fonte de verdade):** `docs/superpowers/specs/2026-06-13-bigtech-plugin-design.md` — escopo, layout, higienização (política zero-wikilinks-sem-órfãos), despersonalização, acesso a docs em runtime, mapa de rastreabilidade (Apêndice A).
- **Testes:** `TESTES.md`. **Auditorias:** `AUDITORIAS.md`.

## Pendências

A tabela de pendências e planejamento do projeto está em `TODO.md` na raiz (ordenada por execução;
a coluna Onda marca passos paralelizáveis). Caminho crítico: `F1 → H3 → A2 → S1 → TST-ORFAOS → AUD-PRIV → R4`.

## Princípios inegociáveis deste projeto

1. **Produto público:** zero referências locais (`~/.claude`, `/home/petrus`), zero wikilinks `[[ ]]`
   (exceto atributos C++ em código), zero identidade/infra pessoal. Ver §4 do spec + `TST-ORFAOS`.
2. **Execução por agents especialistas** (technical-writer, devops-sre, software-architect, qa-engineer,
   compliance-legal), orquestrados por C-level; nunca higienização inline.
3. **`R4` (publicar) e `F1` (contrato público) são one-way-doors** — go/no-go do líder supremo.
