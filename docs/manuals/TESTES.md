# Guia Completo de Testes, Qualidade e Auditoria

Manual de governança que acompanha o plugin. Manuais irmãos: [CONTRACT](CONTRACT.md) · [AGILE](AGILE.md) · [AUDITORIAS](AUDITORIAS.md) · [DEPLOY_CHECKLIST](DEPLOY_CHECKLIST.md). O `CLAUDE.md` na raiz do seu projeto define as preferências locais; estes manuais são seus padrões de engenharia.

---

> Documento instrucional para qualquer agente de IA ou engenheiro executar a suíte
> completa de verificação em projetos **C · C++ · Python · Rust · Node.js/TypeScript**.
> As seções T1-T12 e A1-A10 cobrem C/C++/Qt. As seções T13-T15 e A11-A13 cobrem os demais stacks.
> Adapte os caminhos e nomes de módulos conforme o projeto alvo.

> **Portabilidade dos comandos (agnóstico de SO):** os comandos de instalação abaixo usam `dnf`
> (Fedora/RHEL) e `apt` (Debian/Ubuntu) como exemplos concretos, mas o plugin é agnóstico de
> sistema operacional e cobre Windows nativo, WSL, macOS e Linux.
> - **Linux:** adapte ao gerenciador da distribuição: `apt` (Debian/Ubuntu), `dnf` (Fedora/RHEL),
>   `pacman` (Arch), `zypper` (openSUSE). O nome do pacote costuma ser o mesmo.
> - **macOS:** use `brew` (Homebrew).
> - **Windows:** use `winget` (nativo), `choco` (Chocolatey) ou `scoop`.
> - **Detecção de ferramenta conforme o SO:** `command -v <ferramenta>` no Unix, WSL ou Git-Bash;
>   `Get-Command <ferramenta>` ou `where <ferramenta>` no Windows (PowerShell ou cmd).
> - **Prefira gerenciadores cross-platform quando a ferramenta os oferece:** `pip`/`uv` (Python),
>   `cargo` (Rust), `npm`/`pnpm` (Node) funcionam igual em Windows, macOS e Linux: um só comando
>   serve para todos os SO.
> - **No Windows, rodar o Claude Code via WSL** torna válidos todos os comandos Unix deste manual
>   (incluindo `command -v` e os gerenciadores `apt`/`dnf`), evitando a tradução para PowerShell.

> **Política - ferramenta ausente.** Ao executar um item de teste (`TST-*` / `T*`) cuja ferramenta
> requerida não está instalada, siga a [política de ferramenta ausente](../principles/missing-tool-policy.md)
> (fonte única do protocolo, agnóstica de SO): detecte conforme o SO; instale sozinho se a ferramenta
> for de userland (`pip`/`uv`, `cargo`, `npm`, binário no `$HOME`) ou OFEREÇA antes via AskUserQuestion
> se a instalação exigir `sudo`/gerenciador do sistema; nunca falhe por falta de ferramenta nem fique
> silencioso. O comando de instalação de cada ferramenta está no [TOOLING](../TOOLING.md); os
> pré-requisitos básicos do ambiente (ex.: Python/pytest) seguem o T15.0.

---

## Índice

Este manual é um excerto operacional: documenta os procedimentos de teste e auditoria abaixo. A suíte completa de tipos (T1-T15) e o catálogo de auditorias por stack vivem no `TESTES.md` e no `AUDITORIAS.md` da raiz do seu projeto, gerados pela skill `/tab_pendencias` conforme o stack detectado.

