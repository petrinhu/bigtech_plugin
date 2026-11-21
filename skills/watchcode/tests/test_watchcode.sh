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

# --- D4: sourcing duplo tem que ser idempotente (achado da revisao adversarial) ---
d4_err="$(bash -c '. "'"$DIR"'/bin/lib.sh"; . "'"$DIR"'/bin/lib.sh"' 2>&1 1>/dev/null)"
if [ -z "$d4_err" ]; then r=limpo; else r=erro; fi
assert_eq "$r" "limpo" "D4: sourcing duplo de lib.sh nao emite erro no stderr (obtido: '$d4_err')"

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

# --- Task 2: deteccao (redesenho do transporte, 01/09/2026) ---
# O transporte antigo ($(comando)|grep|sed sobre uma JANELA de tempo, um
# wc_detect_<sensor> por sensor) morreu; a INTELIGENCIA de cada sensor (os
# mesmos padroes, mesmos casos de teste) migrou para wc_parse_<sensor>, que
# le UMA linha de journalctl -o json por vez. Paridade de deteccao: para
# cada assert de deteccao de antes existe aqui um equivalente que roda a
# MESMA entrada e cobra o MESMO veredicto (secao 9.2 da spec).
: > "$(wc_findings_file)"
line_cd1='{"__CURSOR":"c1","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_SIGNAL":"6","COREDUMP_EXE":"/opt/exemplo/Projects/loucura_c_asm/build/bin/libcore_consumer","COREDUMP_TIMESTAMP":"1784454486651229"}'
line_cd2='{"__CURSOR":"c2","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_SIGNAL":"11","COREDUMP_EXE":"/var/tmp/aud_sec_probes/probe_alloc","COREDUMP_TIMESTAMP":"1784454635763262"}'
wc_parse_coredump "$line_cd1"
wc_parse_coredump "$line_cd2"
got_cd="$(jq -c 'select(.kind=="coredump")' "$(wc_findings_file)" | jq -s -c .)"
exp_cd='[{"kind":"coredump","ts":1784454486,"sig":6,"exe":"/opt/exemplo/Projects/loucura_c_asm/build/bin/libcore_consumer"},{"kind":"coredump","ts":1784454635,"sig":11,"exe":"/var/tmp/aud_sec_probes/probe_alloc"}]'
assert_eq "$got_cd" "$exp_cd" "wc_parse_coredump: paridade com wc_detect_coredumps de antes (ts/sig/exe)"

: > "$(wc_findings_file)"
line_oom='{"__CURSOR":"c3","_TRANSPORT":"kernel","MESSAGE":"Memory cgroup out of memory: Killed process 917642 (python) total-vm:20400964kB, anon-rss:8356648kB"}'
wc_parse_oom "$line_oom"
assert_eq "$(jq -r '.pid + "\t" + .comm' "$(wc_findings_file)")" "$(printf '917642\tpython')" "wc_parse_oom: paridade com wc_detect_oom de antes (pid+comm)"

# --- Task 2b: sensor systemd-oomd ---
: > "$(wc_findings_file)"
line_oomd1='{"_SYSTEMD_UNIT":"systemd-oomd.service","MESSAGE":"Killed /user.slice/user-1000.slice/user@1000.service/app.slice/app-cc1plus.scope due to memory pressure for /user.slice/user-1000.slice/user@1000.service being 99.98% > 50.00% for > 20s with reclaim activity"}'
line_oomd2='{"_SYSTEMD_UNIT":"systemd-oomd.service","MESSAGE":"Considered /user.slice/user-1000.slice/user@1000.service/app.slice/app-firefox.scope"}'
wc_parse_oomd "$line_oomd1"
wc_parse_oomd "$line_oomd2"
assert_eq "$(jq -r '.cgroup' "$(wc_findings_file)")" "/user.slice/user-1000.slice/user_1000.service/app.slice/app-cc1plus.scope" "wc_parse_oomd so pega linha Killed (Considered e ruido, ignorado)"
assert_eq "$(_wc_comm_from_cgroup '/user.slice/user-1000.slice/user@1000.service/app.slice/app-cc1plus.scope')" "cc1plus" "comm extraido do cgroup (prefixo app- e sufixo .scope removidos)"
assert_eq "$(_wc_comm_from_cgroup '/user.slice/some-opaque.slice')" "some-opaque" "comm extraido de cgroup sem padrao app-/run- reconhecido (best-effort)"

# --- Task 2c: sensor VRAM/GPU ---
: > "$(wc_findings_file)"
for l in \
  '{"_TRANSPORT":"kernel","MESSAGE":"NVRM: Xid (PCI:0000:01:00): 31, pid=4242, name=cc1plus, MMU Fault: ch 8"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"NVRM: GPU 0000:01:00: NVLink is not supported"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"NVRM: VM: nv_vm_malloc_pages: failed to allocate contiguous memory: Out of memory [NV_ERR_NO_MEMORY]"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"NVRM: Xid (PCI:0000:01:00): 99, pid=555, name=someapp, harmless code fora da lista"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"amdgpu 0000:03:00.0: amdgpu: GPU reset begin!"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"amdgpu 0000:03:00.0: ring gfx_0.0.0 timeout, signaled seq=100, emitted seq=102"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"amdgpu 0000:03:00.0: [gfxhub] VM_L2_PROTECTION_FAULT status 0x0"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"something totally unrelated line about wifi"}' \
  ; do wc_parse_vram "$l"; done
got_vram="$(jq -r '[.code,(.pid//""),(.comm//"")] | join(":")' "$(wc_findings_file)" | tr '\n' '|')"
exp_vram="Xid:31:4242:cc1plus|NV_ERR_NO_MEMORY::|amdgpu:GPU reset::|amdgpu:ring timeout::|amdgpu:VM_L2_PROTECTION_FAULT::|"
assert_eq "$got_vram" "$exp_vram" "wc_parse_vram: paridade (NVIDIA Xid/NV_ERR_NO_MEMORY + AMD reset/timeout/VM_L2; Xid:99 e wifi = ruido, ignorados)"
assert_eq "$(wc -l < "$(wc_findings_file)" | tr -d ' ')" "5" "wc_parse_vram nao gera achado para Xid fora da lista nem ruido generico"

# --- Task 2d: sensor de disco/IO ---
: > "$(wc_findings_file)"
for l in \
  '{"_TRANSPORT":"kernel","MESSAGE":"EXT4-fs error (device sda1): ext4_find_entry:1436: inode #131074: comm cc1plus: reading directory lblock 0"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"Buffer I/O error on dev sda1, logical block 12345, async page read"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"BTRFS warning (device sda1): csum failed root 5 ino 300 off 0 csum 0x12345678 expected csum 0x87654321"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"EXT4-fs (sda1): Remounting filesystem read-only"}' \
  '{"_TRANSPORT":"kernel","MESSAGE":"random unrelated wifi message"}' \
  ; do wc_parse_disk "$l"; done
assert_eq "$(wc -l < "$(wc_findings_file)" | tr -d ' ')" "5" "wc_parse_disk pega as 5 linhas de falha real (wifi generico e ruido, ignorado)"
jq -r '.line' "$(wc_findings_file)" | grep -qx "No space left on device" && r=sim || r=nao
assert_eq "$r" "sim" "wc_parse_disk casa ENOSPC"

