---
name: bigtech
description: "Monta o time de agents C-level (constelação) para um projeto como se fosse uma bigtech. Invoca Cósimo (Chief of Staff), classifica o PORTE do projeto, seleciona a VARIANTE de pipeline (anti over-engineering), e devolve o MAPA DE ATIVAÇÃO (quais C-levels e agents operacionais ligar, em quais das 12 fases). Opcionalmente dispara os C-levels ativos. Camada de NEGÓCIO e LIDERANÇA (produto, marketing, vendas, legal, finanças, release); delega a execução de engenharia ao /bigtech:proj_software. Use quando o usuário disser \"montar o time\", \"organizar como bigtech\", \"qual pipeline e quais agents\", \"quem lidera isso\", \"classificar o porte\", \"estruturar a empresa do projeto\", ou invocar /bigtech:bigtech. Para SDLC puro de engenharia sem camada de negócio, usar /bigtech:proj_software."
argument-hint: "[caminho ou descrição do projeto] [--porte early|scale|bigtech] [--dispatch]"
allowed-tools: [Read, Grep, Glob, Bash, Agent, TodoWrite]
---

# bigtech: montar a constelação C-level via Cósimo

Materializa a organização descrita nos manuais de governança e liderança do plugin (`ORG`, `pipeline_release_1.0`, `lideranca_pipeline_release`). Esta skill opera na **camada de empresa** (C-levels + pipeline de produto de 12 fases). A execução de engenharia (fases 4 a 9) é delegada ao `/bigtech:proj_software`, que aloca os agents operacionais de engenharia por nível S0-S4.

> **Acesso aos manuais.** O caminho absoluto de `docs/` é injetado no contexto da sessão pelo docs-bootstrap (hook `SessionStart`). Esta skill é carregada de um diretório conhecido, então também pode ler os manuais por caminho relativo (a partir de `skills/bigtech/`): governança em `ORG` (`${CLAUDE_PLUGIN_ROOT}/docs/house/ORG.md`), pipeline em `pipeline_release_1.0` (`${CLAUDE_PLUGIN_ROOT}/docs/house/pipeline_release_1.0.md`), liderança em `lideranca_pipeline_release` (`${CLAUDE_PLUGIN_ROOT}/docs/house/lideranca_pipeline_release.md`). Se o caminho não estiver no contexto, localize via Glob `**/bigtech:bigtech/docs/**/<NOME>.md`.

> **Regra de ouro (anti-OE):** quem decide o tamanho do time é Cósimo. Porte arquitetural = `early | scale | bigtech` (piso **early**). Headcount/capacity humana **não** define porte. Em early, a maioria dos C-levels fica dormente. Calibrar por complexidade, criticidade e escala.

Argumentos recebidos: $ARGUMENTS

> **Alias deprecado:** `--porte solo` é aceito e normalizado para `early` (com aviso ao usuário). Não grave `porte=solo` em marcadores novos.

---

## 0. Coleta de sinais (obrigatório antes de Cósimo)

Reúna o contexto. Se faltar, pergunte no máximo 1 a 3 itens críticos.

| Dimensão | Pergunta |
|---|---|
| Complexidade / criticidade | Baixa (escopo pequeno, uso próprio) / Média (PMF, primeiros usuários) / Alta (multi-produto, compliance, escala): **isto** orienta o porte, não o número de pessoas |
| Capacity humana (nota, não porte) | 1 pessoa / time pequeno / time médio / org grande: só capacity; **não** vira valor de `--porte` |
| Stake | Pessoal / Interno / Cliente externo / Crítico (financeiro, saúde, vida) |
| Compliance | Nenhuma / LGPD básico / Regulada (PCI, HIPAA, ANVISA, BACEN) |
| Dado pessoal/PII | Não / Sim (sobe a régua de Narciso e Cláudio) |
| Modelo de negócio | Sem receita / B2C / B2B / open source / interno |
| Tipo | CLI / web / mobile / desktop / serviço / lib / firmware |

Se há projeto em CWD, leia `CLAUDE.md`, `TODO.md` e `README` do projeto para inferir sinais antes de perguntar.

---

## 1. Invocar Cósimo (Chief of Staff)

Dispare o agent `bigtech:cosimo-chief-of-staff` (tool Agent, subagent_type `bigtech:cosimo-chief-of-staff`) passando os sinais coletados. Peça que devolva o **mapa de ativação** no formato:

