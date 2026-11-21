---
name: manter_ligado
description: Mantém a conexão de dados viva com a tampa fechada (laptop na mochila, tethering) e salva o estado de todas as sessões quando a bateria chega a ≤5%, sem desligar a máquina. Use quando o usuário disser "manter ligado", "vou pôr o laptop na mochila", "não deixa suspender com a tampa fechada", "salva a sessão se a bateria acabar", ou invocar /bigtech:manter_ligado {on|off|status|limpar}. Só serve para Linux com systemd --user (systemd-run e systemd-inhibit); em outro SO falha com mensagem clara.
---

# manter_ligado

Skill controladora. Executa o script conforme o argumento (default `status`):

- `on` → `bash ${CLAUDE_SKILL_DIR}/bin/manter_ligado.sh on`
- `off` → `bash ${CLAUDE_SKILL_DIR}/bin/manter_ligado.sh off`
- `status` → `bash ${CLAUDE_SKILL_DIR}/bin/manter_ligado.sh status`
- `limpar` → `bash ${CLAUDE_SKILL_DIR}/bin/manter_ligado.sh limpar`

Ao invocar, rode o comando correspondente com a Bash tool e relate a saída ao usuário.
Não peça confirmação para `on`/`off`/`status`. Para `limpar` (apaga snapshots), confirme antes.

## O que faz

- `on`: registra a sessão atual e sobe um guardião singleton (`systemd --user` transitório) que segura
  um inhibitor `sleep:handle-lid-switch` (tampa fechada não suspende; a tela apaga/acorda pelo KDE) e
  roda um loop de bateria.
- A **20%**: push de aviso ao celular (KDE Connect; fallback notify-send). O texto sugere rodar `/memo` nas
  sessões pelo `/rc`. O `/rc` é o Remote Control do próprio Claude Code; o `/memo` não vem no plugin, é
  opcional e só existe se estiver na configuração do usuário. Sem ele, o aviso vale só como alerta de bateria.
- A **≤5%**: salva o estado de **todas** as sessões registradas (cópia do transcript, retenção=1). **Não
  desliga nem hiberna**: a máquina segue.
- Com `MEMO_HEADLESS=1` (desligado por padrão), a **≤5%** também roda `claude -p` com a skill
  `/memo_persistente` para destilar memórias de cada sessão. Essa skill não vem no plugin: é opcional e só
  funciona se existir na configuração do usuário. O código não falha sem ela (a saída e o erro do
  `claude -p` são descartados), mas cada chamada pode levar até 90 s e atrasa a cópia das sessões
  seguintes. Sem a skill, deixe `MEMO_HEADLESS` desligado.
- `off`: desregistra; guardião cai só no último `off`. `status`: mostra se está armado. `limpar`: faxina.

Detalhes: ver `DESIGN.md` e `PLAN.md` nesta pasta.

## Plataforma

Só Linux com systemd --user (`systemd-run` e `systemd-inhibit`). A guarda `ml_require_linux_systemd` (em `bin/lib.sh`) sai com código 3 e mensagem clara fora disso. Este arquivo é só o controlador; não há caminho de instalação em outro SO.

A bateria e a tomada são lidas em `/sys/class/power_supply/BAT1/capacity` e `/sys/class/power_supply/ACAD/online`, os nomes da máquina onde a skill foi desenvolvida. Em máquina com outros nomes (por exemplo `BAT0` ou `AC`; confira com `ls /sys/class/power_supply/`), a leitura cai no padrão, 100% e fora da tomada, e o aviso de 20% e o salvamento de 5% não disparam.

## Nota cross-platform (não implementado)

Esta versão é Linux/systemd/KDE. Gêmeos a portar no futuro:
- macOS: `caffeinate -disu` no lugar do inhibitor; `pmset -g batt` para a bateria.
- Windows: `powercfg`/`presentationsettings` para o inhibitor; `WMICBattery`/`Get-CimInstance Win32_Battery`.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
