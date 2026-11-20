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

# --- Fix: leitura vazia de sysfs cai no default ---
: > "$SANDBOX/cap_vazio"; export MANTER_BAT_CAPACITY_FILE="$SANDBOX/cap_vazio"
assert_eq "$(ml_battery_capacity)" "100" "capacidade vazia -> default 100"
: > "$SANDBOX/ac_vazio"; export MANTER_AC_ONLINE_FILE="$SANDBOX/ac_vazio"
assert_eq "$(ml_on_ac)" "0" "ac vazio -> default 0"
# restaura para nao afetar blocos seguintes (se houver)
printf '42\n' > "$SANDBOX/cap"; export MANTER_BAT_CAPACITY_FILE="$SANDBOX/cap"
printf '1\n' > "$SANDBOX/ac"; export MANTER_AC_ONLINE_FILE="$SANDBOX/ac"

# --- Guarda de plataforma (CONS-09W): so Linux com systemd --user ---
g_os="$(OSTYPE=darwin23 bash -c '. "'"$DIR"'/bin/lib.sh"; ml_require_linux_systemd 2>/dev/null; echo $?')"
assert_eq "$g_os" "3" "fora de Linux: sai com 3"
g_path="$(PATH=/nonexistent /bin/bash -c '. "'"$DIR"'/bin/lib.sh"; ml_require_linux_systemd 2>/dev/null; echo $?')"
assert_eq "$g_path" "3" "sem systemd-run/systemd-inhibit no PATH: sai com 3"

# --- CONS-09S (item 1): estado privado, sem /tmp compartilhado ---
ml_home="$SANDBOX/ml_home"; mkdir -p "$ml_home"
r="$(env -u MANTER_STATE_DIR -u XDG_RUNTIME_DIR HOME="$ml_home" bash -c '. "'"$DIR"'/bin/lib.sh"; ml_state_dir')"
assert_eq "$r" "$ml_home/.cache/manter_ligado" "CONS-09S 1: sem env, estado vai para \$HOME/.cache e nao para /tmp"
r="$(env -u MANTER_STATE_DIR XDG_RUNTIME_DIR="$SANDBOX/ml_xdg" bash -c '. "'"$DIR"'/bin/lib.sh"; ml_state_dir')"
assert_eq "$r" "$SANDBOX/ml_xdg/manter_ligado" "CONS-09S 1: com XDG_RUNTIME_DIR, usa o XDG"
r="$(env MANTER_STATE_DIR="$SANDBOX/ml_perm/st" bash -c '. "'"$DIR"'/bin/lib.sh"; ml_init_state && stat -c %a "$(ml_state_dir)"' 2>/dev/null)"
assert_eq "$r" "700" "CONS-09S 1: diretorio de estado criado com modo 700"
mkdir -p "$SANDBOX/ml_target"; ln -s "$SANDBOX/ml_target" "$SANDBOX/ml_link"
rc_link="$(MANTER_STATE_DIR="$SANDBOX/ml_link" bash -c '. "'"$DIR"'/bin/lib.sh"; if ml_init_state 2>/dev/null; then echo 0; else echo 1; fi')"
assert_eq "$rc_link" "1" "CONS-09S 1: estado que e symlink e recusado (rc!=0)"

# --- CONS-09S (item 3): $sid e transcript antes do claude -p ---
BIN_STUB="$SANDBOX/stubbin"; mkdir -p "$BIN_STUB"
CALLS="$SANDBOX/claude_calls.log"
printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$*" >> "%s"\n' "$CALLS" > "$BIN_STUB/claude"; chmod +x "$BIN_STUB/claude"
PROJ="$SANDBOX/projects/p1"; mkdir -p "$PROJ"
echo '{}' > "$PROJ/sid-ok-1.jsonl"
rm -f "$CALLS"
rm -rf "$(ml_sessions_dir)"; mkdir -p "$(ml_sessions_dir)"
printf '%s\n%s\n%s\n' "slug" "slug" "$PROJ/sid-ok-1.jsonl" > "$(ml_sessions_dir)/sid;touch-x"
assert_eq "$(ml_register_session 'sid;touch-x' slug x >/dev/null 2>&1; echo $?)" "1" "CONS-09S 3: ml_register_session recusa \$sid fora do padrao"
PATH="$BIN_STUB:$PATH" MEMO_HEADLESS=1 bash -c '. "'"$DIR"'/bin/lib.sh"; ml_save s1' >/dev/null 2>&1
assert_eq "$([ -e "$CALLS" ] && echo chamou || echo nao_chamou)" "nao_chamou" "CONS-09S 3: \$sid fora de ^[A-Za-z0-9-]+\$ nao chega ao claude -p"
rm -rf "$(ml_sessions_dir)"; mkdir -p "$(ml_sessions_dir)"
ml_register_session 'sid-ok-1' "slug" "$PROJ/sid-ok-1.jsonl"
PATH="$BIN_STUB:$PATH" MEMO_HEADLESS=1 bash -c '. "'"$DIR"'/bin/lib.sh"; ml_save s2' >/dev/null 2>&1
assert_eq "$([ -e "$CALLS" ] && echo chamou || echo nao_chamou)" "chamou" "CONS-09S 3: \$sid valido (sid-ok-1) chega ao claude -p"
rm -rf "$(ml_sessions_dir)"; mkdir -p "$(ml_sessions_dir)"
ml_register_session 'sid-tr-1' "slug" "/etc/hostname"
ml_save s3 >/dev/null 2>&1
assert_eq "$(find "$(ml_snap_dir)" -name 'sid-tr-1.jsonl' 2>/dev/null | wc -l | tr -d ' ')" "0" "CONS-09S 3: transcript fora do diretorio de projetos nao e copiado"
rm -rf "$(ml_sessions_dir)"; mkdir -p "$(ml_sessions_dir)"
ml_register_session 'sid-ok-1' "slug" "$PROJ/sid-ok-1.jsonl"
ml_save s4 >/dev/null 2>&1
assert_eq "$(find "$(ml_snap_dir)" -name 'sid-ok-1.jsonl' 2>/dev/null | wc -l | tr -d ' ')" "1" "CONS-09S 3: transcript sob o diretorio de projetos e copiado"

