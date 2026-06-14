# Catálogo de Testes e Auditorias (embutido)

> Catálogo GENÉRICO usado pela skill tab_pendencias para injetar itens de teste e
> auditoria na tabela. Derivado de guias de teste/auditoria multi-stack. NÃO contém
> nada específico de um sistema pessoal. Quando o projeto tem ./TESTES.md ou
> ./AUDITORIAS.md próprios, eles têm precedência; este catálogo é a base/fallback e
> a fonte dos manuais que a skill cria quando faltam.

> **Política - ferramenta ausente (agnóstica de SO; vale para todo `TST-*` e `AUD-*` deste
> catálogo).** Ao executar um item cuja ferramenta requerida não está instalada, o agente NÃO
> falha em silêncio, NÃO pula o item sem avisar e NÃO instala nada sem consentimento. Em vez
> disso: (1) detecta a ausência de forma adequada ao SO (`command -v <ferramenta>` no Unix/WSL;
> `Get-Command <ferramenta>` ou `where <ferramenta>` no Windows); (2) OFERECE instalar, via
> AskUserQuestion, mostrando o comando de instalação adequado ao SO e ao gerenciador disponível
> (`apt`/`dnf`/`brew`/`winget`/`choco`/`scoop`), preferindo gerenciadores cross-platform
> (`pip`/`uv`, `cargo`, `npm`) quando a ferramenta os suporta, a partir da coluna Ferramentas da
> linha ou de T15.0 para pré-CI; (3) com a confirmação do usuário, instala e então roda o item;
> (4) sem confirmação, NÃO roda: registra o item como pendente na tabela, com nota visível do que
> faltou e o comando de instalação, para retomar depois. Nunca silencioso. Pré-requisitos básicos
> do ambiente (ex.: Python/pytest) seguem o T15.0.

## Detecção de stack

> Sinais marcados "(conteúdo)" são detectados lendo deps/imports dos arquivos (Grep/Read), não apenas por nome de arquivo na raiz.

Por arquivos na raiz (via Glob):

| Stack | Sinais |
|---|---|
| C/C++/Qt | `CMakeLists.txt`, `*.cpp`, `*.h`, `*.hpp`, `*.pro` |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt`, `*.py` |
| Rust | `Cargo.toml` |
| Node/TS | `package.json`, `tsconfig.json`, `*.ts`, `*.js` |
| Web/PHP | `*.php`, `composer.json`, `public_html/`, `index.html` |

Características (habilitam tipos condicionais):

| Característica | Sinais | Habilita |
|---|---|---|
| DB SQL | `*.sql`, `migrations/`, libs sqlite/mysql/psycopg/PDO | T10, AUD-DB |
| Rede/API | deps/imports de framework HTTP (flask, fastapi, django, express, actix-web, gin, spring) ou uso de http.server/socket listen (conteúdo) | T6, T9, AUD-API |
| Protocolo de rede custom | sockets raw (socket/bind/recv) com protocolo não-HTTP próprio (conteúdo) | T11 |
| Binário compilado | C/C++/Rust | T3, T4, T7 |
| UI | QML, widgets, HTML, componentes front | AUD-UI |
| Framework de app/UI | Qt (find_package(Qt), *.pro, *.ui, *.qml) ou framework nas deps (django/flask/fastapi/react/vue/angular/express/spring) (conteúdo) | AUD-FRAMEWORK |

## Testes (T1-T15)

`Aplica`: `sempre` | condição (característica). T1 é SEMPRE EXCLUÍDO (coberto pelo
hook de TDD; nunca vira item na tabela).

| ID | Tipo | Objetivo (1 linha) | Aplica | Ferramentas típicas |
|---|---|---|---|---|
| (T1) | Testes Unitários | módulo isolado conforme spec | EXCLUÍDO (hook TDD) | QtTest, gtest, pytest, vitest, cargo test |
| TST-T2 | Análise Estática | bugs/má prática sem executar | sempre | cppcheck+clang-tidy, ruff+mypy, eslint+tsc, clippy, phpstan |
| TST-T3 | Fuzzing de Inputs | parsing de input não-confiável | binário compilado | libFuzzer/AFL, atheris |
| TST-T4 | Análise Dinâmica de Memória | leaks/UB em runtime | binário compilado | ASan + UBSan |
| TST-T5 | Scanning de Dependências | deps vulneráveis/desatualizadas | sempre | trivy/grype, pip-audit, npm audit, cargo audit, composer audit |
| TST-T6 | Teste de APIs | contratos de endpoints | rede/API | schemathesis, postman/newman, REST client |
| TST-T7 | Scanning de Binário | flags de hardening do binário | binário compilado | checksec, hardening-check |
| TST-T8 | Verificação de Secrets | credencial commitada | sempre | gitleaks, trufflehog |
| TST-T9 | Teste de Rede | comportamento de rede | rede/API | nmap, ferramentas de socket |
| TST-T10 | SQL Injection | queries seguras | DB SQL | sqlmap + revisão de prepared statements |
| TST-T11 | Fuzzing de Protocolos | protocolo de rede custom | rede com protocolo próprio | boofuzz |
| TST-T12 | Busca de CVEs | CVE nas deps | sempre | trivy, grype, OSV/NVD |
| TST-T14 | Integração (fim-a-fim) | sistema integrado contra fontes de verdade | sempre (quase) | harness de integração por stack |
| TST-T15 | Pré-CI (espelhar CI local) | rodar a suíte do CI antes do push | sempre | scripts/preci.sh por stack |

## Auditorias (consolidadas)

Funde os blocos de auditoria genéricos (A1-A10) com os temas por stack, deduplicando
por tema. ID semântico e estável. `Aplica` igual ao das tabelas de teste.

| ID | Tema | Objetivo (1 linha) | Aplica | Ferramentas |
|---|---|---|---|---|
| AUD-DISC | Descoberta e Modelagem | mapear superfície, ativos, modelo de ameaça | sempre | OWASP Threat Dragon, diagramas C4/DFD, revisão manual de superfície e ativos |
| AUD-ARCH | Arquitetura e Camadas | 4 camadas, SOLID, DRY, sem violação de dependência | sempre | import-linter (Py), dependency-cruiser (JS/TS), ArchUnit (JVM), deptrac (PHP), clang-tidy (C++), revisão de camadas |
| AUD-SEC | Segurança | memory safety, secrets, SQLi, binário, LGPD/privacidade | sempre | SAST (semgrep, CodeQL, bandit, cppcheck), gitleaks/trufflehog (secrets), trivy/grype (CVE), OWASP ZAP (DAST) |
| AUD-DB | Banco de Dados | schema, queries, EXPLAIN, migrations, índices, LGPD | DB SQL | EXPLAIN / EXPLAIN ANALYZE, sqlfluff (lint SQL), revisão de migrations e índices, sqlmap (SQLi) |
| AUD-API | API e Contratos | verbos REST, status codes, auth, OpenAPI | rede/API | OpenAPI/Swagger validator, Spectral (lint OpenAPI), schemathesis, Postman/newman |
| AUD-UI | UI/UX e Acessibilidade | contraste, navegação por teclado, WCAG | UI | axe-core, Lighthouse, pa11y, WAVE, WebAIM contrast; em Qt: revisão manual de acessibilidade |
| AUD-QUALITY | Qualidade de Código | god classes, complexidade, dead code, duplicação | sempre | linters (clang-tidy, ruff, eslint, clippy, phpstan), complexidade (lizard, radon), dead code (vulture, ts-prune), SonarQube |
| AUD-COV | Cobertura de Testes | cobertura significativa nos módulos críticos | sempre | lcov/gcov, llvm-cov (C/C++); coverage.py / pytest-cov (Python); c8 / nyc / vitest --coverage (Node/TS); cargo-tarpaulin / llvm-cov (Rust); coverlet (.NET); phpunit --coverage com Xdebug/PCOV (PHP) |
| AUD-DEPS | Dependências e Acoplamento | grafo de deps, acoplamento, ciclos | sempre | dependency-cruiser (JS/TS), pydeps / import-linter (Py), cargo-tree (Rust), deptrac (PHP), license-checker; revisão do grafo de deps |
| AUD-LANG | Idiomas Modernos da Linguagem | tipos/concorrência/idioms do stack | sempre (Baixa) | clang-tidy (modernize, cppcoreguidelines) (C++), pyupgrade + mypy (Py), clippy (Rust), tsc strict + eslint (TS); revisão de idioms |
| AUD-FRAMEWORK | Framework Específico | padrões do framework (ex.: Qt signals/slots, model/view, i18n) | framework de app/UI | clazy (Qt), django checks / django-stubs (Django), eslint-plugin-react / -vue (React/Vue); revisão de padrões do framework |
| AUD-REPORT | Relatório Final de Auditoria | score 0-100, sumário de problemas, patches | sempre (consolida) | consolidação manual + gerador de relatório (markdown/HTML); agrega os achados das auditorias anteriores |

## Criação dos manuais do projeto (poda por stack)

Quando `./TESTES.md` ou `./AUDITORIAS.md` faltam na raiz do projeto e o usuário
confirma acrescentar, a skill os CRIA a partir dos templates abaixo, removendo as
linhas cujo `Aplica` não casa o stack/características detectados. NUNCA sobrescreve
um manual existente.

### Template ./TESTES.md

```markdown
# Testes do Projeto