# --- Task 3: baseline e classificacao ---
cat > "$WATCHCODE_BASELINE_FILE" <<'BL'
# baseline de teste
/var/tmp/*_probes/*
/var/tmp/glsym_review/*
*death*test*
BL
wc_baseline_match "/var/tmp/aud_sec_probes/probe_alloc" && r=sim || r=nao
assert_eq "$r" "sim" "baseline casa sonda de sanitizer"
wc_baseline_match "/opt/exemplo/Projects/loucura_c_asm/build/bin/libcore_consumer" && r=sim || r=nao
assert_eq "$r" "nao" "baseline NAO casa binario de produto"

SCOPE="/opt/exemplo/Projects/appatual"; PROOT="/opt/exemplo/Projects"
assert_eq "$(wc_classify_exe "$SCOPE/build/bin/app" "$SCOPE" "$PROOT")" "this" "classifica this"
assert_eq "$(wc_classify_exe "$PROOT/outro/build/bin/x" "$SCOPE" "$PROOT")" "other:outro" "classifica other:<proj>"
assert_eq "$(wc_classify_exe "/usr/bin/kwin_wayland" "$SCOPE" "$PROOT")" "system" "classifica system"

mkdir -p "$SANDBOX/scope/build"; : > "$SANDBOX/scope/build/meuapp"
assert_eq "$(wc_classify_oom meuapp "$SANDBOX/scope")" "this" "OOM comm no scope = this"
assert_eq "$(wc_classify_oom python "$SANDBOX/scope")" "system" "OOM comm fora do scope = system"

# --- Task 3b: classe "build" (OOM que mata toolchain de compilacao) ---
assert_eq "$(wc_classify_oom cc1plus "$SANDBOX/scope")" "build" "OOM comm de toolchain (cc1plus) fora do scope = build, nao system"
assert_eq "$(wc_classify_oom ld "$SANDBOX/scope")" "build" "OOM comm de toolchain (ld) = build"
assert_eq "$(wc_classify_oom rustc "$SANDBOX/scope")" "build" "OOM comm de toolchain (rustc) = build"
assert_eq "$(wc_classify_oom firefox "$SANDBOX/scope")" "system" "OOM comm que NAO e toolchain nem esta no scope = system (caso negativo)"
: > "$SANDBOX/scope/build/cc1plus"
assert_eq "$(wc_classify_oom cc1plus "$SANDBOX/scope")" "this" "ordem de prioridade: this vence build quando o comm TAMBEM esta no scope"
rm -f "$SANDBOX/scope/build/cc1plus"

# --- Task 3c: bundlers JS + compiladores versionados (achado do review adversarial) ---
for c in vite webpack esbuild rollup babel swc parcel turbo npm yarn pnpm bun deno next-server webpack-cli; do
  assert_eq "$(wc_classify_oom "$c" "$SANDBOX/scope")" "build" "OOM comm de bundler/gerenciador JS ($c) = build"
done
for c in gcc-13 g++-14 clang-17 clang++-15; do
  assert_eq "$(wc_classify_oom "$c" "$SANDBOX/scope")" "build" "OOM comm de compilador versionado ($c) = build (via padrao de sufixo)"
done
# casos negativos que o padrao de sufixo numerico NAO pode passar a casar
assert_eq "$(wc_classify_oom systemd "$SANDBOX/scope")" "system" "systemd continua NAO casando (caso negativo pre-existente)"
assert_eq "$(wc_classify_oom world "$SANDBOX/scope")" "system" "world continua NAO casando (caso negativo pre-existente)"
assert_eq "$(wc_classify_oom gold "$SANDBOX/scope")" "system" "gold continua NAO casando (caso negativo pre-existente)"
assert_eq "$(wc_classify_oom clang-tidy-14 "$SANDBOX/scope")" "system" "clang-tidy-14 NAO casa o padrao clang-[0-9]* (letra logo apos o hifen)"
assert_eq "$(wc_classify_oom noded "$SANDBOX/scope")" "system" "noded (substring de node) continua NAO casando"
assert_eq "$(wc_classify_oom systemdx "$SANDBOX/scope")" "system" "systemdx (substring de systemd) NAO casa"
assert_eq "$(wc_classify_oom goldx "$SANDBOX/scope")" "system" "goldx (substring de gold) NAO casa"

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

# --- Hardening: fronteira de projeto-irmao (prefixo compartilhado) ---
assert_eq "$(wc_classify_exe /proj/appatual-evil/x /proj/appatual /proj)" "other:appatual-evil" "irmao com prefixo compartilhado NAO e this"
assert_eq "$(wc_classify_exe /proj/appatual/build/x /proj/appatual /proj)" "this" "mesmo projeto continua this"

# =====================================================================
# TESTES DO TRANSPORTE NOVO (fluxo continuo, SPEC-transporte-watchcode.md)
# =====================================================================
# Helper: roda o daemon em ONESHOT com um WATCHCODE_STREAM_CMD movido a
# plano (fixture_stream_cmd.sh); devolve so depois do daemon sair.
run_daemon_stream() {
  # <plan_file> <log_file> <count_file> [env extras...]
  local plan="$1" log="$2" cnt="$3"; shift 3
  : > "$log"; : > "$cnt"
  env WATCHCODE_ONESHOT=1 \
      WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh" \
      WC_TEST_STREAM_PLAN_FILE="$plan" \
      WC_TEST_STREAM_LOG="$log" \
      WC_TEST_STREAM_COUNT_FILE="$cnt" \
      "$@" \
      bash "$DIR/bin/watchcode_daemon.sh"
}

# --- Task 5: daemon consumindo o fluxo continuo (mistura os 5 sensores +
# baseline, equivalente de fluxo do antigo Task 5/5b baseado em jq/janela) ---
T5_DIR="$SANDBOX/t5"; mkdir -p "$T5_DIR"
cat > "$T5_DIR/mix.jsonl" <<JSONL
{"__CURSOR":"t5-1","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_SIGNAL":"11","COREDUMP_EXE":"/proj/appatual/build/bin/app","COREDUMP_TIMESTAMP":"1784454486651229"}
{"__CURSOR":"t5-2","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_SIGNAL":"6","COREDUMP_EXE":"/var/tmp/aud_sec_probes/probe_alloc","COREDUMP_TIMESTAMP":"1784454635763262"}
{"__CURSOR":"t5-3","_TRANSPORT":"kernel","MESSAGE":"Killed process 917642 (python) total-vm:1kB"}
{"__CURSOR":"t5-4","_SYSTEMD_UNIT":"systemd-oomd.service","MESSAGE":"Killed /user.slice/user-1000.slice/user@1000.service/app.slice/app-cc1plus.scope due to memory pressure"}
{"__CURSOR":"t5-5","_SYSTEMD_UNIT":"systemd-oomd.service","MESSAGE":"Killed /user.slice/user-1000.slice/user@1000.service/app.slice/app-tool_death_test.scope due to memory pressure"}
{"__CURSOR":"t5-6","_TRANSPORT":"kernel","MESSAGE":"NVRM: Xid (PCI:0000:01:00): 31, pid=4242, name=cc1plus, MMU Fault: ch 8"}
{"__CURSOR":"t5-7","_TRANSPORT":"kernel","MESSAGE":"NVRM: Xid (PCI:0000:02:00): 43, pid=555, name=death_test_probe, MMU Fault: ch 2"}
{"__CURSOR":"t5-8","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}
{"__CURSOR":"t5-9","_TRANSPORT":"kernel","MESSAGE":"BTRFS warning (device sda1): csum failed noise_csum_failed_probe"}
JSONL
printf '%s\n' "$T5_DIR/mix.jsonl" > "$T5_DIR/plan.txt"
printf '*noise_csum_failed_probe*\n' >> "$WATCHCODE_BASELINE_FILE"
: > "$(wc_findings_file)"
run_daemon_stream "$T5_DIR/plan.txt" "$T5_DIR/log.txt" "$T5_DIR/count.txt" >/dev/null 2>&1
n5="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n5" "5" "daemon (fluxo) com todos os sensores: coredump(this,baseline-filtrado)+oom(kernel)+oom(oomd,baseline-filtrado)+vram(baseline-filtrado)+disk(baseline-filtrado) = 5"
kinds5="$(jq -r '.kind' "$(wc_findings_file)" | sort | tr '\n' ',')"
assert_eq "$kinds5" "coredump,disk,oom,oom,vram," "daemon (fluxo) anexa coredump+2xoom(kernel+oomd)+vram+disk; 2os itens de oomd/vram/disk ficam de fora por baseline"
srcs5="$(jq -r 'select(.kind=="oom") | .src' "$(wc_findings_file)" | sort | tr '\n' ',')"
assert_eq "$srcs5" "kernel,oomd," "as duas entradas oom distinguem src kernel vs oomd"
[ -f "$(wc_state_dir)/daemon.armed" ] && armed=nao_removeu || armed=ok
assert_eq "$armed" "ok" "daemon (fluxo) remove flag armed ao sair"
[ -p "$(wc_state_dir)/sleep.fifo" ] && fifo_orfao=nao_removeu || fifo_orfao=ok
assert_eq "$fifo_orfao" "ok" "daemon (fluxo) remove sleep.fifo ao sair (trap nao deixa fifo orfao)"

# =====================================================================
# TESTE 1 (secao 9.3): CURA DO DEFEITO MEDIDO -- o gate de estreia do
# redesenho inteiro. Achado documentado do transporte antigo (janela
# devida + teto por sensor): 20 coredumps distintos, so 14 apareciam, o
# item de indice 14 (o 15o) nunca aparecia mesmo apos 2 ciclos. O fluxo
# novo nao tem teto nem janela: cada entrada e entregue exatamente uma vez.
# ---------------------------------------------------------------------
T1_DIR="$SANDBOX/t1"; mkdir -p "$T1_DIR"
python3 - "$T1_DIR/cores20.jsonl" <<'PYEOF'
import sys
out = open(sys.argv[1], "w")
for i in range(20):
    out.write(
        '{"__CURSOR":"cur%d","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1",'
        '"COREDUMP_SIGNAL":"11","COREDUMP_EXE":"/proj/app%d",'
        '"COREDUMP_TIMESTAMP":"%d"}\n' % (i, i, 1784454486651229 + i)
    )
PYEOF
printf '%s\n' "$T1_DIR/cores20.jsonl" > "$T1_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T1_DIR/plan.txt" "$T1_DIR/log.txt" "$T1_DIR/count.txt" >/dev/null 2>&1
n_total="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
n_unicos="$(jq -r '.exe' "$(wc_findings_file)" | sort -u | wc -l | tr -d ' ')"
tem_item15="$(jq -r '.exe' "$(wc_findings_file)" | grep -qx '/proj/app14' && echo sim || echo nao)"
printf '  [ESTREIA] fluxo novo com 20 coredumps distintos: total=%s unicos=%s item-15(index14)-apareceu=%s (referencia do transporte antigo, medida: total=28 unicos=14 item-15=nao apos 2 ciclos)\n' \
  "$n_total" "$n_unicos" "$tem_item15"
assert_eq "$n_total" "20" "ESTREIA: fluxo novo entrega os 20 coredumps (transporte antigo entregava 28 com reanuncio, so 14 unicos)"
assert_eq "$n_unicos" "20" "ESTREIA: os 20 sao unicos (sem reanuncio duplicado)"
assert_eq "$tem_item15" "sim" "ESTREIA: item 15 (indice 14), que o transporte antigo NUNCA entregava, aparece"

# Sabotagem de estreia: reintroduzir um teto artificial tem que
# fazer ESTE MESMO teste reprovar -- prova que o gate mede o comportamento
# real, nao um numero fixo. Sabota uma COPIA de watchcode_daemon.sh fora da
# arvore (nunca o arquivo rastreado, nunca in-place).
D3S_DIR="$SANDBOX/d3_stream_sabotage"; mkdir -p "$D3S_DIR"
cp "$DIR/bin/watchcode_daemon.sh" "$D3S_DIR/watchcode_daemon.sh"
cp "$DIR/bin/lib.sh" "$D3S_DIR/lib.sh"
sed -i 's#\. "\$DIR/lib\.sh"#. "'"$D3S_DIR"'/lib.sh"#' "$D3S_DIR/watchcode_daemon.sh"
# injeta um teto de 14 achados de coredump na copia sabotada (mesmo numero
# do teto antigo WC_CAP_COREDUMP), direto no laco de dispatch da copia.
python3 - "$D3S_DIR/lib.sh" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p).read()
marker = "wc_baseline_match \"$exe\" && return 0\n  wc_append_coredump"
assert marker in s, "marcador nao encontrado na copia (sabotagem invalida)"
sabotado = (
    'WC_SABOTAGE_CD_COUNT="${WC_SABOTAGE_CD_COUNT:-0}"\n'
    '  WC_SABOTAGE_CD_COUNT=$((WC_SABOTAGE_CD_COUNT + 1))\n'
    '  [ "$WC_SABOTAGE_CD_COUNT" -gt 14 ] && return 0\n'
    '  wc_baseline_match "$exe" && return 0\n  wc_append_coredump'
)
open(p, "w").write(s.replace(marker, sabotado, 1))
PYEOF
: > "$(wc_findings_file)"
env WATCHCODE_ONESHOT=1 \
    WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh" \
    WC_TEST_STREAM_PLAN_FILE="$T1_DIR/plan.txt" \
    WC_TEST_STREAM_LOG="$D3S_DIR/log.txt" \
    WC_TEST_STREAM_COUNT_FILE="$D3S_DIR/count.txt" \
    bash "$D3S_DIR/watchcode_daemon.sh" >/dev/null 2>&1
n_sabotado="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
if [ "$n_sabotado" = "20" ]; then r_sab=passou; else r_sab=pegou; fi
printf '  [D3-stream] copia sabotada com teto artificial de 14: total=%s (gate=%s)\n' "$n_sabotado" "$r_sab"
assert_eq "$r_sab" "pegou" "D3-stream: sabotagem de estreia -- reintroduzir teto artificial de 14 FAZ o teste da cura do defeito reprovar"
: > "$(wc_findings_file)"

# --- TESTE 2 (secao 9.3): passthrough de escape ---
# MESSAGE com aspa real, barra invertida real, TAB real e multibyte (ç/ú):
# gerada por python (json.dumps) para nao depender de escapar-o-escape a
# mao em shell -- exp_line vem do MESMO valor original (nao redigitado),
# entao a asssercao prova passthrough de verdade, nao coincidencia de digitacao.
T2_DIR="$SANDBOX/t2"; mkdir -p "$T2_DIR"
python3 - "$T2_DIR/esc.jsonl" "$T2_DIR/expected.txt" <<'PYEOF'
import json, sys
msg = 'No space left on device: path "weird", back\\slash, tab\tthere, açúcar'
with open(sys.argv[1], "w") as f:
    # journalctl -o json nao usa espaco depois de ":"/"," (formato compacto,
    # confirmado na maquina de desenvolvimento); json.dumps por padrao usa ": "/", ", que
    # wc_json_str (regex sem espaco, igual ao formato real) nao casaria.
    f.write(json.dumps({"__CURSOR": "t2-1", "_TRANSPORT": "kernel", "MESSAGE": msg},
                        separators=(",", ":")) + "\n")
with open(sys.argv[2], "w") as f:
    f.write(msg)
PYEOF
printf '%s\n' "$T2_DIR/esc.jsonl" > "$T2_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T2_DIR/plan.txt" "$T2_DIR/log.txt" "$T2_DIR/count.txt" >/dev/null 2>&1
jq -e . "$(wc_findings_file)" >/dev/null 2>&1 && r=valido || r=invalido
assert_eq "$r" "valido" "TESTE 2: passthrough de escape -- findings.jsonl inteiro passa jq -e . (JSON valido)"
got_line="$(jq -j '.line' "$(wc_findings_file)")"
exp_line="$(cat "$T2_DIR/expected.txt")"
assert_eq "$got_line" "$exp_line" "TESTE 2: valor decodificado bate byte a byte com o texto original (aspas/barra/tab/multibyte sobrevivem ao passthrough)"

# --- TESTE 3 (secao 9.3): parser tolerante a ordem dos campos ---
T3_DIR="$SANDBOX/t3"; mkdir -p "$T3_DIR"
printf '%s\n' \
  '{"COREDUMP_TIMESTAMP":"1784454486651229","COREDUMP_SIGNAL":"11","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_EXE":"/proj/ordemA","__CURSOR":"t3-1"}' \
  '{"__CURSOR":"t3-2","COREDUMP_EXE":"/proj/ordemB","MESSAGE_ID":"fc2e22bc6ee647b6b90729ab34a250b1","COREDUMP_SIGNAL":"11","COREDUMP_TIMESTAMP":"1784454486651229"}' \
  > "$T3_DIR/ordem.jsonl"
printf '%s\n' "$T3_DIR/ordem.jsonl" > "$T3_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T3_DIR/plan.txt" "$T3_DIR/log.txt" "$T3_DIR/count.txt" >/dev/null 2>&1
got_t3="$(jq -c '{sig,ts}' "$(wc_findings_file)" | sort -u | wc -l | tr -d ' ')"
assert_eq "$got_t3" "1" "TESTE 3: a MESMA entrada com campos em 2 ordens diferentes produz o MESMO achado (sig/ts identicos)"
n_t3="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n_t3" "2" "TESTE 3: as 2 entradas (ordens diferentes) sao processadas, nenhuma se perde por causa da ordem"

# --- TESTE 4 (secao 9.3): formas nao-parseaveis (controle negativo das 3
# excecoes do -o json: campo >4096B vira null; campo repetido/nao-UTF8 vira
# array) nao produzem achado falso nem quebram o laco ---
T4_DIR="$SANDBOX/t4"; mkdir -p "$T4_DIR"
printf '%s\n' \
  '{"__CURSOR":"t4-1","_TRANSPORT":"kernel","MESSAGE":null}' \
  '{"__CURSOR":"t4-2","_TRANSPORT":"kernel","MESSAGE":[75,105,108,108,101,100]}' \
  '{"__CURSOR":"t4-3","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' \
  > "$T4_DIR/naoparse.jsonl"
printf '%s\n' "$T4_DIR/naoparse.jsonl" > "$T4_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T4_DIR/plan.txt" "$T4_DIR/log.txt" "$T4_DIR/count.txt" >/dev/null 2>&1
rc_run=$?
assert_eq "$rc_run" "0" "TESTE 4: o daemon NAO quebra (sai limpo) diante de MESSAGE null e MESSAGE array"
kinds4="$(jq -r '.kind' "$(wc_findings_file)" | sort | tr '\n' ',')"
assert_eq "$kinds4" "disk,unparseable," "TESTE 4: MESSAGE null nao gera achado (silenciosamente ausente, honesto -- o proprio journal declinou o campo); MESSAGE array vira achado 'unparseable' visivel (C1); a 3a linha legivel continua detectada normalmente"

# --- TESTE 5 (secao 9.3): EOF -> reinicio com cursor ---
T5R_DIR="$SANDBOX/t5r"; mkdir -p "$T5R_DIR"
printf '%s\n' '{"__CURSOR":"t5r-cursorA","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' > "$T5R_DIR/a.jsonl"
printf '%s\n' '{"__CURSOR":"t5r-cursorB","_TRANSPORT":"kernel","MESSAGE":"Buffer I/O error on dev sda1"}' > "$T5R_DIR/b.jsonl"
printf '%s\n%s\n' "$T5R_DIR/a.jsonl" "$T5R_DIR/b.jsonl" > "$T5R_DIR/plan.txt"
rm -f "$(wc_state_dir)/stream_cursor"
: > "$(wc_findings_file)"
# Este teste precisa dos DOIS opens (A morre -> restart -> B), entao roda
# fora do modo ONESHOT (que para no primeiro EOF); usa WATCHCODE_INTERVAL
# curto e mata o daemon depois que o segundo arquivo for consumido.
(
  export WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh"
  export WC_TEST_STREAM_PLAN_FILE="$T5R_DIR/plan.txt"
  export WC_TEST_STREAM_LOG="$T5R_DIR/log.txt"
  export WC_TEST_STREAM_COUNT_FILE="$T5R_DIR/count.txt"
  export WATCHCODE_INTERVAL=1
  : > "$T5R_DIR/log.txt"; : > "$T5R_DIR/count.txt"
  timeout 5 bash "$DIR/bin/watchcode_daemon.sh" >/dev/null 2>&1
)
n_t5r="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n_t5r" "2" "TESTE 5: achados de A e B, sem duplicata (EOF de A -> reinicio -> B)"
n_invoc_t5r="$(wc -l < "$T5R_DIR/log.txt" | tr -d ' ')"
[ "$n_invoc_t5r" -ge 2 ] && r=sim || r=nao
assert_eq "$r" "sim" "TESTE 5: houve pelo menos 2 aberturas do fluxo (A e depois B)"
segunda_pos="$(sed -n '2p' "$T5R_DIR/log.txt" | sed -n 's/.*pos=//p')"
case "$segunda_pos" in
  --after-cursor=t5r-cursorA) r=sim ;;
  *) r=nao ;;
esac
assert_eq "$r" "sim" "TESTE 5: o segundo open recebeu --after-cursor=<cursor real de A> (sentinela gravou: '$segunda_pos')"

# --- TESTE 6 (secao 9.3): cursor rejeitado -> fallback --since ---
T6_DIR="$SANDBOX/t6"; mkdir -p "$T6_DIR"
printf '%s\n' '{"__CURSOR":"t6-cursorA","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' > "$T6_DIR/a.jsonl"
printf '%s\n%s\n%s\n' "$T6_DIR/a.jsonl" REJECT_CURSOR "$T6_DIR/a.jsonl" > "$T6_DIR/plan.txt"
rm -f "$(wc_state_dir)/stream_cursor"
: > "$(wc_findings_file)"
(
  export WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh"
  export WC_TEST_STREAM_PLAN_FILE="$T6_DIR/plan.txt"
  export WC_TEST_STREAM_LOG="$T6_DIR/log.txt"
  export WC_TEST_STREAM_COUNT_FILE="$T6_DIR/count.txt"
  export WATCHCODE_INTERVAL=4
  : > "$T6_DIR/log.txt"; : > "$T6_DIR/count.txt"
  timeout 5 bash "$DIR/bin/watchcode_daemon.sh" >/dev/null 2>&1
)
terceira_pos="$(sed -n '3p' "$T6_DIR/log.txt" | sed -n 's/.*pos=//p')"
case "$terceira_pos" in
  --since=@*) r=sim ;;
  *) r=nao ;;
esac
assert_eq "$r" "sim" "TESTE 6: 2o reinicio (apos morte rapida em cima de cursor) veio com --since=@... (sentinela: '$terceira_pos')"

# --- TESTE 7 (secao 9.3): tempestade de reinicio -> guarda de rotacao para o daemon ---
T7_DIR="$SANDBOX/t7"; mkdir -p "$T7_DIR"
printf 'DIE\nDIE\nDIE\nDIE\nDIE\n' > "$T7_DIR/plan.txt"
rm -f "$(wc_state_dir)/stream_cursor" "$(wc_state_dir)/spin_guard"
: > "$(wc_findings_file)"
(
  export WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh"
  export WC_TEST_STREAM_PLAN_FILE="$T7_DIR/plan.txt"
  export WC_TEST_STREAM_LOG="$T7_DIR/log.txt"
  export WC_TEST_STREAM_COUNT_FILE="$T7_DIR/count.txt"
  export WATCHCODE_INTERVAL=4
  : > "$T7_DIR/log.txt"; : > "$T7_DIR/count.txt"
  timeout 10 bash "$DIR/bin/watchcode_daemon.sh" >/dev/null 2>&1
)
spin_content="$(cat "$(wc_state_dir)/spin_guard" 2>/dev/null || true)"
case "$spin_content" in stopped*) r=sim ;; *) r=nao ;; esac
assert_eq "$r" "sim" "TESTE 7: daemon encerra apos reinicios rapidos consecutivos, spin_guard explica o motivo (conteudo: '$spin_content')"

# --- TESTE 8 (secao 9.3): crit nao cega e nao forka ---
# 8a: stream JA aberto, pids em crit -> deteccao de journal CONTINUA (
# inversao consciente do D0-b antigo: "some" o pulo dos sensores).
T8A_DIR="$SANDBOX/t8a"; mkdir -p "$T8A_DIR"
printf '%s\n' '{"__CURSOR":"t8a-1","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' > "$T8A_DIR/linhas.jsonl"
printf '%s\n' "$T8A_DIR/linhas.jsonl" > "$T8A_DIR/plan.txt"
: > "$(wc_findings_file)"
(
  PIDS_D8_FILE="$T8A_DIR/pids.cur"
  printf '3300\n' > "$PIDS_D8_FILE"
  run_daemon_stream "$T8A_DIR/plan.txt" "$T8A_DIR/log.txt" "$T8A_DIR/count.txt" \
    env WATCHCODE_PIDS_CURRENT_FILE="$PIDS_D8_FILE" WATCHCODE_PIDS_LIMIT=4000 \
    >/dev/null 2>&1
)
kinds8a="$(jq -r '.kind' "$(wc_findings_file)" | sort | tr '\n' ',')"
assert_eq "$kinds8a" "disk,pids," "TESTE 8a: com pids JA critico no arranque, o achado de disco (journal) E gravado normalmente (deteccao continua sob crit)"

# 8b: stream MORTO + crit -> reinicio adiado ate o rearme (sentinela prova
# que o open NAO rodou durante o crit).
T8B_DIR="$SANDBOX/t8b"; mkdir -p "$T8B_DIR"
printf 'DIE\n%s\n' "$T8A_DIR/linhas.jsonl" > "$T8B_DIR/plan.txt"
rm -f "$(wc_state_dir)/stream_cursor" "$(wc_state_dir)/spin_guard"
: > "$(wc_findings_file)"
(
  PIDS_D8B_FILE="$T8B_DIR/pids.cur"
  printf '3300\n' > "$PIDS_D8B_FILE"
  export WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh"
  export WC_TEST_STREAM_PLAN_FILE="$T8B_DIR/plan.txt"
  export WC_TEST_STREAM_LOG="$T8B_DIR/log.txt"
  export WC_TEST_STREAM_COUNT_FILE="$T8B_DIR/count.txt"
  export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_D8B_FILE"
  export WATCHCODE_PIDS_LIMIT=4000
  export WATCHCODE_INTERVAL=2
  : > "$T8B_DIR/log.txt"; : > "$T8B_DIR/count.txt"
  timeout 6 bash "$DIR/bin/watchcode_daemon.sh" >/dev/null 2>&1
)
n_invoc_t8b="$(wc -l < "$T8B_DIR/log.txt" | tr -d ' ')"
assert_eq "$n_invoc_t8b" "1" "TESTE 8b: sob crit persistente (pids nunca sai de 3300/4000), so a 1a abertura (a inicial) roda -- o reinicio depois da morte NAO chega a abrir (sentinela: $n_invoc_t8b abertura(oes) registrada(s))"

# --- TESTE 9 (F1, achado da revisao adversarial 01/09/2026): fluxo que
# fecha SEM nova linha final apos a ultima entrada nao pode perder o
# registro. O `read` builtin (fato do manual do bash, medido na maquina de desenvolvimento)
# POPULA a variavel mesmo retornando rc=1 quando o produtor termina logo
# apos escrever um JSON completo mas ANTES do '\n' -- essa e a 3a forma de
# descarte silencioso do parser (as outras duas, campo nulo e campo em
# array de bytes, sao o TESTE 4 acima).
T9_DIR="$SANDBOX/t9"; mkdir -p "$T9_DIR"
printf '%s' '{"__CURSOR":"t9-1","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' > "$T9_DIR/nonl.jsonl"
printf '%s\n' "$T9_DIR/nonl.jsonl" > "$T9_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T9_DIR/plan.txt" "$T9_DIR/log.txt" "$T9_DIR/count.txt" >/dev/null 2>&1
n_t9="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n_t9" "1" "TESTE 9 (F1): fixture de 1 linha JSON valida SEM '\\n' final (cenario exato do revisor) -- o achado nao some"
kinds_t9="$(jq -r '.kind' "$(wc_findings_file)" | tr '\n' ',')"
assert_eq "$kinds_t9" "disk," "TESTE 9 (F1): o achado recuperado e o disk esperado (No space left on device)"

# Sabotagem de estreia: reverter o conserto de F1 numa COPIA
# fora da arvore tem que fazer ESTE MESMO teste (9) reprovar -- prova que o
# teste mede o defeito real, nao um numero fixo. Nunca sabota o arquivo
# rastreado nem in-place.
D9S_DIR="$SANDBOX/d9_f1_sabotage"; mkdir -p "$D9S_DIR"
cp "$DIR/bin/watchcode_daemon.sh" "$D9S_DIR/watchcode_daemon.sh"
cp "$DIR/bin/lib.sh" "$D9S_DIR/lib.sh"
sed -i 's#\. "\$DIR/lib\.sh"#. "'"$D9S_DIR"'/lib.sh"#' "$D9S_DIR/watchcode_daemon.sh"
python3 - "$D9S_DIR/watchcode_daemon.sh" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p).read()
marker_start = "  # rc=1 (nao timeout): fim de fluxo."
marker_end = "  # EOF/erro: o filho do fluxo morreu.\n"
i = s.index(marker_start)
j = s.index(marker_end, i)
assert i != -1 and j != -1, "marcador do conserto F1 nao encontrado na copia (sabotagem invalida)"
sabotado = s[:i] + s[j:]
assert sabotado != s, "sabotagem nao mudou nada"
open(p, "w").write(sabotado)
PYEOF
: > "$(wc_findings_file)"
env WATCHCODE_ONESHOT=1 \
    WATCHCODE_STREAM_CMD="bash $DIR/tests/fixture_stream_cmd.sh" \
    WC_TEST_STREAM_PLAN_FILE="$T9_DIR/plan.txt" \
    WC_TEST_STREAM_LOG="$D9S_DIR/log.txt" \
    WC_TEST_STREAM_COUNT_FILE="$D9S_DIR/count.txt" \
    bash "$D9S_DIR/watchcode_daemon.sh" >/dev/null 2>&1
n_t9_sabotado="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
if [ "$n_t9_sabotado" = "1" ]; then r_t9_sab=passou; else r_t9_sab=pegou; fi
printf '  [D9-F1] copia com o conserto F1 revertido: achados=%s (gate=%s)\n' "$n_t9_sabotado" "$r_t9_sab"
assert_eq "$r_t9_sab" "pegou" "D9-F1: sabotagem de estreia -- reverter o conserto de F1 FAZ o teste 9 reprovar (achado some de novo)"
: > "$(wc_findings_file)"

# TESTE 9b (F1, um passo alem da fronteira): duas linhas onde SO A
# ULTIMA fica sem '\n' final -- a normal (com '\n') e a orfa (sem '\n')
# tem que ser despachadas as duas, nenhuma some e nenhuma duplica.
T9B_DIR="$SANDBOX/t9b"; mkdir -p "$T9B_DIR"
printf '%s\n%s' \
  '{"__CURSOR":"t9b-1","_TRANSPORT":"kernel","MESSAGE":"No space left on device"}' \
  '{"__CURSOR":"t9b-2","_TRANSPORT":"kernel","MESSAGE":"Buffer I/O error on dev sda1"}' \
  > "$T9B_DIR/duas.jsonl"
printf '%s\n' "$T9B_DIR/duas.jsonl" > "$T9B_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T9B_DIR/plan.txt" "$T9B_DIR/log.txt" "$T9B_DIR/count.txt" >/dev/null 2>&1
n_t9b="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$n_t9b" "2" "TESTE 9b (F1, fronteira): duas linhas, SO a ultima sem '\\n' final -- as duas chegam (nenhuma some, nenhuma duplica)"

# TESTE 9c (F1, fronteira): fluxo que fecha SEM escrever nada (linha
# vazia no plano) nao pode inventar achado nem quebrar o daemon -- prova
# que a guarda '[ -n "$line" ]' distingue "sobrou conteudo sem \n" de
# "nunca chegou nada".
T9C_DIR="$SANDBOX/t9c"; mkdir -p "$T9C_DIR"
printf '\n' > "$T9C_DIR/plan.txt"
: > "$(wc_findings_file)"
run_daemon_stream "$T9C_DIR/plan.txt" "$T9C_DIR/log.txt" "$T9C_DIR/count.txt" >/dev/null 2>&1
rc_t9c=$?
n_t9c="$(wc -l < "$(wc_findings_file)" | tr -d ' ')"
assert_eq "$rc_t9c" "0" "TESTE 9c (F1, fronteira): fluxo vazio (fecha sem escrever nada) nao quebra o daemon"
assert_eq "$n_t9c" "0" "TESTE 9c (F1, fronteira): fluxo vazio nao inventa achado nenhum"

unset WATCHCODE_PIDS_CURRENT_FILE WATCHCODE_PIDS_LIMIT
rm -f "$(wc_state_dir)/stream_cursor" "$(wc_state_dir)/spin_guard"
unset -f run_daemon_stream

# --- Pin: should_stop_daemon e estado ---
rm -f "$(wc_pin_file)"
wc_should_stop_daemon 0 && r=sim || r=nao
assert_eq "$r" "sim" "count=0 sem pin -> para daemon"
wc_should_stop_daemon 1 && r=sim || r=nao
assert_eq "$r" "nao" "count=1 -> nao para"
: > "$(wc_pin_file)"
wc_should_stop_daemon 0 && r=sim || r=nao
assert_eq "$r" "nao" "count=0 pinado -> NAO para"
wc_is_pinned && r=sim || r=nao
assert_eq "$r" "sim" "wc_is_pinned true com flag"
rm -f "$(wc_pin_file)"
wc_is_pinned && r=sim || r=nao
assert_eq "$r" "nao" "wc_is_pinned false sem flag"

# --- D1: sleep sem fifo (mkfifo/exec falham) cai pra sleep externo, e o
# sleep externo REALMENTE dorme (nao so "gira mais devagar"). Achado do
# usuário sobre a versao anterior deste teste: contar "voltas num teto de 2s"
# contra um numero redondo escolhido DEPOIS de ver o resultado nao prova
# nada -- com intervalo de 0,01s, ~150-200 voltas em 2s sao exatamente o
# ESPERADO (2s / 0,01s), nao rotacao livre, e o teto de 600 nao vinha de
# lugar nenhum. Critério certo (criterio definido ANTES de medir, deduzido do
# intervalo pedido): o MESMO que wc_spin_guard_tick usa pra separar
# "dormiu" de "girou" -- elapsed decorrido de CADA volta >= intervalo/2.
D1_DIR="$SANDBOX/d1_readonly"
mkdir -p "$D1_DIR"
chmod 555 "$D1_DIR"
D1_INTERVALO=2
D1_MIN_OK=$(( D1_INTERVALO / 2 ))
d1_out_file="$SANDBOX/d1_out"
(
  export WATCHCODE_STATE_DIR="$D1_DIR"
  wc_daemon_sleep_init 2>/dev/null
  total=0
  ok_count=0
  for i in 1 2 3; do
    t0=$EPOCHSECONDS
    wc_daemon_sleep "$D1_INTERVALO"
    t1=$EPOCHSECONDS
    elapsed=$((t1-t0))
    total=$((total+elapsed))
    [ "$elapsed" -ge "$D1_MIN_OK" ] && ok_count=$((ok_count+1))
  done
  printf '%s %s\n' "$total" "$ok_count" > "$d1_out_file"
)
chmod 755 "$D1_DIR"
read -r d1_total d1_ok_count < "$d1_out_file"
assert_eq "$d1_ok_count" "3" "D1: sleep com fifo indisponivel cai para sleep externo que REALMENTE dorme -- as 3 voltas (intervalo=${D1_INTERVALO}s) tiveram elapsed >= ${D1_MIN_OK}s cada (criterio identico ao de wc_spin_guard_tick), nao so 'girou mais devagar' (total decorrido: ${d1_total}s)"

# happy path continua eficiente quando o fifo funciona (sem regressao)
D1_OK_DIR="$SANDBOX/d1_ok"
mkdir -p "$D1_OK_DIR"
(
  export WATCHCODE_STATE_DIR="$D1_OK_DIR"
  wc_daemon_sleep_init
  printf '%s\n' "${WC_SLEEP_FIFO_OK:-0}" > "$SANDBOX/d1_ok_flag"
)
assert_eq "$(cat "$SANDBOX/d1_ok_flag")" "1" "D1: com state dir gravavel, fifo inicializa OK (WC_SLEEP_FIFO_OK=1)"

# --- Task 6: sensor pids (preventivo, fork-free) ---
PIDS_DIR="$SANDBOX/pids"
mkdir -p "$PIDS_DIR"
export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_DIR/pids.cur"
export WATCHCODE_PIDS_LIMIT="4000"

# <cur> -> escreve cur na fonte, reinicializa o sensor (nivel volta a 0) e zera findings
pids_reset() {
  printf '%s\n' "$1" > "$WATCHCODE_PIDS_CURRENT_FILE"
  wc_pids_init
  : > "$(wc_findings_file)"
}
pids_count() { grep -c '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null || true; }
pids_last_level() {
  grep '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null | tail -n1 \
    | sed -n 's/.*"level":"\([a-z]*\)".*/\1/p'
}