# --- CONS-09S (item 4): guardas do laco do guardiao ---
FAKE_SLEEP_DIR="$SANDBOX/fake_sleep"; mkdir -p "$FAKE_SLEEP_DIR"
printf '#!/usr/bin/env bash\nexit 1\n' > "$FAKE_SLEEP_DIR/sleep"; chmod +x "$FAKE_SLEEP_DIR/sleep"
rot_err="$SANDBOX/rot.err"
env -u MANTER_ONESHOT MANTER_INTERVAL=5 MANTER_BAT_CAPACITY_FILE=/nonexistent MANTER_AC_ONLINE_FILE=/nonexistent \
  PATH="$FAKE_SLEEP_DIR:$PATH" timeout 20 bash "$DIR/bin/guardiao.sh" >/dev/null 2>"$rot_err"; rot_rc=$?
assert_eq "$([ "$rot_rc" = "124" ] && echo girou || echo encerrou)" "encerrou" "CONS-09S 4a: sleep que falha em loop -> o guardiao encerra sozinho (nao gira ate o timeout)"
assert_eq "$(/usr/bin/grep -c 'rotacao' "$rot_err")" "1" "CONS-09S 4a: encerra com aviso de guarda de rotacao"

printf '3900\n' > "$SANDBOX/pids_hi"
env -u MANTER_ONESHOT MANTER_INTERVAL=5 MANTER_PIDS_CURRENT_FILE="$SANDBOX/pids_hi" MANTER_PIDS_LIMIT=4000 \
  MANTER_BAT_CAPACITY_FILE=/nonexistent timeout 10 bash "$DIR/bin/guardiao.sh" >/dev/null 2>&1; hi_rc=$?
assert_eq "$([ "$hi_rc" != "0" ] && [ "$hi_rc" != "124" ] && echo recusou || echo subiu)" "recusou" "CONS-09S 4b: sob escassez de processos (97%) o guardiao recusa o arranque"
assert_eq "$([ -e "$(ml_state_dir)/guardian.armed" ] && echo armado || echo nao_armado)" "nao_armado" "CONS-09S 4b: recusado nao grava o flag armed"

# pai morto: o guardiao reparentado (ppid muda) encerra em um ciclo
# o pai vive ~3 s (o guardiao registra o pai certo) e morre; o guardiao deve sair no ciclo seguinte
PAI_OUT="$SANDBOX/pai.out"
env -u MANTER_ONESHOT MANTER_INTERVAL=1 MANTER_BAT_CAPACITY_FILE=/nonexistent \
  bash -c 'bash "'"$DIR"'/bin/guardiao.sh" >/dev/null 2>&1 & echo $!; sleep 3' > "$PAI_OUT" 2>/dev/null &
sleep 1
pai_pid="$(head -n1 "$PAI_OUT")"
meio="$(kill -0 "$pai_pid" 2>/dev/null && echo vivo || echo morto)"
sleep 4.5
fim="$(kill -0 "$pai_pid" 2>/dev/null && ! /usr/bin/grep -q '^State:.*Z' "/proc/$pai_pid/status" 2>/dev/null && echo vivo || echo morto)"
assert_eq "$meio" "vivo" "CONS-09S 4c: com o pai vivo o guardiao segue rodando"
assert_eq "$fim" "morto" "CONS-09S 4c: pai morto -> guardiao encerra sozinho no ciclo seguinte"

# teto declarado: processos externos por ciclo (medido com strace, nao estimado)
ST_OUT="$SANDBOX/st.out"
env -u MANTER_ONESHOT MANTER_INTERVAL=1 MANTER_BAT_CAPACITY_FILE=/nonexistent MANTER_AC_ONLINE_FILE=/nonexistent \
  timeout 8 strace -f -e trace=execve -o "$ST_OUT" bash "$DIR/bin/guardiao.sh" >/dev/null 2>&1 &
ST_PID=$!; sleep 4.5; kill -TERM "$ST_PID" 2>/dev/null; wait "$ST_PID" 2>/dev/null
ciclos_exec="$(/usr/bin/grep -c 'execve("[^"]*sleep"' "$ST_OUT" 2>/dev/null || true)"
total_exec="$(/usr/bin/grep -c 'execve(' "$ST_OUT" 2>/dev/null || true)"
fora_sleep=$(( ${total_exec:-0} - ${ciclos_exec:-0} ))
printf '  [4-teto] execve total=%s, sleep (1 por ciclo)=%s, fora do sleep=%s (arranque/saida, fixo)\n' "$total_exec" "$ciclos_exec" "$fora_sleep"
assert_eq "$([ "${ciclos_exec:-0}" -ge 1 ] && [ "$fora_sleep" -le 5 ] && echo limitado || echo estourou)" "limitado" "CONS-09S 4d: laco cria so o sleep externo por ciclo; o resto e arranque/saida fixos (teto declarado)"

echo "---"
[ "$FAILS" -eq 0 ] && echo "TODOS OS TESTES PASSARAM" || { echo "$FAILS FALHA(S)"; exit 1; }
