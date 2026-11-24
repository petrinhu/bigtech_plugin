# watchcode - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Skill global que vigia o journal/coredumps enquanto agentes/main codam, detecta crashes reais (OOM/SIGSEGV/SIGABRT/coredump de produto fora do baseline), classifica por sessão e roteia: crash desta sessao delega Caetano/CTO, de outra sessao ou do sistema vira relatorio.

**Architecture:** Daemon "burro" (`systemd --user` transitorio, singleton) detecta e anexa achados crus a `findings.jsonl`; a tick do Claude le, classifica (this/other/system) contra o scope da sessao e roteia. Refcount de sessoes com adocao de orfao. Logica pura em `lib.sh` com costuras injetaveis por env.

**Tech Stack:** Bash, `coredumpctl --json=short` + `jq`, `journalctl`, `systemd-run --user`, ScheduleWakeup (tick Claude). Linux com systemd --user e journald.

## Global Constraints

- **Zero root:** user-space (`systemd --user`, leitura de journal via grupo `wheel`, `coredumpctl` como user). Nunca `sudo`.
- **So erro REAL conta:** todo coredump listado pelo `coredumpctl` (ja e um crash) menos baseline; + OOM do journal. Baseline por padrao de caminho/comm em `baseline.txt`.
- **Daemon burro:** so detecta + filtra baseline + anexa cru (`kind,ts,sig,exe` ou `kind,pid,comm`). NAO classifica.
- **Classificacao na leitura** (tick Claude) por caminho do EXE contra o scope: `this` (sob scope) | `other:<proj>` (sob outro Projects/<x>) | `system` (resto). OOM: por `comm` (sem path) -> match no scope senao `system`.
- **So `this` delega Caetano/CTO** (modelo herdado da sessao; diagnostica + propoe, NAO aplica). `other`/`system` = relatorio puro, formato fixo.
- **Idempotencia:** `on` duplo = no-op; `off` de uma sessao nao afeta as outras; daemon cai no ultimo `off`. Orfao (daemon no ar, registro vazio) = adotar (so registrar).
- **Higiene:** state em `$XDG_RUNTIME_DIR/watchcode/` (tmpfs); reap de sid morto; daemon transitorio + journald.
- **Costuras de teste (env):** `WATCHCODE_STATE_DIR`, `WATCHCODE_COREDUMP_CMD`, `WATCHCODE_JOURNAL_CMD`, `WATCHCODE_BASELINE_FILE`, `WATCHCODE_SCOPE`, `WATCHCODE_PROJECTS_ROOT`, `WATCHCODE_INTERVAL` (default 120), `WATCHCODE_ONESHOT`.
- **Formatos de relatorio fixos** (verbatim):
  - outra sessao: `De: WatchCode` / `Para: sessão de <proj>` / (linha em branco) / corpo
  - sistema/usuario: `De: WatchCode` / `Para: Usuário` / (linha em branco) / corpo
- **Identificadores/comentarios em pt-br. Hifen simples, NUNCA em-dash** (hook no_mdash). Nenhum push sem ordem.

**Estrutura de arquivos:**
- `skills/watchcode/SKILL.md` - controlador (on/off/status) + comportamento da tick (arma ScheduleWakeup, le/classifica/roteia, fim de loop, resumo) + nota cross-platform.
- `skills/watchcode/baseline.txt` - padroes de baseline (defaults + extensivel).
- `skills/watchcode/bin/lib.sh` - funcoes puras (state, registro/reap, deteccao, baseline, classificacao, findings/cursor, relatorios).
- `skills/watchcode/bin/watchcode_daemon.sh` - loop do daemon.
- `skills/watchcode/bin/watchcode.sh` - controlador.
- `skills/watchcode/tests/test_watchcode.sh` - harness shell com fixtures.

---

### Task 1: `lib.sh` - state e registro de sessoes

**Files:**
- Create: `skills/watchcode/bin/lib.sh`
- Test: `skills/watchcode/tests/test_watchcode.sh`

**Interfaces:**
- Produces: `wc_state_dir`, `wc_sessions_dir`, `wc_init_state`, `wc_register_session <sid> <scope>`, `wc_unregister_session <sid>`, `wc_count`, `wc_live_sids`, `wc_reap`

- [ ] **Step 1: Write the failing test**

Create `skills/watchcode/tests/test_watchcode.sh`:

```bash
#!/usr/bin/env bash
# Harness de teste em shell puro para a skill watchcode.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
FAILS=0
pass() { printf '  ok  - %s\n' "$1"; }
fail() { printf '  NOK - %s\n' "$1"; FAILS=$((FAILS+1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (esperado='$2' obtido='$1')"; fi; }

SANDBOX="$(mktemp -d)"
export WATCHCODE_STATE_DIR="$SANDBOX/state"
export WATCHCODE_BASELINE_FILE="$SANDBOX/baseline.txt"
trap 'rm -rf "$SANDBOX"' EXIT

# shellcheck source=/dev/null
. "$DIR/bin/lib.sh"

# --- Task 1: registro ---
wc_init_state
wc_register_session "sid-A" "/proj/a"
wc_register_session "sid-B" "/proj/b"
assert_eq "$(wc_count)" "2" "registra duas sessoes"
wc_unregister_session "sid-A"
assert_eq "$(wc_count)" "1" "desregistra uma sessao"
wc_register_session "sid-morta" "/proj/x"
export WATCHCODE_LIVE_SIDS="sid-B"
wc_reap
assert_eq "$(wc_count)" "1" "reap remove sid morto"
assert_eq "$(ls "$(wc_sessions_dir)")" "sid-B" "reap preserva sid vivo"

echo "---"
[ "$FAILS" -eq 0 ] && echo "TODOS OS TESTES PASSARAM" || { echo "$FAILS FALHA(S)"; exit 1; }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: FAIL - `lib.sh` nao existe.

- [ ] **Step 3: Write minimal implementation**

Create `skills/watchcode/bin/lib.sh`:

```bash
#!/usr/bin/env bash
# Funcoes da skill watchcode. Sourced pelo controlador, daemon e testes.

wc_state_dir() { printf '%s\n' "${WATCHCODE_STATE_DIR:-${XDG_RUNTIME_DIR:-/tmp}/watchcode}"; }
wc_sessions_dir() { printf '%s\n' "$(wc_state_dir)/sessions"; }
wc_init_state() { mkdir -p "$(wc_sessions_dir)"; }

wc_register_session() {
  # <sid> <scope>
  wc_init_state
  printf '%s\n' "$2" > "$(wc_sessions_dir)/$1"
}

wc_unregister_session() { rm -f "$(wc_sessions_dir)/$1"; }

wc_count() {
  local d; d="$(wc_sessions_dir)"
  [ -d "$d" ] || { printf '0\n'; return; }
  find "$d" -maxdepth 1 -type f | wc -l | tr -d ' '
}

wc_live_sids() {
  if [ -n "${WATCHCODE_LIVE_SIDS:-}" ]; then
    printf '%s\n' $WATCHCODE_LIVE_SIDS
    return
  fi
  local pid env_sid
  for pid in $(pgrep -u "$(id -u)" -f claude 2>/dev/null); do
    env_sid="$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null \
      | sed -n 's/^CLAUDE_CODE_SESSION_ID=//p' | head -n1)"
    [ -n "$env_sid" ] && printf '%s\n' "$env_sid"
  done
}

