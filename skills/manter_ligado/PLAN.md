# manter_ligado — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Skill global que mantém a conexão viva com a tampa fechada e salva o estado de todas as sessões quando a bateria chega a ≤5%, sem desligar a máquina.

**Architecture:** Controlador fino (shell) invocado pela SKILL.md gerencia um registro de sessões em `$XDG_RUNTIME_DIR` e sobe/derruba um guardião singleton (`systemd --user` transitório) que segura um inhibitor do logind e roda um loop de bateria. A lógica pura (decisão de bateria, registro/reap, retenção de snapshots) fica em `lib.sh` com costuras injetáveis por env, testada por um harness de shell sem dependências.

**Tech Stack:** Bash, systemd (`systemd-run --user`, `systemd-inhibit`), KDE Connect (`kdeconnect-cli`), `notify-send`, `claude -p` (headless). Fedora 44 + KDE Wayland.

## Global Constraints

- **Zero root:** tudo user-space (`systemd --user`, leitura de `/sys`, `/proc` do próprio user). Nunca `sudo`.
- **Não desligar, não hibernar:** a 5% só salva estado; a máquina segue rodando.
- **Inibir só `sleep:handle-lid-switch`** (NÃO `idle`) — a tela apaga/acorda pelo KDE.
- **Idempotência:** `on` duplo = no-op; `off` de uma sessão não afeta as outras; guardião cai só no último `off`.
- **Higiene por padrão:** registro em tmpfs + reap de sid morto; snapshots com **retenção = 1**; log via journald.
- **Costuras de teste (env overrides):** `MANTER_STATE_DIR`, `MANTER_SNAP_DIR`, `MANTER_BAT_CAPACITY_FILE`, `MANTER_AC_ONLINE_FILE`, `MANTER_LIVE_SIDS`, `MANTER_NOTIFY_CMD`, `MANTER_PROJECTS_DIR`, `MANTER_WARN_PCT` (default 20), `MANTER_SAVE_PCT` (default 5), `MANTER_INTERVAL` (default 60), `MEMO_HEADLESS` (default 0).
- **Paths reais:** bateria `/sys/class/power_supply/BAT1/capacity`; AC `/sys/class/power_supply/ACAD/online`; transcripts `$CLAUDE_CONFIG_DIR/projects/*/<sid>.jsonl`; snapshots `$CLAUDE_CONFIG_DIR/manter_ligado_snapshots/`.
- **Identificadores/comentários em pt-br** (padrão do usuário).

**Estrutura de arquivos:**
- `skills/manter_ligado/SKILL.md` — instruções da skill (dispatch on/off/status/limpar) + nota cross-platform.
- `skills/manter_ligado/bin/lib.sh` — funções puras/reutilizáveis (estado, registro, reap, bateria, decisão, push, save). DRY.
- `skills/manter_ligado/bin/manter_ligado.sh` — controlador (parse de comando; start/stop do guardião).
- `skills/manter_ligado/bin/guardiao.sh` — loop do guardião (rodado pelo systemd-run, dentro do systemd-inhibit).
- `skills/manter_ligado/tests/test_manter_ligado.sh` — harness de teste em shell puro.

---

### Task 1: `lib.sh` — estado e registro de sessões (register/unregister/count/reap)

**Files:**
- Create: `skills/manter_ligado/bin/lib.sh`
- Test: `skills/manter_ligado/tests/test_manter_ligado.sh`

**Interfaces:**
- Produces:
  - `ml_state_dir()` → echo do dir de estado (`$MANTER_STATE_DIR` ou `$XDG_RUNTIME_DIR/manter_ligado`)
  - `ml_sessions_dir()` → `$(ml_state_dir)/sessions`
  - `ml_init_state()` → cria o dir de sessões
  - `ml_register_session <sid> <slug> <transcript>` → grava `sessions/<sid>` com 3 linhas
  - `ml_unregister_session <sid>` → remove `sessions/<sid>`
  - `ml_count()` → nº de arquivos em `sessions/`
  - `ml_live_sids()` → sids vivos, um por linha (default via `/proc`; override `MANTER_LIVE_SIDS`)
  - `ml_reap()` → remove entradas cujo sid não está vivo

