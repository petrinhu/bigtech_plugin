# TOOLING.md - Ferramentas FOSS Automatizáveis dos Agents

> Catálogo das melhores ferramentas livres (FOSS) Linux, automatizáveis via CLI/headless, mapeadas aos agents que devem usá-las SEMPRE que a tarefa pedir.

Manual de governança que acompanha o plugin. Manuais relacionados: [CONTRACT](manuals/CONTRACT.md), [TESTES](manuals/TESTES.md), [AGILE](manuals/AGILE.md), [DEPLOY_CHECKLIST](manuals/DEPLOY_CHECKLIST.md), [AUDITORIAS](manuals/AUDITORIAS.md). Organização da constelação de agents: [ORG](ORG.md).

## Legenda de status

- ✓ **comum**: costuma já estar no toolchain de uma estação de desenvolvimento.
- ⬇ **instalar sob demanda**: instale com o comando da coluna quando a tarefa pedir.
- ↺ **preferir**: alternativa moderna recomendada no lugar da ferramenta legada.

Regra: o agent usa a ferramenta canônica do seu domínio SEMPRE que aplicável (não reinventa em shell cru). Se ela faltar (⬇), instala com o comando aqui antes de usar. Respeite os limites de hardware da máquina ([limites de hardware](principles/hardware-resource-limits.md)) e a prioridade de ferramentas MCP: quando houver um servidor MCP que cubra a tarefa, prefira-o ao shell cru.

> **Portabilidade dos comandos (agnóstico de SO):** os comandos de instalação abaixo usam `dnf` (Fedora/RHEL) como exemplo concreto. Adapte ao gerenciador do seu sistema: Linux (`apt`, `pacman`, `zypper`, `nix`), macOS (`brew`), Windows (`winget`, `choco` ou `scoop`); o nome do pacote costuma ser o mesmo. Prefira gerenciadores cross-platform quando a ferramenta os oferece (`pip`/`uv`, `cargo`, `npm`/`pnpm`, que funcionam igual em Windows, macOS e Linux). No Windows, rodar o Claude Code via WSL valida os comandos Unix.

---

## 1. Base (todos os agents)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| ripgrep (`rg`) | ✓ | busca de código rápida (preferir sobre grep) | `sudo dnf install ripgrep` |
| fd (`fd`) | ✓ | busca de arquivo (preferir sobre find) | `sudo dnf install fd-find` |
| fzf | ✓ | seleção fuzzy interativa | `sudo dnf install fzf` |
| jq | ✓ | manipular JSON | `sudo dnf install jq` |
| yq (mikefarah) | ⬇ | manipular YAML | `go install github.com/mikefarah/yq/v4@latest` |
| git-delta (`delta`) | ⬇↺ | diff legível (preferir sobre diff cru) | `sudo dnf install git-delta` |
| GNU parallel | ⬇ | paralelizar jobs em shell | `sudo dnf install parallel` |
| entr | ⬇ | rodar comando ao mudar arquivo | `sudo dnf install entr` |

---

## 2. Engenharia de código (software-architect, tech-lead, backend, frontend, mobile)

| Ferramenta | Status | Para quê | Agents | Instalar |
|---|---|---|---|---|
| ast-grep (`sg`) | ✓ | busca/refactor por AST | architect, tech-lead, backend, frontend | `cargo install ast-grep` |
| tokei | ⬇ | contar LoC por linguagem (preferir sobre cloc) | architect, tech-lead, internal-auditor | `sudo dnf install tokei` |
| cmake / ninja / make | ✓ | build C++/Qt | backend, architect | `sudo dnf install cmake ninja-build make` |
| ccache | ⬇ | cache de compilação C/C++ | backend | `sudo dnf install ccache` |
| mold | ⬇ | linker rápido | backend | `sudo dnf install mold` |
| pre-commit | ⬇ | hooks de lint/format no commit | tech-lead, todos eng | `pipx install pre-commit` |
| ruff | ⬇ | lint+format Python (substitui flake8+black+isort) | backend, data | `uv tool install ruff` |
| shellcheck | ⬇ | lint de shell | todos eng, devops | `sudo dnf install ShellCheck` |
| shfmt | ⬇ | format de shell | devops | `go install mvdan.cc/sh/v3/cmd/shfmt@latest` |
| biome | ⬇ | lint+format JS/TS (substitui eslint+prettier) | frontend | `npm i -g @biomejs/biome` |
| clang-format / clang-tidy | ✓ | format+lint C++ | backend, architect | `sudo dnf install clang-tools-extra` |
| cppcheck | ✓ | análise estática C/C++ | backend, tech-lead | `sudo dnf install cppcheck` |
| yamllint | ⬇ | lint YAML | devops | `pipx install yamllint` |
| hadolint | ⬇ | lint Dockerfile | devops | binário em github.com/hadolint/hadolint/releases |
| taplo | ⬇ | lint/format TOML | backend | `cargo install taplo-cli` |

