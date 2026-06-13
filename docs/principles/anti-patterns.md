# Anti-patterns universais

Práticas a recusar em **todo projeto**. Valem para qualquer agent da constelação e para o operador.

Princípios relacionados: [arquitetura e princípios](arquitetura-principios.md) · [metodologia ágil](agile-methodology.md). O fluxo de commits e o gate de qualidade estão em [CONTRACT](../manuals/CONTRACT.md).

## Git e versionamento

- `--no-verify` em commits sem pedido explícito. Os hooks de pre-commit/pre-push existem por um motivo; pular o gate esconde regressões.
- `git push --force` em `main`/`master` (recusar a menos que autorizado). Reescrever histórico publicado quebra o clone de todo mundo.
- `git commit --amend` de commits já publicados (sempre criar um novo commit). Amend só é seguro enquanto o commit não saiu da máquina local.

## Texto e estilo

- **em-dash (codepoint U+2014) e en-dash (codepoint U+2013) em texto que o usuário final lê renderizado**. É marca de IA generativa que ninguém escreve à mão em texto técnico, e faz o material parecer "vibe-coded". Substituir por: vírgula em pausas curtas, ponto-e-vírgula entre cláusulas independentes, dois-pontos antes de explicação, parênteses para apartes, hífen simples (caractere ASCII `0x2D`) para compostos e ranges. Aplica-se a conteúdo **user-facing** (HTML publicado, `README.md`, `CHANGELOG.md`, páginas de site/landing, material de marketing). Conteúdo **interno** (código, comentários, configs, arquivos de planejamento e notas, scripts, testes, dependências de terceiros) não exige a regra de forma automática; revisão manual cobre. Quem mantém um hook de bloqueio local pode automatizá-la, mas a regra estilística vale mesmo sem hook.
- Emojis em código ou documentação técnica só com pedido explícito do usuário.

## Escopo e arquivos

- Criar arquivos `.md` de planejamento/análise intermediária **não solicitados**. Notas de trabalho efêmeras poluem o repo; o planejamento canônico vive no `TODO.md` (ver [metodologia ágil](agile-methodology.md)).
- Apagar pastas convencionalmente reservadas a material de referência (`exemplos/`, `examples/`, `references/`, `docs/externos/` ou similares) sem confirmação. Esse material costuma ser preservado de propósito.
- Adicionar dependências, refatorar além do pedido, ou introduzir abstrações "para o futuro" em tarefas cirúrgicas. YAGNI: a tarefa pequena resolve só o que foi pedido.

## Fonte de verdade externa ao projeto

- **Modificar QUALQUER arquivo canônico fora do diretório do projeto**, independentemente de extensão ou tipo (imagem, PDF, DOCX, MD, TXT, LOG, JSON, YAML, SQL, prompt, dataset, fixture, exemplo, manual, modelo, qualquer asset de referência). Arquivos mantidos fora do repo do projeto e usados como **fonte de verdade** (exemplo, manual, prompt, log de referência, material consultivo) são intocáveis e servem de fallback caso a cópia interna do projeto seja corrompida. **Não classificar por tipo de arquivo:** a regra cobre tudo que esteja fora da raiz do projeto e seja usado como referência.

  Procedimento correto:
  1. copiar o arquivo para a pasta padronizada do projeto (`assets/img/`, `assets/templates/`, `references/local/`, `prompts/`, `examples/`, ou similar conforme a convenção do repo);
  2. modificar **apenas** a cópia interna;
  3. bumpar cache buster ou versão se for asset publicado.

  **Antes de tocar qualquer arquivo de referência externo ao projeto, SEMPRE pedir permissão explícita ao usuário e avisar do risco** ("se modificarmos esse arquivo, deixamos de ter cópia íntegra para restaurar; tem certeza?"). Cobre QUALQUER tipo de arquivo, sem exceções por extensão.

## Ver também

- Arquitetura, SOLID, DRY e TDD: [arquitetura e princípios](arquitetura-principios.md).
- Metodologia ágil e backlog em `TODO.md`: [metodologia ágil](agile-methodology.md).
- Fluxo de commits e gate de qualidade: [CONTRACT](../manuals/CONTRACT.md).