```
PORTE: <early | scale | bigtech>
VARIANTE: <Pipeline-Early | Pipeline-Lean | Pipeline-Padrão | Pipeline-Completo>
C-LEVELS ATIVOS: [...]
C-LEVELS DORMENTES: [...]
AGENTS OPERACIONAIS: [...]
FASES APLICÁVEIS: [0..12 ou colapsadas]
CERIMÔNIA: <nenhuma | kanban | scrum>
GATILHO DE RE-ROTEAMENTO: <quando re-avaliar o porte>
JUSTIFICATIVA ANTI-OE: <por que esse nível e não mais>
```

> **Repasse o caminho absoluto de `docs/` no prompt da task de Cósimo.** Subagents não herdam o contexto da sessão (o docs-bootstrap só alcança a thread principal e as skills); sem o caminho no prompt, Cósimo não consegue abrir os manuais de governança (`ORG`, `pipeline_release_1.0`, `lideranca_pipeline_release`) que sustentam a classificação de porte. Use o caminho injetado no contexto da sessão; se ele não estiver disponível, resolva via Glob `**/bigtech:bigtech/docs/` e inclua o resultado no prompt.

Se o usuário passou `--porte`, normalize alias deprecado (`solo` → `early` + aviso) e informe a Cósimo como hint; deixe ele validar contra os sinais (criticidade e complexidade sobrepõem headcount/capacity).

---

## 2. Apresentar o mapa ao usuário

Mostre o mapa de ativação de forma legível: tabela fase x C-level ativo, lista de agents operacionais, cerimônia, e a justificativa anti-OE. **Não dispare nada ainda** sem aprovação, salvo se `--dispatch` foi passado.

Mapeamento de porte entre as duas camadas (mantenha coerência):

| Porte (Cósimo / bigtech) | Variante de pipeline | Nível SDLC (/bigtech:proj_software) |
|---|---|---|
| early (minimalista / projeto pequeno) | Pipeline-Early | S0 / S1 |
| early (early-stage / PMF) | Pipeline-Lean | S2 |
| scale | Pipeline-Padrão | S3 |
| bigtech | Pipeline-Completo | S4 |

---

## 3. Despachar (sob aprovação ou com --dispatch)

Para cada **C-level ativo**, dispare o agent correspondente (tool Agent) para liderar suas fases, em paralelo quando independentes:

| Fase do pipeline | C-level (agent) |
|---|---|
| 0 Ideação, 11 coordenação | `bigtech:celso-ceo` |
| 1-3 Discovery/Definição/Design, 12 Pós | `bigtech:capitolino-cpo` |
| 4-9 Arquitetura a Beta (engenharia) | `bigtech:caetano-cto` -> **delega ao /bigtech:proj_software** |
| 8 Segurança | `bigtech:narciso-ciso` |
| 8 Jurídico | `bigtech:claudio-clo` |
| 2 e 6-12 Dados (se ativo) | `bigtech:candido-cdo` |
| 10 GTM | `bigtech:camilo-cmo` |
| 10 Pricing/orçamento (se ativo) | `bigtech:confucio-cfo` |
| 10-11 Receita (se ativo) | `bigtech:cicero-cro` |
| 6-11 Execução cross-func | `bigtech:cosmo-coo` |

> **Ao disparar cada C-level via Agent tool, inclua o caminho absoluto de `docs/` no prompt da task.** O subagent não herda o contexto da sessão; sem o caminho ele não abre os manuais que precisa para decidir (governança, manuais de execução em `${CLAUDE_PLUGIN_ROOT}/docs/house/`). Repasse o caminho de `docs/` vindo do contexto da sessão (ou resolvido via Glob `**/bigtech:bigtech/docs/`) em toda task de C-level.

Cada C-level devolve decisões + mapa de delegação aos seus operacionais; a thread principal dispara os operacionais (repassando o mesmo caminho de `docs/` no prompt de cada um). Para as fases de engenharia, **invoque `/bigtech:proj_software`** em vez de re-listar os eng agents aqui (DRY).

**Piso de testes.** Teste só para lógica de produto. Com CI na nuvem, o CI seletivo é o portão e o pré-CI é opcional; sem CI na nuvem, o pré-CI seletivo é o portão. Nada de teste de mutação, sabotagem, auditoria, reauditoria, varredura de gêmeos, checklist de perguntas do revisor, script de verificação extra nem portão local novo. Exceção: segurança, privacidade e deploy irreversível. Testes são enabler/DoD (TDD, shift-left): rodam COM a implementação nas Fases 6-7, nunca depois. Auditoria (Fase 8, `bigtech:internal-auditor`) só entra na exceção, depois do código que cobre, uma vez e sem reauditoria; `/bigtech:tab_pendencias` não injeta teste nem auditoria por padrão. Leia `TESTES` (`${CLAUDE_PLUGIN_ROOT}/docs/house/TESTES.md`), `AUDITORIAS` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AUDITORIAS.md`) e `AGILE` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AGILE.md`) (TDD/DoD) antes de fechar a ordem. A verificação é seletiva (seção 6).

