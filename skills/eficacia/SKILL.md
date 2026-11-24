---
name: eficacia
description: Aplica a eficácia, o máximo de trabalho útil pelo menor gasto, às sessões do Claude Code, numa sessão exclusiva de gerência ou numa sessão de projeto que se autogerencia. Use quando o usuário invocar /bigtech:eficacia, disser "abra uma sessão de gerência", "gerencie as sessões", "vou dormir", "a sessão parou esperando resposta", "a gerência gasta sem produzir", "autogerencie este projeto", "enfileire as perguntas e siga", ou pedir disponibilidade, produtividade, sobrecarga de gestão ou custo do atraso. Modos gerente (um timer do sistema, sem modelo, vigia as sessões, e a gerência só decide no desvio), projeto (pré-voo, enfileire e siga, relato por exceção) e status (a equação de eficácia). O timer exige systemd --user.
argument-hint: "[gerente|projeto|status]"
---

# eficacia

Meta: o máximo de trabalho útil pelo menor gasto. Leia [references/eficacia.md](references/eficacia.md) antes do primeiro uso: lá estão os problemas que deram origem à skill, a equação, os detectores (V verificado, A a verificar), as 3 classes de decisão e a dieta de gasto. Este arquivo só diz o que fazer em cada modo. Argumento padrão: `status`.

O vigia é um script sem modelo: `bash ${CLAUDE_SKILL_DIR}/bin/vigia.sh <subcomando>`, com `check [--dry-run]`, `status`, `instalar [--intervalo MIN]`, `remover`, `dormir` e `acordar`. Config opcional em `${XDG_CONFIG_HOME:-$HOME/.config}/bigtech/eficacia.json` (`esperadas`, `limiar_espera_min`, `limiar_travada_min`, `bandeira_auto_min`; 0 desliga a bandeira automática).

## `gerente`: sessão exclusiva de gerência

1. Confira o timer com `systemctl --user is-active bigtech-eficacia.timer`. Se não estiver ativo, ofereça `vigia.sh instalar` e instale só com o sim do líder. A cadência é dele: não a mude sem aprovação dele.
2. Leve ao líder por AskUserQuestion, num bloco só, apenas o que falta: as sessões esperadas (a lista `esperadas` da config) e o % de uso da conta, para medir a eficácia.
3. Quando o líder disser que vai dormir, faça o pré-voo nas sessões (modo `projeto`, passo 1) e rode `vigia.sh dormir`. Na volta dele, rode `vigia.sh acordar` e entregue o resumo único: todas as decisões pendentes em lote, cada uma com a sua recomendação.
4. Opere por exceção. Cada resposta que a gerência tiver para uma sessão vai a ela por SendMessage, nunca só na tela desta. O timer avisa o celular a cada desvio novo, mas não acorda esta sessão (A, veja a referência). Ao ser chamada, leia o estado com `vigia.sh check --dry-run` e trate só as linhas `desvio`, cada uma uma vez. Parada ordenada nunca é desvio: não a retome sem ordem do líder.
5. Leia a pergunta parada antes de classificá-la, decida pela matriz de 3 classes e roteie pela presença. Classe 1 (desempate barato e escolha reversível): a sessão decide sozinha. O C-level, que é caro (opus), só entra na dúvida técnica de verdade. Com a bandeira "líder dormindo", a dúvida vai ao C-level do domínio, que decide e registra para ratificação; com o líder acordado, vai a ele. Commit barrado pelo classificador de permissão, permissão, regra ou lei, gasto, ação irreversível, GPU, merge, tag e deploy são sempre só do líder: vão às pendências com recomendação.
6. Siga a dieta de gasto: um ciclo só (não ligue o `/bigtech:olhe_agentes` junto), prompt de tick curto que aponta para a memória, sem ListAgents nem `docker ps` por rotina, e relato só quando algo muda e exige ação.

## `projeto`: a sessão de projeto se autogerencia

1. Faça o pré-voo antes de o líder dormir: liste as decisões que você prevê precisar e leve-as juntas, num AskUserQuestion só; e marque os próximos itens do TODO.md, para haver trabalho quando a sessão ficar sem o líder.
2. Enfileire e siga. Antes de perguntar, confira a bandeira `${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia/lider_dormindo`. Com ela, a dúvida classe 2 vai ao C-level do domínio, e a pergunta classe 3 vai às pendências (a INBOX do `TODO.md`, se houver), com a sua recomendação, ANTES de bloquear; depois troque de trabalho.
3. Relate por exceção: fale só quando algo muda e exige ação.
4. Use até 4 agentes ao mesmo tempo, sem dois no mesmo arquivo, no mesmo índice do git ou no mesmo trabalho pesado.
5. Rode o trabalho pesado só pelo `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/bin/pesado`, se ele existir na configuração do usuário; sem ele, siga a trava única da seção 11 de [`hardware-resource-limits`](../../docs/principles/hardware-resource-limits.md).
6. Ao fechar cada onda, limpe os seus próprios builds e temporários sem uso, sem esperar cobrança.
7. Para pausar, rode `/memo_persistente` (skill opcional, fora do plugin) e marque a parada ordenada, para a pausa não virar desvio; ao retomar, desmarque. Os comandos estão na referência.

## `status`

Rode `vigia.sh status` e mostre, por sessão e no total das últimas 24 h:

- **Disponibilidade:** a coluna `disponibilidade` (fração das passadas em que a sessão estava ocupada, fora as paradas ordenadas).
- **Custo do atraso:** a parte medida é a coluna `esperando_min`.
- **Produtividade** (entregas aceitas ÷ gasto total) e **sobrecarga de gestão** (gasto de gestão ÷ gasto de produção, meta perto de zero): o script não as mede; monte-as com as entregas aceitas no período e com o % de uso que o líder informar.
- **Eficácia = Disponibilidade × Produtividade.**

Avise sempre que o % de uso vem do líder: a sessão não o vê.

## Trava "líder dormindo"

`vigia.sh dormir` cria a bandeira e `vigia.sh acordar` a apaga. Enquanto ela existir, o hook PreToolUse `bin/hook_lider_dormindo.sh`, registrado no `hooks/hooks.json` do plugin, nega o AskUserQuestion e manda gravar a pergunta nas pendências. Verificado ao vivo em 24/11/2026: com a bandeira ligada, a pergunta foi negada. A pergunta barrada vai a `<estado>/fila.md` (flock, varias sessoes). `vigia.sh registrar "<texto>"` anota a decisao de C-level em `decisoes_clevel.md`. `vigia.sh acordar` imprime fila e decisoes e as move para `arquivo/<data-hora>/`. O hook Stop (`bin/hook_fim_turno.sh`, no hooks.json) bloqueia o fim de turno uma vez, com a bandeira, e libera com `stop_hook_active` verdadeiro, sem laco. Permissão barrada (hook PermissionRequest) também vai à fila, como `permissão: <ferramenta> <resumo>`. Com a bandeira, `vigia.sh check` não avisa o celular: grava os desvios em `desvios_noite.md`. A bandeira também se liga sozinha com a tela bloqueada há mais de `bandeira_auto_min` min (padrão 30, via loginctl); ao desbloquear, só a automática é apagada. `vigia.sh status` mostra tokens e entregas por sessão nas últimas 24 h. `vigia.sh acordar` agrupa fila, decisões e desvios por sessão e os arquiva; a saída vem sem caracteres de controle. Lembrete em prompt e memória não segura: o conserto é mecânico e preventivo.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
