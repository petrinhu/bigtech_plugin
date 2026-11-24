## [2.1.0] - 2026-11-24

Release de eficácia: o máximo de trabalho útil pelo menor gasto. A constelação segue com **71 agents**; as skills passam a **16**, com a nova `eficacia`. O `hooks/hooks.json` passa a ter **12 entradas em 6 eventos** (SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, Stop e PostToolUse), servidas por **10 scripts**: os 7 em Python de antes e 3 em bash da `eficacia`. Entram também o piso de testes e as regras de trabalho pesado, orquestração, publicação e deploy seguro nos agents, nas skills e nos manuais.

### Added

- **Skill `eficacia`.** Aplica às sessões do Claude Code a conta Eficácia = Disponibilidade × Produtividade, em três modos: `--gerente` (uma sessão exclusiva de gerência, que só age no desvio), `--projeto` (a sessão de projeto se autogerencia, com pré-voo antes de o usuário sair, "enfileire e siga" e relato por exceção) e `--status` (disponibilidade, minutos em espera, tokens e entregas por sessão nas últimas 24 h). A referência traz a matriz de 3 classes de decisão, os detectores verificados e a verificar e a dieta de gasto da gerência.
- **Vigia sem modelo, por timer do sistema.** O `skills/eficacia/bin/vigia.sh` roda sem modelo de IA e offline. O `check` lê os JSONs de sessão e a hora da última mudança dos transcritos, marca cada sessão como ocupada, esperando resposta, travada, morta ou em parada ordenada, grava a passada no `log.tsv` e avisa só o desvio novo, no celular pareado pelo KDE Connect ou na área de trabalho. O `instalar` cria e liga o `bigtech-eficacia.timer` do `systemd --user` (a cada 5 min por padrão, com prioridade mínima), só com o sim do usuário; o `remover` desliga e apaga o timer e o serviço.
- **Trava "líder dormindo", com três hooks novos.** `vigia.sh dormir` liga a bandeira e `vigia.sh acordar` a apaga. Com ela, o hook PreToolUse de `AskUserQuestion` (`hook_lider_dormindo.sh`) nega a pergunta e a grava na fila; o hook PermissionRequest (`hook_permissao.sh`) nega o pedido de permissão e o grava na fila; e o hook Stop (`hook_fim_turno.sh`) bloqueia uma vez o fim do turno e manda a sessão trocar de trabalho (as três saídas do item a seguir), liberando na tentativa seguinte, sem laço. Sem a bandeira, os três saem em silêncio. A negação da pergunta foi verificada ao vivo em 24/11/2026.
- **Três saídas quando a fatia depende da resposta.** Com a pergunta à espera do usuário, a sessão (1) pega um item que não dependa dela, pela coluna Pré-requisito do `TODO.md`; (2) se a escolha for reversível, segue a opção recomendada num ramo próprio, sem merge, sem push no main e sem tag, para o usuário aprovar ou descartar depois, e nunca com o que é irreversível; (3) se nada sobrar, para. O motivo do hook Stop cita essas saídas.
- **Fila, `registrar` e resumo ao acordar.** A pergunta e o pedido de permissão barrados vão a `fila.md`, com hora, sessão e opções, gravados com `flock` para várias sessões ao mesmo tempo. `vigia.sh registrar "<texto>"` anota a decisão de C-level em `decisoes_clevel.md`. Com a bandeira, o `check` não avisa o celular e grava os desvios em `desvios_noite.md`. `vigia.sh acordar` mostra tudo agrupado por sessão e move os três arquivos para `arquivo/<data-hora>/`, sem apagar nada.
- **Bandeira automática pela tela bloqueada.** Com a tela bloqueada há mais de `bandeira_auto_min` minutos (padrão 30, lido pelo `loginctl`), o `check` liga a bandeira sozinho; no desbloqueio, apaga só a bandeira automática e roda o `acordar`. A bandeira manual nunca se apaga sozinha, e `"bandeira_auto_min": 0` desliga a automática.
- **Proteções da `eficacia`.** Um sanitizador único, `bin/limpa_texto.py`, tira todo caractere de controle, inclusive escape de terminal e override bidi, antes de qualquer texto chegar à fila, às decisões, aos desvios ou à tela do `acordar`. O `vigia.sh status` conta as entregas com `git` endurecido (sem fsmonitor, hooks nem verificação de assinatura) e só em `.git` do próprio usuário. Todo campo numérico é validado antes da aritmética do bash. Os testes ficam em `skills/eficacia/tests/`.
- **Deploy seguro** em `release-manager`, `devops-sre`, `proj_software` e `proj_jogo`: smoke curto depois do deploy, com rollback automático depois de duas falhas seguidas; erro em produção vira aviso ao usuário; o Dependabot abre a atualização de segurança, o CI a testa e o usuário aprova; a parte pela metade sobe desligada, atrás de uma chave de recurso; o ramo de cada parte dura no máximo um dia. (EFIC-2)
- **Máquina compartilhada por vários agentes.** A seção 11 de `docs/principles/hardware-resource-limits.md` traz um trabalho pesado por vez numa trava única, núcleos reservados ao sistema, teto de memória e de processos por trabalho, ajustável por projeto, prioridade mínima para agente, a publicação fora da fila e espera sem laço. Os 16 agents que planejam ou rodam build, suíte, teste de navegador e contêiner ganham o resumo dela, e o `docs/principles/anti-patterns.md` ganha "Diagnóstico e testes". (EFIC-1)
- **Ordem de serviço e entrega.** Os 12 C-levels ganham "Ordem de serviço": decidem e escrevem a ordem fechada, sem editar arquivo. Os 59 operacionais ganham "Entrega": entregam o SHA no ramo e param, pausam num ponto limpo e relatam curto. `bigtech`, `proj_software` e `proj_jogo` ganham orquestração, verificação seletiva (uma verificação não pode custar mais que a mudança que ela confere) e publicação uma parte por vez. (EFIC-1)
- **Build nativo (C/C++, CMake, Qt)** nos 11 agents de engenharia que compilam ou planejam código nativo e em `proj_software` e `proj_jogo`: ccache comum às worktrees, build fora da árvore, ctest seletivo pelo grafo do CMake, widget Qt offscreen no host e pacote só na tag. (EFIC-1)
- **CI: push só de docs pula os testes.** O job `mudanca` compara o push com a base e pula os testes quando só mudaram arquivos que nenhum teste nem portão lê; o job novo `privacidade` roda o `validate_plugin.py` em todo push, e o gitleaks segue sem filtro. A execução de tag nunca é cancelada. (EFIC-1)