# caso 1 (POSITIVO): 50% de ocupacao, zero achados
pids_reset 2000
wc_pids_sense
assert_eq "$(pids_count)" "0" "pids: 2000/4000 (50%) fica ok, zero achados"

# caso 2: borda exata e um passo alem
pids_reset 2399
wc_pids_sense
assert_eq "$(pids_count)" "0" "pids: 2399/4000 (59,97%) abaixo da borda, sem achado"

pids_reset 2400
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: 2400/4000 (60% exato) cruza a borda de warn"
assert_eq "$(pids_last_level)" "warn" "pids: borda exata 2400 classifica como warn"

pids_reset 2401
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: 2401/4000 um passo alem da borda tambem warn"
assert_eq "$(pids_last_level)" "warn" "pids: 2401 classifica como warn"

# caso 3 (NEGATIVO): salto 0->2 emite UMA linha crit
pids_reset 3300
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: salto 0->2 (3300/4000=82,5%) emite UMA linha"
assert_eq "$(pids_last_level)" "crit" "pids: 3300 classifica direto como crit (salto de nivel)"

# caso 2c: borda exata do CRIT (3199/3200/3201) -- espelha o caso 2 para o
# teto CRIT_ON; necessario para a sabotagem de estreia da secao 6.3, que
# inverte >= para > exatamente em CRIT_ON (o caso 2/WARN sozinho nao pega
# essa mutacao, pois usa WARN_ON, nao CRIT_ON)
pids_reset 3199
wc_pids_sense
assert_eq "$(pids_last_level)" "warn" "pids: 3199/4000 (79,975%) abaixo da borda do crit, ainda warn"
pids_reset 3200
wc_pids_sense
assert_eq "$(pids_last_level)" "crit" "pids: 3200/4000 (80% exato) cruza a borda do crit"
pids_reset 3201
wc_pids_sense
assert_eq "$(pids_last_level)" "crit" "pids: 3201/4000 um passo alem da borda do crit tambem crit"