> Tipos de teste aplicáveis a este projeto (stack: {STACK}). T1 unitário fica sob o
> hook de TDD, não listado aqui. Cada tipo vira um item TST-* na tabela de pendências.
> Política - ferramenta ausente (agnóstica de SO): ao rodar um TST-* cuja ferramenta falta, NÃO
> falhar em silêncio nem instalar sozinho: detectar conforme o SO (`command -v` no Unix/WSL;
> `Get-Command` ou `where` no Windows), OFERECER instalar via AskUserQuestion com o comando
> adequado ao SO e ao gerenciador disponível (apt/dnf/brew/winget/choco/scoop), preferindo
> gerenciadores cross-platform (pip/uv, cargo, npm) quando a ferramenta os suporta e, sem
> confirmação, deixar o item pendente com nota.

<<linhas de TST-* aplicáveis, no formato: "## TST-T<n> <Tipo>\n<objetivo>\n**Ferramentas:** ...">>
```

### Template ./AUDITORIAS.md

```markdown
# Auditorias do Projeto

> Auditorias aplicáveis a este projeto (stack: {STACK}). Cada uma vira um item AUD-*
> na tabela de pendências, nas ondas finais (downstream de código+teste).
> Política - ferramenta ausente (agnóstica de SO): ao rodar um AUD-* cuja ferramenta falta, NÃO
> falhar em silêncio nem instalar sozinho: detectar conforme o SO (`command -v` no Unix/WSL;
> `Get-Command` ou `where` no Windows), OFERECER instalar via AskUserQuestion com o comando
> adequado ao SO e ao gerenciador disponível (apt/dnf/brew/winget/choco/scoop), preferindo
> gerenciadores cross-platform (pip/uv, cargo, npm) quando a ferramenta os suporta e, sem
> confirmação, deixar o item pendente com nota.

<<linhas de AUD-* aplicáveis, no formato: "## AUD-<ID> <Tema>\n<objetivo>\n**Ferramentas:** ...">>
```

A poda usa a coluna `Aplica` das tabelas acima contra a detecção de stack/características.
