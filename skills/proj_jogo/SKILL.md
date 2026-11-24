---
name: proj_jogo
description: "Orquestra desenvolvimento de jogo (game-dev SDLC) em 5 macrofases, alocando os agentes globais corretos por etapa, com proteção anti-over-engineering em prototipos/game-jams e trilha de escalonamento (game jam → indie pequeno → indie médio → AAA). Aplica DevSecOps / Shift-Left (security transversal) e produção game-dev (pre-prod / production / alpha / beta / gold / live-ops). Use IMEDIATAMENTE quando o usuário disser \"vou fazer um jogo\", \"criar game\", \"game design\", \"novo jogo\", \"prototype de jogo\", \"estruturar projeto de jogo\", \"game jam\", ou invocar /bigtech:proj_jogo. Não usar pra software não-jogo (usar /bigtech:proj_software)."
---

# proj_jogo: orquestração game-dev com squad global

Aplica o **macrofluxo de game-dev em 5 fases** delegando aos agentes globais de design + arte + áudio + engenharia. Inclui **gatekeeper anti-over-engineering** (game jam ≠ AAA), **shift-left de segurança** (proporcional), e **trilha de escalonamento** quando jogo cresce de jam → estúdio.

> **Regra de ouro:** game jam de 48h não precisa de ADR, art bible de 200 páginas, nem CI/CD k8s. Calibrar SEMPRE pela matriz de tamanho.

> **Piso de testes.** Teste só para lógica de produto. Com CI na nuvem, o CI seletivo é o portão e o pré-CI é opcional; sem CI na nuvem, o pré-CI seletivo é o portão. Nada de teste de mutação, sabotagem, auditoria, reauditoria, varredura de gêmeos, checklist de perguntas do revisor, script de verificação extra nem portão local novo. Exceção: segurança, privacidade e deploy irreversível. Os gates de fase abaixo seguem este piso; playtest é validação de design, não portão de teste. A verificação é seletiva, e a publicação vai uma parte por vez (seção 8).

---

## 0. Calibragem inicial (obrigatório)

Antes de invocar agentes, identifique:

| Dimensão | Pergunta |
|---|---|
| Tamanho | Solo jam / Hobby / Indie pequeno (2-5) / Indie médio (5-20) / AA (20-50) / AAA (50+) |
| Porte | Jam / hackathon / 1-3 pessoas / 3-8 pessoas / 8-25 pessoas / 50+ pessoas |
| Plataforma | Web / mobile / desktop (Steam/itch) / console / VR/AR / multi-plataforma |
| Gênero + estilo | (define team mix: arte 3D? 2D pixel? narrativa-heavy? procedural?) |
| Live service? | One-shot / 1 patch / season pass / GaaS / MMO |
| Monetização | Free / Paid / F2P / sub |
| Compliance | Nenhuma / age rating / loot box regulation / privacy / acessibilidade legal |
| Multiplayer | Single / co-op local / co-op online / PvP / massively |
| Engine | Unity / Unreal / Godot / GameMaker / RPG Maker / Bevy / custom / proprietary |

Pergunte 1-3 se faltar. Resto deriva.

---

## 1. Matriz tamanho → agentes a invocar

Use o **mínimo viável**.

### Nivel G0: Game jam / Prototype (1-2 pessoas)
**Agentes:** 1-2 agentes especialistas sob demanda implementam. A thread principal só confere: lê, mede, verifica, despacha e reporta; nunca produz. Esta regra vale sem exceção de tamanho, inclusive em G0. Time enxuto continua sendo o objetivo (1-2 agentes, não uma squad completa); só não é a thread principal quem codifica.
- `bigtech:lead-game-designer` opcional pra clarificar pillars + core loop em 1 hora
- Sem narrativa designer separado (mesma pessoa escreve)
- Sem art director separado (uma pessoa decide)
- Sem `bigtech:engine-graphics-programmer`: engine padrão resolve
- **Foco:** descobrir se a ideia é fun em 48h
- Sem ADR, sem doc bible, sem GDD de 50 páginas
- Doc: 1 pillar statement + 1 paragraph pitch
- **Guardrail:** se não consegue protótipo jogável em N horas, simplificar mecânica

