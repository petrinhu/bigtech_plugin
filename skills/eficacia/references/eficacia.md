# Eficácia de sessões: referência

> Referência da skill `/bigtech:eficacia` ([SKILL.md](../SKILL.md)), com a explicação da origem. Público: quem opera várias sessões do Claude Code na mesma máquina, como gerência ou como sessão de projeto. Revisada em 24/11/2026.

## Origem

Uma madrugada de trabalho autônomo, com duas sessões de projeto e uma sessão de gerência, produziu quase nada e gastou uso da conta. Os problemas abaixo são dessa noite, descritos de forma genérica, e cada conserto da skill nasce de um deles. A meta é a do líder: o máximo de trabalho útil pelo menor gasto.

## A equação

**Eficácia = Disponibilidade × Produtividade**

| Termo | Definição | Meta |
|---|---|---|
| Disponibilidade | tempo ocupado ÷ janela autorizada | perto de 1 |
| Produtividade | entregas aceitas ÷ gasto total | a maior possível |
| Sobrecarga de gestão | gasto de gestão ÷ gasto de produção | perto de 0 |
| Custo do atraso | o que se perde enquanto uma entrega espera; a parte medida é o tempo de espera | perto de 0 |

A eficácia não cresce sem limite. O que tende a zero é a espera e a sobrecarga de gestão; o teto é o custo de produção de cada entrega. Linha de base da noite de origem: disponibilidade perto de zero, com duas sessões paradas mais de cinco horas e a gerência gastando cerca de 130 turnos sem nenhuma ação.

Onde medir: o `vigia.sh status` dá a disponibilidade (fração das passadas do timer em que a sessão estava ocupada, fora as paradas ordenadas) e os minutos em espera. O gasto vem do % de uso da conta, que só o líder vê e informa.

## Vocabulário

- **Gestão por exceção:** a gerência só age quando um indicador sai da faixa. Sem desvio, não há turno.
- **Teoria das Restrições:** o sistema rende o que rende o gargalo. Aqui os gargalos são a atenção do líder e o orçamento de uso da conta; otimize esses dois antes de qualquer outra coisa.
- **Lean:** espera e inspeção sem achado são desperdício. Um tick que conclui "tudo igual" é inspeção sem achado.
- **Direitos de decisão (RACI):** cada decisão tem dono declarado antes de surgir. A matriz de 3 classes, abaixo, é o RACI das dúvidas.
- **Custo do atraso:** o valor que se perde, por unidade de tempo, enquanto uma entrega espera. Uma pergunta bloqueante com o líder dormindo cobra o custo do atraso inteiro da sessão parada.

## Os 11 problemas e o conserto de cada um

| # | O que aconteceu | Conserto |
|---|---|---|
| 1 | Duas sessões ficaram paradas 5 h 37 min numa pergunta bloqueante ao líder dormindo. Uma pedia autorização de commit depois que o classificador de permissão barrou um agente; a outra tinha uma dúvida técnica. Disponibilidade perto de zero. | Pré-voo antes de dormir; enfileire e siga; bandeira "líder dormindo" com hook que nega a pergunta. |
| 2 | A gerência gastou sem produzir: cerca de 130 turnos (um tick de 5 min e um monitor de cerca de 4 min), cada um recarregando a conversa inteira, só para concluir "tudo igual". O uso da conta subiu de 11% para 15% com as sessões paradas. | Vigia sem modelo, por timer do sistema; a gerência só age no desvio. |
| 3 | Uma ordem do líder ("dúvidas vão ao C-level") estava escrita em todo prompt de tick e não foi cumprida: a gerência só repetiu o alerta de espera. A mesma lição já estava na memória havia cinco dias. | Lembrete em prompt e memória não segura: conserto mecânico (bandeira, hook, pendência gravada antes de bloquear). |
| 4 | Roteamento errado. A gerência mandou ao C-level um bloqueio de classificador e commit, que é só do líder, e repassou ao líder uma dúvida técnica, que era do C-level. E a ordem de mandar ao C-level valia só com o líder dormindo. | Matriz de 3 classes e roteamento pela presença. |
| 5 | Mensagem a sessão presa não destrava: três mensagens entre sessões ficaram sem leitura enquanto a sessão estava presa na pergunta. | Previna a pergunta bloqueante; não conte com mensagem para destravar. |
| 6 | Desperdício da gerência: dois ciclos redundantes; prompt de tick longo e vencido; relato repetido de estado sem mudança; limpeza de hora em hora que rodou três vezes sem apagar nada; listagem de agentes e de contêineres a cada ciclo; dois ticks no mesmo minuto; push repetido. | Dieta de gasto, abaixo; push uma vez por episódio. |
| 7 | Mudança sem aprovação: a gerência alargou a cadência do monitor de 5 para 10 e depois para 15 min sem o líder aprovar. | A cadência só muda com aprovação do líder. |
| 8 | Infraestrutura frágil. Laço de sessão (CronCreate, ScheduleWakeup) vive só na sessão e morre com `/compact`, reinício e fechamento; com o limite de uso atingido ou a gerência morta, a vigilância e a pausa agendada somem. Uma sessão fantasma apareceu por segundos, de origem desconhecida. | Timer do sistema (systemd --user), fora da sessão; lista de sessões esperadas em arquivo. |
| 9 | Detector enganoso: o `updatedAt` do JSON de sessão não é batimento (estava 926 s velho com a sessão trabalhando). | `statusUpdatedAt`, mtime do transcript e CPU da árvore do pid, conforme a tabela de detectores. |
| 10 | Suposição sem evidência: a gerência afirmou que as duas paradas eram decidíveis pelo C-level sem ter lido as perguntas. | Leia a pergunta antes de classificar; monte a matriz a partir das paradas reais. |
| 11 | Causas de parada fora do plano inicial: prompt de permissão, limite de uso da conta, rede caída, sessão morta, sessão ocupada mas travada, parada ordenada (que não é desvio) e a própria gerência. | Um detector para cada uma, verificado ou marcado a verificar. |

