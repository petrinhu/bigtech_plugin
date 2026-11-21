<!--
  docs/house sync
  origem: vault claudebrain / TESTES.md
  sync_date: 2026-11-21
  hmac_vault_sha256: 8ee8d00d09465be7eae74830aa03435ab353afa9ee6babd1a6597373578cfa42
  transformacoes: T1=4 T2=0 T3a=0 T3=0 T4=0 T5=0
  regra: As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário. Se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# Guia Completo de Testes, Qualidade e Auditoria

> **Cópia canônica** na raiz do vault. Versão estável espelhada em [[Resources/Standards/TESTES]].

## Referências cruzadas

- Manuais irmãos: [[CONTRACT]] · [[AGILE]] · [[AUDITORIAS]] · [[DEPLOY_CHECKLIST]]
- Hub: [[Standards]] · [[CLAUDE]]

---

> Catálogo de referência de testes e auditoria para qualquer agente de IA ou engenheiro,
> em projetos **C · C++ · Python · Rust · Node.js/TypeScript**. O que de fato roda num
> projeto segue o piso de testes abaixo.
> As seções T1-T12 e A1-A10 cobrem C/C++/Qt. As seções T13-T15 e A11-A13 cobrem os demais stacks.
> Adapte os caminhos e nomes de módulos conforme o projeto alvo.

> **Portabilidade dos comandos (agnóstico de SO).** Os comandos de instalação usam `dnf` (Fedora/RHEL) e `apt` (Debian/Ubuntu) como exemplos. Adapte ao gerenciador do sistema: `apt`, `dnf`, `pacman` ou `zypper` no Linux; `brew` no macOS; `winget`, `choco` ou `scoop` no Windows. Prefira gerenciadores cross-platform quando houver: `pip`/`uv`, `cargo` e `npm`/`pnpm` valem igual em Windows, macOS e Linux. Para detectar uma ferramenta, use `command -v <ferramenta>` no Unix ou no WSL, e `Get-Command <ferramenta>` ou `where <ferramenta>` no Windows. No Windows, rodar o Claude Code via WSL torna válidos os comandos Unix deste manual.

> **Ferramenta ausente.** Siga a regra de [[TOOLING]] (legenda de status): ferramenta de linha de comando de uso geral pode ser instalada com aviso; biblioteca, dependência de projeto, modelo, extensão, navegador e serviço só com permissão do usuário; nunca falhar calado.

> **Piso de testes (vale acima de qualquer seção deste manual).** Teste só para lógica de produto. O CI é o único portão. Nada de teste de mutação, sabotagem, auditoria, reauditoria, varredura de gêmeos, checklist de perguntas do revisor, script de verificação extra nem portão local novo. Exceção: segurança, privacidade e deploy irreversível. Varredura de gêmeos é caçar o mesmo defeito em outros pontos depois de achar um. As seções T e A abaixo são catálogo: entram num projeto só quando testam lógica de produto, quando caem na exceção ou quando o usuário pede. Auditoria da exceção roda uma vez, sem reauditoria; a correção de um achado se confere no CI.

---

## Índice

