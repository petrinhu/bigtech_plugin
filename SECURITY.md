# Segurança

Política de segurança e modelo de confiança do plugin **bigtech** (versão 2.0.0).

Este documento existe para que você decida, com informação completa, se quer
instalar e operar o plugin. O resumo em uma frase: **os hooks deste plugin
executam código na sua máquina, um deles pode rodar o comando de teste
definido pelo projeto que você abrir, e alguns skills são opt-in e sobem
processos ou serviços locais.** Abaixo, o detalhe de cada ponto.

## Modelo de confiança em uma frase

Instalar o `bigtech` equivale, em nível de confiança, a rodar `make test` ou
`npm test` num repositório: você está concedendo a um arquivo versionado o
direito de executar um comando na sua máquina. A diferença é que aqui isso
acontece de forma automática durante a sessão, e não quando você digita o
comando. Trate repositórios de terceiros com o mesmo cuidado que já teria
antes de rodar a suíte de testes deles.

## Superfície do plugin

O arquivo `hooks/hooks.json` registra **9 entradas** de hook, que usam **7
scripts** distintos. Os hooks são executados localmente, com o seu usuário.

| Script | Evento | O que faz |
|---|---|---|
| `hooks/bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto; avisa sobre conflito e sobre dependências recomendadas ausentes, lendo as configurações do Claude Code (`CLAUDE_CONFIG_DIR` ou `$HOME/.claude`). |
| `hooks/bigtech_porte_reminder.py` | SessionStart | Lembra de classificar o porte do projeto; só age em projeto de código ainda não classificado. |
| `hooks/tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Carimba o início da sessão e lembra de revisar o `TODO.md` quando a sessão passa do tempo configurado. Ver "Estado gravado pelos hooks". |
| `skills/tab_pendencias/tools/hooks/tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Adaptador do motor de sinais de frescor da tabela de pendências: avisa quando o `TODO.md` falta ou está defasado. Lê o histórico do `git` em modo somente-leitura. |
| `hooks/bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo de operação e roteia pedidos em linguagem natural. |
| `hooks/tdd_guard.py` | PreToolUse (`Write\|Edit`) | Gate opt-in de TDD; pode bloquear a escrita de código de produção. |
| `hooks/tdd_runner.py` | PostToolUse (`Write\|Edit`) | Roda a suíte de testes do projeto após a edição e grava o resultado. |

Os 9 registros se distribuem assim: quatro em SessionStart, três em
UserPromptSubmit, um em PreToolUse e um em PostToolUse.

### Os hooks não usam a rede

Nenhum dos 7 scripts abre conexão de rede, faz telemetria ou envia dados para
fora da máquina. A única exceção é o próprio comando de teste do projeto,
executado pelo `tdd_runner`, que pode fazer o que o projeto já faz quando você
roda a suíte à mão.

### Estado gravado pelos hooks

- **TDD:** `$HOME/.claude/state/tdd-guard/<hash>/last-run.json`, resolvido em
  tempo de execução. Nenhum caminho é fixado no código.
- **`tab_pendencias` (cópia da skill):** diretório `$XDG_RUNTIME_DIR/tab_pendencias_hook_state`
  ou, na falta dele, `$HOME/.cache/tab_pendencias_hook_state`, criado com
  permissão `0700`. Guarda um arquivo por sessão e é podado por idade.
- **Carimbo de sessão do hook da raiz (`hooks/tab_pendencias_reminder.py`):**
  diretório `$XDG_RUNTIME_DIR/bigtech_tab_sessao` ou, na falta dele,
  `$HOME/.cache/bigtech_tab_sessao`, criado com permissão `0700`. Nunca grava
  no diretório temporário compartilhado (`/tmp`). Recusa symlink no diretório
  e diretório de outro dono: nesse caso nada é gravado e a sessão segue
  (fail-open). Os arquivos são podados por idade.

## O `git` dentro do hook de pendências

