# Hook de TDD (guard + runner)

Enforcement determinístico do ciclo red/green/refactor, **opt-in por projeto**.
Faz parte do plugin **bigtech**; o registro dos eventos está em `hooks/hooks.json`.

- **Tipo:** How-to / Reference
- **Audiência:** desenvolvedores que usam Claude Code e querem disciplina de TDD automatizada

---

## Como ativar num projeto

Crie o arquivo `.claude/tdd-guard.json` na **raiz do projeto** (o mesmo nível onde fica a pasta `.git`):

```json
{
  "preset": "python-pytest",
  "strict": true,
  "exclude_globs": ["scripts/**", "prototypes/**"]
}
```

Sem esse arquivo o hook fica completamente inerte. Nenhum projeto é afetado por padrão.

### Campos do arquivo de configuração

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `preset` | string | - | Nome do preset de stack (ver lista abaixo) |
| `strict` | bool | `true` | Reservado para uso futuro; atualmente não altera o comportamento do guard |
| `test_command` | string | depende do preset | Comando completo para rodar a suíte |
| `fast_command` | string | `null` | Comando alternativo rápido (subset da suíte); se presente, o runner usa este em vez de `test_command` |
| `production_globs` | array de strings | depende do preset | Padrões glob para arquivos de produção |
| `test_globs` | array de strings | depende do preset | Padrões glob para arquivos de teste |
| `exclude_globs` | array de strings | `[]` | Padrões glob isentos de qualquer verificação |
| `timeout_sec` | int | `120` | Tempo máximo (segundos) para a suíte rodar antes de timeout |
| `enabled` | bool | `true` | `false` desativa o hook para o projeto sem remover o arquivo |

Qualquer campo listado acima sobrescreve o valor herdado do preset. O preset é aplicado primeiro; os campos explícitos do arquivo vêm depois e ganham.

---

## Presets disponíveis

São 7 presets prontos para uso:

| Preset | Comando padrão | Extensões de produção | Extensões de teste |
|---|---|---|---|
| `python-pytest` | `pytest -x -q` | `**/*.py` | `tests/**`, `**/test_*.py`, `**/*_test.py`, `conftest.py` |
| `php-phpunit` | `vendor/bin/phpunit` | `**/*.php` | `tests/**`, `**/*Test.php` |
| `node-vitest` | `npx vitest run` | `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx` | `**/*.test.*`, `**/*.spec.js`, `**/*.spec.ts` |
| `node-jest` | `npx jest` | `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx` | `__tests__/**`, `**/*.test.js`, `**/*.test.ts` |
| `go-test` | `go test ./...` | `**/*.go` | `**/*_test.go` |
| `cpp-ctest` | `ctest --output-on-failure` | `**/*.cpp`, `**/*.cc`, `**/*.cxx`, `**/*.h`, `**/*.hpp` | `tests/**`, `**/test_*.cpp`, `**/*_test.cpp` |
| `dotnet-test` | `dotnet test` | `**/*.cs` | `**/*Tests.cs`, `**/*Test.cs` |

### Exemplo: sobrescrevendo o comando e adicionando exclusões

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

Fluxo de decisão:

1. Se `TDD_GUARD=off`, permite sem verificação.
2. Se o arquivo editado não pertence a um projeto com `.claude/tdd-guard.json`, permite (inerte).
3. Classifica o arquivo pelo caminho relativo: `excluded` / `test` / `production` / `ignored`.
4. Se não é `production`, permite. **Escrever ou editar teste nunca é bloqueado.**
5. Se `TDD_PHASE=refactor`, permite (modo refatoração com suíte verde).
6. Lê o estado mais recente em `$HOME/.claude/state/tdd-guard/<hash>/last-run.json`:
   - Estado ausente: bloqueia com mensagem pedindo um teste vermelho.
   - `ran=false` (runner não executou): **fail-open** com aviso; não bloqueia.
   - `has_red=true`: permite (há teste vermelho, produção pode avançar).
   - `has_red=false` (tudo verde): bloqueia pedindo um novo teste que falhe, ou `TDD_PHASE=refactor`.

