# Desenvolvimento — Projeto plugin `bigtech`

> Doc de contexto para quem **desenvolve/contribui** com este repositório (não é carregado como
> contexto de plugin nem distribuído como instrução de uso). Para usar o plugin, veja o `README.md`.

Construção de um **plugin Claude Code distribuível** que empacota a organização "bigtech"
(constelação de agents C-level + operacionais, sem jogo nem perícia) com skills de orquestração,
hooks e docs. Destino: `https://codeberg.org/petrinhu/bigtech_plugin.git`. Licença: Apache-2.0.

## Artefatos de construção (locais, não versionados)

O planejamento e o processo deste projeto vivem em artefatos **locais**, mantidos fora do pacote
distribuível via `.gitignore` (não vão para o repo público nem são carregados pelo plugin):

- **Spec de design** (escopo, layout, higienização zero-wikilinks-sem-órfãos, despersonalização,
  acesso a docs em runtime, mapa de rastreabilidade).
- **Tabela de pendências** (`TODO.md`, ordenada por execução; a coluna Onda marca passos paralelizáveis).
- **Manuais de teste/auditoria do próprio projeto** (`TESTES.md`, `AUDITORIAS.md` na raiz) e o relatório
  de auditoria. Não confundir com os manuais de governança que **acompanham** o plugin em `docs/manuals/`.

Eles guiam a construção, mas, por conterem material de processo (e, no caso da spec/template/relatório,
até nome do autor e wikilinks de exemplo), ficam restritos à cópia de trabalho local.

## Princípios inegociáveis deste projeto

1. **Produto público:** zero referências locais (config local do Claude Code, paths absolutos da máquina), zero wikilinks `[[ ]]`
   (exceto atributos C++ em código), zero identidade/infra pessoal. Ver §4 do spec + `TST-ORFAOS`.
2. **Execução por agents especialistas** (technical-writer, devops-sre, software-architect, qa-engineer,
   compliance-legal), orquestrados por C-level; nunca higienização inline.
3. **`R4` (publicar) e `F1` (contrato público) são one-way-doors** — go/no-go do líder supremo.