### Nivel G1: Hobby project / itch.io small (1-3 pessoas)
**Agentes ativos:**
- `bigtech:lead-game-designer` (pillars, core loop, balance simples)
- `bigtech:art-director` (style guide leve)
- `bigtech:narrative-designer` (arquitetura) + `bigtech:narrative-writer` (redação final de diálogos, lore narrado, descrição de cena) se há história
- `bigtech:level-designer` opcional (se mais de 1 nivel não-procedural)
- Engineers e artistas das disciplinas necessárias
- `bigtech:compliance-legal` mínimo (age rating, política privacidade básica)
- Sem `bigtech:game-producer` formal: designer principal coordena
- Sem `bigtech:engineering-manager` / `bigtech:engineering-coach` / `bigtech:scrum-master`
- Doc: 1-page GDD + style guide curto + pillar statement
- **Divisão narrativa:** designer entrega beat sheet + dialogue tree com stubs; writer materializa falas + descrições em prosa final

### Nivel G2: Indie pequeno / Steam release (3-8 pessoas)
**Adicionar a G1:**
- `bigtech:game-producer` part-time (milestones, scope)
- `bigtech:audio-designer-composer` (música + SFX próprios)
- `bigtech:3d-artist-rigger` ou pixel artists (conforme estilo)
- `bigtech:game-animator`
- `bigtech:engine-graphics-programmer` se custom shader / perf-critical
- `bigtech:qa-engineer` part-time (playtests estruturados, bug tracking)
- `bigtech:economy-designer` opcional (só se F2P / live service)
- `bigtech:accessibility-specialist` opcional (CVAA/EAA compliance)
- `bigtech:i18n-l10n-specialist` se localizado (recomendado pra alcance Steam)
- Doc: GDD modular (vision + pillars + mecânicas-chave + level docs), style bible, audio brief

### Nivel G3: Indie médio / AA (8-25 pessoas)
**Adicionar a G2:**
- `bigtech:game-producer` full-time + assistentes
- `bigtech:engineering-manager` e/ou `bigtech:tech-lead`
- `bigtech:scrum-master`
- `bigtech:narrative-designer` dedicado (arquitetura, dialogue tree graph, foreshadowing tracker, ludonarrative)
- `bigtech:narrative-writer` dedicado (redação polida de diálogos, lore narrativo, descrições, monólogo, codex entries)
- `bigtech:level-designer` dedicado (não-misturado com gameplay design)
- `bigtech:economy-designer` se monetização complexa
- `bigtech:compliance-legal` regular (cert process, age rating multi-país)
- `bigtech:accessibility-specialist` (cumprimento legal CVAA/EAA)
- `bigtech:data-engineer` + `bigtech:data-scientist` se telemetria/analytics
- `bigtech:security-engineer` (anti-cheat, login, IAP, save protection)
- Doc: vision doc + pillars + style bible completo + lore bible + tech doc

### Nivel G4: AAA / large studio (50+ pessoas)
**Squad completa game-dev + suporte software:**
- Tudo de G3 + `bigtech:ml-engineer` (se ML in-game: matchmaking, anti-cheat, recomendação)
- `bigtech:devops-sre` completo (build farm, telemetria, live ops infra)
- `bigtech:engineering-coach` formal
- Outsourcing structures (`bigtech:game-producer` + arts)
- Compliance regulada (PEGI/ESRB/IARC, loot box laws, GDPR/LGPD, console cert TRC/TCR)
- Doc: vision pillar pyramid + design bibles (sistema, narrativa, mundo, personagem, arte, áudio) + tech architecture + production schedule + risk RAID + live ops plan

---

## 2. As 5 Macrofases (game-dev)

### Fase 1: Concepção, Design de Sistemas, Especificação

**G0:** 1 hora pillars + 1 paragraph pitch.
**G1:** 1-page GDD + style guide leve.
**G2+:** vertical slice planning.