## Detectores

**V** = verificado (medido no dia de origem ou coberto pelos testes do `vigia.sh`); **A** = a verificar. Os limiares vêm da config; os padrões são 10 min de espera e 15 min de transcript parado.

| Situação | Como detectar | Estado |
|---|---|---|
| Esperando resposta | `status` igual a `waiting` no JSON da sessão e `agora − statusUpdatedAt` acima de `limiar_espera_min` | V |
| Ocupada mas travada | transcript `.jsonl` do projeto parado acima de `limiar_travada_min`; falta somar a CPU da árvore do pid sem avanço e a ausência de ticket na fila do trabalho pesado | V (transcript), A (CPU e limiar) |
| Ociosa | não tem estado próprio: com o transcript parado acima do limiar, sai como travada | A |
| Morta | sessão da lista `esperadas` sem processo vivo | V |
| Parada ordenada | arquivo `parada/<nome>` no diretório de estado; nunca é desvio | V |
| Prompt de permissão | bloqueia como uma pergunta; falta ver se aparece como `waiting` | A |
| Limite de uso da conta, rede caída | ainda sem detector | A |
| Disco, memória, OOM | fora do vigia: o cgroup e o `/bigtech:watchcode` já cobrem; não duplique | (fora) |
| Trabalho pesado parado | fora do vigia: o próprio `pesado` corta no teto de 15 min | (fora) |
| Contexto cheio | fora do vigia: o autocompact cobre | (fora) |
| A própria sessão esperando | o hook `Notification` (matchers como `permission_prompt` e `idle_prompt`) roda comando sem modelo e pode avisar o celular; não está confirmado que o `idle_prompt` dispare num AskUserQuestion (teste gravando em arquivo), e não existe evento "esperando há X s" | A |
| Outra sessão terminou | o `notify_when_idle` do SendMessage avisa uma vez quando outra sessão local fica ociosa ou sai (sem custo de token ao assinar, expira em 12 h, só a conversa principal assina); serve para "terminou", não para "esperando o líder"; falta confirmar se é o `notify_idle` do `peerFeatures` | A |
| Valores de `status` | `busy` e `waiting` não são documentados; observe o arquivo durante um AskUserQuestion e um prompt de permissão. O JSON também traz `waitingFor`, que o vigia ainda não lê | A |
| Presença do líder | bandeira explícita (`vigia.sh dormir` e `vigia.sh acordar`); `IdleHint` e `LockedHint` do logind; nunca o `UserPromptSubmit`, que dispara também em tick de cron | V (bandeira), A (logind) |

## As 3 classes de decisão

| Classe | Quem decide | Quando | O que a sessão faz |
|---|---|---|---|
| 1 | a própria sessão | decisão técnica, reversível, dentro do escopo da ordem | decide, registra e segue |
| 2 | o C-level do domínio (por exemplo, `bigtech:caetano-cto` em engenharia) | dúvida técnica ou de produto, reversível, fora do escopo da sessão | com o líder dormindo, pergunta ao C-level, que decide e registra para ratificação do líder; com o líder acordado, pergunta ao líder |
| 3 | só o líder | commit depois que o classificador de permissão barrou um agente; permissão; regra ou lei; gasto; ação irreversível; uso da GPU; merge no ramo principal; tag; deploy | grava a pergunta nas pendências, com a recomendação, ANTES de bloquear, e troca de trabalho |

A presença vem da bandeira "líder dormindo", nunca de suposição. Leia a pergunta antes de classificá-la e ajuste a matriz a partir das paradas reais.

## Pré-voo, enfileire e siga, resumo ao acordar

- **Pré-voo:** antes de o líder dormir, cada sessão lista as decisões que prevê precisar, e o líder responde tudo de uma vez.
- **Enfileire e siga:** diante de uma decisão classe 3, a sessão grava a pergunta nas pendências do projeto (a INBOX do `TODO.md`, se houver), com a recomendação, e passa ao próximo item que não depende dela.
- **Resumo único ao acordar:** todas as decisões pendentes, em lote, cada uma com a sua recomendação.

## Vigia sem modelo (`bin/vigia.sh`)