Para medir a defasagem da tabela de pendências, o hook da skill executa o `git`
no projeto que você abriu **em modo somente-leitura**: apenas `git log` e
`git rev-list`, com argumentos fixos, sem interpolar entrada do projeto e
**sem passar por um shell** (a chamada usa lista de argumentos, com tempo
limite de 15 segundos). Ele só conta quantos commits e quantos dias se
passaram desde o último toque no `TODO.md`; não escreve no repositório, não
acessa a rede e não altera nenhum arquivo. É benigno e **fail-open**: qualquer
erro (sem `git`, fora de um repositório, saída inesperada) faz o hook
simplesmente não avisar, nunca interromper o turno.

## Paridade de confiança do `tdd_runner`

Este é o ponto que exige atenção explícita.

O hook `tdd_runner.py` executa **como comando de shell** o que estiver
definido em `fast_command` ou `test_command` dentro do arquivo
`.claude/tdd-guard.json` do **projeto que você abriu**. Por isso, trate esse
arquivo como código confiável e não ative o modo TDD em repositório de
terceiro não-confiável sem antes inspecionar esse comando. Em termos
práticos:

- Se você abre um repositório de terceiros que já traz um
  `.claude/tdd-guard.json` e, durante a sessão, edita um arquivo de produção
  ou de teste, o plugin roda **aquele** comando de teste, como o autor do
  repositório o escreveu.
- Isso tem a **mesma natureza de confiança** de rodar `make test`,
  `npm test`, `pytest` ou qualquer alvo de build que o repositório traz: o
  comando é controlado pelo arquivo versionado, não por você no momento da
  execução.

Por isso, abrir repositório de terceiros tem a mesma diligência que você já
deveria aplicar antes de executar a suíte de testes deles: dê uma olhada no
`test_command`/`fast_command` declarado em `.claude/tdd-guard.json` antes de
editar arquivos numa sessão sobre código que você não auditou.

### O recurso é opt-in

O TDD (guard e runner) **só atua em projetos que contêm
`.claude/tdd-guard.json`**. Sem esse arquivo, os dois hooks de TDD ficam
completamente inertes: nada é executado, nada é gravado, nada é bloqueado.
Um repositório que não traz esse arquivo não dispara o `tdd_runner`.

### Ancorado no diretório da sessão

O `tdd_runner` só roda a suíte se o arquivo editado estiver **dentro do
diretório de trabalho da sessão** (o `cwd` enviado no payload do hook).
Editar um arquivo de um projeto vizinho (um diretório irmão que também traga
o seu próprio `.claude/tdd-guard.json`) não dispara o comando de teste da
sua sessão atual. O `tdd_guard` aplica a mesma guarda de contenção: arquivo
fora da raiz do projeto não é avaliado.

## Comportamento dos hooks: silent-fail

Os hooks são **silent-fail**: qualquer erro interno é capturado e o turno
segue normalmente. Eles nunca interrompem o seu trabalho por falha própria. A
única exceção intencional é o `tdd_guard`, que é o **gate de TDD** e pode
recusar a escrita de código de produção quando não há um teste vermelho
registrado. Esse gate também é opt-in (só atua com `.claude/tdd-guard.json`) e
tem válvulas de escape descritas abaixo.

Em particular:

- `tdd_runner.py` retorna sempre código 0; mesmo que a suíte falhe, demore
  ou o comando não exista, o fluxo do Claude Code não é interrompido.
- Se o runner não conseguir executar (comando ausente, timeout, binário não
  executável), o guard faz **fail-open**: avisa, mas permite a edição.

## Skills com processos ou serviços locais

Estes skills não são hooks. Rodam só quando você os invoca, e só no Linux com
systemd. Nenhum deles é instalado como serviço permanente pelo plugin.

### `watchcode`

- Vigia o diário do sistema (`journalctl -f -o json`) e os coredumps, em busca
  de falhas de GPU, falta de espaço, processos mortos pelo kernel e
  `systemd-oomd`.
