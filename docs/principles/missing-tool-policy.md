---
title: Política de ferramenta ausente
description: O que um agent faz quando uma ferramenta externa de que precisa não está instalada. Ferramenta de linha de comando de uso geral é instalada com aviso. Biblioteca, dependência de projeto, modelo, extensão, navegador e serviço só são instalados com permissão do usuário, perguntada antes. Agnóstica de SO.
---

# Política de ferramenta ausente

> As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.

> Orientação para os agents: quando uma ferramenta externa de que você precisa não está instalada, detecte-a, classifique o que falta e nunca falhe calado. Ferramenta de linha de comando de uso geral pode ser instalada com aviso. Os demais tipos de item só são instalados com a permissão do usuário, perguntada antes. Se não for possível instalar, diga o que falta e o comando de instalação, pause apenas o passo que depende dela e siga o resto da tarefa.

Este documento é a fonte única do protocolo de ferramenta ausente. Vale para qualquer tarefa de qualquer agent: build, lint, conversão de documento, diagrama, scan, profiling, benchmark, o que for. O catálogo de qual é o comando de cada ferramenta vive no [TOOLING](../house/TOOLING.md). Este arquivo diz o que pode ser instalado com aviso e o que exige permissão antes.

Este arquivo é autolistado no `SessionStart` pelo glob `principles/*.md`: a doutrina entra em contexto no início de toda sessão.

---

## Doutrina: o que falta decide quem autoriza

A pergunta que decide é **que tipo de item está faltando**, não qual gerenciador o instala.

| Tipo do item faltante | Exemplos | Ação |
|---|---|---|
| **Ferramenta de linha de comando de uso geral** | `vale`, `jq`, `shellcheck`, `pandoc`, `ripgrep`, `tcpdump` | **Pode instalar, com aviso.** Informa o que instalou e como, depois segue a tarefa. |
| **Biblioteca ou dependência de projeto** | pacote de `pip`, `npm`, `cargo` ou `go` que o código do projeto importa | **Pergunta antes** via AskUserQuestion. Só instala com o "sim". |
| **Modelo** | modelo de linguagem, de visão ou de áudio baixado para uso local | **Pergunta antes.** Só baixa com o "sim". |
| **Extensão** | extensão de editor, plugin de IDE, extensão de navegador | **Pergunta antes.** Só instala com o "sim". |
| **Navegador** | Chromium, Firefox, Brave, ou o binário de navegador baixado para testes | **Pergunta antes.** Só instala com o "sim". |
| **Serviço ou daemon** | banco de dados ou Docker rodando como serviço, com habilitação no boot | **Pergunta antes.** Habilitar serviço é decisão do dono da máquina. |

Na dúvida sobre o tipo do item, pergunte antes de instalar.

---

## Protocolo (4 passos)

### 1. Detecta, conforme o SO

Antes de usar uma ferramenta, confirme se ela existe:

- **Unix, macOS, WSL, Git Bash:** `command -v <ferramenta>`
- **Windows (PowerShell):** `Get-Command <ferramenta>` ou `where <ferramenta>`
- **Windows (cmd):** `where <ferramenta>`

Se existe, use. Se não existe, vá ao passo 2.

### 2. Classifica o que falta

Consulte o [TOOLING](../house/TOOLING.md) para saber o comando de instalação e use a tabela da doutrina para decidir o caminho:

- Ferramenta de linha de comando de uso geral: vá ao passo 3.
- Biblioteca, dependência de projeto, modelo, extensão, navegador ou serviço: vá ao passo 4.

### 3. Ferramenta de uso geral: instala com aviso

- Escolha o gerenciador de menor atrito que funcione no SO detectado. Quando a ferramenta tiver um gerenciador cross-platform (`pip`/`uv`, `cargo`, `npm`/`pnpm`, `go`), prefira-o.
- Instale e informe ao usuário, em uma linha, **o que** instalou e **como** (ex.: "instalei `vale` via `pip install vale`").
- Confirme que a ferramenta responde (`command -v`) e siga a tarefa.
- Nunca silencioso: a instalação é sempre comunicada.

### 4. Demais tipos: pergunta antes

