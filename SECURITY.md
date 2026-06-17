# Segurança

Política de segurança e modelo de confiança do plugin **bigtech**.

Este documento existe para que você decida, com informação completa, se quer
instalar e operar o plugin. O resumo em uma frase: **os hooks deste plugin
executam código na sua máquina, e um deles pode rodar o comando de teste
definido pelo projeto que você abrir**. Abaixo, o detalhe de cada ponto.

## Modelo de confiança em uma frase

Instalar o `bigtech` equivale, em nível de confiança, a rodar `make test` ou
`npm test` num repositório: você está concedendo a um arquivo versionado o
direito de executar um comando na sua máquina. A diferença é que aqui isso
acontece de forma automática durante a sessão, e não quando você digita o
comando. Trate repositórios de terceiros com o mesmo cuidado que já teria
antes de rodar a suíte de testes deles.

## Os hooks rodam na sua máquina

Quando o plugin está instalado, o Claude Code registra seis hooks (ver
`hooks/hooks.json`). Todos executam localmente, com o seu usuário, sob os
seguintes eventos:

| Hook | Evento | O que faz |
|---|---|---|
| `bigtech_session_init.py` | SessionStart | Injeta o caminho dos manuais no contexto; avisa sobre conflito e dependências ausentes. |
| `bigtech_porte_reminder.py` | SessionStart | Reavalia o porte do projeto; só age em projeto de código ainda não classificado. |
| `tab_pendencias_reminder.py` | SessionStart, UserPromptSubmit | Lembra de gerar o `TODO.md` quando há `.bigtech-porte` sem a tabela e, com a tabela presente, mede a defasagem dela rodando `git` em modo somente-leitura; só lembra, nunca bloqueia. |
| `bigtech_reinforce.py` | UserPromptSubmit | Reforça o modo de operação e roteia pedidos em linguagem natural. |
| `tdd_guard.py` | PreToolUse (`Write`/`Edit`/`MultiEdit`) | Gate opt-in de TDD; pode bloquear a escrita de código de produção. |
| `tdd_runner.py` | PostToolUse (`Write`/`Edit`/`MultiEdit`) | Roda a suíte de testes do projeto após a edição e grava o resultado. |

Nenhum desses hooks faz acesso de rede, telemetria ou envio de dados para
fora da máquina. O estado do TDD é gravado apenas em
`$HOME/.claude/state/tdd-guard/<hash>/last-run.json`, sob o seu `HOME`,
resolvido em tempo de execução. Nenhum caminho é fixado no código.

## O `tab_pendencias_reminder` lê o histórico do `git`

Para medir a defasagem da tabela de pendências, o `tab_pendencias_reminder.py`
executa o `git` no projeto que você abriu **em modo somente-leitura**: comandos
de consulta com argumentos fixos (como `git rev-list` e `git log`), sem
interpolar entrada do projeto e **sem passar por um shell**. Ele só conta
quantos commits e quantos dias se passaram desde o último toque no `TODO.md`;
não escreve no repositório, não acessa a rede e não altera nenhum arquivo.
É benigno e **fail-open**: qualquer erro (sem `git`, fora de um repositório,
saída inesperada) faz o hook simplesmente não avisar, nunca interromper o
turno.

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

Todos os hooks são **silent-fail**: qualquer erro interno é capturado e o
turno segue normalmente. Eles nunca interrompem o seu trabalho por falha
própria. A única exceção intencional é o `tdd_guard`, que é o **gate de
TDD** e pode recusar a escrita de código de produção quando não há um teste
vermelho registrado. Esse gate também é opt-in (só atua com
`.claude/tdd-guard.json`) e tem válvulas de escape descritas abaixo.

Em particular:

- `tdd_runner.py` retorna sempre código 0; mesmo que a suíte falhe, demore
  ou o comando não exista, o fluxo do Claude Code não é interrompido.
- Se o runner não conseguir executar (comando ausente, timeout, binário não
  executável), o guard faz **fail-open**: avisa, mas permite a edição.

## Como desativar

Você tem três níveis de controle, do mais amplo ao mais específico:

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

Para desinstalar o plugin por completo, use o gerenciador de plugins do
Claude Code (`/plugin`), o que remove o registro de todos os hooks.

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
público (`petrinhu/bigtech_plugin` no Codeberg). Para falhas sensíveis,
descreva o impacto e o passo a passo de reprodução sem expor dados de
terceiros. Correções de segurança são tratadas com prioridade.
