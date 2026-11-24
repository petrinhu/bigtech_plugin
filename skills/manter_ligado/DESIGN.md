# DESIGN — skill `manter_ligado`

> Spec de design validado em brainstorm. Data: 2026-07-13. Porte: solo/pessoal (sem constelação bigtech). Escopo: fase única, **100% user-space, zero root**.

## Propósito

Com o laptop na mochila (tampa fechada, conectado ao tethering do celular), **manter a conexão de dados viva e as sessões Claude rodando** enquanto o usuário controla tudo pelo celular via `/rc`, o Remote Control do Claude Code. Quando a bateria chega a **≤5%**, **salvar automaticamente o estado de todas as sessões** (conversa, contexto, decisões) no disco, **sem desligar nem hibernar**: a máquina segue rodando até a bateria zerar sozinha.

Alvo: Linux com systemd e KDE Plasma (o aviso ao celular usa o KDE Connect). Hibernar ficou fora de escopo (ver "Fora de escopo").

## Comandos

- `/bigtech:manter_ligado --on` — arma o keep-alive + guardião de bateria; registra a sessão atual.
- `/bigtech:manter_ligado --off` — desregistra a sessão atual; derruba o guardião só se for a última.
- `/bigtech:manter_ligado --status` — mostra se está armado e por quantas sessões; reconcilia o registro.
- `/bigtech:manter_ligado --limpar` — faxina geral sob demanda (apaga snapshots, zera registro).

## Arquitetura — controlador fino + guardião singleton

A skill é um **controlador fino**. O trabalho real roda numa unidade `systemd --user` **transitória** que vive **independente de qualquer sessão Claude** (o laptop está na mochila; sessões podem estar ociosas ou encerradas).

| Peça | Responsabilidade | Onde vive |
|---|---|---|
| skill `manter_ligado` | parse do comando; registra/desregistra a sessão; sobe/derruba o guardião | `skills/manter_ligado/` |
| registro de sessões | flag `guardian.armed` + `sessions/<sid>` (session-id, slug, path do transcript, PID) — refcount anti-corrida | `$XDG_RUNTIME_DIR/manter_ligado/` (tmpfs) |
| guardião (script) | segura o inhibitor do logind; roda o loop de bateria | chamado pela unidade transitória |
| unidade `systemd --user` transitória (SINGLETON) | `systemd-inhibit --what=sleep:handle-lid-switch --mode=block` + loop | `systemd-run --user` (sem arquivo permanente) |
| push | KDE Connect (`kdeconnect-cli`) → celular, local; fallback `notify-send` | dentro do loop |

**Por que singleton resolve a concorrência:** uma unidade systemd está ativa ou não; mandar iniciar de novo é no-op. Quem salva/hiberna (aqui: quem salva) é o **guardião único**, nunca cada sessão. Ele salva **todas as sessões registradas de uma vez** — sem corrida, e funciona mesmo com zero sessões vivas.

## Tela (importante para uso na rua)

O guardião **NÃO força DPMS**. Inibe apenas `sleep` + `handle-lid-switch` (não inibe `idle`). Consequência:

- tampa fechada **não suspende** → conexão viva;
- sistema **não dorme sozinho**;
- a tela **apaga sozinha** pelo comportamento normal do KDE (economia de bateria) e **acorda ao abrir a tampa / tecla / touchpad**, ligado **ou na bateria** — pelo caminho testado do compositor, sem risco de tela preta travada.

## Registro de sessões (anti-corrida + refcount)

```
$XDG_RUNTIME_DIR/manter_ligado/          # tmpfs: limpo em boot real (semântica correta)
├── guardian.armed                        # presença = guardião no ar
└── sessions/<session-id>                 # 1 por sessão que armou: id, slug, transcript path, PID
```

Ciclo de vida:

- `on` → reconcilia o registro (remove entradas de PID morto); registra a sessão atual; sobe o guardião se ainda não estiver no ar (senão no-op).
- `off` → remove a entrada da sessão atual; guardião cai **só quando `sessions/` fica vazio** (o último a sair apaga a luz). `off` de uma sessão nunca desarma as outras.
- `status` → reconcilia e reporta ("armado por N sessões").

## Loop de bateria (dentro do guardião)