wc_reap() {
  local d sid live f; d="$(wc_sessions_dir)"
  [ -d "$d" ] || return 0
  live="$(wc_live_sids)"
  for f in "$d"/*; do
    [ -e "$f" ] || continue
    sid="$(basename "$f")"
    printf '%s\n' "$live" | grep -qx "$sid" || rm -f "$f"
  done
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - "registra duas sessoes", "desregistra uma sessao", "reap remove sid morto", "reap preserva sid vivo".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/lib.sh skills/watchcode/tests/test_watchcode.sh
git commit -m "feat(watchcode): registro de sessoes + reap com costura de teste"
```

---

### Task 2: `lib.sh` - deteccao (coredumps + OOM)

**Files:**
- Modify: `skills/watchcode/bin/lib.sh` (append)
- Test: `skills/watchcode/tests/test_watchcode.sh` (append antes do rodape)

**Interfaces:**
- Produces:
  - `wc_detect_coredumps <since_epoch>` -> TSV `ts_us<TAB>sig<TAB>exe` (usa `$WATCHCODE_COREDUMP_CMD` ou `coredumpctl ... --json=short` + jq)
  - `wc_detect_oom <since_epoch>` -> TSV `pid<TAB>comm` (usa `$WATCHCODE_JOURNAL_CMD` ou `journalctl`)

- [ ] **Step 1: Write the failing test**

Append em `tests/test_watchcode.sh` (antes do bloco `echo "---"`):

```bash
# --- Task 2: deteccao ---
cat > "$SANDBOX/cores.json" <<'JSON'
[{"time":1784454486651229,"pid":155526,"uid":1000,"gid":1000,"sig":6,"corefile":"present","exe":"/opt/exemplo/Projects/meu_produto/build/bin/app_consumer","size":53578},
{"time":1784454635763262,"pid":160737,"uid":1000,"gid":1000,"sig":11,"corefile":"present","exe":"/var/tmp/aud_sec_probes/probe_alloc","size":39000}]
JSON
export WATCHCODE_COREDUMP_CMD="cat $SANDBOX/cores.json"
got_cd="$(wc_detect_coredumps 0 | tr '\t' ':' | tr '\n' '|')"
assert_eq "$got_cd" "1784454486651229:6:/opt/exemplo/Projects/meu_produto/build/bin/app_consumer|1784454635763262:11:/var/tmp/aud_sec_probes/probe_alloc|" "detect coredumps TSV"

cat > "$SANDBOX/journal.txt" <<'JRN'
jul 16 21:49:55 meuhost kernel: Memory cgroup out of memory: Killed process 917642 (python) total-vm:20400964kB, anon-rss:8356648kB
jul 16 21:50:01 meuhost systemd[1]: something unrelated
JRN
export WATCHCODE_JOURNAL_CMD="cat $SANDBOX/journal.txt"
assert_eq "$(wc_detect_oom 0)" "$(printf '917642\tpython')" "detect OOM pid+comm"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: FAIL - `wc_detect_coredumps`/`wc_detect_oom` indefinidas.

- [ ] **Step 3: Write minimal implementation**

Append em `bin/lib.sh`:

```bash
wc_detect_coredumps() {
  local since="$1" json
  if [ -n "${WATCHCODE_COREDUMP_CMD:-}" ]; then
    json="$($WATCHCODE_COREDUMP_CMD 2>/dev/null)"
  else
    json="$(coredumpctl list --since "@$since" --json=short 2>/dev/null)"
  fi
  [ -z "$json" ] && return 0
  printf '%s\n' "$json" | jq -r '.[] | [.time, .sig, .exe] | @tsv' 2>/dev/null
}

wc_detect_oom() {
  local since="$1" text
  if [ -n "${WATCHCODE_JOURNAL_CMD:-}" ]; then
    text="$($WATCHCODE_JOURNAL_CMD 2>/dev/null)"
  else
    text="$(journalctl --since "@$since" --no-pager 2>/dev/null)"
  fi
  printf '%s\n' "$text" \
    | grep -oE 'Killed process [0-9]+ \([^)]+\)' \
    | sed -E 's/Killed process ([0-9]+) \((.+)\)/\1\t\2/'
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - "detect coredumps TSV", "detect OOM pid+comm".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/lib.sh skills/watchcode/tests/test_watchcode.sh
git commit -m "feat(watchcode): deteccao de coredumps (jq) e OOM (journal)"
```

---

### Task 3: `lib.sh` - baseline e classificacao

**Files:**
- Modify: `skills/watchcode/bin/lib.sh` (append)
- Test: `skills/watchcode/tests/test_watchcode.sh` (append)

**Interfaces:**
- Produces:
  - `wc_baseline_match <string>` -> exit 0 se casa padrao do baseline
  - `wc_classify_exe <exe> <scope> <projects_root>` -> `this` | `other:<proj>` | `system`
  - `wc_classify_oom <comm> <scope>` -> `this` | `system`

- [ ] **Step 1: Write the failing test**

Append em `tests/test_watchcode.sh`:

```bash
# --- Task 3: baseline e classificacao ---
cat > "$WATCHCODE_BASELINE_FILE" <<'BL'
# baseline de teste
/var/tmp/*_probes/*
*/audit/scratch/*
*death*test*
BL
wc_baseline_match "/var/tmp/aud_sec_probes/probe_alloc" && r=sim || r=nao
assert_eq "$r" "sim" "baseline casa sonda de sanitizer"
wc_baseline_match "/opt/exemplo/Projects/meu_produto/build/bin/app_consumer" && r=sim || r=nao
assert_eq "$r" "nao" "baseline NAO casa binario de produto"

SCOPE="/opt/exemplo/Projects/appatual"; PROOT="/opt/exemplo/Projects"
assert_eq "$(wc_classify_exe "$SCOPE/build/bin/app" "$SCOPE" "$PROOT")" "this" "classifica this"
assert_eq "$(wc_classify_exe "$PROOT/outro/build/bin/x" "$SCOPE" "$PROOT")" "other:outro" "classifica other:<proj>"
assert_eq "$(wc_classify_exe "/usr/bin/kwin_wayland" "$SCOPE" "$PROOT")" "system" "classifica system"

mkdir -p "$SANDBOX/scope/build"; : > "$SANDBOX/scope/build/meuapp"
assert_eq "$(wc_classify_oom meuapp "$SANDBOX/scope")" "this" "OOM comm no scope = this"
assert_eq "$(wc_classify_oom python "$SANDBOX/scope")" "system" "OOM comm fora do scope = system"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: FAIL - `wc_baseline_match`/`wc_classify_exe`/`wc_classify_oom` indefinidas.

- [ ] **Step 3: Write minimal implementation**

Append em `bin/lib.sh`:

```bash
wc_baseline_match() {
  local s="$1" f pat
  f="${WATCHCODE_BASELINE_FILE:-skills/watchcode/baseline.txt}"
  [ -r "$f" ] || return 1
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$pat" in \#*) continue ;; esac
    # shellcheck disable=SC2254  # glob intencional vindo do baseline
    case "$s" in $pat) return 0 ;; esac
  done < "$f"
  return 1
}

wc_classify_exe() {
  local exe="$1" scope="$2" proot="$3" rest proj
  case "$exe" in
    "$scope"/*) printf 'this\n'; return ;;
  esac
  case "$exe" in
    "$proot"/*)
      rest="${exe#"$proot"/}"; proj="${rest%%/*}"
      printf 'other:%s\n' "$proj"; return ;;
  esac
  printf 'system\n'
}

wc_classify_oom() {
  local comm="$1" scope="$2"
  if find "$scope" -maxdepth 8 -type f -name "$comm" 2>/dev/null | head -n1 | grep -q .; then
    printf 'this\n'
  else
    printf 'system\n'
  fi
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - baseline casa/nao-casa e as 5 classificacoes (this/other/system/oom-this/oom-system).

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/lib.sh skills/watchcode/tests/test_watchcode.sh
git commit -m "feat(watchcode): filtro baseline e classificacao this/other/system"
```

---

### Task 4: `lib.sh` - findings, cursor e relatorios

**Files:**
- Modify: `skills/watchcode/bin/lib.sh` (append)
- Test: `skills/watchcode/tests/test_watchcode.sh` (append)

**Interfaces:**
- Produces:
  - `wc_findings_file` -> path do `findings.jsonl`
  - `wc_append_coredump <ts_s> <sig> <exe>` / `wc_append_oom <pid> <comm>` -> anexa linha JSON
  - `wc_read_new <sid>` -> imprime linhas novas de findings e avanca `cursor/<sid>`
  - `wc_sig_name <n>` -> nome do sinal (11->SIGSEGV etc.)
  - `wc_report_other <proj> <corpo>` / `wc_report_user <corpo>` -> texto de relatorio no formato fixo

- [ ] **Step 1: Write the failing test**

Append em `tests/test_watchcode.sh`:

```bash
# --- Task 4: findings, cursor, relatorios ---
: > "$(wc_findings_file)"
wc_append_coredump 1784454486 11 "/proj/app"
wc_append_oom 999 "python"
assert_eq "$(wc -l < "$(wc_findings_file)" | tr -d ' ')" "2" "append cria 2 findings"
first="$(wc_read_new sid-R | head -n1 | jq -r '.exe')"
assert_eq "$first" "/proj/app" "read_new le do inicio (backlog do orfao)"
assert_eq "$(wc_read_new sid-R)" "" "cursor avancou: nada novo na 2a leitura"

assert_eq "$(wc_sig_name 11)" "SIGSEGV" "sig 11 = SIGSEGV"
assert_eq "$(wc_sig_name 6)" "SIGABRT" "sig 6 = SIGABRT"

exp_other="$(printf 'De: WatchCode\nPara: sessão de /opt/exemplo/Projects/outro\n\nSIGSEGV em app')"
assert_eq "$(wc_report_other /opt/exemplo/Projects/outro 'SIGSEGV em app')" "$exp_other" "relatorio outra sessao formato fixo"
exp_user="$(printf 'De: WatchCode\nPara: Usuário\n\nOOM matou python')"
assert_eq "$(wc_report_user 'OOM matou python')" "$exp_user" "relatorio usuario formato fixo"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: FAIL - funcoes de findings/relatorio indefinidas.

- [ ] **Step 3: Write minimal implementation**

Append em `bin/lib.sh`:

```bash
wc_findings_file() { printf '%s\n' "$(wc_state_dir)/findings.jsonl"; }

wc_append_coredump() {
  wc_init_state
  jq -cn --argjson ts "$1" --argjson sig "$2" --arg exe "$3" \
    '{kind:"coredump",ts:$ts,sig:$sig,exe:$exe}' >> "$(wc_findings_file)"
}

wc_append_oom() {
  wc_init_state
  jq -cn --arg pid "$1" --arg comm "$2" \
    '{kind:"oom",pid:$pid,comm:$comm}' >> "$(wc_findings_file)"
}

wc_read_new() {
  local sid="$1" cur cf ff total
  ff="$(wc_findings_file)"; cf="$(wc_state_dir)/cursor/$sid"
  [ -f "$ff" ] || return 0
  cur=0; [ -f "$cf" ] && cur="$(cat "$cf")"
  total="$(wc -l < "$ff" | tr -d ' ')"
  if [ "$total" -gt "$cur" ]; then
    sed -n "$((cur+1)),${total}p" "$ff"
    mkdir -p "$(dirname "$cf")"; printf '%s\n' "$total" > "$cf"
  fi
}

wc_sig_name() {
  case "$1" in
    4) printf 'SIGILL\n' ;; 6) printf 'SIGABRT\n' ;; 7) printf 'SIGBUS\n' ;;
    8) printf 'SIGFPE\n' ;; 11) printf 'SIGSEGV\n' ;; *) printf 'SIG%s\n' "$1" ;;
  esac
}

wc_report_other() {
  # <proj> <corpo>
  printf 'De: WatchCode\nPara: sessão de %s\n\n%s\n' "$1" "$2"
}

wc_report_user() {
  # <corpo>
  printf 'De: WatchCode\nPara: Usuário\n\n%s\n' "$1"
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - append/cursor/backlog, sig_name, e os dois relatorios no formato fixo.

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/lib.sh skills/watchcode/tests/test_watchcode.sh
git commit -m "feat(watchcode): findings jsonl, cursor por sessao e relatorios formato fixo"
```

---

### Task 5: `watchcode_daemon.sh` - loop do daemon

**Files:**
- Create: `skills/watchcode/bin/watchcode_daemon.sh`
- Test: `skills/watchcode/tests/test_watchcode.sh` (append)

**Interfaces:**
- Consumes: `wc_detect_coredumps`, `wc_detect_oom`, `wc_baseline_match`, `wc_append_coredump`, `wc_append_oom`, `wc_state_dir`
- Produces: escreve `findings.jsonl` (crus, sem baseline) + `last_scan` + flag `daemon.armed`; `WATCHCODE_ONESHOT=1` roda 1 ciclo.

- [ ] **Step 1: Write the failing test**

Append em `tests/test_watchcode.sh`:

```bash
# --- Task 5: daemon (1 ciclo) ---
export WATCHCODE_ONESHOT=1
rm -f "$(wc_findings_file)"
# reaproveita os stubs de cores.json (1 produto + 1 baseline) e journal (1 OOM)
bash "$DIR/bin/watchcode_daemon.sh"
n="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n" "2" "daemon anexa 2 (produto + OOM), baseline filtrado"
kinds="$(jq -r '.kind' "$(wc_findings_file)" | sort | tr '\n' ',')"
assert_eq "$kinds" "coredump,oom," "daemon anexa 1 coredump e 1 oom"
[ -f "$(wc_state_dir)/daemon.armed" ] && armed=nao_removeu || armed=ok
assert_eq "$armed" "ok" "daemon remove flag armed ao sair"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: FAIL - `watchcode_daemon.sh` nao existe.

- [ ] **Step 3: Write minimal implementation**

Create `skills/watchcode/bin/watchcode_daemon.sh`:

```bash
#!/usr/bin/env bash
# Daemon "burro" do watchcode: detecta crashes reais, filtra baseline, anexa achados crus.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

wc_init_state
FLAG="$(wc_state_dir)/daemon.armed"
: > "$FLAG"
trap 'rm -f "$FLAG"' EXIT

wc_daemon_cycle() {
  local since ts sig exe pid comm
  since="$(cat "$(wc_state_dir)/last_scan" 2>/dev/null || printf '%s' "$(( $(date +%s) - 130 ))")"
  wc_detect_coredumps "$since" | while IFS="$(printf '\t')" read -r ts sig exe; do
    [ -z "${exe:-}" ] && continue
    wc_baseline_match "$exe" && continue
    wc_append_coredump "$(( ts / 1000000 ))" "$sig" "$exe"
  done
  wc_detect_oom "$since" | while IFS="$(printf '\t')" read -r pid comm; do
    [ -z "${comm:-}" ] && continue
    wc_baseline_match "$comm" && continue
    wc_append_oom "$pid" "$comm"
  done
  date +%s > "$(wc_state_dir)/last_scan"
}

while :; do
  wc_daemon_cycle
  [ "${WATCHCODE_ONESHOT:-0}" = "1" ] && break
  sleep "${WATCHCODE_INTERVAL:-120}"
done
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - "daemon anexa 2 (produto + OOM), baseline filtrado", "daemon anexa 1 coredump e 1 oom", "daemon remove flag armed ao sair".

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/watchcode_daemon.sh skills/watchcode/tests/test_watchcode.sh
git commit -m "feat(watchcode): daemon de deteccao com filtro baseline e last_scan"
```

---

### Task 6: `watchcode.sh` - controlador + baseline.txt default

**Files:**
- Create: `skills/watchcode/bin/watchcode.sh`
- Create: `skills/watchcode/baseline.txt`
- Test: integracao real com `systemd --user`.

**Interfaces:**
- Consumes: todo o `lib.sh`; `watchcode_daemon.sh`
- Produces: CLI `watchcode.sh {on|off|status}`; unidade `watchcode-daemon.service` (user, transitoria).

- [ ] **Step 1: Criar o baseline default**

Create `skills/watchcode/baseline.txt`:

```
# baseline do watchcode - padroes de EXE (glob) / comm a IGNORAR (um por linha).
# Linhas iniciadas por # sao comentario. Estenda a vontade.
/var/tmp/*_probes/*
*/audit/scratch/*
*death*test*
*death_test*
```

- [ ] **Step 2: Criar o controlador**

Create `skills/watchcode/bin/watchcode.sh`:

```bash
#!/usr/bin/env bash
# Controlador da skill watchcode.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/lib.sh"

UNIT="watchcode-daemon"

wc_daemon_active() { systemctl --user is-active --quiet "$UNIT.service"; }

wc_daemon_start() {
  wc_daemon_active && return 0
  systemd-run --user --unit="$UNIT" --collect \
    --setenv=WATCHCODE_STATE_DIR="$(wc_state_dir)" \
    --setenv=WATCHCODE_BASELINE_FILE="${WATCHCODE_BASELINE_FILE:-$DIR/../baseline.txt}" \
    --setenv=WATCHCODE_INTERVAL="${WATCHCODE_INTERVAL:-120}" \
    "$DIR/watchcode_daemon.sh"
}

wc_daemon_stop() {
  wc_daemon_active && systemctl --user stop "$UNIT.service" >/dev/null 2>&1 || true
  rm -f "$(wc_state_dir)/daemon.armed"
}

_sid() { printf '%s\n' "${CLAUDE_CODE_SESSION_ID:-desconhecida}"; }
_scope() { printf '%s\n' "${WATCHCODE_SCOPE:-$PWD}"; }

cmd_on() {
  wc_init_state; wc_reap
  local adotou=nao
  wc_daemon_active && [ "$(wc_count)" = "0" ] && adotou=sim
  wc_register_session "$(_sid)" "$(_scope)"
  wc_daemon_start
  if [ "$adotou" = "sim" ]; then
    printf 'vigiando (ADOTOU daemon orfao; scope=%s; sessoes: %s)\n' "$(_scope)" "$(wc_count)"
  else
    printf 'vigiando (scope=%s; sessoes: %s)\n' "$(_scope)" "$(wc_count)"
  fi
}

cmd_off() {
  wc_unregister_session "$(_sid)"; wc_reap
  if [ "$(wc_count)" = "0" ]; then
    wc_daemon_stop
    printf 'encerrado (daemon derrubado)\n'
  else
    printf 'saiu; ainda vigiando por %s sessao(oes)\n' "$(wc_count)"
  fi
}

cmd_status() {
  wc_reap
  local nf=0; [ -f "$(wc_findings_file)" ] && nf="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
  if wc_daemon_active; then
    printf 'VIGIANDO por %s sessao(oes); %s achado(s) acumulado(s)\n' "$(wc_count)" "$nf"
  else
    printf 'parado\n'
  fi
}

case "${1:-status}" in
  on) cmd_on ;; off) cmd_off ;; status) cmd_status ;;
  *) printf 'uso: watchcode.sh {on|off|status}\n' >&2; exit 2 ;;
esac
```

- [ ] **Step 3: Testar on/status/off + adocao de orfao (integracao real)**

Run:
```bash
chmod +x skills/watchcode/bin/*.sh
export CLAUDE_CODE_SESSION_ID=wc-integ WATCHCODE_LIVE_SIDS=wc-integ
export WATCHCODE_INTERVAL=3600 WATCHCODE_SCOPE="$PWD"
skills/watchcode/bin/watchcode.sh on
skills/watchcode/bin/watchcode.sh status
systemctl --user is-active watchcode-daemon.service
# adocao: simula orfao removendo o registro mas deixando o daemon vivo
rm -f "${XDG_RUNTIME_DIR}/watchcode/sessions/wc-integ"
CLAUDE_CODE_SESSION_ID=wc-integ2 WATCHCODE_LIVE_SIDS="wc-integ2" \
  skills/watchcode/bin/watchcode.sh on   # deve dizer "ADOTOU daemon orfao"
CLAUDE_CODE_SESSION_ID=wc-integ2 WATCHCODE_LIVE_SIDS="wc-integ2" \
  skills/watchcode/bin/watchcode.sh off  # derruba (ultima sessao)
systemctl --user is-active watchcode-daemon.service || echo "daemon parado (ok)"
```
Expected:
- `on` -> "vigiando (scope=...; sessoes: 1)"; `status` -> "VIGIANDO por 1 sessao(oes); N achado(s)"; `is-active` -> `active`
- segundo `on` (apos remover o registro, daemon ainda vivo) -> linha com "ADOTOU daemon orfao"
- `off` -> "encerrado (daemon derrubado)"; `is-active` -> inactive -> imprime "daemon parado (ok)"

- [ ] **Step 4: Rodar a suite completa (regressao)**

Run: `bash skills/watchcode/tests/test_watchcode.sh`
Expected: PASS - TODOS OS TESTES PASSARAM.

- [ ] **Step 5: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/bin/watchcode.sh skills/watchcode/baseline.txt
git commit -m "feat(watchcode): controlador on/off/status com refcount e adocao de orfao"
```

---

### Task 7: `SKILL.md` - comportamento da tick + nota cross-platform

**Files:**
- Create: `skills/watchcode/SKILL.md`

**Interfaces:**
- Consumes: `bin/watchcode.sh`, `bin/lib.sh`

- [ ] **Step 1: Escrever a SKILL.md**

Create `skills/watchcode/SKILL.md`:

````markdown
---
name: watchcode
description: Vigia o journal/coredumps enquanto agentes ou main estao codando e captura crashes reais (OOM, SIGSEGV, SIGABRT, coredump de produto fora do baseline). Crash desta sessao delega o Caetano/CTO (fable) pra diagnosticar e propor; crash de outra sessao Claude ou do sistema/apps do usuario vira relatorio. Use quando o usuario disser "vigia o codigo", "arma o watchcode", "monitora crashes enquanto coda", "avisa se algo quebrar", ou invocar /bigtech:watchcode {--on|--off|--status}.
---

# watchcode

Vigia crashes reais durante a codificacao. O daemon detecta; esta sessao (a tick) classifica e roteia.

## Comandos (rode com a Bash tool)

- `on`  -> `bash skills/watchcode/bin/watchcode.sh on`
- `off` -> `bash skills/watchcode/bin/watchcode.sh off`
- `status` -> `bash skills/watchcode/bin/watchcode.sh status`

Ao dar `on`, ALEM de rodar o comando, ARME o loop de tick: use ScheduleWakeup (~120s) para reacordar e processar achados. Ao dar `off` ou ao detectar que os agentes de codificacao pararam (thread ociosa), faca a LEITURA FINAL, emita o RESUMO e pare (o `off` ja derruba o daemon no ultimo).

## A cada tick (vigilancia; NAO delega ainda)

1. `sid="$CLAUDE_CODE_SESSION_ID"`, `scope` = cwd de quando armou, `proot` = dir pai do scope (ou `$WATCHCODE_PROJECTS_ROOT`).
2. Leia os achados novos: `bash -c '. skills/watchcode/bin/lib.sh; wc_read_new "'"$sid"'"'` (cada linha e um JSON).
3. Classifique cada achado e ACUMULE (guarde classe + dados):
   - `coredump`: `wc_classify_exe <exe> <scope> <proot>`
   - `oom`: `wc_classify_oom <comm> <scope>`
4. NAO delegue nem gere o resumo agora. Opcional: um heads-up de 1 linha se houver achado novo (ex: "watchcode: +1 crash desta sessao detectado; reporto no fim").
5. Sem achado novo -> siga silencioso ate o proximo tick.

## Resumo final (semaforo)

Ao encerrar (agentes pararam OU `off`): faca a leitura final, **VERIFIQUE o daemon de verdade** (`systemctl --user is-active watchcode-daemon.service` - nunca assuma), e emita UMA das tres, sempre com o icone 👿 antes do status do daemon.

Precedencia: se ha QUALQUER achado desta sessao -> VERMELHO; senao se ha achado de fora -> AMARELO; senao VERDE.

🟢 **VERDE - sem erros**
- 👿 daemon: <parado | AINDA NO AR> (verificado via is-active)
- relatorio: "N ciclos, nada anormal"

🟡 **AMARELO - so erros de fora desta sessao** (outra sessao / sistema / apps)
- 👿 daemon: <parado | no ar> (verificado)
- relatorio classificado dos achados
- para cada OUTRA sessao Claude afetada: `wc_report_other <proj> "<corpo>"` (uma mensagem por sessao)
- para erros de sistema/apps: `wc_report_user "<corpo>"`

🔴 **VERMELHO - ha erro DESTA sessao** (o relatorio inclui tambem os de fora, se houver)
- 👿 daemon: <parado | no ar> (verificado)
- relatorio completo (this + quaisquer de fora)
- as mensagens `wc_report_other` / `wc_report_user` para os de fora (se houver)
- **PERGUNTA ao usuario via AskUserQuestion: iniciar o ciclo de resolucao?** Se sim -> delega **Caetano/CTO (fable)** (subagent_type `bigtech:caetano-cto`, model `fable`) pra entender a causa-raiz (`coredumpctl info`, `coredumpctl gdb`, backtrace, codigo/logs), **PROPOR o fix SEM aplicar**, e recomendar "simples (1 especialista) vs Cosimo montar time". So os crashes DESTA sessao entram no ciclo.

## Baseline

Ignora ruido conhecido via `skills/watchcode/baseline.txt` (sondas de sanitizer, death-tests, scratch de auditoria). Estenda esse arquivo para novos falsos-positivos. Ruido de journal (NVRM, drkonqi, servico local que responde 503) nao casa OOM/coredump, entao ja e ignorado naturalmente.

## Nota cross-platform (nao implementado)

Linux/systemd/coredumpctl. Portes futuros: macOS (`log show` + DiagnosticReports); Windows (Event Log / WER).
````

- [ ] **Step 2: Verificar frontmatter e ausencia de em-dash**

Run:
```bash
grep -n '—' skills/watchcode/SKILL.md && echo "TEM EM-DASH (corrigir)" || echo "sem em-dash (ok)"
head -3 skills/watchcode/SKILL.md
```
Expected: "sem em-dash (ok)"; frontmatter com `name: watchcode`.

- [ ] **Step 3: Commit**

```bash
cd <raiz-do-plugin>
git add skills/watchcode/SKILL.md
git commit -m "feat(watchcode): SKILL.md com comportamento da tick e roteamento por classe"
```

---

## Self-Review

**1. Cobertura do spec (DESIGN.md):**
- Comandos on/off/status -> Task 6 (+ tick em Task 7) OK
- Daemon burro (detecta+baseline+append cru) -> Task 5 OK
- Deteccao coredumpctl (jq) + OOM journal -> Task 2 OK
- Baseline extensivel -> Task 3 (funcao) + Task 6 (arquivo default) OK
- Classificacao na leitura this/other/system (+ OOM por comm) -> Task 3 OK
- 3 destinos com formato fixo de relatorio -> Task 4 (formatters) + Task 7 (roteamento) OK
- So `this` delega Caetano/CTO fable (diagnostica+propoe, nao aplica) -> Task 7 OK
- Refcount + adocao de orfao -> Task 1 (registro) + Task 6 (cmd_on) OK
- Cursor por sessao (backlog do orfao) -> Task 4 OK
- Ciclo Opcao 1 (auto ao ociar + off) + resumo final -> Task 7 OK
- State tmpfs + reap + daemon transitorio/journald -> Task 1/5/6 OK
- Costuras de teste -> todas as tasks usam os env overrides OK

**2. Placeholders:** nenhum passo com TBD/TODO; todo codigo presente.

**3. Consistencia de nomes:** `wc_state_dir`, `wc_register_session`, `wc_reap`, `wc_detect_coredumps`, `wc_detect_oom`, `wc_baseline_match`, `wc_classify_exe`, `wc_classify_oom`, `wc_findings_file`, `wc_append_coredump`, `wc_append_oom`, `wc_read_new`, `wc_sig_name`, `wc_report_other`, `wc_report_user` usados com a mesma assinatura no lib, daemon, controlador e SKILL.md. Env `WATCHCODE_*` identicos entre lib/daemon/controlador/testes.

**Nota de decisao (grounding):** OOM so expoe `comm` (sem path), entao a atribuicao de OOM e por match do comm no scope (senao `system`) - registrado em Task 3 e no DESIGN. Nao distingue OOM de "outra sessao" (vai pra relatorio ao usuario).
````