**Agentes:**
- `bigtech:product-manager` (se houver visão comercial; opcional em G0/G1 hobby)
- `bigtech:lead-game-designer`: pillars, MDA, core loop, mecânicas primárias
- `bigtech:narrative-designer`: história, dialogue tree, atmosfera
- `bigtech:art-director`: style guide, palette, lighting bible
- `bigtech:ux-ui-designer`: jornada, UI, HUD
- `bigtech:ux-writer`: voice/tone, microcópia in-game
- `bigtech:accessibility-specialist`: game a11y (CVAA/EAA, color, controles remappáveis)
- `bigtech:software-architect`: arquitetura técnica (engine choice, networking, save format)
- `bigtech:hardware-engineer`: se HW custom (arcade, dispositivo proprietário)
- `bigtech:security-engineer` (**Shift-Left**): threat model (cheat, account, IAP, save tampering)

**Gates:**
- Pillars escritos e testáveis
- Core loop validável em prototype
- Aesthetic alvo declarado (MDA)
- Style guide v0 + 1 cena em color script
- Decisões one-way door registradas (engine, networking model, save format)
- Threat model proporcional (G0 = pula; G2+ = leve; G3+ = pleno)

### Fase 2: Implementação

**Agentes:**
- `bigtech:engineering-manager` (G3+)
- `bigtech:scrum-master` (G2+)
- `bigtech:engineering-coach` (G4)
- `bigtech:tech-lead` (G3+)
- `bigtech:backend-engineer` (se há server: matchmaking, leaderboard, save cloud)
- `bigtech:frontend-engineer` (se há companion web / launcher)
- `bigtech:mobile-engineer` (se mobile)
- `bigtech:embedded-firmware-engineer` (se HW custom / arcade / cartucho)
- `bigtech:level-designer`: blockout / greybox → playtest → iteração
- `bigtech:3d-artist-rigger`: modelagem + UV + rig + texturização PBR
- `bigtech:game-animator`: locomotion, combat, facial, game feel
- `bigtech:engine-graphics-programmer`: render, shader, perf, physics, memory
- `bigtech:audio-designer-composer`: SFX + música adaptive + mix
- `bigtech:security-engineer` (**transversal**): anti-cheat, IAP validação server-side, save tamper protection

**Gates por milestone:**
- **First playable:** core loop jogável end-to-end
- **Vertical slice:** 1 nivel completo com qualidade alvo
- **Alpha:** todas features implementadas (content placeholder OK)
- **Beta:** content-complete, balance pass, localization in
- **Gold/RC:** cert passed (TRC console), no critical bug

### Fase 3: Dados, IA, MLOps (game-specific)

**G0/G1:** geralmente vazia.
**G2+:** ativa se telemetria/analytics/ML.

**Agentes:**
- `bigtech:data-engineer`: pipeline de telemetria (eventos de gameplay → warehouse)
- `bigtech:data-scientist`: análise de playtests, churn modeling, segmentação, balance via dado
- `bigtech:ml-engineer`: modelos in-game (matchmaking, recomendação, DDA, anti-cheat ML, procedural)
- `bigtech:economy-designer`: modelagem matemática de currency / sinks / inflação
- `bigtech:security-engineer` (**transversal**): model security (anti-cheat), PII em telemetria, prompt injection se LLM in-game

### Fase 4: Qualidade, Segurança, Compliance, Docs

**Agentes:**
- `bigtech:qa-engineer`: playtests estruturados e teste da lógica de jogo (regressão, balance) no CI; performance test só a pedido
- `bigtech:security-engineer` (**gatekeeper formal**): pentest, cert prep, IAP security, save protection, anti-cheat
- `bigtech:compliance-legal`: ESRB/PEGI/IARC age rating, loot box laws (BE/NL/CN), GDPR/LGPD, console TRC/TCR, OSS licenses
- `bigtech:technical-writer`: manual + tutorial + release notes + dev docs internos

**Gates:**
- Playtests N≥30 com hipóteses validadas
- Portão verde com o teste da lógica de jogo (com CI na nuvem, o CI seletivo é o portão e o pré-CI é opcional; sem CI na nuvem, o pré-CI seletivo é o portão)
- Cert submitted + passed
- Age rating obtido (IARC/ESRB/PEGI)
- Loot box compliance verificada por mercado
- Manual + tutorial + release notes prontos