Laço de sessão morre com `/compact`, reinício e fechamento; o timer do sistema sobrevive a sessão morta, a limite de uso e a `/clear`, e a parte mecânica roda offline, sem modelo. O vigia não lê journal nem coredump: a detecção de crash é só do daemon do `/bigtech:watchcode`.

| Subcomando | O que faz |
|---|---|
| `check [--dry-run]` | uma passada: lê os JSON de sessão e o mtime dos transcripts, aplica os detectores, grava o estado no `log.tsv` e avisa o celular só do desvio novo (KDE Connect; sem ele, `notify-send`). Com `--dry-run`, só imprime o estado e os desvios (`NOVO` ou `ja avisado`), sem gravar nem avisar. |
| `status` | por sessão e no total, a disponibilidade e os minutos em espera das últimas 24 h, lidos do `log.tsv` |
| `instalar [--intervalo MIN]` | instala e liga o timer `bigtech-eficacia.timer` do systemd --user, com prioridade mínima (padrão 5 min); sem `systemctl`, falha com mensagem clara |
| `remover` | desliga e apaga o timer e o serviço |
| `dormir` e `acordar` | criam e apagam a bandeira `lider_dormindo` |

**Config opcional** em `${XDG_CONFIG_HOME:-$HOME/.config}/bigtech/eficacia.json`. A chave `esperadas` lista os nomes de sessão (o campo `name` do JSON da sessão, como o `check --dry-run` os mostra). Sem o arquivo, valem os padrões e nenhuma sessão conta como esperada, e o detector de sessão morta fica desligado.

```json
{
  "esperadas": ["projeto-a", "projeto-b"],
  "limiar_espera_min": 10,
  "limiar_travada_min": 15
}
```

**Estado** em `${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia/`: `log.tsv`, `desvios.txt`, a bandeira `lider_dormindo` e as paradas em `parada/<nome>`. Para marcar uma parada ordenada e desmarcá-la ao retomar:

```bash
d="${XDG_STATE_HOME:-$HOME/.local/state}/bigtech-eficacia/parada"
mkdir -p "$d" && touch "$d/projeto-a"   # pausa: a sessão não vira desvio
rm -f "$d/projeto-a"                    # retomada
```

**Limite atual (A):** o timer avisa o celular, mas não acorda a sessão de gerência. A gerência age quando é chamada e lê o estado com `vigia.sh check --dry-run`.

## Trava "líder dormindo": estado da verificação

- **Estado: registrado; prova ao vivo A.** O script `bin/hook_lider_dormindo.sh` está no `hooks/hooks.json` do plugin, no PreToolUse com matcher `AskUserQuestion`. Com a bandeira, ele nega a pergunta e manda gravá-la nas pendências e trocar de trabalho; sem ela, sai em silêncio. A documentação oficial diz que o PreToolUse cobre toda chamada de ferramenta, e o script tem teste próprio (`tests/test_hook_lider_dormindo.sh`). Falta a prova ao vivo: numa sessão real, com a bandeira, o AskUserQuestion volta negado.
- **Como conferir:** na raiz do plugin, `grep -n lider_dormindo hooks/hooks.json` mostra o registro. Para a prova ao vivo, num perfil de teste (`CLAUDE_CONFIG_DIR` isolado) com o plugin instalado, rode `vigia.sh dormir`, provoque uma pergunta e confira que ela volta negada com o motivo; depois, `vigia.sh acordar`.
- **Se a prova falhar,** a bandeira só vale se a sessão a ler antes de perguntar (modo `projeto`, passo 2). Isso é lembrete, e lembrete não segura (último tópico desta página).

## Dieta de gasto da gerência

- Prompt de tick curto, que aponta para a memória em vez de repetir regras.
- Relato por exceção: gerência e sessões só falam quando algo muda e exige ação.
- Um ciclo, não dois: não rode o `/bigtech:olhe_agentes` junto com outro tick.
- Sem ListAgents nem `docker ps` por rotina.
- Push uma vez por episódio.
- Cadência só muda com aprovação do líder.
- Recomeço enxuto da sessão de gerência: `/memo_persistente` e `/clear` são do líder.
- Não discuta plano na sessão mais cara: grave o plano e implemente numa sessão nova.
- Meça a sobrecarga de gestão e o custo do atraso e mostre-os ao líder. O % de uso vem dele.

## Limpeza

Cada sessão limpa os próprios builds e temporários sem uso ao fechar cada onda, sem ser cobrada. A gerência não cobra limpeza de hora em hora, porque a cobrança horária rodou três vezes sem apagar nada. Esta skill não muda nenhuma regra do usuário: a regra de limpeza dele continua como está.

## O limite: lembrete não segura

Lembrete em prompt e memória não segura; o conserto é mecânico e preventivo. Na noite de origem, a ordem estava em todo prompt de tick e a mesma lição estava na memória havia dias, e nada disso mudou o comportamento. Por isso cada conserto desta skill é um mecanismo (timer, bandeira, hook, pendência gravada antes de bloquear) ou um passo que acontece antes do problema (o pré-voo), nunca mais um aviso.