# caso 4: dedup (mesmo grau nao reanuncia)
pids_reset 2500
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: dedup - warn inicial em 2500"
printf '2600\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: dedup - 2600 ainda warn, nao reanuncia"

# caso 5: histerese e rearme
pids_reset 2500
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: histerese - warn inicial em 2500"
printf '2300\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: 2300 (57,5%) entre OFF(55%) e ON(60%) nao gera novo achado nem desarma"
printf '2100\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: 2100 (52,5%) abaixo do OFF de warn, desarma sem gerar achado de descida"
printf '2450\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "2" "pids: rearmado, 2450 cruza de novo warn -> segunda linha"

# caso 6: escalada warn->crit
pids_reset 2500
wc_pids_sense
assert_eq "$(pids_count)" "1" "pids: escalada - warn inicial em 2500"
printf '3250\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "2" "pids: 3250 (81,25%) escalada warn->crit gera segunda linha"
assert_eq "$(pids_last_level)" "crit" "pids: escalada 1->2 classifica como crit"

# --- D2: perda de fonte em CRIT preserva SKIP_FORKS=1 (fail-closed, decisao de produto) ---
pids_reset 3300
wc_pids_sense
assert_eq "$WC_PIDS_SKIP_FORKS" "1" "D2: pre-condicao - crit direto ativa SKIP_FORKS=1"
rm -f "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$WC_PIDS_SKIP_FORKS" "1" "D2: fail-closed - perder a fonte estando em crit MANTEM SKIP_FORKS=1 (nao libera sensores que forkam)"
printf '3300\n' > "$WATCHCODE_PIDS_CURRENT_FILE"