- [ ] **Step 1: Write the failing test**

Create `skills/manter_ligado/tests/test_manter_ligado.sh`:

```bash
#!/usr/bin/env bash
# Harness de teste em shell puro para a skill manter_ligado.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi; }

# Sandbox isolado por rodada.
SANDBOX="$(mktemp -d)"
export MANTER_STATE_DIR="$SANDBOX/state"
export MANTER_SNAP_DIR="$SANDBOX/snaps"
export MANTER_PROJECTS_DIR="$SANDBOX/projects"
trap 'rm -rf "$SANDBOX"' EXIT

# shellcheck source=/dev/null
. "$DIR/bin/lib.sh"

# --- Task 1: registro ---
ml_init_state
ml_register_session "sid-A" "slug-a" "/tmp/a.jsonl"
ml_register_session "sid-B" "slug-b" "/tmp/b.jsonl"
assert_eq "$(ml_count)" "2" "registra duas sessoes"

ml_unregister_session "sid-A"
assert_eq "$(ml_count)" "1" "desregistra uma sessao"

# reap: só sid-B está vivo -> entrada morta some, viva fica
ml_register_session "sid-morta" "slug-x" "/tmp/x.jsonl"
export MANTER_LIVE_SIDS="sid-B"
ml_reap
assert_eq "$(ml_count)" "1" "reap remove sid morto"
assert_eq "$(ls "$(ml_sessions_dir)")" "sid-B" "reap preserva sid vivo"

echo "---"
[ "$FAILS" -eq 0 ] && echo "TODOS OS TESTES PASSARAM" || { echo "$FAILS FALHA(S)"; exit 1; }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: FAIL — `lib.sh` não existe (erro no `. lib.sh` / função não encontrada).

- [ ] **Step 3: Write minimal implementation**

Create `skills/manter_ligado/bin/lib.sh`:

```bash
#!/usr/bin/env bash
# Funções da skill manter_ligado. Sourced pelo controlador, guardião e testes.

ml_state_dir() { printf '%s\n' "${MANTER_STATE_DIR:-${XDG_RUNTIME_DIR:-/tmp}/manter_ligado}"; }
ml_sessions_dir() { printf '%s\n' "$(ml_state_dir)/sessions"; }
ml_init_state() { mkdir -p "$(ml_sessions_dir)"; }

ml_register_session() {
  # <sid> <slug> <transcript>
  ml_init_state
  { printf '%s\n' "$1"; printf '%s\n' "$2"; printf '%s\n' "$3"; } > "$(ml_sessions_dir)/$1"
}

ml_unregister_session() { rm -f "$(ml_sessions_dir)/$1"; }

ml_count() {
  local d; d="$(ml_sessions_dir)"
  [ -d "$d" ] || { printf '0\n'; return; }
  find "$d" -maxdepth 1 -type f | wc -l | tr -d ' '
}

ml_live_sids() {
  # Override para testes; senão varre /proc por CLAUDE_CODE_SESSION_ID.
  if [ -n "${MANTER_LIVE_SIDS:-}" ]; then
    printf '%s\n' $MANTER_LIVE_SIDS
    return
  fi
  local pid env_sid
  for pid in $(pgrep -u "$(id -u)" -f claude 2>/dev/null); do
    env_sid="$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null \
      | sed -n 's/^CLAUDE_CODE_SESSION_ID=//p' | head -n1)"
    [ -n "$env_sid" ] && printf '%s\n' "$env_sid"
  done
}

