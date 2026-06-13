# Hook de TDD (guard + runner)

Enforcement deterministico do ciclo red/green/refactor, **opt-in por projeto**.
Faz parte do plugin **bigtech**; o registro dos eventos esta em `hooks/hooks.json`.

- **Tipo:** How-to / Reference
- **Audiencia:** desenvolvedores que usam Claude Code e querem disciplina de TDD automatizada

---

## Como ativar num projeto

Crie o arquivo `.claude/tdd-guard.json` na **raiz do projeto** (o mesmo nivel onde fica a pasta `.git`):

```json
{
  "preset": "python-pytest",
  "strict": true,
  "exclude_globs": ["scripts/**", "prototypes/**"]
}
```

Sem esse arquivo o hook fica completamente inerte. Nenhum projeto e afetado por padrao.

### Campos do arquivo de configuracao

| Campo | Tipo | Default | Descricao |
|---|---|---|---|
| `preset` | string | - | Nome do preset de stack (ver lista abaixo) |
| `strict` | bool | `true` | Reservado para uso futuro; atualmente nao altera o comportamento do guard |
| `test_command` | string | depende do preset | Comando completo para rodar a suite |
| `fast_command` | string | `null` | Comando alternativo rapido (subset da suite); se presente, o runner usa este em vez de `test_command` |
| `production_globs` | array de strings | depende do preset | Padroes glob para arquivos de producao |
| `test_globs` | array de strings | depende do preset | Padroes glob para arquivos de teste |
| `exclude_globs` | array de strings | `[]` | Padroes glob isentos de qualquer verificacao |
| `timeout_sec` | int | `120` | Tempo maximo (segundos) para a suite rodar antes de timeout |
| `enabled` | bool | `true` | `false` desativa o hook para o projeto sem remover o arquivo |

Qualquer campo listado acima sobrescreve o valor herdado do preset. O preset e aplicado primeiro; os campos explicitos do arquivo vem depois e ganham.

---

## Presets disponiveis

Sao 7 presets prontos para uso:

| Preset | Comando padrao | Extensoes de producao | Extensoes de teste |
|---|---|---|---|
| `python-pytest` | `pytest -x -q` | `**/*.py` | `tests/**`, `**/test_*.py`, `**/*_test.py`, `conftest.py` |
| `php-phpunit` | `vendor/bin/phpunit` | `**/*.php` | `tests/**`, `**/*Test.php` |
| `node-vitest` | `npx vitest run` | `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx` | `**/*.test.*`, `**/*.spec.js`, `**/*.spec.ts` |
| `node-jest` | `npx jest` | `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx` | `__tests__/**`, `**/*.test.js`, `**/*.test.ts` |
| `go-test` | `go test ./...` | `**/*.go` | `**/*_test.go` |
| `cpp-ctest` | `ctest --output-on-failure` | `**/*.cpp`, `**/*.cc`, `**/*.cxx`, `**/*.h`, `**/*.hpp` | `tests/**`, `**/test_*.cpp`, `**/*_test.cpp` |
| `dotnet-test` | `dotnet test` | `**/*.cs` | `**/*Tests.cs`, `**/*Test.cs` |

### Exemplo: sobrescrevendo o comando e adicionando exclusoes

```json
{
  "preset": "python-pytest",
  "test_command": "pytest -x -q src/tests/",
  "fast_command": "pytest -x -q src/tests/ -k smoke",
  "timeout_sec": 60,
  "exclude_globs": ["migrations/**", "scripts/**"]
}
```

### Exemplo: sem preset, globs manuais

```json
{
  "test_command": "make test",
  "production_globs": ["src/**/*.rb"],
  "test_globs": ["spec/**/*_spec.rb"],
  "timeout_sec": 90
}
```

---

## Como funciona

### tdd_guard.py (PreToolUse)

Intercepta toda escrita de arquivo (ferramentas `Write`, `Edit`, `MultiEdit`) **antes** de ela acontecer.

Fluxo de decisao:

1. Se `TDD_GUARD=off`, permite sem verificacao.
2. Se o arquivo editado nao pertence a um projeto com `.claude/tdd-guard.json`, permite (inerte).
3. Classifica o arquivo pelo caminho relativo: `excluded` / `test` / `production` / `ignored`.
4. Se nao e `production`, permite. **Escrever ou editar teste nunca e bloqueado.**
5. Se `TDD_PHASE=refactor`, permite (modo refatoracao com suite verde).
6. Le o estado mais recente em `$HOME/.claude/state/tdd-guard/<hash>/last-run.json`:
   - Estado ausente: bloqueia com mensagem pedindo um teste vermelho.
   - `ran=false` (runner nao executou): **fail-open** com aviso; nao bloqueia.
   - `has_red=true`: permite (ha teste vermelho, producao pode avancar).
   - `has_red=false` (tudo verde): bloqueia pedindo um novo teste que falhe, ou `TDD_PHASE=refactor`.

### tdd_runner.py (PostToolUse)