### Fase 5: Integração Contínua, Operação, Live Ops

**Agentes:**
- `bigtech:devops-sre`: build farm (Unity Cloud Build / Unreal pipeline custom / Jenkins), CI/CD, telemetria infra, live ops monitoring, hotfix rollout
- `bigtech:i18n-l10n-specialist`: locale, RTL, ICU, voice acting localizado, screen text revisado em country
- `bigtech:economy-designer`: live ops balance (sazonal, evento, store rotation)
- `bigtech:game-producer`: milestone cert + post-launch roadmap + season planning
- `bigtech:security-engineer` (**transversal**): SecOps live (anti-cheat reativo, fraud detection IAP, account takeover defense)

**Gates:**
- Pipeline build estável < N min
- Telemetria viva (DAU, retention, balance metrics)
- Hotfix process testado
- Post-launch roadmap S1-S2 definido

---

## 3. Shift-Left de segurança (security-engineer transversal)

`bigtech:security-engineer` atua em **todas as 5 fases**:

| Fase | Atuação game-specific |
|---|---|
| 1: Concepção | Threat model: cheaters, exploiters, IAP fraud, save tampering, account hijack |
| 2: Implementação | Server-authoritative design; IAP validation server-side; obfuscação seletiva client; HMAC em comunicação |
| 3: Dados/IA | Anti-cheat ML; telemetria com PII mínima; opt-in tracking |
| 4: QA | Pentest dirigido (server, save, IAP); cert security (console TRC) |
| 5: Operação | SecOps live; ban wave automatizado; fraud detection; account recovery seguro |

**Calibre:** G0 = não precisa; G1 = checklist básico; G2+ = anti-cheat + IAP security; G3+ = pleno (server-authoritative + telemetria + IR).

---

## 4. Anti-over-engineering (game-specific)

**Antes de invocar agente / camada / sistema, pergunte:**

1. **Vai melhorar fun?** Toda mecânica/sistema responde isso. Se não, corta.
2. **Custo de implementar > valor pro player?** Sistema de météo super realista que ninguém nota = corta.
3. **Pillar serve a isto?** Toda feature serve ≥1 pillar. Se não, fora.
4. **Vai sobreviver ao playtest?** Sistema fancy raramente sobrevive ao "ninguém usa".

### Smells de over-engineering game-dev

| Smell | Correção |
|---|---|
| Custom engine antes de prototype | Use Unity/Unreal/Godot: sempre |
| Procedural generation pra evitar level design | LD primeiro; procedural sobre LD validado |
| Sistema de crafting + economia complexa em jogo single-player de 5h | Cortar; loot direto |
| Multiplayer netcode antes de mecânica single funcionar | Single-player primeiro |
| Sistema de diálogo branching gigante pré-vertical-slice | Linear primeiro |
| 50 inimigos antes de 1 inimigo divertido | Polish 1 → variar |
| Save system com 30 slots antes de loop core fechar | 1 save primeiro |
| Editor in-game antes de jogo existir | Hard-code primeiro |
| Modding framework antes de release | Pós-release |
| Achievements / leaderboard antes de gameplay validado | Esperar |
| Tutorial elaborado antes de loop ser fun | Sandbox de aprendizado orgânica |
| Cinemática AAA quando arte é programmer-art | Coerência > polish isolado |
| Sistema de skills com 100 nodes pré-vertical-slice | 3-5 nodes primeiro |

### Princípios anti-over-engineering game

- **Prototype antes de doc.** GDD-épico-200-páginas mata projetos.
- **Greybox/blockout primeiro.** Arte sobre level que joga.
- **Mecânica única bem polida > 10 mecânicas medíocres.**
- **Cortar é virtude.** Toda feature corta cabe coragem de produção.
- **Vertical slice prova viabilidade.** Sem vertical slice = projeto teatral.
- **Playtest > intuição.** Hipótese + 5 playtesters captura 85% dos problemas.
- **Engine escolhida é one-way door.** Cuidado; mas escolha cedo e cumpra.