# caso 7: VARREDURA VAZIA REPROVA - fonte some em pleno voo
pids_reset 2000
rm -f "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_read; rc_read=$?
assert_eq "$rc_read" "2" "pids_read: fonte sumida em pleno voo retorna 2"
wc_pids_sense
n_err="$(grep -c '"level":"err"' "$(wc_findings_file)" 2>/dev/null || true)"
assert_eq "${n_err:-0}" "1" "pids: transicao para err grava achado unico level=err (nao finge verde)"

# --- D6: recuperacao de err com o MESMO grau nao reanuncia (nao forca nivel 0) ---
pids_reset 2500
wc_pids_sense
assert_eq "$(pids_count)" "1" "D6: pre-condicao - warn inicial em 2500"
rm -f "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "2" "D6: pre-condicao - fonte some, grava err (warn+err=2)"
printf '2500\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
wc_pids_sense
assert_eq "$(pids_count)" "2" "D6: recuperacao com o MESMO cur=2500 nao reanuncia warn (continua warn+err=2, sem 3o achado)"
assert_eq "$(pids_last_level)" "err" "D6: ultimo achado apos recuperacao continua sendo o err (nenhum warn novo foi gravado)"

# caso 7b: fonte ausente JA NO ARRANQUE -> sensor nasce inativo (disabled), nao silencioso
(
  export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_DIR/nunca-existe"
  export WATCHCODE_PIDS_LIMIT="4000"
  wc_pids_init
  st="$(cat "$(wc_state_dir)/pids_sensor" 2>/dev/null || true)"
  case "$st" in disabled*) r=sim ;; *) r=nao ;; esac
  printf '%s\n' "$r" > "$PIDS_DIR/case7b_disabled"
  : > "$(wc_findings_file)"
  wc_pids_sense
  cnt="$(grep -c '"kind":"pids"' "$(wc_findings_file)" 2>/dev/null || true)"
  printf '%s\n' "${cnt:-0}" > "$PIDS_DIR/case7b_count"
)
assert_eq "$(cat "$PIDS_DIR/case7b_disabled")" "sim" "pids: fonte ausente no arranque -> sensor nasce inativo (disabled)"
assert_eq "$(cat "$PIDS_DIR/case7b_count")" "0" "pids: sensor inativo nao grava nada em wc_pids_sense (estado explicito, nao silencio)"