- Lê `/sys/class/power_supply/BAT1/capacity` e `/sys/class/power_supply/ACAD/online` a cada ~60s. São os nomes da máquina de desenvolvimento; em outra máquina, ver a nota de plataforma no `SKILL.md`.
- **AC conectado a qualquer momento → aborta ações de bateria** (reseta debounce).
- **20% (aviso, 1x com debounce):** push KDE Connect com o aviso de bateria, que sugere rodar `/memo` nas sessões pelo `/rc`. Só conveniência; o 5% salva de qualquer jeito. O `/memo` é opcional e só existe se estiver na configuração do usuário; o `/rc` é o Remote Control do Claude Code.
- **≤5% (latch, 1x por descarga):** executa o **salvamento** (abaixo).

## Salvamento automático a 5% (feito 1x pelo guardião)

1. **Push forte** → celular: *"Bat 5% — salvando estado."*
2. **Para cada sessão no registro:** copia o `transcript .jsonl` da sessão → `$CLAUDE_CONFIG_DIR/manter_ligado_snapshots/<data>/<session-id>.jsonl` + metadata (slug, cwd, hora). **Mecânico, offline, sempre funciona — é a garantia.** O transcript é a conversa inteira em fidelidade total.
3. **Melhor-esforço (se configurado e houver tempo/bateria):** `claude -p` headless destila cada transcript em memórias tipadas (o que o `memo_persistente` faz), **sobrescrevendo no lugar** a memória de snapshot da sessão (ex: `project_session_atual.md`). O `memo_persistente` é uma skill opcional: não vem no plugin e só existe se estiver na configuração do usuário. Sem ela, não conte com este passo; o passo 2 continua sendo a garantia.
4. **NÃO desliga, NÃO hiberna.** A máquina **segue rodando**. Abrir a tampa a qualquer hora → uso normal. Bateria chega a 0% → morre sozinha; o estado já está no disco.

## Higiene de artefatos (nada acumula sem `--limpar`)

| Artefato | Onde | Higiene automática |
|---|---|---|
| Registro de sessões | `$XDG_RUNTIME_DIR/manter_ligado/` | tmpfs (some no boot) + reap de PID morto em `on`/`status` |
| Snapshots de transcript | `$CLAUDE_CONFIG_DIR/manter_ligado_snapshots/` | **retenção = 1**: cada save poda os anteriores |
| Memos destilados (só com a skill opcional `memo_persistente`) | `memory/` da sessão | **sobrescrita no lugar** (dedup nativo do memo_persistente) |
| Log do guardião | **journald** (`systemd --user`) | rotação automática do journald; sem arquivo crescendo |
| Unidade do guardião | `systemd-run` transitória | sem arquivo permanente; morre no `off` |

`--limpar` = faxina geral sob demanda (apaga o dir de snapshots inteiro, zera o registro, opcional limpar a memória de snapshot). **Não é necessário** para evitar acúmulo — cada artefato já tem retenção=1 / sobrescrita / tmpfs / journald por padrão.

## Bordas e erros

- `on` duplo = no-op (só registra). `off` idempotente.
- Guardião morre inesperado → o `status`/`on` seguinte reconcilia via flag + registro.
- KDE Connect offline (celular fora de alcance) → fallback `notify-send` local + log no journald; não trava.
- Sessão fecha sem `off` → entrada morta reapada no próximo `on`/`status`; guardião não fica zumbi.
- Latch/debounce evita salvar em loop na faixa de 5%.

## Fora de escopo

- **Hibernate / swap / resume** (exige swapfile ≥ RAM; contradiz "deixar rodando"). Descartado.
- **Shutdown** a 5% — descartado (máquina deve seguir usável).
- **Mexer em NetworkManager** — o tethering já está ajustado pelo usuário; só evitamos suspend (que é o que derruba a conexão).

## Nota cross-platform (documentar, não implementar)

Fase 1 é Linux/systemd/KDE. Gêmeos a documentar no `SKILL.md`: macOS (`caffeinate` para inhibitor; `pmset` para bateria); Windows (`powercfg` / presentation settings). Não implementados agora.

## Entregáveis

- `skills/manter_ligado/SKILL.md` — a skill (controlador: on/off/status/limpar).
- Script do guardião (inhibitor + loop de bateria + salvamento).
- Script/lógica do registro de sessões (reap + refcount).
- Nota cross-platform no `SKILL.md`.

## Diagramas ASCII (referência canônica do algoritmo)

Ver a conversa de brainstorm: Diagrama 1 (ciclo de vida multi-sessão), Diagrama 2 (loop de bateria), Diagrama 3 (salvamento a 5%) — todos válidos com a revisão "não desliga / não hiberna".