---

## 5. Trilha de escalonamento (jam → studio)

Jogo cresce. Reconheça sinais e migre incrementalmente.

### Sinais que indicam migração

**G0 → G1:**
- Prototype fun confirmado em jam
- Querem continuar pós-jam
- 1-3 pessoas com escopo fechado

**Ações:** introduzir pillars escritos, style guide leve, GDD-1-página, bug tracker (issue list em git suffice), playtest plan simples.

**G1 → G2:**
- Vai sair publicado (Steam/itch/console)
- Team estabilizou 3-8 pessoas
- Produção com milestones formais e mais de um ciclo de entrega

**Ações:** game-producer part-time, milestones formais (vertical slice, alpha, beta, gold), QA estruturado, audio próprio, art bible robusto, compliance básica (age rating).

**G2 → G3:**
- Multi-time
- Live service ou content updates regulares
- Compliance multi-país (incluindo loot box law)
- Console cert obrigatória

**Ações:** game-producer full-time, EM + tech leads, scrum master, narrative + level designers dedicados, security/anti-cheat formal, telemetria/analytics, accessibility cumprimento legal, localização full.

**G3 → G4:**
- Time 50+
- Multi-engine teams (motion capture, procedural, ML)
- Multi-plataforma simultânea
- Live ops MMO/GaaS

**Ações:** estrutura matricial; engine team dedicado; AI/ML in-game team; DevOps formal; compliance regulada plena; multi-region live ops.

### Refactor pra suportar crescimento

- **Engine escolhida cedo é one-way door**: escolher considerando o horizonte de produção, não a jam
- **Save format / serialização desde D1 com versioning**: facilita patches
- **Telemetria event schema versionado** desde primeira release publicada
- **Server-authoritative se há multiplayer** desde primeiro protótipo dele (refactor depois é caro)
- **Modular content pipeline** (DLC, season pass, mods) pensado em G2; obrigatório em G3+
- **Localization-friendly** desde D1 (sem string concat; ICU MessageFormat / engine native): mesmo se não localiza no v1

---

## 6. Templates rápidos por nivel

### G0/G1: 1-page GDD
```markdown
# [Título]
## Tagline (1 frase)
## Pillars (3-5)
## Aesthetic alvo (MDA, 2-3 das 8 fontes de fun)
## Core loop (30s-2min)
## Meta loop (sessão + long-term)
## Plataforma + sessão típica
## Referências (com diferencial)
## Métrica de sucesso (1 número)
```

### G2+: GDD modular
[Invocar `bigtech:lead-game-designer`: template completo embutido]

### G2+: style guide leve
[Invocar `bigtech:art-director`]

### G2+: pillar statement
```markdown
**Pillar 1: [Nome] -- [1 frase]**
- Significa: ...
- Decide: SIM ..., NÃO ...
```

### G2+: threat model leve
```markdown
# Threat Model -- [Jogo]
## Assets: contas, saves, IAP, leaderboards, conteúdo proprietário
## Atores: cheater, exploiter, fraudster, leaker
## Top 5 riscos + mitigação
## Server-authoritative: SIM/NÃO em decisões críticas
```

---

## 7. Como usar esta skill

1. **Identifique o nivel** (G0-G4) com 1-3 perguntas se necessário
2. **Mapeie quais agentes** invocar conforme matriz
3. **Execute as fases** com agentes apenas onde adicionam valor: prototype antes de doc
4. **Aplique shift-left de segurança** proporcional (G0 = nada; G2+ = anti-cheat + IAP)
5. **Cheque smells de over-engineering** game-dev (custom engine, multiplayer prematuro, etc.)
6. **Reconheça sinais de escalonamento** e migre incrementalmente
7. **Pillars decidem.** Toda feature: "isso serve a qual pillar?"
8. **Playtest valida.** Hipóteses específicas + 5+ playtesters; observar mais que perguntar
9. **Sempre prefira o agente correto** ao gerar conteúdo / decisão genericamente
10. **Siga a seção 8** ao despachar agentes, verificar e publicar builds