### Changed

- **Piso de testes.** Teste só para lógica de produto. Com CI na nuvem, o CI é o portão, uma vez, depois do push; sem ele, o pré-CI seletivo é o portão. Mutação, sabotagem, auditoria e portão local novo ficam só para segurança, privacidade e deploy irreversível. Agents, skills e os manuais `TESTES`, `AUDITORIAS` e `CONTRACT` passam a dizer isso. A `tab_pendencias` deixa de injetar itens de teste e auditoria e de criar `TESTES.md` e `AUDITORIAS.md` por padrão (o `--add_tests_audit` os acrescenta a pedido), e o item passa a concluído quando o CI do ramo fica verde. (PISO-1)
- **CI do próprio plugin.** No job de testes, o Ubuntu roda só o `preci.sh`, e os passos de portão ficam no Windows; os contêineres Debian, Fedora e Arch rodam só na tag; saem os testes que só conferiam texto, contagem ou paridade de documentação, e os de lógica dos hooks ficam. O `preci.sh` fica com os 9 portões do CI e deixa de ser exigido antes do push. (PISO-1)
- **Merge por agente operacional.** Na "Entrega" dos agents e nas skills `bigtech`, `proj_software` e `proj_jogo`, o merge no principal passa a ser feito por um agente operacional, e o main revisa.
- **Lembrete por turno em no máximo 2 linhas.** O `bigtech_reinforce.py` injetava 942 caracteres a cada prompt no modo classificado e 877 no roteamento; agora cada um cabe em 2 linhas e 240 caracteres. O texto longo fica só no SessionStart, uma vez por sessão. (EFIC-2)
- **`olhe_agentes` cede ao timer.** Com o `bigtech-eficacia.timer` ativo, o `--on` não arma o tick de 5 minutos e sugere `/bigtech:eficacia --gerente`, para não haver dois ciclos.
- **Opções com `--` em quatro skills.** `/bigtech:eficacia --gerente|--projeto|--status`, `/bigtech:olhe_agentes --on|--off|--status`, `/bigtech:manter_ligado --on|--off|--status|--limpar` e `/bigtech:watchcode --on|--off|--status`. A forma antiga, sem `--`, continua aceita.
- **Agents de leitura.** `internal-auditor` e `revisor-textual` ficam só com ferramentas de leitura (o auditor também com WebFetch e WebSearch), sem Edit, Write nem Bash, no effort do grupo; o `linux-diag` ganha `effort: low` e mantém o Bash só para leitura. (EFIC-1)
- **Rito irreversível de 7 fases** só para login, permissão, token, segredo, apagar dado, schema de banco e rotação de chave, nos agents, nas skills e no `DEPLOY_CHECKLIST`; no `devops-sre`, também para firmware gravado em aparelho, sistema embarcado e contrato externo final. (EFIC-1)
- **Manuais em `docs/house`** sincronizados com o vault (`sync_house.py --write`, HMAC): piso de testes, trava com fila e teto, ordem de serviço, ramo de um dia, smoke com rollback e os agents de leitura no ORG. (PISO-1, EFIC-1)
- **Contagens e portões.** 16 skills no README, no LLM.md e no portão de drift (`EXPECTED_SKILL_COUNT` de 15 para 16); o smoke offline espera 12 hooks na forma exec, com `python3` ou `bash`.
- **Documentação.** O README (EN e PT) lista os hooks novos; o PRIVACY descreve o que o vigia lê e grava e o aviso ao celular; o SECURITY descreve os hooks novos, o timer permanente, o sanitizador e como desligar tudo.

## [2.0.0] - 2026-11-20

