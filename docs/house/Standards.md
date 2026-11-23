<!--
  docs/house sync
  origem: vault claudebrain / Standards.md
  sync_date: 2026-11-23
  hmac_vault_sha256: 6d73c4c246498ae8027a59166408393f0a42d3fe00bba40b5a6d0ec59af25eaf
  transformacoes: T1=1 T2=0 T3a=0 T3=0 T4=0 T5=0
  regra: As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário. Se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# Standards & Manuais de Referência

Hub canônico do vault. Os manuais oficiais ficam na **raiz** (este diretório). Cópias estáveis espelhadas em [[Resources/Standards]].

## Manuais Principais (raiz, canônicos)

- [[CONTRACT]] : AI Coder Contract (padrões de código, SOLID, Clean Code, Git, RFC 2119)
- [[TESTES]] : Guia Completo de Testes, Qualidade e Auditoria (T1-T15, A1-A13)
- [[AGILE]] : Metodologia Ágil (Manifesto, Scrum, Kanban, PDCA, INVEST)
- [[DEPLOY_CHECKLIST]] : Checklist 7 fases de deploy irreversível, só para login, permissão, token, segredo, apagar dado, schema de banco e rotação de chave
- [[AUDITORIAS]] : Checklists C++/Python/Web com prioridade CRÍTICO, IMPORTANTE ou COSMÉTICO
- [[TOOLING]] : Ferramentas FOSS automatizáveis dos agents (catálogo tool->agent, status temos/baixar, comando de instalar, kit canônico por agent)

## Organização e Pipeline (constelação de agents)

- [[ORG]] : Organização tipo bigtech no Claude (constelação C-level Celso/Capitolino/Caetano/Camilo/Cosmo/Narciso/Cândido/Confúcio/Cícero/Cláudio + Cósimo Chief of Staff, RACI, variantes de pipeline por porte, tabela de pendências)
- [[pipeline_release_1.0]] : Pipeline completo de 12 fases (ideia ao 1.0), com agent e C-level responsável por fase
- [[lideranca_pipeline_release]] : Teoria de liderança C-level e como ela vira a constelação de agents

## Espelhos estáveis

- [[Resources/Standards/CONTRACT]] · [[Resources/Standards/TESTES]] · [[Resources/Standards/AGILE]] · [[Resources/Standards/DEPLOY_CHECKLIST]] · [[Resources/Standards/AUDITORIAS]]

## Como usar com Claude

Sessão nova: o [[CLAUDE]] da raiz já injeta os 5 manuais como obrigatórios. Não precisa repetir no prompt. Pausa e retomada de agente: [[CONTRACT]] 10.7.

## Estrutura PARA (configurada)

- [[Projects]] : 16 projetos ativos (C++/Qt, Python, Web, embedded)
- [[Resources]] : referência reutilizável ([[Resources/Standards]], [[Resources/Livros]], [[Resources/Snippets]], [[Resources/Prompts]], [[Resources/Datasets]])
- [[Inbox]] : captura rápida pré-triagem (triar semanalmente)
- [[Journal]] : notas datadas ([[Journal/daily]] + [[Journal/eventos]])
- [[Archive]] : projetos / areas / resources encerrados

Cada pasta tem `_README.md` próprio explicando escopo e padrão de notas.