- O daemon sobe como **unidade transitória** do `systemd --user`
  (`systemd-run --user --collect`). Não há arquivo de unidade instalado nem
  `enable`.
- Estado em `${XDG_RUNTIME_DIR:-$HOME/.cache}/watchcode`; baseline local em
  `$HOME/.config/bigtech/watchcode_baseline.txt`.
- Para parar: a própria skill tem o comando `off`, que encerra a unidade.

### `manter_ligado`

- Mantém a máquina acordada com a tampa fechada, por meio de
  `systemd-inhibit` na unidade transitória, e salva o estado das sessões
  quando a bateria chega a 5%.
- Enquanto está ativo, a suspensão automática fica bloqueada. Use `off` para
  devolver o comportamento normal de energia.
- Estado em `${XDG_RUNTIME_DIR:-$HOME/.cache}/manter_ligado`; snapshots em
  `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/manter_ligado_snapshots`.

## `github-gossips`: saiu do plugin

O `github-gossips` saiu do plugin na versão 2.0.0 e continua disponível fora dele. Nenhum servidor, hook ou túnel dele vem com o plugin, então esta versão não tem essa superfície.

## Dependências do bundle

O bundle `bigtech-completo` declara como dependências:

- `bigtech` (este plugin);
- `playwright@claude-plugins-official`;
- `superpowers@claude-plugins-official`;
- `frontend-design@claude-plugins-official`.

Esses são plugins de terceiros, com hooks, permissões e políticas próprios.
Este plugin não os controla nem audita. O `bigtech_session_init.py` apenas
avisa, no início da sessão, quais dependências recomendadas não estão
habilitadas. O plugin também chama ferramentas do sistema: `python3` (hooks),
`git` (pendências), `systemd` e `journalctl` (`watchcode` e `manter_ligado`).

## Como desativar

Você tem três níveis de controle para o TDD, do mais amplo ao mais específico:

1. **Desligar o TDD no projeto inteiro.** Remova ou renomeie o arquivo
   `.claude/tdd-guard.json`. Sem ele, os hooks de TDD ficam inertes. Como
   alternativa sem apagar o arquivo, defina `"enabled": false` dentro dele.

2. **Desligar o TDD na sessão atual.** Exporte a variável de ambiente:

   ```bash
   export TDD_GUARD=off
   ```

   Guard e runner ficam inertes até o fim da sessão do terminal.

3. **Permitir refatoração com a suíte verde.** Exporte:

   ```bash
   export TDD_PHASE=refactor
   ```

   O guard passa a permitir a edição de produção mesmo quando todos os testes
   estão verdes (`has_red=false`), útil para reorganizar código sem adicionar
   funcionalidade nova.

Para os skills de processo local, use o comando `off` de cada um. 

Para desinstalar o plugin por completo, use o gerenciador de plugins do
Claude Code (`/plugin`), o que remove o registro de todos os hooks. A
desinstalação não apaga o estado local listado acima; remova esses diretórios
à mão se quiser um estado limpo.

## Boas práticas ao abrir código de terceiros

- Antes de editar arquivos numa sessão sobre um repositório que você não
  auditou, inspecione `.claude/tdd-guard.json` (se existir) e confira o
  `test_command`/`fast_command`.
- Se não quiser que qualquer comando de teste rode automaticamente, exporte
  `TDD_GUARD=off` antes de começar a sessão.
- Mantenha o hábito que você já tem com `make test`/`npm test`: rodar a suíte
  de um projeto é executar código que veio com ele.

## Reportar uma vulnerabilidade

Encontrou um problema de segurança no plugin? Abra uma issue no repositório
público (`petrinhu/bigtech_plugin` no GitHub). Para falhas sensíveis,
descreva o impacto e o passo a passo de reprodução sem expor dados de
terceiros. Correções de segurança são tratadas com prioridade.