Roda apos cada escrita de arquivo de producao ou teste.

1. Localiza a raiz do projeto pelo mesmo mecanismo de busca ascendente.
2. Classifica o arquivo; se nao e `production` nem `test`, nao faz nada.
3. Executa `fast_command` (se definido) ou `test_command` com `shell=True` e `cwd=<raiz>`.
4. Grava o resultado em `$HOME/.claude/state/tdd-guard/<hash>/last-run.json`. O `<hash>` e os primeiros 16 hex do SHA-256 do caminho absoluto da raiz do projeto.
5. **Nunca retorna exit code diferente de 0.** O fluxo do Claude Code nunca e interrompido pelo runner.

> O diretorio de estado fica sob o `HOME` de quem usa o plugin (`$HOME/.claude/state/...`),
> resolvido em runtime via `os.path.expanduser("~")`. Nenhum caminho e fixado no codigo.

### Campos gravados no estado

```json
{
  "ran": true,
  "command": "pytest -x -q",
  "exit_code": 1,
  "has_red": true,
  "totals": { "passed": 4, "failed": 1 },
  "tail": "... ultimas 20 linhas da saida ...",
  "ts": 1749740000
}
```

Quando o runner nao consegue executar:

```json
{
  "ran": false,
  "reason": "timeout",
  "ts": 1749740000
}
```

---

## Valvulas de escape

### Desligar na sessao atual

```bash
export TDD_GUARD=off
```

Todos os hooks ficam inertes ate o fim da sessao do terminal. Nenhum arquivo e modificado.

### Modo refatoracao (suite verde, sem novo teste)

```bash
export TDD_PHASE=refactor
```

Permite editar producao mesmo com `has_red=false`. Use quando a suite ja passou e voce quer reorganizar codigo sem adicionar funcionalidade nova.

### Isentar arquivos pelo caminho

No `.claude/tdd-guard.json`:

```json
{
  "preset": "python-pytest",
  "exclude_globs": [
    "prototypes/**",
    "scripts/**",
    "migrations/**",
    "setup.py"
  ]
}
```

Arquivos que casam com `exclude_globs` sao classificados como `excluded` e nunca bloqueados, independente do estado da suite.

---

## Classificacao de arquivos

A precedencia e: `excluded` > `test` > `production` > `ignored`.

Um arquivo `pkg/test_x.py` casa tanto com `test_globs` (`**/test_*.py`) quanto com `production_globs` (`**/*.py`), mas e classificado como `test` porque teste tem precedencia sobre producao.

---

## Limitacoes conhecidas

- **Custo de execucao a cada edicao:** a suite roda apos cada `Write`/`Edit` em arquivo relevante. Use `fast_command` para rodar um subset de testes mais rapido (ex: apenas a tag `smoke` ou os testes do modulo atual).
- **Erro de coleta conta como red:** se o pytest falha na fase de coleta (import error, fixture quebrada), o exit code e diferente de zero, logo `has_red=true`. Isso e intencional: um projeto com suite quebrada nao esta verde.
- **Exit code 126/127 = fail-open:** se o binario do test runner nao for encontrado (ex: `pytest` nao instalado no venv ativo), o runner grava `ran=false` e o guard faz fail-open com aviso. Nenhuma edicao e bloqueada; corrija o `test_command` ou o ambiente.
- **Timeout = fail-open:** suite que excede `timeout_sec` grava `ran=false, reason=timeout`. O guard tambem faz fail-open. Aumente o `timeout_sec` ou use `fast_command`.
- **Nenhum arquivo de configuracao = nenhum efeito:** o hook nunca atua em projetos sem `.claude/tdd-guard.json`. Isso e intencional.

---

## Estrutura de arquivos

```
hooks/
    tdd_common.py        # logica pura: presets, classify, estado, glob_match
    tdd_guard.py         # PreToolUse: evaluate() -> (exit_code, msg)
    tdd_runner.py        # PostToolUse: run_suite() -> dict; grava estado
    tests/
        conftest.py
        test_tdd_common.py
        test_tdd_guard.py
        test_tdd_runner.py
    README-tdd.md        # este arquivo

$HOME/.claude/state/tdd-guard/
    <hash16>/
        last-run.json    # estado mais recente por projeto
```

Os hooks resolvem o modulo irmao `tdd_common` inserindo o proprio diretorio
(`pathlib.Path(__file__).parent`) no `sys.path` em runtime — funcionam de
qualquer cwd, sem depender de variavel de ambiente ou caminho fixo.

Para rodar a suite do proprio hook (a partir da raiz do plugin):

```bash
python3 -m pytest hooks/tests/ -v
```

---

## Registro no plugin

O plugin registra os hooks em `hooks/hooks.json` (eventos `PreToolUse` e
`PostToolUse`), usando `${CLAUDE_PLUGIN_ROOT}` para resolver o caminho dos
scripts. Nada precisa ser configurado manualmente em `settings.json` quando o
plugin esta instalado.