---

## 4. Gravar o marcador de porte

Após classificar, grave (ou devolva o texto ao usuário, se as regras dele reservarem a escrita no repositório) o marcador `.bigtech-porte` na raiz do projeto (uma linha: `porte=<early|scale|bigtech>` + data + variante). **Nunca** grave `porte=solo` (alias deprecado; se um marcador legado tiver `solo`, os hooks normalizam a leitura para `early`). Com o marcador, o hook SessionStart (`bigtech_porte_reminder.py`) para de lembrar a classificação e passa a ancorar o modo de operação, citando o porte gravado. Reescreva o marcador quando o porte mudar no re-roteamento.

## 5. Re-roteamento

Registre o porte escolhido e o gatilho de re-avaliação. A cada marco (fim de fase, release, mudança de complexidade/criticidade, capacity humana só como sinal auxiliar, novo requisito regulatório), reinvoque `/bigtech:bigtech` ou Cósimo para checar se o projeto subiu ou desceu de porte, e ajustar a constelação. Documente a transição no changelog ou diário do projeto e na governança do próprio projeto; os manuais do plugin não são editados.

## 6. Orquestração, verificação e trabalho pesado

### Orquestração dos agentes

- **Consulta e leitura ficam na sessão**, sem abrir agent; toda alteração de código continua com agente especialista.
- **C-level decide e escreve a ordem de serviço, sem editar nada.** A ordem é fechada: os arquivos que o agente pode tocar e os que não pode, o comportamento, o teste que prova, o critério de pronto, as proibições e "relatório em até N linhas", com N de 3 a 6.
- **Operacional entrega o SHA no ramo e para.** O merge no principal é da thread principal, entre uma publicação e outra. Pausado, o agente para num ponto limpo: commit do que está verde, patch do resto e o caminho do patch no relatório.
- **Retome o mesmo agente** por SendMessage para continuar, corrigir ou destravar o trabalho dele, em vez de despachar outro do zero.
- **Pendências do usuário** (decisões e confirmações que esperam por ele) **vão juntas num AskUserQuestion só**, com até 4 perguntas e multiSelect, nunca como lista em texto solto.
- **"Resolva com clevel"** delega a decisão ao C-level do domínio, e ela entra marcada "a ratificar" até o usuário confirmar.
- **Um arquivo único de decisões, só de acréscimo:** entrada nova no fim, nunca reescrita; correção vira entrada nova que aponta a anterior.
- **Vigie pela notificação** de fim do agente ou da ferramenta, sem polling curto.
- **Worktree barata:** `git worktree add --no-checkout` e, dentro dela, só os arquivos da parte (sparse-checkout); dependências já instaladas entram por symlink, sem reinstalar.
- **Antes de escrever a causa de uma falha no briefing**, leia a asserção que falhou.
- **No fim da onda, olhe o `/usage` por tipo de agent**, para ver onde foi o custo.

### Verificação seletiva (pré-CI e CI)

Régua: uma verificação não pode custar mais que a mudança que ela confere.

- **Roda o que a mudança toca** desde a última versão publicada: os testes ligados aos arquivos mudados pelo grafo de imports **e** pelos caminhos de arquivo que os testes, e os auxiliares deles, citam em texto.
- **Segurança e privacidade rodam sempre**, qualquer que seja a mudança.
- **Tudo roda** quando muda ferramenta de build, de teste ou de publicação, configuração ou dependência, ou quando não há versão anterior para comparar.
- **Para no primeiro erro e mostra o tempo de cada passo.**
- **Com CI na nuvem, o CI fica seletivo e o pré-CI é opcional.** Sem CI na nuvem, o pré-CI faz esse papel, com as mesmas regras.

A publicação de engenharia, uma parte por vez, segue a seção 8 de `/bigtech:proj_software` e o agent `bigtech:release-manager`.

### Trabalho pesado na máquina

Build, suíte, teste de navegador e container seguem a seção 11 de [`hardware-resource-limits`](../../docs/principles/hardware-resource-limits.md): um pesado por vez na trava única da máquina, núcleos reservados ao sistema, teto de memória e de processos por trabalho, prioridade mínima para agente, a publicação primeiro, espera sem laço, teste sem janela no host com esses limites e o que abre janela isolado. Repasse isso na ordem de serviço de quem roda trabalho pesado.