## 8. Orquestração, verificação e publicação

### Orquestração dos agentes

- **Consulta e leitura ficam na sessão**, sem abrir agent; toda alteração de código continua com agente especialista.
- **C-level decide e escreve a ordem de serviço, sem editar nada.** A ordem é fechada: os arquivos que o agente pode tocar e os que não pode, o comportamento, o teste que prova, o critério de pronto, as proibições e "relatório em até N linhas", com N de 3 a 6.
- **Operacional entrega o SHA no ramo e para.** O merge no principal é feito por um agente operacional, e o main revisa. Pausado, o agente para num ponto limpo: commit do que está verde, patch do resto e o caminho do patch no relatório.
- **Retome o mesmo agente** por SendMessage para continuar, corrigir ou destravar o trabalho dele, em vez de despachar outro do zero.
- **Pendências do usuário** (decisões e confirmações que esperam por ele) **vão juntas num AskUserQuestion só**, com até 4 perguntas e multiSelect, nunca como lista em texto solto.
- **"Resolva com clevel"** delega a decisão ao C-level do domínio, e ela entra marcada "a ratificar" até o usuário confirmar.
- **Um arquivo único de decisões, só de acréscimo:** entrada nova no fim, nunca reescrita; correção vira entrada nova que aponta a anterior.
- **Vigie pela notificação** de fim do agente ou da ferramenta, sem polling curto.
- **Worktree barata:** `git worktree add --no-checkout` e, dentro dela, só os arquivos da parte (sparse-checkout); dependências e assets já baixados entram por symlink, sem baixar de novo.
- **Antes de escrever a causa de uma falha no briefing**, leia a asserção que falhou.
- **No fim da onda, olhe o `/usage` por tipo de agent**, para ver onde foi o custo.

### Verificação seletiva (pré-CI e CI)

Régua: uma verificação não pode custar mais que a mudança que ela confere.

- **Roda o que a mudança toca** desde a última build publicada: os testes ligados aos arquivos mudados pelo grafo de imports **e** pelos caminhos de arquivo que os testes, e os auxiliares deles, citam em texto. Teste que abre um arquivo e lê o texto não aparece no grafo de imports; o que lê arquivo sem citar o caminho roda sempre que mudar código ou teste.
- **Segurança e privacidade rodam sempre** (anti-cheat, save, IAP, dado pessoal), qualquer que seja a mudança.
- **Tudo roda** quando muda ferramenta de build, de teste ou de publicação, configuração do projeto ou da engine, ou dependência, ou quando não há build anterior para comparar.
- **Para no primeiro erro e mostra o tempo de cada passo**, para achar o passo que pesa e cortar só o desperdício.
- **Com CI na nuvem, o CI fica seletivo e o pré-CI é opcional.** Sem CI na nuvem, o pré-CI faz esse papel, com as mesmas regras.

### CI na nuvem

- **Concurrency com cancel-in-progress no mesmo ramo:** um push novo cancela a execução velha do mesmo ramo. Nunca em deploy nem release: o workflow de deploy e a execução de tag de release não se cancelam.
- **Cache de dependências com chave pelo lock** (`actions/setup-python` com `cache: pip` e `cache-dependency-path` apontando o arquivo de dependências, ou `actions/cache` com a chave pelo hash do lock).
- **Push só de docs pula os testes, mas a varredura de segredos e o portão de privacidade rodam sempre.** O job de testes pula quando a mudança toca só docs que nenhum teste lê como texto; os jobs de segredos e de privacidade ficam sem esse filtro. `paths-ignore` no workflow inteiro pularia também a segurança.

### Publicação: uma parte por vez

