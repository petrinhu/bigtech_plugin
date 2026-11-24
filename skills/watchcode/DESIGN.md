# DESIGN - skill `watchcode`

> Spec validado em brainstorm. Data: 2026-07-19. Porte: solo/pessoal (sem constelação bigtech). Escopo: fase única, user-space (systemd --user), Linux com systemd/journald.

## Propósito

Enquanto agentes/main estão codando (compilando e RODANDO binários de produto), crashes reais (OOM, SIGSEGV, SIGABRT, coredump de produto) às vezes passam despercebidos. O `watchcode` é um vigia: um daemon leve varre o journal/coredumps a cada 120s procurando crashes REAIS causados pelo trabalho de codificação, e a sessão Claude reage a cada achado. Crash **desta sessão** dispara um ciclo de diagnóstico (Caetano/CTO, modelo herdado da sessao); crash de **outra sessão** ou do **sistema/apps do usuário** vira só relatório.

## Comandos

- `/bigtech:watchcode --on` - arma (scoped ao cwd), registra a sessão, sobe o daemon (ou adota um órfão).
- `/bigtech:watchcode --off` - encerra na hora: desregistra a sessão, scan final, resumo, derruba o daemon se for a última.
- `/bigtech:watchcode --status` - mostra se está armado, por quantas sessões, e achados acumulados.

## Arquitetura - daemon "burro" + leitor "inteligente" (Claude)

O trabalho mecânico (detecção) é do daemon; o julgamento (classificar + rotear) é da tick do Claude. Isso torna a **adoção de órfão** trivial: quem classifica é o leitor, contra o escopo da sessão atual.

| Peça | Responsabilidade |
|---|---|
| skill `watchcode` (`on`/`off`/`status`) | registra/desregistra a sessão; sobe/adota/derruba o daemon; arma a tick |
| daemon `systemd --user` transitório (SINGLETON) | loop 120s: detecta crash real, filtra baseline, **anexa achado cru** (`time,sig,exe,pid`) a `findings.jsonl`; persiste `last_scan` |
| tick Claude (~120s, ScheduleWakeup) | lê achados novos (cursor por sessão); **classifica** por caminho do EXE contra o `scope`; roteia |
| `baseline.txt` | padrões de EXE / regex a ignorar (usuário estende) |
| registro `sessions/<sid>` | refcount: daemon vive enquanto >= 1 sessão registrada |
| state `$XDG_RUNTIME_DIR/watchcode/` (tmpfs) | `scope`, `last_scan`, `findings.jsonl`, `cursor/<sid>`, `daemon.armed`, `sessions/` |

## Detecção (só erro REAL conta)

Duas fontes, a cada ciclo, na janela desde o último scan (default 130s de sobreposição sobre a cadência de 120s; `coredumpctl` retém dumps, então scan atrasado não perde nada):

- **coredumpctl** (`coredumpctl list --since <last> --no-legend`): SIGSEGV / SIGABRT / coredump de produto. Saída estruturada: `TIME PID SIG EXE`.
- **journal OOM** (`journalctl --since <last> | grep 'Out of memory: Killed process'`): OOM não gera coredump (SIGKILL), por isso ramo separado.

**Baseline ignorado** (`baseline.txt`, defaults):
- `/var/tmp/*_probes/*` (sondas de sanitizer que abortam de propósito)
- `*/audit/scratch/*` (binários de scratch de auditoria)
- `*death*test*` (death-tests que abortam de propósito)
- ramo journal: linhas `NVRM`, `drkonqi` e de um serviço local que responde 503

Regra: só **OOM / coredump de produto inesperado / SIGSEGV fora do baseline** vira achado.

## Classificação na leitura (3 classes por caminho do EXE)

A tick do Claude lê cada achado novo e classifica contra o `scope` (project root = cwd de quem armou/lê):

1. **`this`** - EXE sob o project root da sessão atual -> **único caso que dispara o ciclo de conserto**: delega **Caetano/CTO (modelo herdado da sessao)** que diagnostica (coredumpctl + `gdb`/backtrace, código, logs), **propõe o fix SEM aplicar**, e recomenda *simples (1 especialista) vs Cosimo montar time bigtech*.
2. **`other-session`** - EXE sob outro `.../Projects/<x>/` -> **só relatório, NÃO propor, NÃO debugar** (o trabalho é da outra sessão):
   ```
   De: WatchCode
   Para: sessão de <caminho do projeto x>

   [Relatório técnico por tipo de erro]
   ```