# caso extra: fallback de limite = MENOR valor numerico entre ulimit real e pids.max (secao 0.2)
(
  unset WATCHCODE_PIDS_LIMIT
  export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_DIR/pids.cur.fb"
  printf '2000\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
  real_ulimit="$(ulimit -u)"

  printf '8000\n' > "$PIDS_DIR/pids.max"
  wc_pids_init
  printf '%s\n' "$WC_PIDS_LIMIT" > "$PIDS_DIR/fb1"

  printf '2000\n' > "$PIDS_DIR/pids.max"
  wc_pids_init
  printf '%s\n' "$WC_PIDS_LIMIT" > "$PIDS_DIR/fb2"

  printf 'max\n' > "$PIDS_DIR/pids.max"
  wc_pids_init
  printf '%s\n' "$WC_PIDS_LIMIT" > "$PIDS_DIR/fb3"

  printf '%s\n' "$real_ulimit" > "$PIDS_DIR/fb_ulimit"
)
assert_eq "$(cat "$PIDS_DIR/fb1")" "$(cat "$PIDS_DIR/fb_ulimit")" "pids: fallback usa o MENOR entre ulimit real e pids.max=8000 -> vence o ulimit"
assert_eq "$(cat "$PIDS_DIR/fb2")" "2000" "pids: fallback usa o MENOR entre ulimit real e pids.max=2000 -> vence o pids.max"
assert_eq "$(cat "$PIDS_DIR/fb3")" "$(cat "$PIDS_DIR/fb_ulimit")" "pids: pids.max nao numerico (max) -> usa so o ulimit numerico"
rm -f "$PIDS_DIR/pids.max"
export WATCHCODE_PIDS_LIMIT="4000"

# --- D5: limite 0 (ou negativo) NAO pode ativar o sensor (silencio disfarcado de alerta) ---
(
  export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_DIR/pids.cur.d5"
  printf '5\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
  export WATCHCODE_PIDS_LIMIT="0"
  wc_pids_init
  printf '%s\n' "$WC_PIDS_ENABLED" > "$PIDS_DIR/d5_enabled"
  st="$(cat "$(wc_state_dir)/pids_sensor" 2>/dev/null || true)"
  case "$st" in disabled*) r=sim ;; *) r=nao ;; esac
  printf '%s\n' "$r" > "$PIDS_DIR/d5_disabled"
  : > "$(wc_findings_file)"
  wc_pids_sense
  cnt="$(grep -c '\"kind\":\"pids\"' "$(wc_findings_file)" 2>/dev/null || true)"
  printf '%s\n' "${cnt:-0}" > "$PIDS_DIR/d5_findings"
)
assert_eq "$(cat "$PIDS_DIR/d5_enabled")" "0" "D5: WATCHCODE_PIDS_LIMIT=0 nao ativa o sensor"
assert_eq "$(cat "$PIDS_DIR/d5_disabled")" "sim" "D5: limite 0 cai no ramo disabled com motivo explicito"
assert_eq "$(cat "$PIDS_DIR/d5_findings")" "0" "D5: sensor com limite 0 desativado nao grava achado nenhum (nao fica preso em crit permanente)"