### tdd_runner.py (PostToolUse)

Roda após cada escrita de arquivo de produção ou teste.

1. Localiza a raiz do projeto pelo mesmo mecanismo de busca ascendente.
2. Classifica o arquivo; se não é `production` nem `test`, não faz nada.
3. Executa `fast_command` (se definido) ou `test_command` com `shell=True` e `cwd=<raiz>`.
4. Grava o resultado em `$HOME/.claude/state/tdd-guard/<hash>/last-run.json`. O `<hash>` é os primeiros 16 hex do SHA-256 do caminho absoluto da raiz do projeto.
5. **Nunca retorna exit code diferente de 0.** O fluxo do Claude Code nunca é interrompido pelo runner.

> O diretório de estado fica sob o `HOME` de quem usa o plugin (`$HOME/.claude/state/...`),
> resolvido em runtime via `os.path.expanduser("~")`. Nenhum caminho é fixado no código.

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

Quando o runner não consegue executar:

```json
{
  "ran": false,
  "reason": "timeout",
  "ts": 1749740000
}
```

---

## Válvulas de escape

### Desligar na sessão atual

```bash
export TDD_GUARD=off
```

Todos os hooks ficam inertes até o fim da sessão do terminal. Nenhum arquivo é modificado.

### Modo refatoração (suíte verde, sem novo teste)

```bash
export TDD_PHASE=refactor
```

Permite editar produção mesmo com `has_red=false`. Use quando a suíte já passou e você quer reorganizar código sem adicionar funcionalidade nova.

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

Arquivos que casam com `exclude_globs` são classificados como `excluded` e nunca bloqueados, independente do estado da suíte.

---

## Classificação de arquivos

A precedência é: `excluded` > `test` > `production` > `ignored`.

Um arquivo `pkg/test_x.py` casa tanto com `test_globs` (`**/test_*.py`) quanto com `production_globs` (`**/*.py`), mas é classificado como `test` porque teste tem precedência sobre produção.

---

## Limitações conhecidas

- **Custo de execução a cada edição:** a suíte roda após cada `Write`/`Edit` em arquivo relevante. Use `fast_command` para rodar um subset de testes mais rápido (ex: apenas a tag `smoke` ou os testes do módulo atual).
- **Erro de coleta conta como red:** se o pytest falha na fase de coleta (import error, fixture quebrada), o exit code é diferente de zero, logo `has_red=true`. Isso é intencional: um projeto com suíte quebrada não está verde.
- **Exit code 126/127 = fail-open:** se o binário do test runner não for encontrado (ex: `pytest` não instalado no venv ativo), o runner grava `ran=false` e o guard faz fail-open com aviso. Nenhuma edição é bloqueada; corrija o `test_command` ou o ambiente.
- **Timeout = fail-open:** suíte que excede `timeout_sec` grava `ran=false, reason=timeout`. O guard também faz fail-open. Aumente o `timeout_sec` ou use `fast_command`.
- **Nenhum arquivo de configuração = nenhum efeito:** o hook nunca atua em projetos sem `.claude/tdd-guard.json`. Isso é intencional.

---

## Estrutura de arquivos

```
hooks/
    tdd_common.py        # lógica pura: presets, classify, estado, glob_match
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

Os hooks resolvem o módulo irmão `tdd_common` inserindo o próprio diretório
(`pathlib.Path(__file__).parent`) no `sys.path` em runtime; funcionam de
qualquer cwd, sem depender de variável de ambiente ou caminho fixo.

Para rodar a suíte do próprio hook (a partir da raiz do plugin):

```bash
python3 -m pytest hooks/tests/ -v
```

---

## Registro no plugin

O plugin registra os hooks em `hooks/hooks.json` (eventos `PreToolUse` e
`PostToolUse`), usando `${CLAUDE_PLUGIN_ROOT}` para resolver o caminho dos
scripts. Nada precisa ser configurado manualmente em `settings.json` quando o
plugin está instalado.
