# Arquitetura e princípios universais

Aplicáveis a **todo projeto novo** e como meta de refatoração para projetos existentes. Desvios devem virar item rastreado na tabela de pendências.

Princípios relacionados: [anti-patterns](anti-patterns.md) · [metodologia ágil](agile-methodology.md). Manuais de engenharia que detalham o fluxo: [CONTRACT](../manuals/CONTRACT.md), [TESTES](../manuals/TESTES.md), [AGILE](../manuals/AGILE.md).

## Arquitetura em 4 camadas

Toda solução, mesmo pequena, separa em quatro camadas com dependência unidirecional (cada camada só depende das de baixo, nunca o inverso):

1. **Front**: interface com usuário/sistema externo. HTML/CSS/JS na web; QML/widgets em apps desktop nativos; flags/argv no CLI. Sem lógica de negócio, sem SQL, sem cripto.
2. **Mid**: orquestração e protocolo. Endpoints REST, controllers, casos de uso, glue. Recebe input, valida, chama back, devolve resposta. Sem regra de domínio embutida.
3. **Back**: domínio + serviços de aplicação. Regras de negócio, repositories, helpers de criptografia/auth/persistência. Não conhece HTTP nem widget; pode ser invocado de CLI, web ou GUI.
4. **Foundation**: infraestrutura. Schema DB + migrations, configs/secrets fora do código-fonte, configuração de servidor web/serviço (`.htaccess`/nginx/systemd), cron, integrações 3rd-party (SMTP, captcha, analytics), build, CI/CD, observabilidade.

Convenções de diretório/nomenclatura devem refletir essa separação (ex.: `assets/` `api/` `lib/` na web; `view/` `controller/` `domain/` `infra/` no backend; `ui/` `app/` `core/` `platform/` em app desktop). Vazamentos cruzados (SQL na view, regra de negócio no controller, cripto na foundation) são dívida (abrir item de auditoria na tabela de pendências).

## SOLID

- **S**ingle Responsibility: cada classe/módulo/função tem **uma** razão para mudar.
- **O**pen/Closed: aberto para extensão, fechado para modificação. Funcionalidade nova vira nova classe/método, não edita o existente.
- **L**iskov Substitution: subtipos honram o contrato do supertipo. Sem `if (x instanceof X)` ramificando comportamento.
- **I**nterface Segregation: interfaces pequenas e específicas. Clientes não dependem de métodos que não usam.
- **D**ependency Inversion: depender de abstrações; injeção de dependência sobre criação direta. Mocks/fakes em teste só funcionam se o código respeita isso.

Violar consciente é permitido **com comentário explicando o porquê**. Violar inconsciente é dívida.

## DRY (Don't Repeat Yourself)

- **Regra de 3**: na terceira ocorrência do mesmo padrão, extrair. Antes disso, aceitar duplicação para não criar abstração prematura (WET, Write Everything Twice, é melhor que abstração errada).
- Distinguir **duplicação real** (mesma razão de mudar) de **coincidência** (parecem similares hoje, divergem amanhã). Não unificar coincidência (vira abstração que não cabe em ninguém).
- Toda refatoração DRY deve nomear explicitamente a "razão de mudança comum", não só a similaridade de código.

## TDD obrigatório (red / green / refactor)

Para todo código de domínio (back) e endpoint (mid):

1. **Red**: escrever o teste **primeiro**, rodá-lo, ver falhar. O teste descreve a regra desejada antes de existir implementação. Sem teste vermelho, não há licença para escrever código de produção.
2. **Green**: código mínimo para o teste passar. Sem elegância, sem otimização. Objetivo exclusivamente: sair do vermelho.
3. **Refactor**: limpar mantendo todos os testes verdes. Renomear, extrair, simplificar. Os testes garantem que nada quebrou.

Ciclo curto (idealmente < 10 min por iteração). **Cobertura não é meta**, mudança guiada por teste é. Bug fix sempre começa por teste que reproduz o bug em vermelho; só então a correção.

Exceções aceitáveis (script ad-hoc descartável, exploração de API externa, protótipo throwaway) devem ser declaradas explicitamente, não viram default.

## Ver também

- Anti-patterns universais a evitar: [anti-patterns](anti-patterns.md).
- Metodologia ágil e decomposição de trabalho: [metodologia ágil](agile-methodology.md).
- Detalhamento do fluxo de engenharia: [CONTRACT](../manuals/CONTRACT.md) · [TESTES](../manuals/TESTES.md) · [AGILE](../manuals/AGILE.md).