1. [Pré-requisitos e Instalação](#1-pré-requisitos-e-instalação)
2. [T1  -  Testes Unitários](#t1--testes-unitários)
3. [T2  -  Análise Estática](#t2--análise-estática)
4. [T3  -  Fuzzing de Inputs](#t3--fuzzing-de-inputs)
5. [T4  -  Análise Dinâmica de Memória](#t4--análise-dinâmica-de-memória)
6. [T5  -  Scanning de Dependências](#t5--scanning-de-dependências)
7. [T6  -  Teste de APIs](#t6--teste-de-apis)
8. [T7  -  Scanning de Binário](#t7--scanning-de-binário)
9. [T8  -  Verificação de Secrets](#t8--verificação-de-secrets)
10. [T9  -  Teste de Rede](#t9--teste-de-rede)
11. [T10  -  SQL Injection](#t10--sql-injection)
12. [T11  -  Fuzzing de Protocolos de Rede](#t11--fuzzing-de-protocolos-de-rede)
13. [T12  -  Busca de CVEs nas Dependências](#t12--busca-de-cves-nas-dependências)
14. [T14  -  Integração (Sandbox)](#t14--integração-sandbox)
15. [T15  -  Pré-CI · Espelhar CI Localmente](#t15--pré-ci--espelhar-ci-localmente) (instalação de ferramentas em T15.0)
16. [A1  -  Descoberta e Modelagem](#a1--descoberta-e-modelagem)
17. [A2  -  Auditoria de Arquitetura e Camadas](#a2--auditoria-de-arquitetura-e-camadas)
18. [A3  -  UI/UX e Acessibilidade](#a3--uiux-e-acessibilidade)
19. [A4  -  QA Geral C++](#a4--qa-geral-c)
20. [A5  -  Análise Estática e Dinâmica C/C++](#a5--análise-estática-e-dinâmica-cc)
21. [A6  -  Cobertura de Testes](#a6--cobertura-de-testes)
22. [A7  -  Dependências e Acoplamento](#a7--dependências-e-acoplamento)
23. [A8  -  Consistência .h vs .cpp](#a8--consistência-h-vs-cpp)
24. [A9  -  Análise Arquitetural Geral](#a9--análise-arquitetural-geral)
25. [A10  -  Relatório Final de Auditoria](#a10--relatório-final-de-auditoria)
26. [Classificação de Problemas](#classificação-de-problemas)
27. [Formato de Patch](#formato-de-patch)

---

## T1  -  Testes Unitários

**Objetivo:** verificar que cada módulo se comporta conforme especificado de forma isolada.

**Ferramenta:** QtTest (embutido no Qt6) ou Google Test.

**Critério de aprovação:** 0 falhas; todo comportamento novo nasce de um teste visto falhando antes.

---

## T2  -  Análise Estática

**Objetivo:** detectar bugs, má práticas e problemas de segurança sem executar o código.

**Ferramentas:** `cppcheck` + `clang-tidy`.

---

## T4  -  Análise Dinâmica de Memória

**Objetivo:** detectar vazamentos de memória, acessos inválidos e comportamento indefinido em runtime.

**Ferramentas:** AddressSanitizer (ASan) + UndefinedBehaviorSanitizer (UBSan).

---

## T8  -  Verificação de Secrets

**Objetivo:** garantir que nenhuma credencial, token ou chave privada foi commitada no repositório.

**Ferramentas:** `gitleaks` + `trufflehog`.

---

## T10  -  SQL Injection

**Objetivo:** verificar que as queries SQLite são seguras contra injeção de SQL.

**Ferramenta:** `sqlmap` + revisão manual de prepared statements.

---

## T12  -  Busca de CVEs nas Dependências

**Objetivo:** identificar vulnerabilidades conhecidas (CVE) nas bibliotecas usadas pelo projeto.

**Ferramentas:** `trivy` + `grype` + consulta a NVD/OSV.

---

## T14  -  Integração (Sandbox)

**Objetivo:** Validação fim-a-fim contra fontes de verdade (Dumps binários).

---

## T15  -  Pré-CI · Espelhar CI Localmente

**Objetivo:** rodar na máquina, quando for útil, a mesma suíte que o CI roda. É opcional e nunca obrigatório antes do push ou da tag. Funciona em qualquer stack porque os comandos do CI são exatamente os mesmos comandos locais.

> **Escopo de uso:** atalho opcional para ver uma falha óbvia antes de esperar o CI. Não é portão, não é passo obrigatório antes do push e não substitui o CI remoto: o CI é a fonte de verdade e o único portão. 

### T15.0  Instalar ferramentas necessárias

Cada stack exige um conjunto de ferramentas para os testes T15.X. Instale antes do primeiro uso; depois apenas atualizar quando precisar.

> **No Windows.** Os gerenciadores cross-platform já cobrem Windows: `uv`/`pip` (Python), `cargo` (Rust) e `npm`/`pnpm` (Node) instalam igual em Windows, macOS e Linux. Equivalentes nativos quando precisar: Python, instalador do `uv` (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`) ou `pip`; Rust, `rustup-init.exe` ou `winget install Rustlang.Rustup`; Node, `winget install OpenJS.NodeJS` ou nvm-windows; ferramentas de sistema (cmake, clang, cppcheck), `winget`, `choco` ou msys2. Alternativa: rodar o Claude Code via WSL torna válidos os blocos `apt` e `dnf` deste T15.0 sem tradução.
Se rodar o espelho em container, dimensione RAM e número de jobs (`-j`) medindo a máquina atual, nunca estimando; se o projeto precisar de outra especificação, pergunte ao usuário.

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
# Fedora
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

**Container-level (qualquer stack).** Comandos com privilégio: siga as regras do usuário para elevação e mostre a transação antes de executar.
```bash
# Fedora
sudo dnf install docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"  # relogar depois
# Debian/Ubuntu
sudo apt install docker.io
```

**Dois níveis de espelhamento:**

1. **Host-level (rápido, só onde as instruções do usuário permitirem).** Executar binário a binário no host. Idêntico ao CI exceto pelo OS subjacente (libs do sistema). Cobre 90 % das falhas de CI: lint, type-check, testes, contratos, security scan, build.
2. **Container-level (lento, idêntico; nível padrão quando as instruções do usuário exigirem isolamento).** Rodar a imagem Docker que o CI usa via `act` (GitHub Actions) ou `docker run` direto. Necessário quando se suspeita de deps de SO (ex.: PySide6 + libGL).

### T15.1  Python (uv + pyproject)

Se quiser o atalho, crie `scripts/preci.sh` na raiz do repo, modelo abaixo, e rode `./scripts/preci.sh` quando for útil. É opcional: o CI é o único portão.

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

Replicar em container (1:1 com CI GitHub Actions):

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
THREADS="${THREADS:?defina THREADS conforme os limites de hardware do usuário}"

echo "== clang-format check =="
find src/ tests/ -name '*.cpp' -o -name '*.h' | xargs clang-format --dry-run -Werror

echo "== cmake configure (strict warnings) =="
cmake -S . -B "$BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-Wall -Wextra -Wpedantic -Werror -Wshadow -Wnull-dereference"

echo "== compile =="
cmake --build "$BUILD" --parallel "$THREADS"

echo "== clang-tidy =="
find src/ -name '*.cpp' -exec clang-tidy -p "$BUILD" {} +

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

### Limitação

Container-level só é 100 % idêntico se a imagem do CI for pública e fixada por digest. Imagens latest podem divergir entre runs. Para reprodutibilidade total, fixar digest no CI (`image: catthehacker/ubuntu:act-22.04@sha256:...`) e usar o mesmo digest local.

---

> As seções A abaixo são auditoria fora da exceção do piso de testes: só rodam quando o usuário pede. A auditoria de segurança, privacidade e deploy irreversível segue [[AUDITORIAS]] e [[DEPLOY_CHECKLIST]].

## A2  -  Auditoria de Arquitetura e Camadas

**Objetivo:** validar que nenhuma camada viola as regras de dependência da arquitetura.

**Critério de aprovação (quando pedida):** zero violações críticas (API em widget, SQL em domínio).

---

## A3  -  UI/UX e Acessibilidade

**Objetivo:** verificar qualidade visual, contraste, navegação por teclado e conformidade com boas práticas.

---

## A10  -  Relatório Final de Auditoria

**Objetivo:** consolidar todos os resultados em um único documento com score, problemas e patches.

**Entregável (quando pedida):** documento com score global (0-100), sumário de problemas e patches unificados.