---

## 3. QA e Performance (qa-engineer, performance-engineer)

| Ferramenta | Status | Para quê | Agents | Instalar |
|---|---|---|---|---|
| pytest | ⬇ | testes Python (por venv) | qa, data | `uv pip install pytest` (no venv) |
| ctest | ✓ | testes C++/CMake | qa, backend | (vem com cmake) |
| playwright | ✓ | e2e browser | qa, frontend | `npm i -g playwright` |
| k6 | ⬇ | teste de carga HTTP scriptável | performance, qa | binário em dl.k6.io |
| locust | ⬇ | teste de carga em Python | performance | `pipx install locust` |
| hyperfine | ⬇ | benchmark de CLI reproduzível | performance, qa | `sudo dnf install hyperfine` |
| perf | ✓ | profiling CPU (kernel) | performance | `sudo dnf install perf` |
| valgrind | ✓ | memcheck/callgrind | performance, backend | `sudo dnf install valgrind` |
| heaptrack | ✓ | profiling de heap | performance | `sudo dnf install heaptrack` |
| py-spy | ⬇ | profiling Python sampling | performance, data | `pipx install py-spy` |
| strace / ltrace | ✓/⬇ | trace de syscalls/libcalls | performance | `sudo dnf install strace ltrace` |

---

## 4. Segurança (security-engineer, network-security-engineer, internal-auditor, CISO)

| Ferramenta | Status | Para quê | Agents | Instalar |
|---|---|---|---|---|
| semgrep | ⬇ | SAST multi-linguagem | security, internal-auditor | `pipx install semgrep` |
| gitleaks | ✓ | scan de segredos no git | security, internal-auditor | `sudo dnf install gitleaks` |
| trufflehog | ⬇ | scan de segredos (verificado) | security | `go install github.com/trufflesecurity/trufflehog/v3@latest` |
| trivy | ⬇ | scan de container/IaC/deps | security, devops, auditor | repo aquasecurity (dnf) |
| grype | ⬇ | scan de vulnerabilidade de imagem | security, devops | script anchore |
| syft | ⬇ | gerar SBOM | security, compliance-legal, auditor | script anchore |
| bandit | ⬇ | SAST Python | security, backend | `pipx install bandit` |
| osv-scanner | ⬇ | scan de deps via OSV | security | `go install github.com/google/osv-scanner/cmd/osv-scanner@latest` |
| nuclei | ✓ | scan DAST por templates | security, network-security | `go install github.com/projectdiscovery/nuclei/v3@latest` |
| OWASP ZAP | ⬇ | DAST web (headless) | security | flatpak `org.zaproxy.ZAP` |
| nmap | ✓ | scan de portas/serviços (autorizado) | network-security, network | `sudo dnf install nmap` |
| openssl | ✓ | cripto, inspeção de cert/TLS | security, network-security | (base) |
| cosign | ⬇ | assinar/verificar artefato | security, devops | `go install github.com/sigstore/cosign/v2/cmd/cosign@latest` |
| age + sops | ⬇ | cripto de segredo / secrets em git | security, devops | `sudo dnf install age` ; sops binário |
| lynis | ✓ | auditoria de hardening do host | internal-auditor, network-security | `sudo dnf install lynis` |
| chkrootkit | ✓ | detecção de rootkit | network-security | `sudo dnf install chkrootkit` |
| OpenSCAP (`oscap`) | ⬇ | compliance/benchmark CIS | internal-auditor, security | `sudo dnf install openscap-scanner scap-security-guide` |

---