- Pergunte via AskUserQuestion, mostrando o comando exato e o gerenciador disponível no SO do usuário. A opção recomendada vem primeiro.
- Execute a instalação só com o "sim" do usuário.
- Sem o "sim", não instale. Registre o passo como pendente, com a nota do que faltou e do comando, e siga com o resto da tarefa.

---

## Nunca falhar calado

- Se a instalação não puder ser feita (sem permissão, sem gerenciador disponível, erro de instalação), diga na resposta o que falta e o comando de instalação.
- A falta de ferramenta não encerra a tarefa inteira. Pause apenas o passo que depende dela; o resto segue.
- Não diga "não consigo" sem listar o que falta e o comando.

---

## Preferir FOSS e gerenciador cross-platform

- Prefira ferramentas FOSS.
- Quando houver gerenciador cross-platform (`pip`/`uv`, `cargo`, `npm`/`pnpm`, `go`), prefira-o: funciona igual em Windows, macOS e Linux.

---

## Detecção e gerenciadores por SO (referência)

**Detectar se a ferramenta existe:**

| SO / shell | Comando |
|---|---|
| Unix, macOS, WSL, Git Bash | `command -v <ferramenta>` |
| Windows (PowerShell) | `Get-Command <ferramenta>` ou `where <ferramenta>` |
| Windows (cmd) | `where <ferramenta>` |

**Gerenciador a usar ou oferecer, por plataforma:**

| Plataforma | Gerenciador(es) |
|---|---|
| Debian, Ubuntu | `apt` |
| Fedora, RHEL | `dnf` |
| Arch | `pacman` |
| openSUSE | `zypper` |
| macOS | `brew` |
| Windows | `winget` (nativo), `scoop`, `choco` |
| Qualquer (cross-platform, preferir) | `pip`/`uv`, `cargo`, `npm`/`pnpm`, `go` |

No Windows, rodar o Claude Code via WSL torna válidos todos os comandos Unix (incluindo `command -v` e os gerenciadores `apt`/`dnf`), dispensando a tradução para PowerShell.

---

## Exemplos

**Ferramenta de uso geral, com aviso.** A tarefa pede lint de prosa com `vale`, que não está instalado. O agent instala `vale` pelo gerenciador cross-platform, avisa ("instalei `vale` via `pip install vale`") e roda o lint.

**Modelo, com pergunta.** A tarefa pede transcrição local com um modelo de fala, que não está baixado. O agent não baixa o modelo. Pergunta via AskUserQuestion, mostrando o comando e o tamanho do download, e só baixa com o "sim".

**Navegador, sem permissão.** A tarefa pede teste de interface com Chromium, que não está instalado. O agent pergunta antes. O usuário responde "não". O agent registra o passo de teste de interface como pendente, com a nota do que faltou e do comando, e continua com os demais passos da tarefa que não dependem do navegador.

---

## Onde esta política se aplica

Esta é a doutrina geral. Os manuais que descrevem fluxos com ferramentas **referenciam** este arquivo em vez de repetir o protocolo (fonte única):

- [TOOLING](../house/TOOLING.md): catálogo do comando de cada ferramenta. Esta política diz quando instalar com aviso e quando pedir permissão antes.
- [TESTES](../house/TESTES.md): itens de teste (`TST-*` / `T*`) que exigem ferramenta.
- [AUDITORIAS](../house/AUDITORIAS.md): itens de auditoria (`AUD-*` / `A*`) que exigem ferramenta.
- [limites de hardware](hardware-resource-limits.md): respeite os caps de CPU/RAM/GPU ao rodar a ferramenta depois de instalada.

---

## Checklist rápido

- [ ] Detectou a ferramenta com o comando certo para o SO (`command -v` / `Get-Command` / `where`).
- [ ] Classificou o que falta: ferramenta de uso geral, ou biblioteca, dependência, modelo, extensão, navegador ou serviço. Na dúvida, perguntou.
- [ ] Ferramenta de uso geral: instalou e avisou o que instalou e como.
- [ ] Demais tipos: perguntou via AskUserQuestion e só instalou com o "sim".
- [ ] Nunca instalou calado.
- [ ] Sem permissão ou sem instalação possível: disse o que falta e o comando, pausou só o passo que depende da ferramenta e seguiu o resto.
- [ ] Preferiu FOSS e gerenciador cross-platform quando havia.