3. **`system`** - EXE fora de qualquer `Projects/` (apps/sistema do usuário) -> **só relatório**, pra debugar noutra sessão:
   ```
   De: WatchCode
   Para: Usuário

   [Relatório]
   ```

Só a classe **(1)** diagnostica/propõe. **(2)** e **(3)** são relato puro.

## Ciclo de vida

- **`on`**: reap de sids mortos; registra a sessão atual (com seu `scope`=cwd e um `cursor` iniciando em 0 para consumir backlog de um órfão). Se o daemon não está no ar -> sobe. Se está no ar com registro vazio (**órfão**) -> **adota** (só registra; deixa ele coletando). Se está no ar já registrado -> no-op.
- **Enquanto armado**: a tick (~120s) lê `findings.jsonl` do cursor da sessão, classifica e roteia (delega Caetano em `this`; relatório em `other`/`system`). Avança o cursor.
- **Fim do loop (Opção 1 aprovada)**: **automático** quando a thread principal fica ociosa (sem agentes de codificação pendentes por um tick) **OU** `/bigtech:watchcode --off` manual. No fim: desregistra a sessão; **scan final**; emite o **resumo** (achados classificados desta sessão + o que um órfão adotado já havia coletado; inclui erros de sistema/apps do usuário na janela ativa; ou "nada anormal"); se o registro ficou vazio -> **derruba o daemon** (sem órfão).

## Higiene

- state em `$XDG_RUNTIME_DIR/watchcode/` (tmpfs) -> limpo no boot.
- reap de sids mortos em `on`/`status` -> daemon não vira zumbi.
- daemon transitório (`systemd-run --user`) -> sem arquivo permanente; log via journald (rotação automática).
- `findings.jsonl` vive no state tmpfs -> não acumula entre boots; `off` do último derruba tudo.

## Bordas e erros

- Sem crash na janela -> `findings.jsonl` vazio -> resumo final "nada anormal".
- `coredumpctl`/journal ilegível -> daemon loga e segue (não trava); a tick reporta a degradação.
- `on` duplo na mesma sessão = no-op. `off` idempotente.
- Delegação do Caetano falha/retorna vazio -> a tick reporta o achado cru ao usuário (não engole).
- Múltiplos drivers (2 sessões armadas) -> cada uma tem cursor próprio e classifica contra seu escopo; o daemon (singleton) só alimenta dados crus.

## Fora de escopo

- Aplicar/commitar fixes automaticamente (a classe `this` só diagnostica e propõe; `other`/`system` só relatam).
- Monitorar métricas contínuas (CPU/mem) - só crashes reais.
- Cross-platform: fase única Linux/systemd. Nota no SKILL.md (macOS: `log show` + Crash Reporter; Windows: Event Log / WER) sem implementar.

## Costuras de teste (env overrides)

`WATCHCODE_STATE_DIR`, `WATCHCODE_COREDUMP_CMD` (stub de coredumpctl com fixture), `WATCHCODE_JOURNAL_CMD` (stub de journalctl), `WATCHCODE_BASELINE_FILE`, `WATCHCODE_SCOPE`, `WATCHCODE_PROJECTS_ROOT`, `WATCHCODE_ONESHOT`, `WATCHCODE_INTERVAL`. Permite testar detecção/baseline/classificação (this/other/system) sem crash real.

## Entregáveis

- `skills/watchcode/SKILL.md` - controlador (on/off/status) + como a tick lê/roteia + nota cross-platform.
- `bin/lib.sh` - funções puras: state, registro/reap, detecção (parse coredumpctl + OOM), filtro baseline, classificação, formatação de relatório.
- `bin/watchcode_daemon.sh` - loop do daemon (detecção -> findings.jsonl).
- `bin/watchcode.sh` - controlador (on/off/status; sobe/adota/derruba daemon via systemd-run).
- `tests/test_watchcode.sh` - harness shell com fixtures injetáveis.