(
  export WATCHCODE_PIDS_CURRENT_FILE="$PIDS_DIR/pids.cur.d5b"
  printf '5\n' > "$WATCHCODE_PIDS_CURRENT_FILE"
  export WATCHCODE_PIDS_LIMIT="-10"
  wc_pids_init
  printf '%s\n' "$WC_PIDS_ENABLED" > "$PIDS_DIR/d5b_enabled"
)
assert_eq "$(cat "$PIDS_DIR/d5b_enabled")" "0" "D5: WATCHCODE_PIDS_LIMIT negativo (-10) tambem nao ativa o sensor"

# caso 8: formato exato da linha JSONL (secao 2)
pids_reset 2400
wc_pids_sense
fmt_line="$(grep '"kind":"pids"' "$(wc_findings_file)" | tail -n1)"
if [[ "$fmt_line" =~ ^\{\"kind\":\"pids\",\"ts\":[0-9]+,\"cur\":2400,\"max\":4000,\"level\":\"warn\"\}$ ]]; then
  fmt_ok=sim
else
  fmt_ok=nao
fi
assert_eq "$fmt_ok" "sim" "pids: formato da linha warn casa exatamente {kind,ts,cur,max,level}"
assert_eq "$(printf '%s' "$fmt_line" | jq -r .kind)" "pids" "pids: jq -r .kind devolve pids (harness pode forkar)"

# caso 9: gate estatico de fork-free (extracao textual dos 4 atomos do caminho quente)
# --- D3: a blocklist antiga (9 nomes + poucas construcoes) tinha furos reais
# (crase, job em background, process substitution de saida, binario externo
# nu). Gate reescrito como ALLOWLIST (spec sec.3): so passam read, printf,
# case/esac, local, return, if/then/elif/else/fi/do/done/while/for, testes
# builtin ([[ / (( / [), chamada as proprias wc_*, label de case, atribuicao
# de variavel e continuacao de argumentos (linha comecando com aspas);
# qualquer outra palavra de comando em posicao de inicio de instrucao
# reprova. Blacklist textual continua por cima, para pipe/subst/bg em
# qualquer posicao da linha (defesa em profundidade, nao so allowlist).

# autoteste do piso nao-vazio: extracao de funcao inexistente tem que devolver ZERO linhas
pids_body_vazio="$(sed -n '/^wc_pids_nao_existe/,/^}/p' "$DIR/bin/lib.sh")"
pids_lines_vazio="$(printf '%s\n' "$pids_body_vazio" | grep -c . || true)"
if [ "${pids_lines_vazio:-0}" -eq 0 ]; then r=vazio; else r=nao_vazio; fi
assert_eq "$r" "vazio" "pids: autoteste do piso nao-vazio - extracao de funcao inexistente devolve zero linhas"

# pids_gate_check <fn> <arquivo>: predicado puro (0=limpo, 1=violacao), imprime
# em stdout um motivo curto quando reprova. Nao chama pass/fail -- e reaproveitada
# pelo gate real (abaixo, contra o lib.sh commitado) E pela prova de sabotagem
# D3 (contra copias mutadas fora da arvore).
pids_gate_check() {
  local fn="$1" file="$2" body lines body_nopipe body_noamp raw_line trimmed

  body="$(sed -n "/^$fn/,/^}/p" "$file")"
  lines="$(printf '%s\n' "$body" | grep -c . || true)"
  if [ "${lines:-0}" -eq 0 ]; then
    printf 'extracao vazia (funcao nao encontrada)\n'; return 1
  fi

  # Pass 1: blacklist textual, em qualquer posicao da linha (independe de
  # onde na linha a construcao aparece).
  if printf '%s\n' "$body" | grep -qE '\$\(|`|<\(|>\(|\bcoproc\b'; then
    printf 'substituicao de comando/processo ($(), crase, <(), >()) ou coproc\n'; return 1
  fi
  body_nopipe="$(printf '%s\n' "$body" | sed 's/||/  /g')"
  if printf '%s\n' "$body_nopipe" | grep -qE '\|'; then
    printf 'pipe (|)\n'; return 1
  fi
  body_noamp="$(printf '%s\n' "$body_nopipe" | sed 's/&&/  /g')"
  if printf '%s\n' "$body_noamp" | grep -qE '&'; then
    printf 'job em background (&)\n'; return 1
  fi

  # Pass 2: allowlist do token de comando em posicao de inicio de instrucao.
  while IFS= read -r raw_line; do
    trimmed="$(printf '%s' "$raw_line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$trimmed" ] && continue
    case "$trimmed" in
      '#'*|'{'|'}'|';;') continue ;;
      read\ *|printf\ *|'case '*|esac|local\ *|return|'return '*) continue ;;
      'if '*|then|'elif '*|else|fi|do|done|'while '*|'for '*) continue ;;
      '[['*|'(('*|'['*) continue ;;
      wc_*) continue ;;
      *=*) continue ;;
      '"'*) continue ;;
    esac
    if [[ "$trimmed" =~ ^[A-Za-z0-9_\*]+\) ]]; then continue; fi
    printf 'linha fora da allowlist (binario externo nu ou construcao nao reconhecida): %s\n' "$trimmed"
    return 1
  done <<BODYEOF
$body
BODYEOF
  return 0
}

pids_check_forkfree() {
  local fn="$1" reason
  if reason="$(pids_gate_check "$fn" "$DIR/bin/lib.sh")"; then
    pass "pids: $fn e fork-free (allowlist + blacklist ok)"
  else
    fail "pids: $fn contem construcao proibida no caminho quente ($reason)"
  fi
}
for fn in wc_pids_read wc_pids_level_calc wc_pids_append wc_pids_sense wc_spin_guard_tick; do
  pids_check_forkfree "$fn"
done

# --- D3: sabotagem de estreia -- prova que o gate NOVO pega os
# vetores que o gate ANTIGO (blocklist) deixava passar. Cada vetor sabota uma
# COPIA de lib.sh FORA da arvore (nunca o arquivo rastreado, nunca in-place).
D3_DIR="$SANDBOX/d3_sabotage"
mkdir -p "$D3_DIR"
D3_OLD_RE='\$\(|\||\bjq\b|\bdate\b|\bsed\b|\bgrep\b|\bcat\b|\bwc\b|\bsleep\b|\bmkdir\b|coproc|<\('

d3_inject() {
  # <sufixo> <linha> -> copia de lib.sh com <linha> injetada dentro do corpo
  # de wc_pids_sense; imprime o caminho da copia em stdout.
  local suf="$1" linha="$2" out="$D3_DIR/lib.sh.$1" done_flag=0
  : > "$out"
  while IFS= read -r l; do
    printf '%s\n' "$l" >> "$out"
    if [ "$done_flag" -eq 0 ] && [ "$l" = "wc_pids_sense() {" ]; then
      printf '  %s\n' "$linha" >> "$out"
      done_flag=1
    fi
  done < "$DIR/bin/lib.sh"
  printf '%s\n' "$out"
}

d3_report_vector() {
  # <nome> <arquivo> -> imprime old/new e asserta que o gate NOVO pega
  local nome="$1" arq="$2" old_r new_r old_body old_nopipe
  old_body="$(sed -n '/^wc_pids_sense/,/^}/p' "$arq")"
  old_nopipe="$(printf '%s\n' "$old_body" | sed 's/||/  /g')"
  if printf '%s\n' "$old_nopipe" | grep -qE "$D3_OLD_RE"; then old_r=pegou; else old_r=passou; fi
  if pids_gate_check wc_pids_sense "$arq" >/dev/null; then new_r=passou; else new_r=pegou; fi
  printf '  [D3/%s] gate ANTIGO (blocklist)=%s | gate NOVO (allowlist)=%s\n' "$nome" "$old_r" "$new_r"
  assert_eq "$new_r" "pegou" "D3: gate novo pega o vetor '$nome'"
}

d3_report_vector 'crase-id'          "$(d3_inject crase1  'x=`id`')"
d3_report_vector 'crase-hostname'    "$(d3_inject crase2  'x=`hostname`')"
d3_report_vector 'background'        "$(d3_inject bg      'alguma_funcao &')"
d3_report_vector 'process-sub-saida' "$(d3_inject procsub 'echo x > >(id)')"
d3_report_vector 'binario-externo-nu' "$(d3_inject bare    '/usr/bin/id')"
d3_report_vector 'pipe'              "$(d3_inject pipe    'printf x | cat')"