1. [T1 - Testes Unitários](#t1---testes-unitários)
2. [T2 - Análise Estática](#t2---análise-estática)
3. [T4 - Análise Dinâmica de Memória](#t4---análise-dinâmica-de-memória)
4. [T8 - Verificação de Secrets](#t8---verificação-de-secrets)
5. [T10 - SQL Injection](#t10---sql-injection)
6. [T12 - Busca de CVEs nas Dependências](#t12---busca-de-cves-nas-dependências)
7. [T14 - Integração (Sandbox)](#t14---integração-sandbox)
8. [T15 - Pré-CI: Espelhar CI Localmente](#t15---pré-ci-espelhar-ci-localmente) (instalação de ferramentas em T15.0)
9. [A2 - Auditoria de Arquitetura e Camadas](#a2---auditoria-de-arquitetura-e-camadas)
10. [A3 - UI/UX e Acessibilidade](#a3---uiux-e-acessibilidade)
11. [A10 - Relatório Final de Auditoria](#a10---relatório-final-de-auditoria)

---

## T1 - Testes Unitários

**Objetivo:** verificar que cada módulo se comporta conforme especificado de forma isolada.

**Ferramenta:** QtTest (embutido no Qt6) ou Google Test.

**Critério de aprovação:** 0 falhas. Cobertura mínima de 70% nos módulos críticos.

---

## T2 - Análise Estática

**Objetivo:** detectar bugs, má práticas e problemas de segurança sem executar o código.

**Ferramentas:** `cppcheck` + `clang-tidy`.

---

## T4 - Análise Dinâmica de Memória

**Objetivo:** detectar vazamentos de memória, acessos inválidos e comportamento indefinido em runtime.

**Ferramentas:** AddressSanitizer (ASan) + UndefinedBehaviorSanitizer (UBSan).

---

## T8 - Verificação de Secrets

**Objetivo:** garantir que nenhuma credencial, token ou chave privada foi commitada no repositório.

**Ferramentas:** `gitleaks` + `trufflehog`.

---

## T10 - SQL Injection

**Objetivo:** verificar que as queries SQLite são seguras contra injeção de SQL.

**Ferramenta:** `sqlmap` + revisão manual de prepared statements.

---

## T12 - Busca de CVEs nas Dependências

**Objetivo:** identificar vulnerabilidades conhecidas (CVE) nas bibliotecas usadas pelo projeto.

**Ferramentas:** `trivy` + `grype` + consulta a NVD/OSV.

---

## T14 - Integração (Sandbox)

**Objetivo:** Validação fim-a-fim contra fontes de verdade (Dumps binários).

---

## T15 - Pré-CI: Espelhar CI Localmente

**Objetivo:** rodar a MESMA suíte que o CI roda, antes de push/tag, evitando ciclo "push, esperar 8 min, falhar, corrigir". Funciona em qualquer stack porque os comandos do CI são exatamente os mesmos comandos locais.

> **Escopo de uso:** Rodar APENAS como pré-flight antes de `git push` que dispara CI/release. NÃO substituem o CI remoto e NÃO devem ser usados como gate único de envio final: o envio definitivo do projeto SEMPRE passa pelo CI no servidor (fonte de verdade). Pré-CI local antecipa falhas óbvias para reduzir ida-volta; CI remoto valida que o build é reprodutível fora da máquina do dev.

### T15.0  Instalar ferramentas necessárias

Cada stack exige um conjunto de ferramentas para os testes T15.X. Instale antes do primeiro uso; depois apenas atualizar quando precisar.

> **No Windows (nota consolidada).** Os gerenciadores cross-platform abaixo já cobrem Windows: `uv`/`pip` (Python), `cargo` (Rust) e `npm`/`pnpm` (Node) instalam igual em Windows, macOS e Linux. Equivalentes nativos quando precisar:
> - **Python:** instalador Windows do `uv` (PowerShell: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`) ou `pip`.
> - **Rust:** `rustup-init.exe` (do site da rustup) ou `winget install Rustlang.Rustup`.
> - **Node:** `winget install OpenJS.NodeJS` ou nvm-windows.
> - **Ferramentas de sistema** (cmake, clang, cppcheck): `winget`, `choco` ou msys2.
>
> Alternativa: rodar o Claude Code via WSL torna válidos os blocos `apt`/`dnf` deste T15.0 sem tradução.

**Python (uv):**
```bash
# uv (gerenciador único; instala todo o resto via uv sync)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Dentro do projeto: ruff, mypy, pytest, bandit, import-linter, coverage
# vêm de [project.optional-dependencies].dev e instalam com:
uv sync --extra dev
```

**C++ / Qt:**
```bash
# Fedora/RHEL
sudo dnf install cmake ninja-build clang clang-tools-extra cppcheck \
  qt6-qtbase-devel qt6-qttools-devel
# Debian/Ubuntu
sudo apt install cmake ninja-build clang clang-tidy clang-format cppcheck \
  qt6-base-dev qt6-tools-dev
```

**Rust:**
```bash
# Toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# Componentes
rustup component add rustfmt clippy
cargo install cargo-audit
```

**Node/TypeScript:**
```bash
# Node 20+ (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
# Gerenciador de pacotes preferido (pnpm)
npm install -g pnpm
# Dentro do projeto: deps vêm de devDependencies
pnpm install
```

**Container-level (qualquer stack):**
```bash
# Fedora/RHEL
sudo dnf install docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"  # relogar depois
# Debian/Ubuntu
sudo apt install docker.io
```

**Dois níveis de espelhamento:**

1. **Host-level (rápido).** Executar binário a binário no host. Idêntico ao CI exceto pelo OS subjacente (libs do sistema). Cobre 90 % das falhas de CI: lint, type-check, testes, contratos, security scan, build.
2. **Container-level (lento, idêntico).** Rodar a imagem Docker que o CI usa via `act` (GitHub Actions) ou `docker run` direto. Necessário quando se suspeita de deps de SO (ex.: PySide6 + libGL).

### T15.1  Python (uv + pyproject)

Crie `scripts/preci.sh` na raiz do repo, modelo abaixo. Rode `./scripts/preci.sh` antes de `git push`.

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "== ruff check =="
uv run ruff check src/ tests/

echo "== ruff format check =="
uv run ruff format --check src/ tests/

echo "== mypy strict =="
uv run mypy src/

echo "== import-linter (hex/clean arch) =="
uv run lint-imports

echo "== bandit (high+) =="
uv run bandit -r src/ -c bandit.yaml --severity-level medium

echo "== pytest unit =="
uv run pytest -m unit -q --no-cov

echo "== build wheel + sdist =="
uv build

echo "ALL GREEN"
```

Replicar em container (1:1 com o CI):

```bash
docker run --rm -v "$PWD":/work:Z -w /work -e QT_QPA_PLATFORM=offscreen \
  catthehacker/ubuntu:act-22.04 bash -c '
  apt-get update -qq && apt-get install -y -qq libxcb-cursor0 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1 \
    libxkbcommon-x11-0 libegl1 libgl1 libfontconfig1 libdbus-1-3 >/dev/null
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
  export PATH="$HOME/.local/bin:$PATH"
  uv sync --extra dev
  bash scripts/preci.sh
'
```

> Em Fedora/SELinux precisa do flag `:Z` no mount. Em Ubuntu/Debian basta `:rw`.

### T15.2  C++ / Qt (CMake + Ninja)

`scripts/preci.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
BUILD=build/preci

echo "== clang-format check =="
find src/ tests/ -name '*.cpp' -o -name '*.h' | xargs clang-format --dry-run -Werror

echo "== cmake configure (strict warnings) =="
cmake -S . -B "$BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-Wall -Wextra -Wpedantic -Werror -Wshadow -Wnull-dereference"

echo "== compile =="
cmake --build "$BUILD" --parallel

echo "== clang-tidy =="
find src/ -name '*.cpp' -exec clang-tidy {} -p "$BUILD" \;

echo "== cppcheck =="
cppcheck --enable=all --inline-suppr --error-exitcode=1 --suppress=missingIncludeSystem src/

echo "== ctest =="
ctest --test-dir "$BUILD" --output-on-failure

echo "ALL GREEN"
```

### T15.3  Rust (cargo)

```bash
#!/usr/bin/env bash
set -euo pipefail
echo "== fmt =="
cargo fmt --check
echo "== clippy =="
cargo clippy --all-targets --all-features -- -D warnings
echo "== test =="
cargo test --all-features
echo "== audit =="
cargo audit
echo "ALL GREEN"
```

### T15.4  Node/TypeScript (pnpm/npm)

```bash
#!/usr/bin/env bash
set -euo pipefail
echo "== type-check =="
pnpm exec tsc --noEmit
echo "== lint =="
pnpm exec eslint . --max-warnings 0
echo "== format =="
pnpm exec prettier --check .
echo "== test =="
pnpm test
echo "== audit =="
pnpm audit --audit-level=high
echo "ALL GREEN"
```

### T15.5  Hook git pre-push (opcional, recomendado)

Adicionar `.git/hooks/pre-push`:

```bash
#!/usr/bin/env bash
exec scripts/preci.sh
```

`chmod +x .git/hooks/pre-push`. Falha local bloqueia push, evitando viajar até o CI.

### Limitação

Container-level só é 100 % idêntico se a imagem do CI for pública e fixada por digest. Imagens latest podem divergir entre runs. Para reprodutibilidade total, fixar digest no CI (`image: catthehacker/ubuntu:act-22.04@sha256:...`) e usar o mesmo digest local.

---

## A2 - Auditoria de Arquitetura e Camadas

**Objetivo:** validar que nenhuma camada viola as regras de dependência da arquitetura.

**Critério de aprovação:** zero violações críticas (API em widget, SQL em domínio).

---

## A3 - UI/UX e Acessibilidade

**Objetivo:** verificar qualidade visual, contraste, navegação por teclado e conformidade com boas práticas.

---

## A10 - Relatório Final de Auditoria

**Objetivo:** consolidar todos os resultados em um único documento com score, problemas e patches.

**Entregável obrigatório:** documento com score global (0-100), sumário de problemas e patches unificados.
