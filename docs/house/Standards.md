<!--
  docs/house sync
  origem: vault claudebrain / Standards.md
  path_vault: /home/petrus/IDrive/Documentos/projetos_claudebrain/Standards.md
  sync_date: 2026-08-16
  regra: se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# Standards & Manuais de Referência

Hub canônico do vault. Os manuais oficiais ficam na **raiz** (este diretório). Cópias estáveis espelhadas em [[Resources/Standards]].

## Manuais Principais (raiz, canônicos)

- [[CONTRACT]] : AI Coder Contract (padrões de código, SOLID, Clean Code, Git, RFC 2119)
- [[TESTES]] : Guia Completo de Testes, Qualidade e Auditoria (T1-T15, A1-A13)
- [[AGILE]] : Metodologia Ágil (Manifesto, Scrum, Kanban, PDCA, INVEST)
- [[DEPLOY_CHECKLIST]] : Checklist 7 fases de deploy irreversível
- [[AUDITORIAS]] : Checklists C++/Python/Web com prioridade 🔴🟠🟢
- [[TOOLING]] : Ferramentas FOSS automatizáveis dos agents (catálogo tool->agent, status temos/baixar, comando de instalar, kit canônico por agent)

## Organização e Pipeline (constelação de agents)

- [[ORG]] : Organização tipo bigtech no Claude (constelação C-level Celso/Capitolino/Caetano/Camilo/Cosmo/Narciso/Cândido/Confúcio/Cícero/Cláudio + Cósimo Chief of Staff, RACI, variantes de pipeline por porte, tabela de pendências)
- [[pipeline_release_1.0]] : Pipeline completo de 12 fases (ideia ao 1.0), com agent e C-level responsável por fase
- [[lideranca_pipeline_release]] : Teoria de liderança C-level e como ela vira a constelação de agents

## Espelhos estáveis

- [[Resources/Standards/CONTRACT]] · [[Resources/Standards/TESTES]] · [[Resources/Standards/AGILE]] · [[Resources/Standards/DEPLOY_CHECKLIST]] · [[Resources/Standards/AUDITORIAS]]

## Como usar com Claude

Sessão nova: o [[CLAUDE]] da raiz já injeta os 5 manuais como obrigatórios. Não precisa repetir no prompt.

## Estrutura PARA (configurada)

- [[Projects]] : 16 projetos ativos (C++/Qt, Python, Web, embedded)
- [[Areas]] : 4 responsabilidades contínuas ([[Areas/clinica]], [[Areas/hardware]], [[Areas/formacao]], [[Areas/financas]])
- [[Resources]] : referência reutilizável ([[Resources/Standards]], [[Resources/Livros]], [[Resources/Snippets]], [[Resources/Prompts]], [[Resources/Datasets]])
- [[Inbox]] : captura rápida pré-triagem (triar semanalmente)
- [[Journal]] : notas datadas ([[Journal/daily]] + [[Journal/eventos]])
- [[Archive]] : projetos / areas / resources encerrados

Cada pasta tem `_README.md` próprio explicando escopo e padrão de notas.