ml_reap() {
  local d sid; d="$(ml_sessions_dir)"
  [ -d "$d" ] || return 0
  local live; live="$(ml_live_sids)"
  local f
  for f in "$d"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    printf '%s\n' "$live" | grep -qx "$sid" || rm -f "$f"
  done
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: PASS — "registra duas sessoes", "desregistra uma sessao", "reap remove sid morto", "reap preserva sid vivo".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/bin/lib.sh skills/manter_ligado/tests/test_manter_ligado.sh
git commit -m "feat(manter_ligado): registro de sessoes + reap com costura de teste"
```

---

### Task 2: `lib.sh` — bateria, resolução de transcript e decisão pura

**Files:**
- Modify: `skills/manter_ligado/bin/lib.sh` (append)
- Test: `skills/manter_ligado/tests/test_manter_ligado.sh` (append antes do rodapé)

**Interfaces:**
- Consumes: `ml_sessions_dir`, `ml_init_state` (Task 1)
- Produces:
  - `ml_battery_capacity()` → inteiro 0-100 (lê `$MANTER_BAT_CAPACITY_FILE` ou `/sys/class/power_supply/BAT1/capacity`)
  - `ml_on_ac()` → `0`/`1` (lê `$MANTER_AC_ONLINE_FILE` ou `/sys/class/power_supply/ACAD/online`)
  - `ml_resolve_transcript <sid>` → path do `.jsonl` (glob em `$MANTER_PROJECTS_DIR` ou `$CLAUDE_CONFIG_DIR/projects`)
  - `ml_decide <cap> <on_ac> <warned20> <saved5>` → echo `none` | `warn` | `save`

- [ ] **Step 1: Write the failing test**

Append em `tests/test_manter_ligado.sh` (antes do bloco `echo "---"` final):

```bash
# --- Task 2: bateria / transcript / decisao ---
printf '42\n' > "$SANDBOX/cap"; export MANTER_BAT_CAPACITY_FILE="$SANDBOX/cap"
assert_eq "$(ml_battery_capacity)" "42" "le capacidade da bateria"
printf '1\n' > "$SANDBOX/ac"; export MANTER_AC_ONLINE_FILE="$SANDBOX/ac"
assert_eq "$(ml_on_ac)" "1" "le status de AC"

mkdir -p "$MANTER_PROJECTS_DIR/slug-x"
: > "$MANTER_PROJECTS_DIR/slug-x/sid-T.jsonl"
assert_eq "$(ml_resolve_transcript sid-T)" "$MANTER_PROJECTS_DIR/slug-x/sid-T.jsonl" "resolve transcript por sid"

# Decisao (limiares default 20/5), sem latch acionado:
assert_eq "$(ml_decide 21 0 0 0)" "none" "acima de 20 = none"
assert_eq "$(ml_decide 20 0 0 0)" "warn" "20 = warn"
assert_eq "$(ml_decide 6  0 0 0)" "warn" "6 = warn"
assert_eq "$(ml_decide 5  0 0 0)" "save" "5 = save"
assert_eq "$(ml_decide 4  0 0 0)" "save" "abaixo de 5 = save"
assert_eq "$(ml_decide 5  1 0 0)" "none" "em AC = none"
assert_eq "$(ml_decide 20 0 1 0)" "none" "warn ja dado = none"
assert_eq "$(ml_decide 5  0 0 1)" "none" "save ja feito = none"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: FAIL — `ml_battery_capacity`/`ml_decide` não definidas.

- [ ] **Step 3: Write minimal implementation**

Append em `bin/lib.sh`:

```bash
ml_battery_capacity() {
  local f="${MANTER_BAT_CAPACITY_FILE:-/sys/class/power_supply/BAT1/capacity}"
  [ -r "$f" ] && tr -dc '0-9' < "$f" || printf '100'
}

ml_on_ac() {
  local f="${MANTER_AC_ONLINE_FILE:-/sys/class/power_supply/ACAD/online}"
  [ -r "$f" ] && tr -dc '0-9' < "$f" || printf '0'
}

ml_resolve_transcript() {
  local sid="$1" base m
  base="${MANTER_PROJECTS_DIR:-$HOME/.claude/projects}"
  for m in "$base"/*/"$sid".jsonl; do
    [ -e "$m" ] && { printf '%s\n' "$m"; return 0; }
  done
  return 1
}

ml_decide() {
  # <cap> <on_ac> <warned20> <saved5> -> none|warn|save
  local cap="$1" ac="$2" warned="$3" saved="$4"
  local warn_pct="${MANTER_WARN_PCT:-20}" save_pct="${MANTER_SAVE_PCT:-5}"
  [ "$ac" = "1" ] && { printf 'none\n'; return; }
  if [ "$cap" -le "$save_pct" ]; then
    [ "$saved" = "1" ] && printf 'none\n' || printf 'save\n'
    return
  fi
  if [ "$cap" -le "$warn_pct" ]; then
    [ "$warned" = "1" ] && printf 'none\n' || printf 'warn\n'
    return
  fi
  printf 'none\n'
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: PASS — todas as asserções de bateria/transcript/decisão.

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/bin/lib.sh skills/manter_ligado/tests/test_manter_ligado.sh
git commit -m "feat(manter_ligado): leitura de bateria, resolucao de transcript e decisao pura"
```

---

### Task 3: `lib.sh` — push e salvamento (snapshot + retenção=1)

**Files:**
- Modify: `skills/manter_ligado/bin/lib.sh` (append)
- Test: `skills/manter_ligado/tests/test_manter_ligado.sh` (append)

**Interfaces:**
- Consumes: `ml_sessions_dir`, `ml_resolve_transcript`
- Produces:
  - `ml_snap_dir()` → dir base de snapshots (`$MANTER_SNAP_DIR` ou `$CLAUDE_CONFIG_DIR/manter_ligado_snapshots`)
  - `ml_push <msg>` → dispara `$MANTER_NOTIFY_CMD` (teste) ou kdeconnect/notify-send; nunca falha o chamador
  - `ml_prune_snaps()` → mantém só o dir de snapshot mais recente (retenção=1)
  - `ml_save <stamp>` → cria `snaps/<stamp>/`, copia transcript+metadata de cada sessão, chama `ml_prune_snaps`; opcional memo headless se `MEMO_HEADLESS=1`

- [ ] **Step 1: Write the failing test**

Append em `tests/test_manter_ligado.sh`:

```bash
# --- Task 3: push e save ---
export MANTER_NOTIFY_CMD="printf %s\n"   # stub: só ecoa a msg
assert_eq "$(ml_push 'oi')" "oi" "push usa o comando injetado"

# Prepara duas sessoes com transcript real no sandbox.
# Registra com transcript "" para exercitar o resolve on-the-fly (R-1: nao apontar p/ sid-T vazio).
printf 'conteudo-1\n' > "$MANTER_PROJECTS_DIR/slug-x/sid-S1.jsonl"
ml_register_session "sid-S1" "slug-x" ""
ml_register_session "sid-S2" "slug-x" ""   # transcript vazio -> resolve na hora
printf 'conteudo-2\n' > "$MANTER_PROJECTS_DIR/slug-x/sid-S2.jsonl"
export MANTER_LIVE_SIDS="sid-S1 sid-S2 sid-B"

ml_save "20260713-100000"
assert_eq "$(cat "$(ml_snap_dir)/20260713-100000/sid-S1.jsonl")" "conteudo-1" "save copia transcript S1"

# Retencao=1: um segundo save poda o anterior
ml_save "20260713-100500"
assert_eq "$(ls "$(ml_snap_dir)" | wc -l | tr -d ' ')" "1" "retencao=1 mantem so o mais novo"
assert_eq "$(ls "$(ml_snap_dir)")" "20260713-100500" "mantem o snapshot mais recente"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: FAIL — `ml_push`/`ml_save`/`ml_snap_dir` não definidas.

- [ ] **Step 3: Write minimal implementation**

Append em `bin/lib.sh`:

```bash
ml_snap_dir() { printf '%s\n' "${MANTER_SNAP_DIR:-$HOME/.claude/manter_ligado_snapshots}"; }

ml_push() {
  local msg="$1"
  if [ -n "${MANTER_NOTIFY_CMD:-}" ]; then
    $MANTER_NOTIFY_CMD "$msg" 2>/dev/null || true
    return 0
  fi
  local dev
  dev="$(kdeconnect-cli -a --id-only 2>/dev/null | head -n1)"
  if [ -n "$dev" ]; then
    kdeconnect-cli --ping-msg "$msg" -d "$dev" >/dev/null 2>&1 && return 0
  fi
  notify-send "manter_ligado" "$msg" >/dev/null 2>&1 || true
  return 0
}

ml_prune_snaps() {
  local base; base="$(ml_snap_dir)"
  [ -d "$base" ] || return 0
  local d
  ls -1dt "$base"/*/ 2>/dev/null | tail -n +2 | while IFS= read -r d; do
    rm -rf "$d"
  done
}

ml_save() {
  local stamp="$1" out; out="$(ml_snap_dir)/$stamp"
  mkdir -p "$out"
  ml_push "Bateria ${MANTER_SAVE_PCT:-5}% - salvando estado das sessoes."
  local f sid tr
  for f in "$(ml_sessions_dir)"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    tr="$(sed -n '3p' "$f")"
    [ -z "$tr" ] && tr="$(ml_resolve_transcript "$sid" || true)"
    if [ -n "$tr" ] && [ -r "$tr" ]; then
      cp -f "$tr" "$out/$sid.jsonl"
      { printf 'sid=%s\n' "$sid"; printf 'slug=%s\n' "$(sed -n '2p' "$f")";
        printf 'transcript=%s\n' "$tr"; printf 'stamp=%s\n' "$stamp"; } > "$out/$sid.meta"
    fi
    if [ "${MEMO_HEADLESS:-0}" = "1" ] && command -v claude >/dev/null 2>&1; then
      timeout 90 claude -p "/memo_persistente snapshot de emergencia (bateria baixa) da sessao $sid" \
        >/dev/null 2>&1 || true
    fi
  done
  ml_prune_snaps
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: PASS — "push usa o comando injetado", "save copia transcript S1", "retencao=1 mantem so o mais novo", "mantem o snapshot mais recente".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/bin/lib.sh skills/manter_ligado/tests/test_manter_ligado.sh
git commit -m "feat(manter_ligado): push e salvamento com retencao=1"
```

---

### Task 4: `guardiao.sh` — loop do guardião

**Files:**
- Create: `skills/manter_ligado/bin/guardiao.sh`
- Test: manual/scriptado (bateria falsa via env), sem systemd.

**Interfaces:**
- Consumes: `ml_decide`, `ml_battery_capacity`, `ml_on_ac`, `ml_push`, `ml_save` (lib.sh)
- Produces: escreve/remove `$(ml_state_dir)/guardian.armed`; roda um passo de avaliação por iteração.

- [ ] **Step 1: Write the failing test (loop de 1 passo com bateria falsa)**

Append em `tests/test_manter_ligado.sh`:

```bash
# --- Task 4: guardiao (1 passo) ---
export MANTER_INTERVAL=0            # loop roda 1 passo e sai quando MANTER_ONESHOT=1
export MANTER_ONESHOT=1
printf '4\n' > "$SANDBOX/cap"       # 4% -> deve salvar
printf '0\n' > "$SANDBOX/ac"
rm -rf "$(ml_snap_dir)"
bash "$DIR/bin/guardiao.sh"
assert_eq "$(ls "$(ml_snap_dir)" | wc -l | tr -d ' ')" "1" "guardiao salva a 4% num passo"
[ -f "$(ml_state_dir)/guardian.armed" ] && armed=nao_removeu || armed=ok
assert_eq "$armed" "ok" "guardiao remove o flag armed ao sair"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: FAIL — `guardiao.sh` não existe.

- [ ] **Step 3: Write minimal implementation**

Create `skills/manter_ligado/bin/guardiao.sh`:

```bash
#!/usr/bin/env bash
# Guardião singleton: segura o inhibitor (via systemd-inhibit, no controlador) e roda o loop de bateria.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

ml_init_state
FLAG="$(ml_state_dir)/guardian.armed"
: > "$FLAG"
trap 'rm -f "$FLAG"' EXIT

warned=0; saved=0
while :; do
  cap="$(ml_battery_capacity)"; ac="$(ml_on_ac)"
  [ "$ac" = "1" ] && { warned=0; saved=0; }
  acao="$(ml_decide "$cap" "$ac" "$warned" "$saved")"
  case "$acao" in
    warn) ml_push "Bateria ${MANTER_WARN_PCT:-20}% - rode /memo nas sessoes via /rc se quiser."; warned=1 ;;
    save) ml_save "$(date +%Y%m%d-%H%M%S)"; saved=1 ;;
  esac
  [ "${MANTER_ONESHOT:-0}" = "1" ] && break
  sleep "${MANTER_INTERVAL:-60}"
done
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: PASS — "guardiao salva a 4% num passo", "guardiao remove o flag armed ao sair".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/bin/guardiao.sh skills/manter_ligado/tests/test_manter_ligado.sh
git commit -m "feat(manter_ligado): loop do guardiao com latch de warn/save"
```

---

### Task 5: `manter_ligado.sh` — controlador (on/off/status/limpar) + guardião via systemd

**Files:**
- Create: `skills/manter_ligado/bin/manter_ligado.sh`
- Test: integração real com `systemd --user` (bateria alta pra não salvar).

**Interfaces:**
- Consumes: todo o `lib.sh`; `guardiao.sh`
- Produces: CLI `manter_ligado.sh {on|off|status|limpar}`; unidade `manter-ligado-guardian.service` (user, transitória).

- [ ] **Step 1: Escrever o controlador**

Create `skills/manter_ligado/bin/manter_ligado.sh`:

```bash
#!/usr/bin/env bash
# Controlador fino da skill manter_ligado.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

UNIT="manter-ligado-guardian"

ml_guardian_active() { systemctl --user is-active --quiet "$UNIT.service"; }

ml_guardian_start() {
  ml_guardian_active && return 0
  systemd-run --user --unit="$UNIT" --collect \
    --setenv=MANTER_WARN_PCT="${MANTER_WARN_PCT:-20}" \
    --setenv=MANTER_SAVE_PCT="${MANTER_SAVE_PCT:-5}" \
    --setenv=MANTER_INTERVAL="${MANTER_INTERVAL:-60}" \
    --setenv=MEMO_HEADLESS="${MEMO_HEADLESS:-0}" \
    systemd-inhibit --what=sleep:handle-lid-switch \
      --who="manter_ligado" --why="transito com tampa fechada" --mode=block \
      "$DIR/guardiao.sh"
}

ml_guardian_stop() {
  ml_guardian_active && systemctl --user stop "$UNIT.service" >/dev/null 2>&1 || true
  rm -f "$(ml_state_dir)/guardian.armed"
}

_sid() { printf '%s\n' "${CLAUDE_CODE_SESSION_ID:-desconhecida}"; }
_slug() { printf '%s\n' "$PWD" | sed 's#/#-#g; s#_#-#g'; }

cmd_on() {
  ml_init_state; ml_reap
  local sid; sid="$(_sid)"
  ml_register_session "$sid" "$(_slug)" "$(ml_resolve_transcript "$sid" || true)"
  ml_guardian_start
  printf 'armado (sessoes: %s)\n' "$(ml_count)"
}

cmd_off() {
  ml_unregister_session "$(_sid)"; ml_reap
  if [ "$(ml_count)" = "0" ]; then ml_guardian_stop; printf 'desarmado (guardiao derrubado)\n';
  else printf 'saiu; ainda armado por %s sessao(oes)\n' "$(ml_count)"; fi
}

cmd_status() {
  ml_reap
  if ml_guardian_active; then printf 'ARMADO por %s sessao(oes)\n' "$(ml_count)";
  else printf 'desarmado\n'; fi
}

cmd_limpar() {
  ml_guardian_stop
  rm -rf "$(ml_snap_dir)" "$(ml_sessions_dir)"
  printf 'faxina concluida: snapshots e registro zerados\n'
}

case "${1:-status}" in
  on) cmd_on ;; off) cmd_off ;; status) cmd_status ;; limpar) cmd_limpar ;;
  *) printf 'uso: manter_ligado.sh {on|off|status|limpar}\n' >&2; exit 2 ;;
esac
```

- [ ] **Step 2: Testar on/status/off de verdade (bateria alta pra não salvar)**

Run:
```bash
chmod +x skills/manter_ligado/bin/*.sh
MANTER_INTERVAL=3600 skills/manter_ligado/bin/manter_ligado.sh on
skills/manter_ligado/bin/manter_ligado.sh status
systemctl --user is-active manter-ligado-guardian.service
systemd-inhibit --list | grep manter_ligado
skills/manter_ligado/bin/manter_ligado.sh off
systemctl --user is-active manter-ligado-guardian.service || echo "guardiao parado (ok)"
```
Expected:
- `on` → "armado (sessoes: 1)"; `status` → "ARMADO por 1 sessao(oes)"
- `is-active` → `active`
- `systemd-inhibit --list` mostra uma linha com `manter_ligado` em `block` para `handle-lid-switch:sleep`
- `off` → "desarmado (guardiao derrubado)"; `is-active` → `inactive`/`failed` → imprime "guardiao parado (ok)"

- [ ] **Step 3: Verificar idempotência do `on` duplo**

Run:
```bash
MANTER_INTERVAL=3600 skills/manter_ligado/bin/manter_ligado.sh on
MANTER_INTERVAL=3600 skills/manter_ligado/bin/manter_ligado.sh on
skills/manter_ligado/bin/manter_ligado.sh status
skills/manter_ligado/bin/manter_ligado.sh off
```
Expected: segundo `on` não cria segunda unidade (sem erro "unit already exists" fatal — `is-active` guard evita o start); `status` mostra 1 sessão; `off` derruba.

- [ ] **Step 4: Rodar a suíte de teste completa (regressão)**

Run: `bash skills/manter_ligado/tests/test_manter_ligado.sh`
Expected: PASS — TODOS OS TESTES PASSARAM.

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/bin/manter_ligado.sh
git commit -m "feat(manter_ligado): controlador on/off/status/limpar com guardiao systemd --user"
```

---

### Task 6: `SKILL.md` + nota cross-platform + índice de memória

**Files:**
- Create: `skills/manter_ligado/SKILL.md`

**Interfaces:**
- Consumes: `bin/manter_ligado.sh`

- [ ] **Step 1: Escrever a SKILL.md**

Create `skills/manter_ligado/SKILL.md`:

```markdown
---
name: manter_ligado
description: Mantém a conexão de dados viva com a tampa fechada (laptop na mochila, tethering) e salva o estado de todas as sessões quando a bateria chega a ≤5%, sem desligar a máquina. Use quando o usuário disser "manter ligado", "vou pôr o laptop na mochila", "não deixa suspender com a tampa fechada", "salva a sessão se a bateria acabar", ou invocar /bigtech:manter_ligado {on|off|status|limpar}.
---

# manter_ligado

Skill controladora. Executa o script conforme o argumento (default `status`):

- `on` → `bash skills/manter_ligado/bin/manter_ligado.sh on`
- `off` → `bash skills/manter_ligado/bin/manter_ligado.sh off`
- `status` → `bash skills/manter_ligado/bin/manter_ligado.sh status`
- `limpar` → `bash skills/manter_ligado/bin/manter_ligado.sh limpar`

Ao invocar, rode o comando correspondente com a Bash tool e relate a saída ao usuário.
Não peça confirmação para `on`/`off`/`status`. Para `limpar` (apaga snapshots), confirme antes.

## O que faz

- `on`: registra a sessão atual e sobe um guardião singleton (`systemd --user` transitório) que segura
  um inhibitor `sleep:handle-lid-switch` (tampa fechada não suspende; a tela apaga/acorda pelo KDE) e
  roda um loop de bateria.
- A **20%**: push de aviso ao celular (KDE Connect; fallback notify-send).
- A **≤5%**: salva o estado de **todas** as sessões registradas (cópia do transcript, retenção=1) e,
  se `MEMO_HEADLESS=1`, destila memórias via `claude -p`. **Não desliga nem hiberna** — a máquina segue.
- `off`: desregistra; guardião cai só no último `off`. `status`: mostra se está armado. `limpar`: faxina.

Detalhes: ver `DESIGN.md` e `PLAN.md` nesta pasta.

## Nota cross-platform (não implementado)

Esta versão é Linux/systemd/KDE. Gêmeos a portar no futuro:
- macOS: `caffeinate -disu` no lugar do inhibitor; `pmset -g batt` para a bateria.
- Windows: `powercfg`/`presentationsettings` para o inhibitor; `WMICBattery`/`Get-CimInstance Win32_Battery`.
```

- [ ] **Step 2: Verificar que a skill aparece e roda**

Run: `bash skills/manter_ligado/bin/manter_ligado.sh status`
Expected: "desarmado" (nenhum guardião no ar).

- [ ] **Step 3: Atualizar o índice de memória do projeto (rastreabilidade)**

Adicionar uma linha ao `MEMORY.md` do projeto claude-configs apontando pra skill nova (feito na sessão, não no plano de código): `- [Skill manter_ligado](../../skills/...) — keep-alive tampa fechada + save a 5%`. (Passo de sessão; opcional.)

- [ ] **Step 4: Commit**

```bash
cd <raiz-do-plugin>
git add skills/manter_ligado/SKILL.md
git commit -m "feat(manter_ligado): SKILL.md + nota cross-platform"
```

---

## Self-Review

**1. Cobertura do spec (DESIGN.md):**
- Comandos on/off/status/limpar → Task 5 ✅
- Controlador fino + guardião singleton systemd --user transitório → Task 4/5 ✅
- Inhibitor `sleep:handle-lid-switch` (não idle) → Task 5 (`ml_guardian_start`) ✅
- Tela apaga/acorda pelo KDE (não forçamos DPMS) → garantido por não inibir idle nem tocar DPMS ✅
- Registro em `$XDG_RUNTIME_DIR` + refcount + reap de sid morto → Task 1 ✅
- Loop de bateria, ignora AC, 20% warn, 5% save com latch → Task 2 (decide) + Task 4 (loop) ✅
- Save = snapshot de transcript retenção=1 + memo headless best-effort, sem desligar/hibernar → Task 3 ✅
- Higiene (retenção=1, reap, journald via systemd-run, tmpfs) → Task 1/3/5 ✅
- Push KDE Connect + fallback notify-send → Task 3 (`ml_push`) ✅
- Nota cross-platform → Task 6 ✅

**2. Placeholders:** nenhum passo com TBD/TODO; todo código presente.

**3. Consistência de tipos/nomes:** `ml_decide`, `ml_save`, `ml_push`, `ml_reap`, `ml_count`, `ml_resolve_transcript`, `ml_snap_dir`, `ml_state_dir`, `ml_sessions_dir` usados com a mesma assinatura em todas as tasks e no controlador. Costuras de env (`MANTER_*`) idênticas entre lib, guardião e testes.

**Nota de execução:** o teste da Task 4 usa `MANTER_ONESHOT=1` (1 passo) — costura adicionada ao guardião no mesmo passo em que ele é criado; sem isso o loop seria infinito no teste.
```
