---
title: Política de ferramenta ausente
description: O que um agent faz quando uma ferramenta externa FOSS de que precisa não está instalada. Doutrina híbrida por risco, válida para qualquer tarefa de qualquer agent, agnóstica de SO.
---

# Política de ferramenta ausente (híbrido por risco)

> Regra para todos os agents: **a falta de uma ferramenta NUNCA é motivo para não executar a
> tarefa.** Quando uma ferramenta externa FOSS de que você precisa não está instalada, você a
> detecta, a obtém pelo caminho de menor risco e segue. A única não-execução possível é a recusa
> explícita do usuário, e mesmo essa pausa só aquele passo.

Este documento é a **fonte única do protocolo** de ferramenta ausente. Vale para **qualquer
tarefa de qualquer agent** da constelação (não só testes e auditoria): build, lint, conversão de
documento, diagrama, scan, profiling, benchmark, o que for. O catálogo de **qual é o comando** de
cada ferramenta vive no [TOOLING](../TOOLING.md); este arquivo diz **quando você instala sozinho e
quando você pergunta antes**.

Este arquivo é autolistado no `SessionStart` pelo glob `principles/*.md`: a doutrina entra em
contexto no início de toda sessão.

---

## Doutrina: híbrido por risco

A decisão de instalar gira em um único eixo: **o quanto a instalação é invasiva na máquina do
usuário.** Há dois caminhos.

| Caminho | Quando se aplica | Ação |
|---|---|---|
| **Instala sozinho** | A ferramenta entra em **userland**, sem privilégio: `pip`/`uv`, `cargo`, `npm`/`pnpm`, ou um binário baixado para dentro do `$HOME` | Instala **sem perguntar**, informa o que instalou, segue a tarefa |
| **Oferece antes** | A instalação exige **sudo**, o **gerenciador do sistema**, um **pacote global**, ou **download de fora de um gerenciador** | **OFERECE via AskUserQuestion** com o comando certo para o SO/gerenciador; só instala com o "sim" |

A lógica é simples: o que cabe na conta do próprio usuário, sem mexer no sistema, você resolve e
segue (o atrito de perguntar não compensa). O que altera o sistema (pacote global, daemon, sudo)
é decisão do dono da máquina, e a palavra final é dele.

---

## Protocolo (4 passos)

### 1. Detecta, conforme o SO

Antes de usar uma ferramenta, confirme se ela existe:

- **Unix, macOS, WSL, Git Bash:** `command -v <ferramenta>`
- **Windows (PowerShell):** `Get-Command <ferramenta>` ou `where <ferramenta>`
- **Windows (cmd):** `where <ferramenta>`

Se existe, use. Se não existe, vá ao passo 2.

### 2. Híbrido por risco: instala sozinho ou oferece

Classifique o **comando de instalação** da ferramenta (consulte o [TOOLING](../TOOLING.md)):

**Caso A - instala em userland, sem privilégio: INSTALA SOZINHO.**

Reconhece-se pelo gerenciador, não pelo nome da ferramenta:

- `pip install ...` / `uv tool install ...` / `uv pip install ...` / `pipx install ...`
- `cargo install ...`
- `npm i -g ...` / `pnpm add -g ...` (quando o prefixo global do npm é o do usuário)
- `go install ...`
- download de um único binário para um diretório do `$HOME` que esteja no `PATH`

Instala direto, **sem perguntar**. Depois informe ao usuário, em uma linha, **o que** instalou e
**como** (ex.: "instalei `ruff` via `uv tool install ruff`"). Então rode o item. Transparente,
nunca silencioso.

**Caso B - exige sistema/privilégio: OFERECE via AskUserQuestion.**

Reconhece-se por:

- `sudo ...` (qualquer)
- gerenciador do sistema: `apt`, `dnf`, `pacman`, `zypper`, `brew`, `winget`, `choco`, `scoop`
- pacote global que mexe em diretório do sistema, daemon de serviço (ex.: instalar e habilitar
  Docker), ou script de instalação `curl ... | sudo ...`
- download de fora de qualquer gerenciador que precise ir para um diretório do sistema

Não instala calado. **OFERECE via AskUserQuestion**, mostrando o comando **adequado ao SO e ao
gerenciador disponível** do usuário (ver tabela de gerenciadores abaixo) e preferindo, quando a
ferramenta suportar, um gerenciador cross-platform (que cairia no Caso A). Só executa a instalação
com o "sim". A opção recomendada vem primeiro.

### 3. Cláusula negativa (inegociável)