Release de consolidação do plugin. A constelação passa a ter **71 agents** (12 C-level e 59 operacionais) e **15 skills**. Esta versão absorve o bloco `[Unreleased]`, que estava sem tag: a versão 0.2.1 nunca foi publicada. Campanha 2026-08-16 fechada, tag de marco: [campanha/2026-08-16-fechada](https://github.com/petrinhu/bigtech_plugin/releases/tag/campanha/2026-08-16-fechada). Índice dos relatórios: [docs/campanha/README.md](docs/campanha/README.md).

### Breaking

- **`AGENTS.md` virou `LLM.md`.** Não há arquivo de ponte. Ferramentas que procuravam `AGENTS.md` sozinhas (Codex, Cursor e outras) deixam de encontrá-lo; atualize as referências.
- **Suporte ao Grok saiu do plugin.** Saem a seção de instalação do Grok, o selo "Grok-compatible" e as instruções de Grok de README, LLM.md, documentação, scripts e testes. O plugin passa a ser só para Claude Code. As entradas antigas deste changelog continuam citando o Grok como histórico.

- **`github-gossips` saiu do plugin.** Continua disponível fora do plugin; o plugin não registra mais o servidor dele. O `pubmed` saiu do bundle `bigtech-completo`.

### Added

- **Pacote `bigtech-completo` com o aviso de dependência.** Traz o `bigtech` mais `playwright`, `superpowers`, `frontend-design` (marketplace `claude-plugins-official`). Sem o marketplace adicionado antes, o pacote fica instalado e não carrega. Recusar as dependências é instalar só o `bigtech`. O aviso aparece no README (EN e PT), no LLM.md e na descrição do painel. (CONS-16)
- **Aviso de dependência no início da sessão.** O hook `bigtech_session_init` mostra só as dependências recomendadas que faltam, nomeando cada uma. (CONS-14)
- **Três skills novas:** `watchcode` (vigia journal e coredumps e captura crashes), `manter_ligado` (só Linux com systemd), `olhe_agentes` (monitor de agents). (CONS-09W, CONS-09G, CONS-09S)
- **20 agents novos:** o time de desenvolvimento de jogos (entre eles `gameplay-engineer`, antes `gameplay_engineer`), os agents médico-periciais e jurídicos, o pedagógico, o literário e os de diagnóstico. (CONS-06, CONS-07)
- **Skills que chamam os agents entram no plugin:** `dr-advogado`, `dr-medico-perito`, `dr-medico-psiquiatra`, `dr-medico-trabalho`, `learning-designer`, `pericia-medica`, `proj_jogo` e `suporte-linux`. (CONS-09)
- **Skill `tab_pendencias` de volta ao plugin**, sob Apache-2.0, com a escrita de estado endurecida (inbox, journal, lock e sync recusam symlink e diretório alheio). Desfaz a remoção descrita no bloco anterior. (CONS-05, CONS-05S)
- **Manuais em `docs/house/`**, cópia única do vault com transformação só de privacidade, e a regra de que as instruções do usuário prevalecem sobre o plugin. (CONS-10, CONS-04A)
- **Ícone do plugin** pelo art-director. (CONS-11A)

- **BT-8: evals offline de roteamento `/bigtech`.** Suite em `evals/bigtech_routing/` (`cases.json` CASE-A..D + portes, `run_evals.py` stdlib, README). Política pós-BT-5: perfis `early|scale|bigtech`, piso early, nunca `solo` como perfil, headcount peso 0, criticidade eleva agents (CISO/CLO). Gate no `scripts/preci.sh` e no CI multi-OS (`python3 evals/bigtech_routing/run_evals.py`). Não substitui eval LLM real; é harness de política de classificação.
- **BT-7: gate de drift semântico.** Registry/agents/skills alinhados; falha no CI/`preci` se o inventário canônico divergir do pacote.
- **BT-4: CI multi-OS no GitHub Actions.** Matrix ubuntu/windows + containers debian/fedora/arch + gitleaks; smoke offline e gates de campanha.
- **BT-1: ADR de fonte da verdade (SoT).** Classificação dual-authority e critério de o que é produto vs overlay pessoal.
- **BT-2: manuais da casa em `docs/house/`.** Sync dos 10 manuais canônicos do vault para quem consome o plugin sem vault local.
- **BT-6: inventário dual-authority + plano de cutover.** CSV/MD de inventário e plano de cutover opcional de `~/.claude` (canário; sem cutover automático na campanha).
- **BT-9: branch protection em `main`.** Gates de CI obrigatórios no remoto GitHub.
- **Docs de campanha.** Relatórios PHASE 0, verificações BT-0..BT-9, TST-BT-1, AUD-BT-1 em `docs/campanha/` (índice no README da pasta).

### Changed

- **Contagens e roteamento:** 71 agents, 15 skills, com o roteamento do Cósimo e os evals alinhados. (CONS-12, CONS-12C)
- **Versão 2.0.0** em `plugin.json`, `marketplace.json` e no `bigtech-completo`. (CONS-16)
- **`model: inherit`** nos agents: quem despacha escolhe o modelo, dentro das regras do usuário.
- **Padrões que mudam para todos** (decisões do líder): TDD em código de comportamento, sem número-meta de cobertura; biblioteca, modelo, extensão e navegador só com permissão; sem captura da tela nem navegador na sessão viva; sem emoji em modelos de documento; saídas de escape do `tdd_guard` removidas da mensagem ao modelo. (CONS-15)
- **Hook do `tab_pendencias`:** um só lembrete de `TODO.md`, sem comando inexistente. (CONS-14, CONS-14A)

- **BT-5: porte arquitetural sem solo/headcount (piso early).** Valores canônicos de porte = `early | scale | bigtech`. Headcount/capacity humana é nota auxiliar, não valor de `--porte` nem de `.bigtech-porte`. Skill `/bigtech`, hooks `bigtech_porte_reminder`/`bigtech_reinforce`, Cosimo, `docs/ORG.md`, `pipeline_release_1.0`, `lideranca_pipeline_release`, mapeamento em `/proj_software` e `/tab_pendencias` alinhados. Alias deprecado: `--porte solo` e marcador legado `porte=solo` normalizam para `early` (hooks expõem `early` sem reescrever o arquivo). Pipeline-Sprint renomeado operacionalmente para Pipeline-Early (early minimalista).
- **BT-3: host git só GitHub.** `origin` -> `github.com/petrinhu/bigtech_plugin`; remoção de `.forgejo` e purga operacional de Codeberg/Forgejo/Woodpecker em paths de produto e install.

### Fixed

- **`proj_software`: cópia do plugin alinhada à decisão do líder de 2026-08-18.** A thread principal nunca codifica, em nenhum nível (S0 incluído); a cópia do plugin ainda dizia "Main thread codifica direto" em S0, "main thread + 2-3 sob demanda" em S1 e mandava o deploy para a main thread no S1. Agora `skills/proj_software/SKILL.md` é cópia integral da versão global, e o plugin passa a ser a fonte única dessa skill.
- **`tab_pendencias_reminder`: fim do lembrete duplicado quando o produto standalone está ligado.** O `tab_pendencias` virou produto standalone (repo próprio, GPL-3.0) e o motor de sinais dele reescreveu, em 2026-08, os gatilhos 1 (CRIAR) e 2 (STALENESS) que nasceram neste hook em 2026-06. Com os dois registrados, cada `SessionStart` e cada `UserPromptSubmit` emitiam **duas** mensagens de mesmo teor. Agora o hook detecta se o produto está registrado nas settings do usuário e, nesse caso, **cede a ele os gatilhos 1 e 2**, mantendo só o que o produto não tem: o carimbo de sessão (3) e o nudge de tempo de sessão (4). Instalação **só-plugin** (sem o produto) mantém o comportamento legado integral. Override: `BIGTECH_TAB_REMINDER=full` (nunca cede) / `off` (não emite nada) / `auto` (padrão). Duas lacunas conhecidas da cessão estão documentadas no cabeçalho do hook em vez de perdidas em silêncio: projeto com `.bigtech-porte` fora de repo git, e `TODO.md` defasado sem nenhum item ⏳/🔄.
- **Privacidade na árvore:** `scripts/sync_house.py` e o portão de `docs/house` não carregam caminhos nem nomes pessoais. (CONS-04B)
- **`docs/principles/anti-patterns.md`:** a regra de amend local foi trocada por "sem reescrever commit; correção em commit novo". (CONS-17)

### Removed

- **Suporte ao Grok** (ver Breaking).
- **Remoção de `skills/tab_pendencias/`** descrita no bloco anterior: revertida; a skill volta ao plugin (ver Added).

### Verified (campanha)

- **TST-BT-1:** revalidação da suite de campanha - PASS.
- **AUD-BT-1:** auditoria de campanha W7 - APROVADO 96/100; sem cutover de `~/.claude`.

## [0.2.0] - 2026-06-21

Release de agnosticismo de sistema operacional (Linux, macOS e Windows nativo) e da política de ferramenta ausente como doutrina transversal. **As contagens não mudam: a constelação segue em 51 agents e 4 skills** (badges inalterados). Novo arquivo no pacote: `bin/python3.cmd` (shim de referência para Windows).

### Added

- **Shim `bin/python3.cmd` para Windows nativo.** Arquivo de referência que encaminha o comando `python3` para `py -3` (e, em falha, para `python`), cobrindo o caso do instalador do python.org, que provê `python`/`py` mas não garante o nome `python3` exigido pelos hooks. O usuário coloca o shim num diretório do PATH (ex.: `%LOCALAPPDATA%\Microsoft\WindowsApps`); o Python da Microsoft Store já registra o alias `python3` e dispensa o shim.
- **Doutrina "política de ferramenta ausente" (`docs/principles/missing-tool-policy.md`) propagada como regra transversal dos agents.** Híbrido por risco: o agent detecta o SO e autoinstala ferramentas FOSS de userland sem privilégio (`pip`/`uv`, `cargo`, `npm`/`pnpm`, binário no `$HOME`) ou oferece via AskUserQuestion as que exigem `sudo`/gerenciador do sistema, e **nunca recusa uma tarefa por falta de ferramenta** (a única não-execução é a recusa explícita do usuário, que pausa só aquele passo). O arquivo é autolistado no `SessionStart` pelo glob `principles/*.md`, então a doutrina entra em contexto no início de toda sessão. Fonte única do protocolo; o `docs/TOOLING.md` permanece como catálogo do comando de cada ferramenta.
- **Guia de instalação e dependências por SO, para usuários e para o LLM.** O `README.md` (EN+PT) ganha a nota "Pré-requisitos por SO" na seção de instalação; o `AGENTS.md` (EN+PT) ganha a seção "Dependências e instalação por OS" dirigida ao agente instalador; e a página `Instalacao` da wiki (EN+PT) ganha o "Passo 0: pré-requisitos por sistema operacional", em registro didático para iniciante. Os três cobrem o pré-requisito-chave: **`python3` resolvível no PATH**, com o caminho por SO - Linux (quase sempre presente; senão `apt`/`dnf`/`pacman`/`zypper`), macOS (`xcode-select --install` ou `brew install python`) e Windows nativo (Microsoft Store que registra o alias `python3`; instalador python.org mais o shim `bin/python3.cmd` no PATH; ou WSL), sempre com verificação por `python3 --version`. Documentam também que as dependências companion (`superpowers`, `playwright`, `frontend-design`) são instaladas pelo próprio Claude Code (cross-OS) e que as ferramentas de runtime dos agents são tratadas automaticamente pela missing-tool-policy.

### Changed

- **Hooks declarados na forma exec com `command: "python3"`.** O `hooks/hooks.json` invoca os 6 hooks chamando o interpretador pelo nome `python3` (decisão de portabilidade), o que torna **`python3` resolvível no PATH** o único pré-requisito de sistema do plugin. As notas de Plataforma do `README.md` e da wiki (EN+PT) passam a explicitar esse pré-requisito e a apontar para o guia por SO, em especial a nota de Windows, em vez de afirmar que nenhuma configuração de SO é necessária.
- **Notas de portabilidade agnóstica de SO reforçadas nos docs.** O `docs/TOOLING.md` mantém a nota de portabilidade dos comandos (adaptar `apt`/`dnf`/`pacman`/`zypper`/`brew`/`winget`/`scoop`/`choco`, preferir cross-platform `pip`/`uv`, `cargo`, `npm`/`pnpm`) e as marcas "Linux-only" nas ferramentas mono-OS (perf, valgrind, heaptrack, strace/ltrace) com o equivalente de mac/Windows ou WSL. As páginas user-facing passam a deixar claro que a constelação roda em Linux, macOS e Windows nativo, com TDD e design visual incluídos.

## [0.1.16] - 2026-06-20

Release de currency das ferramentas declaradas no frontmatter dos agents. **Nenhuma contagem muda: a constelação segue em 51 agents e 4 skills** (badges inalterados). Só a linha `tools:` de cada agent foi tocada; `claude plugin validate --strict` continua verde.

### Changed

- **Currency de ferramentas nos 51 agents - alinhamento com a tools-reference oficial do Claude Code.** A ferramenta `TodoWrite` (desabilitada por padrão desde a v2.1.142) foi substituída pelo quarteto `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate`, e a `TaskOutput` (depreciada; a doc orienta "Prefer Read") foi removida. Achado da auditoria de conformidade contra a documentação oficial. A alteração é restrita à linha `tools:` do frontmatter de cada agent: nenhuma capacidade some, apenas passa a ser declarada com os nomes vigentes; o corpo dos agents, o roteamento dos C-level e as contagens (51 agents, 4 skills) seguem intactos.

## [0.1.15] - 2026-06-20

Release de frescor da tabela de pendências. **Não há novo agent nem nova skill: as contagens seguem em 51 agents e 4 skills** (badges inalterados). O frescor entra como **convenção** (status mecânico no commit, reordenar à parte), não como ferramenta: **o toolkit de git hooks de sincronização não foi incluído nesta release**.

### Added

- **Convenção "Frescor da TODO.md em commits" embarcada nos 12 agents de implementação.** Os agents `backend-engineer`, `frontend-engineer`, `mobile-engineer`, `embedded-firmware-engineer`, `hardware-engineer`, `software-architect`, `tech-lead`, `devops-sre`, `data-engineer`, `ml-engineer`, `applied-ai-engineer` e `qa-engineer` passam a declarar a regra: ao commitar trabalho que fecha ou avança um item da tabela de pendências (`TODO.md`), citar o ID do item (ex.: `V-12`, `F1.4`) na mensagem do commit (corpo ou footer do Conventional Commit) e tocar a coluna `Status` no mesmo commit (implementação entregue vira `🔍 Pendente verificação`, NUNCA `✅` direto; `✅` só após a onda de teste/auditoria). Marcar status é edição manual de uma célula e nunca dispara o time de agents.
- **Seção "Frescor" e INBOX na skill `tab_pendencias`.** A `SKILL.md` ganhou a seção "Frescor: manter a tabela viva no sprint", que separa as duas operações de naturezas opostas - sincronizar status (mecânico, barato, frequente, no commit) e reordenar (julgamento, caro, raro, só via `--reorder` quando um input de priorização muda) - mais a subseção INBOX (captura imediata de trabalho novo em 1 linha, drenada pelo `--create`/`--reorder`; arquivo-por-descoberta em `inbox/` sob worktrees paralelos; conflito resolvido sempre por união). Reforça que a convenção vale no `TODO.md` de projeto, não no hub agregador.
- **Documento `docs/tabela-pendencias-frescor.md`.** Novo doc de governança (Diátaxis: explanation + reference) que registra a causa-raiz da defasagem, a distinção status (mecânico) vs prioridade (julgamento), o Definition of Done de status (implementação entregue → `🔍 Pendente verificação`; `✅` só pós-teste/auditoria), a INBOX e uma escada de escalonamento opcional apresentada de forma genérica (aviso de frescor no CI, rotina agendada determinística, fonte-da-verdade em issues do repositório), cada camada condicional a evidência de que o mínimo falhou. README e `AGENTS.md` (EN e PT) passam a citar a convenção de frescor onde documentam a skill `/tab_pendencias`, com link para o novo doc.

### Changed

- **Fiação do `visual-design-director` nas tabelas de delegação de Capitolino/CPO e Caetano/CTO.** O agent de design visual (introduzido na 0.1.14) passa a constar explicitamente nas tabelas de delegação dos dois C-level que o acionam: Capitolino (CPO) para o design da Fase 3 e Caetano (CTO) para o handoff de implementação. Ajuste de consistência entre o catálogo e o roteamento dos C-level; nenhuma contagem muda.
- **Mensagens do hook `tab_pendencias_reminder` refinadas.** Os avisos passam a distinguir com clareza as duas ações: **atualizar o `Status`** (mecânico, barato, faça você mesmo no commit que fecha o item) versus **reordenar a tabela** (julgamento do time, só com input de priorização novo). O comportamento do hook não muda - continua somente-leitura e fail-open, só lembra, nunca bloqueia nem reordena -, apenas o texto fica alinhado à convenção de frescor.

## [0.1.14] - 2026-06-20

### Added

- **Novo agent `visual-design-director` (Diretor de Design Visual).** Operacional (cor azul), na família Produto/UX e Design. Conduz design visual de **alta fidelidade renderizado**: pesquisa tendências do domínio, faz brainstorm dirigido (uma pergunta por vez, opções A/B/C), escreve mockups HTML/CSS com conteúdo real do produto e os **abre no navegador do usuário**, itera por seção via screenshot (paleta, navegação, componentes, tabelas, gráficos, estados, tela a tela) e entrega spec versionada em `docs/` (tokens light+dark com hex, decisões e por tela) mais o handoff. Reporta a Capitolino/CPO (design, Fase 3) e a Caetano/CTO (handoff). Distinto do `ux-ui-designer` (jornada, IA, wireframe, design-system textual) e do `art-director` (identidade visual, mood board, style guide); aqui é pixel renderizado e validado no browser. Complementa ux-writer, ux-researcher e accessibility-specialist; delega a implementação ao `frontend-engineer`. Acionável pela skill `/bigtech` quando o porte do projeto pede design dedicado.
- **Nova skill `/visual-design-director`.** Atalho que delega ao subagent homônimo para design visual de alta fidelidade renderizado.
- **A constelação passa a ter 51 agents e 4 skills.** Os operacionais sobem de 38 para 39 (a família Produto/UX e Design vai de 7 para 8) e as skills de 3 para 4. Os badges do README (`agents-51`, `skills-4`), o catálogo de agents (README), o `AGENTS.md` (EN e PT) e a constelação no `docs/ORG.md` foram atualizados. As 3 skills de orquestração (`/bigtech`, `/proj_software`, `/tab_pendencias`) seguem como pontos de entrada principais; `/visual-design-director` é a 4ª skill, no formato de atalho de agent.

## [0.1.13] - 2026-06-17

### Changed

- **`tab_pendencias_reminder` vira detector de defasagem da tabela.** Antes o hook só lembrava de criar o `TODO.md` (via `/tab_pendencias --create`) num projeto classificado (`.bigtech-porte`) mas sem a tabela. Agora, com a tabela presente, ele mede a defasagem real rodando `git` em modo somente-leitura: conta quantos commits e quantos dias se passaram desde o último toque no `TODO.md` e avisa quando os limiares são ultrapassados. O lembrete histórico de criar a tabela continua igual. O hook nunca reordena a tabela sozinho (reordenar exige o time de agents da skill `/tab_pendencias`); tudo é fail-open (qualquer erro não avisa e nunca bloqueia). O número de hooks não muda (continuam 6; o badge `hooks-6` permanece).
- **Wiring do hook em `UserPromptSubmit`.** Além do `SessionStart`, o `tab_pendencias_reminder` passa a disparar também em `UserPromptSubmit` para dar, após uma sessão longa com `TODO.md` presente, um nudge único de higiene (revisar e reordenar a tabela).

### Added

- **Config opcional `.tab-staleness.json` na raiz do projeto.** Ajusta os limiares do detector de defasagem (defaults embutidos): `commits` e `dias` para o gatilho de staleness, `modo` (`"e"` exige os dois limiares, `"ou"` basta um), `horas_sessao` para o nudge de sessão longa e `off: true` para desligar os gatilhos de staleness e de sessão (o lembrete de criar a tabela continua ativo).
- **Testes da nova lógica do hook.** A suíte de testes do `tab_pendencias_reminder` foi reescrita para cobrir os três gatilhos (criar, staleness por `git`, nudge de sessão longa), a leitura da config `.tab-staleness.json` e os caminhos fail-open. A suíte total passou a ter 141 testes (os testes do hook antigo foram substituídos pelos 15 da reforma).

## [0.1.12] - 2026-06-17

### Fixed

- **Fail-open dos três reminders de sessão quando o `stdin` não é um dicionário.** Os hooks `bigtech_porte_reminder.py`, `tab_pendencias_reminder.py` e `bigtech_session_init.py` tratavam um payload de `stdin` não-dict (lista, número ou JSON malformado) como erro e saíam com código 1, gerando ruído de "hook error" no terminal; agora absorvem o caso e seguem o turno sem interromper. Achado da auditoria de corretude dos hooks.
- **`conftest.py` aninhado classificado como código de produção.** A heurística que distingue arquivo de teste de arquivo de produção marcava um `conftest.py` fora da raiz de testes (em subdiretório aninhado) como produção, fazendo o `tdd_guard` bloquear indevidamente a edição no modo TDD; a classificação passa a reconhecê-lo como suporte de teste.
- **Falso-bloqueio do `tdd_guard` por erro de I/O.** Uma falha ao ler ou gravar o estado do TDD (arquivo de estado inacessível, permissão negada) podia ser interpretada como ausência de teste vermelho e barrar a escrita de produção; o guard passa a fazer fail-open diante de erro de I/O, permitindo a edição em vez de travar o trabalho.
- **Falsos positivos do regex de roteamento do `bigtech_reinforce`.** O padrão que detecta ativação por linguagem natural para `/bigtech` casava trechos que apenas continham a substring (por exemplo dentro de outra palavra), roteando pedidos que não eram de ativação; o regex foi ancorado para casar só a intenção real. Achado da mesma auditoria.

### Added

- **Testes para os caminhos de falha antes sem cobertura.** A suíte ganhou casos para o fail-open dos reminders com `stdin` não-dict, a classificação do `conftest.py` aninhado, o fail-open do `tdd_guard` por erro de I/O e os limites do regex de roteamento, fechando as lacunas apontadas pela auditoria de corretude dos hooks.
- **Aviso de segurança no README (EN+PT) sobre o `tdd_runner`.** A seção de Segurança/Security explicita que o modo TDD é opt-in (só liga com `.claude/tdd-guard.json` presente) e que, quando ligado, o `fast_command`/`test_command` do projeto é executado como comando de shell após cada edição; orienta a tratar esse arquivo como código confiável e a não ativar o modo TDD em repositório de terceiro não-confiável. Linha equivalente espelhada no `SECURITY.md`.

## [0.1.11] - 2026-06-17

### Added

- **Campos `$schema` e `displayName` no `.claude-plugin/plugin.json`.** O `$schema` (`https://json.schemastore.org/claude-code-plugin-manifest.json`) habilita autocomplete e validação do manifesto no editor; o `displayName` (`"Bigtech"`) é o nome legível exibido no seletor `/plugin`. Ambos os campos são opcionais e não afetam o carregamento do plugin.

### Changed

- **Campo `$schema` do `.claude-plugin/marketplace.json` corrigido.** Antes apontava para `https://anthropic.com/claude-code/marketplace.schema.json`, uma URL que não resolvia; agora usa o schema canônico do SchemaStore (`https://json.schemastore.org/claude-code-marketplace.json`). O Claude Code ignora esse campo em runtime; o ganho é autocomplete e validação no editor. Ajuste cosmético e não-breaking, fruto da auditoria de conformidade contra os parâmetros oficiais da Anthropic (o validador `claude plugin validate --strict` já passava).

## [0.1.10] - 2026-06-16

### Added

- **Seção "Direção de design distintivo" no agent `frontend-engineer`.** Os princípios da skill `frontend-design` da Anthropic (pensar tom, tipografia, cor, motion, composição e fundos antes de codar; recusar o look genérico de IA) passam a estar embarcados no corpo do agent, porque um subagent não invoca skill nativamente. Aplicam-se sempre que a tarefa cria ou redesenha interface visível, em conjunto com os cuidados de performance, acessibilidade e responsividade (não como troca).

### Changed

- **README (EN+PT) passa a recomendar a skill `frontend-design` da Anthropic para trabalho de UI.** Quando a constelação constrói ou reformula interface (`ux-ui-designer`, `art-director`, `frontend-engineer`, `accessibility-specialist`), a skill ajuda a produzir design visual distintivo em vez de padrões genéricos de template. Recomendação bilíngue (inglês internacional e pt-br), com link canônico para `https://github.com/anthropics/skills` e os comandos `/plugin marketplace add anthropics/skills` + `/plugin install example-skills@anthropic-agent-skills`.
- **`AGENTS.md` e a wiki (Instalação) passam a recomendar a skill `frontend-design`.** A recomendação "instale se ainda não estiver instalada" entra junto das dependências sugeridas, em inglês e português, com os comandos de instalação a partir do plugin `example-skills` do marketplace `anthropic-agent-skills`. A página de wiki do agent `frontend-engineer` ganha o resumo didático da nova seção.

## [0.1.9] - 2026-06-14

### Added

- **Política "ferramenta ausente" canonizada.** Os manuais `TESTES.md` e `AUDITORIAS.md`, o catálogo da skill `tab_pendencias` (e os templates que ela gera) e a `SKILL.md` passam a declarar a regra: ao executar um teste (TST-*) ou auditoria (AUD-*) cuja ferramenta requerida não está instalada, o agente oferece instalá-la com a confirmação do usuário (via AskUserQuestion), nunca em silêncio e nunca pulando o item sem avisar.

### Changed

- **Portabilidade agnóstica de sistema operacional (Linux, macOS, Windows nativo ou WSL).** Os manuais e o `docs/TOOLING.md` passam a tratar detecção e instalação adequadas ao SO (apt/dnf/brew/winget/choco/scoop), preferindo gerenciadores cross-platform (pip/uv, cargo, npm/pnpm). O `README.md` e a wiki (Instalação, Uso) ganham nota de Plataforma e da política, em inglês e português.

## [0.1.8] - 2026-06-14

### Changed

- **README.md passa a recomendar o plugin companheiro `superpowers`.** A suíte de skills de engenharia da Anthropic é apresentada como complemento que se integra bem ao bigtech, com instrução de instalá-la antes do bigtech. A recomendação é bilíngue (inglês internacional e pt-br), com link canônico `https://claude.com/plugins/superpowers` e o comando `/plugin install superpowers@claude-plugins-official`.

## [0.1.7] - 2026-06-14

### Changed

- **Remediação completa da auditoria de 9 dimensões (31 achados).** Acentuação pt-br restaurada nos hooks, no `README-tdd.md`, nas skills e no catálogo de auditorias; índices dos manuais `AUDITORIAS.md` e `TESTES.md` reparados; `SECURITY.md` passa a refletir os 6 hooks de fato; em-dash de prosa removido do conteúdo distribuído. Sincronização com os fontes: a regra de porte "nunca rebaixa para solo / piso early" agora consta no Chief of Staff e nos agents, e a skill `tab_pendencias` ganhou o gate por complexidade.

### Added

- **Cobertura de testes dos hooks de governança e do `tab_pendencias_reminder`.** A suíte de testes cresceu para 97. CI com 8 gates, incluindo o `claude plugin validate --strict` oficial e a paridade de versão entre os manifestos (`plugin.json` == `marketplace.json`).
- **README e AGENTS.md bilíngues.** Ambos passam a trazer inglês internacional e pt-br no mesmo arquivo.
- **Acessibilidade dos docs.** Texto alternativo (`alt`) no badge de CI e alternativa textual aos diagramas Mermaid.
- **Releases formais retroativas 0.1.0 e 0.1.1.** Publicadas para fechar o histórico de tags do projeto.

## [0.1.6] - 2026-06-14

### Added

- **Hook `tab_pendencias_reminder` (SessionStart).** Lembra de gerar a tabela de pendências (`TODO.md`) via `/tab_pendencias` quando o projeto já foi classificado pelo `/bigtech` (marcador `.bigtech-porte`) mas ainda não tem a tabela. Sempre sai sem bloquear (só lembra). Agora são 6 hooks (badge `hooks 6` no README).
- **Pre-flight de tabela de pendências nos 50 agents.** Ao serem acionados, os agents checam o `TODO.md` na raiz: os C-level o exigem como pré-condição no mapa de ativação; os operacionais sinalizam caso falte e seguem com a tarefa.
- **Coluna Ferramentas no catálogo de auditorias** da skill `tab_pendencias` (ex.: lcov/gcov em AUD-COV).

### Changed

- **Pacote enxuto para distribuição.** Artefatos de construção e processo saíram do pacote público (agora gitignored, mantidos só localmente): `docs/superpowers/` (spec, template de higienização e relatório de auditoria, que continham nome do autor e wikilinks de exemplo) e os artefatos de planejamento `TODO.md`, `TESTES.md` e `AUDITORIAS.md` da raiz. Os manuais de governança em `docs/manuals/` permanecem. O distribuível passa a ter zero PII e zero wikilinks.

## [0.1.5] - 2026-06-13

### Fixed

- **Badge de release no README.** O badge de versão apontava para `v0.1.2` (não fora atualizado nos lançamentos 0.1.3 e 0.1.4). Na época passou a usar badge dinâmico de release no host anterior (legado, removido); o canônico é GitHub Releases.

### Changed

- **CI no runner lazy do host anterior.** O workflow de CI do host legado (removido) passou a rodar em pool lazy (carga flexível) após o runner standard ficar longos períodos em fila.

## [0.1.4] - 2026-06-13

### Changed

- **`AskUserQuestion` no `tools` dos 50 agents.** Todos os agents passam a declarar a ferramenta `AskUserQuestion` no frontmatter, corrigindo a inconsistência de o corpo já instruir "pergunte via AskUserQuestion" (regra de autoridade do líder supremo) sem a ferramenta estar disponível. Em foreground o agent pode perguntar ao usuário diante de dúvida ou decisão de alto valor; em background é no-op.

## [0.1.3] - 2026-06-13

### Added

- **Badges no README.** Conjunto curado em estilo `for-the-badge`: Claude Code, Python, licença, release, status de CI (vivo, via o CI do host da época; legado) e contadores de agents, skills e PRs.
- **Aviso de compatibilidade.** O README, o `AGENTS.md` e os 50 agents passam a destacar que o plugin é feito para o Claude Code (Anthropic) e que não há garantia de funcionamento em outros assistentes ou CLIs de código (por exemplo, Grok, Gemini CLI, GitHub Copilot CLI, OpenAI Codex, Cursor ou Aider).

## [0.1.2] - 2026-06-13

### Fixed

- **Conformidade 100% com `claude plugin validate --strict` e `claude plugin tag`.** Resolvidos os dois únicos avisos restantes do empacotamento.
- **`description` do marketplace.** Adicionado o campo `description` no nível raiz do `marketplace.json` (o aviso "No marketplace description provided" reprovava o `--strict`).

### Changed

- **`CLAUDE.md` da raiz renomeado para `DEVELOPMENT.md`.** Um `CLAUDE.md` na raiz de um plugin não é carregado como contexto e poluía o pacote distribuído (aviso do `claude plugin tag`); o conteúdo é doc de desenvolvimento/contribuição e segue versionado com nome honesto. As menções a "CLAUDE.md" nos manuais e skills são ao conceito genérico (o CLAUDE.md do projeto onde o plugin roda) e permanecem inalteradas.

## [0.1.1] - 2026-06-13

### Changed

- **Modelo de orquestração padronizado em `opus`.** Os agents orquestradores (Chief of Staff e COO) migram de `fable` para `opus`; agora os 50 agents usam `opus` (sempre o Opus mais recente, sem versão fixa). A orquestração roda em effort máximo (recomendado). O campo `model` continua modificável manualmente no cabeçalho de cada agent. Documentado no README.

### Fixed

- **CI verde.** Corrigidos 6 avisos do `ruff` (E402, E702, F841) nos testes dos hooks que reprovavam o workflow de CI do host anterior (legado, removido).

### Added

- Seção "Modelo de orquestração" no README e link para a Wiki do projeto.

## [0.1.0] - 2026-06-13

### Added

- **Constelação de 50 agents.** 12 C-level (CEO, CPO, CTO, CMO, COO, CISO, CDO, CAIO, CFO, CRO, CLO e Chief of Staff) e 38 operacionais cobrindo engenharia, dados e IA, produto, UX e design, gestão e pessoas, marketing, crescimento e receita, e suporte, docs, legal e i18n.
- **3 skills de orquestração.** `/bigtech` monta a constelação via Chief of Staff (classifica porte, escolhe a variante de pipeline e devolve o mapa de ativação); `/proj_software` toca o ciclo de vida de software em 5 macrofases com gatekeeper anti-over-engineering; `/tab_pendencias` cria a tabela de planejamento ordenada por valor (WSJF) e dependência (topológica).
- **Hooks de TDD.** `tdd_guard` (PreToolUse) e `tdd_runner` (PostToolUse) implementam o guard-rail do ciclo red, green, refactor, com opt-in por projeto.
- **Hooks de governança bigtech.** `bigtech_porte_reminder` (SessionStart) reavalia o porte do projeto e `bigtech_reinforce` (UserPromptSubmit) reforça o modo de operação e roteia ativação por linguagem natural.
- **Docs-bootstrap.** Hook `bigtech_session_init` (SessionStart) injeta o caminho dos manuais no contexto da sessão, avisa sobre incompatibilidade com o plugin `caveman` e sugere as dependências `playwright` e `superpowers` quando ausentes.
- **13 documentos de governança.** Manuais de organização, pipeline de release, liderança, ferramentas, contrato de qualidade, testes, agile, checklist de deploy, auditorias e princípios de arquitetura, higienizados para distribuição pública.
- **Marketplace `petrinhu`.** Distribuição via `/plugin marketplace add` e `/plugin install bigtech`, sob a licença Apache-2.0.

[0.2.0]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.2.0
[0.1.16]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.16
[0.1.15]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.15
[0.1.14]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.14
[0.1.13]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.13
[0.1.12]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.12
[0.1.11]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.11
[0.1.10]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.10
[0.1.9]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.9
[0.1.8]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.8
[0.1.7]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.7
[0.1.6]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.6
[0.1.5]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.5
[0.1.4]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.4
[0.1.3]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.3
[0.1.2]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.2
[0.1.1]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.1
[0.1.0]: https://github.com/petrinhu/bigtech_plugin/releases/tag/bigtech--v0.1.0