## 5. Rede (network-engineer)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| dig / drill | ✓/⬇ | consulta DNS | `sudo dnf install bind-utils` |
| mtr | ⬇ | traceroute contínuo | `sudo dnf install mtr` |
| iperf3 | ⬇ | medir banda entre hosts | `sudo dnf install iperf3` |
| tcpdump / tshark | ✓ | captura de pacote | `sudo dnf install tcpdump wireshark-cli` |
| nftables (`nft`) | ✓ | firewall (preferir sobre iptables) | (base) |
| wireguard-tools (`wg`) | ⬇ | VPN moderna | `sudo dnf install wireguard-tools` |
| ss | ✓ | sockets/conexões | (base) |
| ipcalc | ✓ | cálculo de subnet | `sudo dnf install ipcalc` |
| whois | ⬇ | consulta de registro | `sudo dnf install whois` |
| bandwhich / nethogs | ⬇ | uso de banda por processo | `cargo install bandwhich` / `sudo dnf install nethogs` |
| dog | ⬇ | cliente DNS moderno | `cargo install dog` |

---

## 6. DevOps / Infra (devops-sre)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| docker / podman | ✓ | containers | `sudo dnf install podman` |
| OpenTofu (`tofu`) | ⬇ | IaC (substitui Terraform, FOSS) | script get.opentofu.org |
| ansible | ⬇ | automação de config | `sudo dnf install ansible` |
| kubectl / k9s / helm | ⬇ | Kubernetes (só se houver k8s) | repo k8s / binários |
| just | ⬇ | task runner (substitui makefile de tarefas) | `sudo dnf install just` |
| restic / borg | ⬇ | backup com dedup+cripto | `sudo dnf install restic borgbackup` |
| caddy | ⬇ | reverse proxy + TLS automático | `sudo dnf install caddy` |
| prometheus / loki / vector | ⬇ | métricas/logs/pipeline de telemetria | binários upstream |
| direnv | ⬇ | env por diretório | `sudo dnf install direnv` |

---

## 7. Dados (data-engineer, data-scientist, ml-engineer, CDO)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| duckdb | ⬇ | OLAP local em arquivo (CSV/Parquet/JSON) | binário em duckdb.org |
| sqlite3 | ✓ | DB embutido / análise | `sudo dnf install sqlite` |
| miller (`mlr`) | ⬇ | processar CSV/TSV/JSON em pipe | `sudo dnf install miller` |
| dasel | ⬇ | query JSON/YAML/TOML/CSV unificado | `go install github.com/TomWright/dasel/v2/cmd/dasel@latest` |
| dbt | ⬇ | transformação analítica (ELT) | `pipx install dbt-core` |
| ollama | ✓ | LLM local (respeitar a VRAM disponível) | (instalado conforme necessidade) |
| whisper.cpp | ⬇ | STT local | build github.com/ggerganov/whisper.cpp |

---

## 8. Docs e Diagramas (technical-writer, todos que produzem doc, C-levels)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| pandoc | ⬇ | conversão universal de documento | `sudo dnf install pandoc` |
| mermaid-cli (`mmdc`) | ⬇ | render Mermaid -> SVG/PNG | `npm i -g @mermaid-js/mermaid-cli` |
| graphviz (`dot`) | ✓ | diagrama por grafo | `sudo dnf install graphviz` |
| d2 | ⬇ | diagrama-as-code moderno | script get.d2lang.com |
| plantuml | ⬇ | UML/sequência | `sudo dnf install plantuml` |
| mkdocs-material | ⬇ | site de docs | `pipx install mkdocs-material` |
| hugo | ⬇ | site estático/blog (content-seo) | `sudo dnf install hugo` |
| asciidoctor | ⬇ | doc técnica AsciiDoc | `sudo dnf install asciidoctor` |
| typst | ⬇ | tipografia/PDF moderno (alt LaTeX) | `cargo install typst-cli` |
| vale | ⬇ | lint de prosa/estilo | binário github.com/errata-ai/vale |
| lychee | ⬇ | checar links quebrados | `cargo install lychee` |

---

## 9. Acessibilidade e Web Perf (accessibility-specialist, frontend, content-seo)

| Ferramenta | Status | Para quê | Instalar |
|---|---|---|---|
| pa11y | ⬇ | auditoria a11y automatizada | `npm i -g pa11y` |
| axe-core CLI | ⬇ | a11y WCAG | `npm i -g @axe-core/cli` |
| lighthouse | ⬇ | Core Web Vitals, perf, SEO, a11y | `npm i -g lighthouse` |
| lhci | ⬇ | Lighthouse CI com budget | `npm i -g @lhci/cli` |
| imagemagick (`convert`/`magick`) | ✓ | processar imagem | `sudo dnf install ImageMagick` |
| ffmpeg | ✓ | processar áudio/vídeo | `sudo dnf install ffmpeg` |
| oxipng / jpegoptim | ⬇ | otimizar imagem web | `cargo install oxipng` / `sudo dnf install jpegoptim` |