- **A build só nasce depois do verde.** A verificação roda primeiro; o commit de versão, a marca (tag) e o pacote para a loja só se criam com ela verde. Se reprovar, nada é commitado nem marcado. Não há ensaio que repete a verificação inteira antes da publicação de verdade; certificação e beta da loja continuam onde a plataforma pede.
- **Uma parte por vez, numa fila.** Cada parte é preparada numa worktree própria, com ramo próprio, e o principal só recebe a parte na hora de publicá-la. Parte recusada volta sozinha para conserto, e a fila segue.
- **Histórico e changelog (patch notes) gravados antes.** A publicação só é lançada depois de conferir que o commit com a entrada da versão existe.
- **Ninguém toca no principal antes de ler a confirmação da publicação anterior**, a linha do registro que diz que ela foi ao ar.
- **O merge é curto e separado.** A conferência da publicação anterior roda num comando; a junção da próxima parte, em outro, depois de ler o resultado.
- **Pacote** (AppImage, Flatpak, instalador, build da loja) **só na tag**, nunca a cada push.

### Deploy seguro

- **Smoke curto depois do deploy.** Teste rápido de saúde em produção logo após cada publicação. Falha duas vezes seguidas: rollback automático, sem esperar decisão. A primeira falha só reconfere.
- **Erro em produção vira aviso ao usuário.** Erro novo em produção é reportado na hora, com o sintoma e o estado do rollback.
- **Dependabot para atualização de segurança.** Ele abre a atualização; o CI testa e o usuário aprova antes do merge.
- **Chave de recurso para subir parte pela metade desligada.** Parte nova nasce desligada e só liga com aval do usuário.
- **Ramo de parte com no máximo um dia.** Parte que passa de um dia se divide.

### Build nativo (C/C++, CMake, Qt)

Vale onde o jogo ou a engine compila código nativo; os valores são exemplos configuráveis.

- **Cache de compilação comum:** `ccache` numa pasta única, compartilhada por todas as worktrees (`CCACHE_DIR=/var/tmp/ccache`), e build fora da árvore do código (`cmake -B <pasta de build>`).
- **ctest seletivo:** só os alvos que dependem dos arquivos mudados, pelo grafo do CMake. Tudo roda quando muda `CMakeLists.txt`, toolchain ou preset.
- **Teste de widget Qt com `QT_QPA_PLATFORM=offscreen` roda no host**; só o que precisa de janela de verdade fica isolado.
- **Teto de memória ajustável por projeto:** o link de um C++ grande pode precisar de mais que o teto padrão.
- **Linker rápido** (`mold`) onde o projeto aceitar.
- **Cabeçalho pré-compilado** (`target_precompile_headers`) só nos cabeçalhos estáveis, que quase não mudam.
- **`-ftime-trace`** (Clang) uma vez antes de otimizar o tempo de build, para medir onde ele vai.

### Trabalho pesado na máquina

Build da engine, suíte, teste com janela e container seguem a seção 11 de [`hardware-resource-limits`](../../docs/principles/hardware-resource-limits.md): um pesado por vez na trava única da máquina, núcleos reservados ao sistema, teto de memória e de processos por trabalho, prioridade mínima para agente, a publicação primeiro, espera sem laço, teste sem janela no host com esses limites e o que abre janela isolado. Repasse isso na ordem de serviço de quem roda trabalho pesado.

## Integração com ecossistema

- Os agentes são chamados como `bigtech:<nome>` e acionados conforme a matriz
- 10 deles game-dev específicos: `bigtech:lead-game-designer`, `bigtech:narrative-designer`, `bigtech:level-designer`, `bigtech:art-director`, `bigtech:3d-artist-rigger`, `bigtech:game-animator`, `bigtech:engine-graphics-programmer`, `bigtech:audio-designer-composer`, `bigtech:economy-designer`, `bigtech:game-producer`
- Skill **`/bigtech:proj_software`**: pra componentes não-jogo (ferramentas, launcher, backend)
- Skill **`/bigtech:tab_pendencias`**: backlog
- **GitHub Actions**: pipeline CI (`.github/workflows/`)
- Linguagem default: **pt-br** (termos técnicos no original: pillar, MDA, core loop, vertical slice, alpha, beta, gold, RC, live ops)

## Autoridade

O usuário é o líder supremo e soberano desta organização (o CEO da sua bigtech). Diante de dúvida ou de mais de uma opção, perguntar via **AskUserQuestion** (recomendada primeiro), nunca decidir sozinho.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