- **NUNCA** responda "não consigo porque a ferramenta X não está instalada".
- **NUNCA** recuse a tarefa por falta de ferramenta.
- A **única** não-execução legítima é a **recusa explícita do usuário** no passo 2 (Caso B).
- E mesmo a recusa **pausa apenas aquele passo**: registre-o como pendente, com nota visível do
  que faltou e do comando de instalação, e **siga com o resto da tarefa**. O trabalho não para
  inteiro por causa de um passo bloqueado.

### 4. Preferir FOSS e cross-platform, sempre transparente

- Prefira ferramentas **FOSS**.
- Quando a ferramenta oferecer um gerenciador **cross-platform** (`pip`/`uv`, `cargo`,
  `npm`/`pnpm`), prefira-o: ele funciona igual em Windows, macOS e Linux **e** cai no Caso A
  (instala sozinho), reduzindo atrito.
- **Nunca silencioso**: tanto a instalação automática (Caso A) quanto a oferta (Caso B) são
  comunicadas ao usuário.

---

## Detecção e gerenciadores por SO (referência)

**Detectar se a ferramenta existe:**

| SO / shell | Comando |
|---|---|
| Unix, macOS, WSL, Git Bash | `command -v <ferramenta>` |
| Windows (PowerShell) | `Get-Command <ferramenta>` ou `where <ferramenta>` |
| Windows (cmd) | `where <ferramenta>` |

**Gerenciador a oferecer no Caso B, por plataforma:**

| Plataforma | Gerenciador(es) |
|---|---|
| Debian, Ubuntu | `apt` |
| Fedora, RHEL | `dnf` |
| Arch | `pacman` |
| openSUSE | `zypper` |
| macOS | `brew` |
| Windows | `winget` (nativo), `scoop`, `choco` |
| Qualquer (cross-platform, preferir) | `pip`/`uv`, `cargo`, `npm`/`pnpm` |

No Windows, rodar o Claude Code via WSL torna válidos todos os comandos Unix (incluindo
`command -v` e os gerenciadores `apt`/`dnf`), dispensando a tradução para PowerShell.

---

## Exemplos

**Instala sozinho (Caso A).** A tarefa pede lint de prosa com `vale`, que não está instalado.
`vale` tem instalação via gerenciador cross-platform ou binário no `$HOME`. O agent instala, avisa
("instalei `vale`"), e roda o lint. Não pergunta.

**Oferece antes (Caso B).** A tarefa pede captura de pacote com `tcpdump`, ausente. A instalação
exige `sudo dnf install tcpdump` (ou o equivalente do SO). O agent NÃO instala calado: pergunta via
AskUserQuestion, mostrando o comando do gerenciador do usuário, e só instala com o "sim".

**Recusa explícita (não trava a tarefa).** No exemplo acima, o usuário responde "não". O agent
registra o passo de captura como pendente, com a nota do que faltou e o comando, e **continua** com
os demais passos da tarefa que não dependem do `tcpdump`.

---

## Onde esta política se aplica

Esta é a doutrina geral. Os manuais que descrevem fluxos com ferramentas **referenciam** este
arquivo em vez de repetir o protocolo (fonte única):

- [TOOLING](../TOOLING.md): catálogo do **comando** de cada ferramenta (esta política diz **quando**
  instalar sozinho versus oferecer).
- [TESTES](../manuals/TESTES.md): itens de teste (`TST-*` / `T*`) que exigem ferramenta.
- [AUDITORIAS](../manuals/AUDITORIAS.md): itens de auditoria (`AUD-*` / `A*`) que exigem ferramenta.
- [limites de hardware](hardware-resource-limits.md): respeite os caps de CPU/RAM/GPU ao rodar a
  ferramenta depois de instalada.

---

## Checklist rápido

- [ ] Detectou a ferramenta com o comando certo para o SO (`command -v` / `Get-Command` / `where`).
- [ ] Classificou o comando de instalação: userland (Caso A) ou sistema/privilégio (Caso B).
- [ ] Caso A: instalou sozinho e **avisou** o que instalou.
- [ ] Caso B: **ofereceu** via AskUserQuestion com o comando do gerenciador do usuário, só instalou com o "sim".
- [ ] Preferiu FOSS e gerenciador cross-platform quando havia.
- [ ] Nunca disse "não consigo por falta de ferramenta"; nunca recusou a tarefa por isso.
- [ ] Recusa do usuário pausou só o passo bloqueado (pendente, com nota); o resto seguiu.
