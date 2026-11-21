---
name: olhe_agentes
description: 'Liga, desliga ou mostra o MONITOR de agentes da sessão. Tick a cada 5 minutos, prazo de 7 dias. Com o modo autônomo LIGADO, se o main e os agentes estiverem sem fazer nada, descobre o motivo, resolve dentro do que o modo autônomo autoriza, registra cada decisão e manda continuarem no projeto. Com o modo autônomo DESLIGADO, se o trabalho acabou escreve na tela "trabalho concluído"; se não acabou, descobre o motivo, apresenta a causa e as opções ao usuário e manda retornarem depois da escolha dele. Uma parada ordenada pelo usuário nunca é retomada sem ordem dele. Use IMEDIATAMENTE quando o usuário invocar /bigtech:olhe_agentes, ou disser "ligue o monitor dos agentes", "olhe os agentes", "vigie se os agentes pararam", "desligue o monitor dos agentes". Argumentos: on (padrão), off, status, tick (uso interno do próprio ciclo).'
---

# olhe_agentes

Monitor de agentes. Requisitos de origem, condensados no procedimento abaixo:

> crie um MONITOR com as seguintes caracteristicas:
> 1-ticks a cada 5 minutos
> 1.1- se modo autonomo ligado
> 1.1.1-se main e os agentes estiverem sem fazer nada, descubra o motivo e resolva. Depois mande que continuem trabalhando no projeto;
> 1.2- se modo autonomo desligado
> 1.2.1-se o trabalho que estavam fazendo acabou, escreva na tela que o trabalho foi concluido
> 1.2.2-se o trabalho que estavam fazendo ainda nao acabou descubra o motivo, resolva e mande retornarem ao trabalho
> 2- prazo 7 dias

e depois: "crie uma skill chamada olhe_agentes que ligue sempre esse monitor".

## Estado (por projeto)

`SLUG` = nome da pasta do cwd (ex.: `meu-projeto`). Diretório de estado: `~/.config/olhe_agentes/$SLUG/`.
- `prazo` – epoch do fim (arranque + 7 dias).
- `parada_do_lider`: existe enquanto houver uma parada ORDENADA PELO USUÁRIO. Linha 1 é a data; o resto é o que parou e por quê.
- `concluido_avisado` – identificador do último trabalho já anunciado como concluído, para não repetir o aviso.

## `on` (padrão)
1. `mkdir -p ~/.config/olhe_agentes/$SLUG`.
2. Se `prazo` não existir ou já tiver vencido, grave `$(( $(date +%s) + 7*86400 ))`.
3. Arme o ciclo: `ScheduleWakeup` com `delaySeconds: 300` e `prompt: "/bigtech:olhe_agentes tick"`.
4. Responda ao usuário em uma linha: monitor ligado, a hora do próximo tick, o prazo e se há parada do usuário ativa.
**Limite que tem de ser declarado:** o monitor vive DENTRO da sessão. Se a janela fechar ou o Claude cair, os ticks param junto. Nada de fora retoma a sessão com segurança. Para sobreviver a reinício, ofereça ao usuário o gêmeo local: agendador local do sistema ou `/schedule`; a escolha é dele.

## `off`
`ScheduleWakeup` com `stop: true`, depois uma linha confirmando. Os arquivos de estado ficam.

## `status`
Mostra o prazo restante, a parada do usuário (sim/não e o texto), o modo autônomo, os agentes em voo e os comandos de trabalho em execução.

## `tick` (o ciclo, a cada 5 minutos)
1. **Prazo:** se vencido, escreva "monitor de agentes encerrado (prazo de 7 dias)" e NÃO reagende. Fim.
2. **Leitura do estado**, sempre por comando e nunca de memória:
   - modo autônomo: arquivo `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/autonomo/$SLUG.json` presente e dentro do prazo;
   - agentes despachados por esta sessão ainda sem relatório final, com o mtime do `.output` de cada um. Ele fica no diretório temporário do Claude Code: a base é `$CLAUDE_CODE_TMPDIR` quando definido e, sem ele, o diretório temporário do sistema (`$TMPDIR` ou `/tmp` no Linux, `/tmp` no macOS), seguida de `claude-$UID/`; dentro dela o caminho observado é `<slug-do-cwd>/<sid>/tasks/*.output`, então confira com `ls` antes de medir. **O `.output` é LINK SIMBÓLICO: meça com `stat -L -c %Y`, nunca `stat -c %Y`, que lê a data de criação do link e acusa silêncio falso (medido em 03/10/2026: 881 s sem `-L` contra 2 s com `-L`, com o agente escrevendo);**
   - comandos de trabalho em execução, numa ÚNICA chamada de `ps`/`pgrep` (nunca um processo por item): ctest, cmake, ninja, cc1plus, clang-tidy, cppcheck, preci.sh, docker build/run/exec, wine, cl.exe, link.exe;
   - `git status` e `git log -3`;
   - o snapshot da sessão (`project_session_atual.md` na memória do projeto), para saber qual é o trabalho em curso.
3. **PARADO** quer dizer calado há 5 min ou mais **E** sem nenhum comando em execução. Um agente calado no meio de um build ou teste longo está TRABALHANDO e não recebe ordem (o usuário corrigiu: "eu disse PARADO!").
4. **A parada do usuário vence tudo.** Se `parada_do_lider` existir, o monitor só vigia e informa, numa linha curta. Não retoma nada. Quando o usuário mandar seguir, o main apaga o arquivo.
5. **Modo autônomo LIGADO**, com o main e todos os agentes parados:
   - descobrir o motivo (relatório que ficou sem resposta, agente que disse "aguardando", portão vermelho, build que falhou);
   - descobrir a causa; resolver só dentro do escopo que o modo autônomo autoriza, delegando a um agente especialista quando for trabalho de produto, e registrar cada decisão;
   - retomar o trabalho do projeto pelo snapshot.
   Agente parado em voo recebe primeiro o teste mais simples (uma palavra, pedindo o estado); só se continuar parado, recebe `SendMessage` com a retomada: "siga, relate em 3 linhas o que já tem".
6. **Modo autônomo DESLIGADO:**
   - o trabalho em curso acabou (tudo commitado e relatado, sem agente nem pendência do snapshot): escreva "trabalho concluído: <o quê>", uma vez por trabalho (`concluido_avisado`);
   - não acabou e parou SEM ordem do usuário: descubra o motivo, apresente a causa e as opções, e retome o trabalho só depois da escolha dele.
7. Nada a fazer: uma linha curta ("tick hh:mm, tudo em ordem" ou "tick hh:mm, parada do líder ativa").
8. Reagende na sessão enquanto ela viver: `ScheduleWakeup` 300 s com `prompt: "/bigtech:olhe_agentes tick"`; a morte por reinício está declarada no limite do `on`.

Nunca fazer, em nenhum ramo:
- push, merge, tag ou ação irreversível sem a autorização que o projeto exige;
- `SendMessage` de "siga" para agente que está trabalhando;
- retomar uma parada ordenada pelo usuário.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