---

## 10. Negócio: Licença, Finanças, VCS avançado

| Ferramenta | Status | Para quê | Agents | Instalar |
|---|---|---|---|---|
| scancode-toolkit | ⬇ | scan de licença OSS | compliance-legal, CLO, auditor | `pipx install scancode-toolkit` |
| reuse | ⬇ | conformidade de licença (SPDX) | compliance-legal | `pipx install reuse` |
| syft | ⬇ | SBOM (também licenças) | compliance-legal, security | script anchore |
| hledger | ⬇ | contabilidade texto-plano | CFO | `sudo dnf install hledger` |
| gh / glab | ✓/⬇ | CLI GitHub/GitLab | todos | `sudo dnf install gh` ; glab binário |
| jujutsu (`jj`) | ⬇ | VCS moderno sobre git | tech-lead (opcional) | `cargo install jujutsu` |

---

## 11. Kit canônico por agent (usar SEMPRE que a tarefa pedir)

| Agent | Ferramentas canônicas |
|---|---|
| software-architect | dot, d2, plantuml, mermaid-cli, ast-grep, tokei |
| tech-lead | ast-grep, tokei, cppcheck, semgrep, pre-commit, delta |
| backend-engineer | toolchain, ruff/bandit, shellcheck, duckdb/sqlite, jq/yq, httpie, semgrep |
| frontend-engineer | biome, playwright, lighthouse, pa11y, axe |
| mobile-engineer | toolchain nativo, lighthouse (web views), adb |
| devops-sre | podman, tofu, ansible, just, restic, caddy, hadolint, yamllint, age/sops, trivy |
| network-engineer | dig, mtr, iperf3, tcpdump/tshark, wg, nmap, ss, ipcalc, whois |
| network-security-engineer | nft, nmap, suricata, fail2ban, tcpdump/tshark, openssl, lynis, nuclei |
| qa-engineer | pytest, ctest, playwright, hyperfine, k6 |
| performance-engineer | k6, locust, hyperfine, perf, valgrind, heaptrack, py-spy, strace |
| security-engineer | semgrep, gitleaks, trufflehog, trivy, grype, syft, bandit, osv-scanner, nuclei, zaproxy, cosign, openssl |
| data-engineer | duckdb, sqlite, miller, dasel, jq/yq, dbt |
| data-scientist | python (pandas/sklearn), duckdb, py-spy |
| ml-engineer | ollama, whisper.cpp, python ML |
| accessibility-specialist | pa11y, axe, lighthouse |
| technical-writer | pandoc, mermaid-cli, d2, plantuml, vale, lychee, mkdocs |
| content-seo | lighthouse, lychee, wget, hugo, pa11y |
| internal-auditor | lynis, oscap, trivy, semgrep, gitleaks, syft, tokei, scancode |
| compliance-legal | scancode-toolkit, reuse, syft, licensee |

---

## 12. Tiers de adoção

- **Preferir (↺) ao legado:** `rg` sobre grep, `fd` sobre find, `delta` sobre diff, `nft` sobre iptables, `uv`/`pipx` sobre pip global, `biome` sobre eslint+prettier, `ruff` sobre flake8+black, `tokei` sobre cloc, `tofu` sobre terraform.
- **Tier 1 (instalar primeiro, mais usado):** ruff, shellcheck, shfmt, yamllint, vale, semgrep, trivy, syft, pandoc, mermaid-cli, duckdb, yq, miller, hyperfine, delta, pa11y, lighthouse, restic, parallel, entr, tokei.
- **Sob demanda (⬇):** as demais: instale com o comando da linha de cada ferramenta quando a tarefa exigir.

---

## Ver também

- Governança da constelação: [ORG](ORG.md) · pipeline de release: [pipeline_release_1.0](pipeline_release_1.0.md).
- Manuais: [CONTRACT](manuals/CONTRACT.md) · [TESTES](manuals/TESTES.md) · [AGILE](manuals/AGILE.md) · [DEPLOY_CHECKLIST](manuals/DEPLOY_CHECKLIST.md) · [AUDITORIAS](manuals/AUDITORIAS.md).
- Princípios: [limites de hardware](principles/hardware-resource-limits.md).
- O `CLAUDE.md` e o `TODO.md` na raiz do seu projeto definem, respectivamente, as preferências e a fila de pendências locais.