---

## Roteamento de domínios e skills novas

Além dos C-levels, esta skill conhece os agents e as skills de domínio do plugin. O catálogo dos 71 agents, por domínio e com o gatilho de cada um, está na seção "Catálogo de agents" do agent `bigtech:cosimo-chief-of-staff`; consulte-o antes de rotear.

- **Projeto de jogo:** `/bigtech:proj_jogo` orquestra o desenvolvimento de jogo e aloca os agents de jogo por etapa (design, produção, arte, áudio e código). Sem projeto de jogo declarado, eles não entram.
- **Caso médico-jurídico:** `/bigtech:pericia-medica` aciona o quarteto (`bigtech:dr-medico-perito`, `bigtech:dr-medico-trabalho`, `bigtech:dr-medico-psiquiatra`, `bigtech:dr-advogado`) conforme a natureza do caso. Cada um também tem atalho próprio: `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-trabalho`, `/bigtech:dr-medico-psiquiatra` e `/bigtech:dr-advogado`.
- **Ensino e capacitação:** `/bigtech:learning-designer` (aula, plano de aula, quiz, rubrica).
- **Diagnóstico Linux:** `/bigtech:suporte-linux`, que coleta com `bigtech:linux-diag` em modo somente leitura.
- **Pendências:** `/bigtech:tab_pendencias` (tabela canônica; substitui qualquer referência sem o prefixo do plugin).
- **Vigia de crashes:** `/bigtech:watchcode {on|off|status}`, quando se quer vigiar o journal e os coredumps enquanto agentes ou a thread principal codam; crash da sessão vai ao `bigtech:caetano-cto` para diagnóstico, e crash de outra sessão ou do sistema vira relatório.
- **Conexão com a tampa fechada:** `/bigtech:manter_ligado {on|off|status|limpar}`, quando o laptop vai na mochila; mantém a conexão de dados e salva o estado das sessões com a bateria baixa (só Linux com systemd).
- **Design visual de alta fidelidade:** `/bigtech:visual-design-director`, para design visual, redesign, mockup renderizado e spec visual; conduz o agent `bigtech:visual-design-director`.
- **Monitor de agentes:** `/bigtech:olhe_agentes {on|off|status}`, quando se quer um tick a cada 5 minutos que vigia se os agentes pararam; o monitor vive na sessão e morre com ela.
- **Marketing de produto:** `bigtech:product-marketing-manager` atua sob `bigtech:camilo-cmo`; blog, SEO e calendário editorial ficam com `bigtech:content-seo`.
- **Desenvolvimento de pessoas:** `bigtech:engineering-coach` trabalha junto de `bigtech:engineering-manager`, que mantém a promoção e a performance formal.
- **Revisão e narrativa:** `bigtech:revisor-textual` (copydesk e cânone), `bigtech:narrative-designer` (arquitetura) e `bigtech:narrative-writer` (prosa final).

## Integração com ecossistema

- Agent `bigtech:cosimo-chief-of-staff`: o roteador que esta skill invoca.
- Skill `/bigtech:proj_software`: execução SDLC de engenharia (fases 4-9); esta skill delega a ela.
- Skill `/bigtech:tab_pendencias`: tabela canônica de pendências (formato de `ORG` (`${CLAUDE_PLUGIN_ROOT}/docs/house/ORG.md`)).
- Docs canônicos: `ORG` (`${CLAUDE_PLUGIN_ROOT}/docs/house/ORG.md`), `pipeline_release_1.0` (`${CLAUDE_PLUGIN_ROOT}/docs/house/pipeline_release_1.0.md`), `lideranca_pipeline_release` (`${CLAUDE_PLUGIN_ROOT}/docs/house/lideranca_pipeline_release.md`), e os 5 manuais em `${CLAUDE_PLUGIN_ROOT}/docs/house/`: `CONTRACT` (`${CLAUDE_PLUGIN_ROOT}/docs/house/CONTRACT.md`), `TESTES` (`${CLAUDE_PLUGIN_ROOT}/docs/house/TESTES.md`), `AGILE` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AGILE.md`), `DEPLOY_CHECKLIST` (`${CLAUDE_PLUGIN_ROOT}/docs/house/DEPLOY_CHECKLIST.md`), `AUDITORIAS` (`${CLAUDE_PLUGIN_ROOT}/docs/house/AUDITORIAS.md`).
- Linguagem default: pt-br.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