unset WATCHCODE_PIDS_CURRENT_FILE WATCHCODE_PIDS_LIMIT

# --- Estrato B: fixture com consumo REAL de processos, isolada em scope systemd ---
if [ "${WATCHCODE_TEST_SKIP_LIVE:-0}" = "1" ]; then
  echo "  SKIP explicito - fixture real de pids nao executada (WATCHCODE_TEST_SKIP_LIVE=1)"
else
  real_pids_file="/sys/fs/cgroup/user.slice/user-$(id -u).slice/pids.current"
  real_cur=""
  [ -r "$real_pids_file" ] && read -r real_cur < "$real_pids_file"
  real_ulimit="$(ulimit -u)"
  if command -v systemd-run >/dev/null 2>&1 \
     && systemctl --user is-system-running >/dev/null 2>&1 \
     && [[ "$real_cur" =~ ^[0-9]+$ ]] && [[ "$real_ulimit" =~ ^[0-9]+$ ]] \
     && [ "$((real_cur+64))" -lt "$real_ulimit" ]; then
    # CONS-09S (item 8): a folga exigida e a do proprio scope (TasksMax=64), nao
    # o dobro da carga atual da maquina, que fazia o estrato B depender do momento.
    out="$(systemd-run --user --scope -p TasksMax=64 --collect bash "$DIR/tests/fixture_pids_scope.sh" 2>&1)"
    rc_fix=$?
    printf '%s\n' "$out"
    if [ "$rc_fix" -eq 0 ] && printf '%s\n' "$out" | grep -q '^FIXTURE OK$'; then
      pass "estrato B: fixture real de consumo de processos passou (isolada em scope TasksMax=64)"
    else
      fail "estrato B: fixture real de consumo de processos falhou (rc=$rc_fix)"
    fi
  elif command -v systemd-run >/dev/null 2>&1 && systemctl --user is-system-running >/dev/null 2>&1; then
    fail "estrato B: sem folga para teste de consumo real (cur=$real_cur limite=$real_ulimit)"
  else
    echo "NOK - fixture real nao executada: isolamento indisponivel (systemd-run --user ausente ou user bus fora do ar)"
    FAILS=$((FAILS+1))
  fi
fi

# --- CONS-09S (item 1): estado privado, sem /tmp compartilhado ---
cs_home="$SANDBOX/cs_home"; mkdir -p "$cs_home"
r="$(env -u WATCHCODE_STATE_DIR -u XDG_RUNTIME_DIR HOME="$cs_home" bash -c '. "'"$DIR"'/bin/lib.sh"; wc_state_dir')"
assert_eq "$r" "$cs_home/.cache/watchcode" "CONS-09S 1: sem env, estado vai para \$HOME/.cache e nao para /tmp"
r="$(env -u WATCHCODE_STATE_DIR XDG_RUNTIME_DIR="$SANDBOX/xdg" bash -c '. "'"$DIR"'/bin/lib.sh"; wc_state_dir')"
assert_eq "$r" "$SANDBOX/xdg/watchcode" "CONS-09S 1: com XDG_RUNTIME_DIR, usa o XDG"
r="$(env WATCHCODE_STATE_DIR="$SANDBOX/cs_perm/st" bash -c '. "'"$DIR"'/bin/lib.sh"; wc_init_state && stat -c %a "$(wc_state_dir)"' 2>/dev/null)"
assert_eq "$r" "700" "CONS-09S 1: diretorio de estado criado com modo 700"
mkdir -p "$SANDBOX/cs_target"; ln -s "$SANDBOX/cs_target" "$SANDBOX/cs_link"
rc_link="$(WATCHCODE_STATE_DIR="$SANDBOX/cs_link" bash -c '. "'"$DIR"'/bin/lib.sh"; if wc_init_state 2>/dev/null; then echo 0; else echo 1; fi')"
assert_eq "$rc_link" "1" "CONS-09S 1: estado que e symlink e recusado (rc!=0)"
assert_eq "$([ -e "$SANDBOX/cs_target/sessions" ] && echo criou || echo nada)" "nada" "CONS-09S 1: symlink recusado nao cria nada no alvo"
rc_own="$(WATCHCODE_STATE_DIR=/usr bash -c '. "'"$DIR"'/bin/lib.sh"; if wc_init_state 2>/dev/null; then echo 0; else echo 1; fi')"
assert_eq "$rc_own" "1" "CONS-09S 1: diretorio de outro dono (/usr) e recusado"

# --- CONS-09S (item 2): exe/comm vindos do journal, charset estrito, JSON valido ---
cs_exe_line="$(jq -cn --arg e '/opt/x/$(id) `id` "q"' '{__CURSOR:"c9",MESSAGE_ID:"fc2e22bc6ee647b6b90729ab34a250b1",COREDUMP_SIGNAL:"6",COREDUMP_EXE:$e,COREDUMP_TIMESTAMP:"1784454486651229"}')"
: > "$(wc_findings_file)"
wc_parse_coredump "$cs_exe_line"
assert_eq "$(jq -e . "$(wc_findings_file)" >/dev/null 2>&1 && echo json_ok || echo json_quebrado)" "json_ok" "CONS-09S 2: exe hostil nao quebra o JSON do finding"
cs_exe="$(jq -r '.exe' "$(wc_findings_file)" | head -n1)"
assert_eq "$(printf '%s' "$cs_exe" | /usr/bin/grep -Ec '^[A-Za-z0-9._/+-]+$')" "1" "CONS-09S 2: exe gravado so com charset [A-Za-z0-9._/+-] (obtido '$cs_exe')"
cs_oom_line="$(jq -cn --arg m 'Memory cgroup out of memory: Killed process 42 (a"b$(id))' '{_TRANSPORT:"kernel",MESSAGE:$m}')"
: > "$(wc_findings_file)"
wc_parse_oom "$cs_oom_line"
assert_eq "$(jq -e . "$(wc_findings_file)" >/dev/null 2>&1 && echo json_ok || echo json_quebrado)" "json_ok" "CONS-09S 2: comm hostil nao quebra o JSON do finding oom"
assert_eq "$(jq -r '.comm' "$(wc_findings_file)" | /usr/bin/grep -c '[$`"]')" "0" "CONS-09S 2: comm do oom sem metacaractere de shell"
/usr/bin/grep -q 'DADO NAO CONFIAVEL' "$DIR/SKILL.md" && r=marcado || r=sem_marca
assert_eq "$r" "marcado" "CONS-09S 2: SKILL.md marca exe/comm/cgroup como dado nao confiavel"

# --- CONS-09S (item 5): sem nome de modelo fixo no diagnostico (herda a sessao) ---
/usr/bin/grep -q 'fable' "$DIR/SKILL.md" && r=fixo || r=herda
assert_eq "$r" "herda" "CONS-09S 5: SKILL.md nao fixa o modelo fable"
/usr/bin/grep -q 'fable' "$DIR/DESIGN.md" && r=fixo || r=herda
assert_eq "$r" "herda" "CONS-09S 5: DESIGN.md nao fixa o modelo fable"
sed -n 17p "$DIR/PLAN.md" | /usr/bin/grep -q 'fable' && r=fixo || r=herda
assert_eq "$r" "herda" "CONS-09S 5: PLAN.md:17 nao fixa o modelo fable"

# --- Resolvedor unico de baseline (CONS-09W): env > local nao versionado > exemplo da skill ---
# Sandbox de HOME para nunca ler a baseline real do usuario durante o teste.
FAKE_HOME="$SANDBOX/fakehome"; mkdir -p "$FAKE_HOME/.config/bigtech"
r_exemplo="$(env -u WATCHCODE_BASELINE_FILE HOME="$FAKE_HOME" bash -c '. "'"$DIR"'/bin/lib.sh"; wc_baseline_path')"
assert_eq "$r_exemplo" "$DIR/baseline.txt" "sem env e sem local: cai no exemplo da skill"
printf '# local\n' > "$FAKE_HOME/.config/bigtech/watchcode_baseline.txt"
r_local="$(env -u WATCHCODE_BASELINE_FILE HOME="$FAKE_HOME" bash -c '. "'"$DIR"'/bin/lib.sh"; wc_baseline_path')"
assert_eq "$r_local" "$FAKE_HOME/.config/bigtech/watchcode_baseline.txt" "sem env, com local: usa o local nao versionado"
r_env="$(HOME="$FAKE_HOME" WATCHCODE_BASELINE_FILE=/opt/outra.txt bash -c '. "'"$DIR"'/bin/lib.sh"; wc_baseline_path')"
assert_eq "$r_env" "/opt/outra.txt" "env WATCHCODE_BASELINE_FILE vence o local"

echo "---"
if [ "$FAILS" -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; else echo "$FAILS FALHA(S)"; exit 1; fi
