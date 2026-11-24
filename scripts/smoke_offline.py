#!/usr/bin/env python3
"""Smoke test OFFLINE do plugin bigtech (sem instalar no Claude Code).

Valida que o plugin esta "carregavel": manifestos, frontmatter de todos os
agents/skills, hooks.json com scripts resolviveis, e executa os hooks de
governanca com um ambiente simulado (CLAUDE_PLUGIN_ROOT + payload de evento),
conferindo o comportamento real (docs-bootstrap, roteamento, silent-fail).

NAO substitui 100% o teste de instalacao real (use uma instancia com
CLAUDE_CONFIG_DIR isolado para isso), mas pega frontmatter quebrado, JSON
invalido, script de hook ausente e hook que falha/bloqueia.

Uso: python3 scripts/smoke_offline.py    (exit 0 = PASS)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails: list[str] = []
# Temp portátil (Windows não tem /tmp). Usado como cwd e em payloads de hook.
SMOKE_TMP = tempfile.gettempdir()
SMOKE_TMP_FILE = str(Path(SMOKE_TMP) / "x.py")


def fail(msg: str) -> None:
    fails.append(msg)
    print(f"  [FAIL] {msg}")


def parse_frontmatter(path: Path) -> dict | None:
    txt = path.read_text(encoding="utf-8")
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in txt[3:end].splitlines():
        m = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


print("== Smoke OFFLINE do plugin bigtech ==")
print(f"root: {ROOT}\n")

# 1. Manifestos JSON validos + name esperado
print("[1] Manifestos")
manifests = {
    ".claude-plugin/plugin.json": "bigtech",
    ".claude-plugin/marketplace.json": "petrinhu",
    "hooks/hooks.json": None,
}
for rel, expected_name in manifests.items():
    p = ROOT / rel
    if not p.exists():
        fail(f"manifesto ausente: {rel}")
        continue
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"JSON invalido em {rel}: {e}")
        continue
    if expected_name and obj.get("name") != expected_name:
        fail(f"{rel}: name esperado '{expected_name}', obtido '{obj.get('name')}'")
print(f"  manifestos checados: {len(manifests)}")

# 2. Frontmatter de todos os agents (name presente, name == arquivo, description presente)
print("[2] Agents (frontmatter)")
agents = sorted((ROOT / "agents").glob("*.md"))
orange = blue = 0
for a in agents:
    fm = parse_frontmatter(a)
    base = a.stem
    if not fm:
        fail(f"agent sem frontmatter: {base}")
        continue
    if not fm.get("name"):
        fail(f"agent sem 'name': {base}")
    elif fm["name"] != base:
        fail(f"agent name '{fm['name']}' != arquivo '{base}'")
    if not fm.get("description"):
        fail(f"agent sem 'description': {base}")
    color = fm.get("color")
    if color == "orange":
        orange += 1
    elif color == "blue":
        blue += 1
print(f"  agents: {len(agents)} | color orange={orange} blue={blue}")

# 3. Frontmatter das skills
print("[3] Skills (frontmatter)")
skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
for s in skills:
    fm = parse_frontmatter(s)
    if not fm or not fm.get("name"):
        fail(f"skill sem name no frontmatter: {s.parent.name}")
print(f"  skills: {len(skills)}")

# 4. hooks.json: cada script referenciado existe + forma exec correta.
#    A forma EXEC (command + args[]) e a recomendada pela doc oficial para paths:
#    cada arg e literal (sem parsing de shell), o que resolve espacos no caminho
#    e elimina a dependencia de um shell. Aqui validamos a estrutura dos 7 hooks
#    e coletamos a invocacao DECLARADA de cada um (command + args expandidos),
#    para a secao [5] exercitar exatamente o que o Claude Code rodaria.
#    Desde a CONS-14 o hook do produto tab_pendencias e registrado direto no
#    hooks.json (SessionStart e UserPromptSubmit): 9 blocos.
print("[4] hooks.json (scripts resolviveis + forma exec)")
hj = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))


def _expand(token: str) -> str:
    """Expande ${CLAUDE_PLUGIN_ROOT} (= raiz do plugin) num token literal."""
    return token.replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT))


# Percorre TODOS os hooks de TODOS os eventos e coleta os blocos type=command.
# declared[script_basename] = [command, *args_expandidos]  (a invocacao real).
declared: dict[str, list[str]] = {}
# declared_all: todas as invocacoes (eventos e caminhos), para o 5e. Dois hooks
# tem o mesmo nome de arquivo (plugin e produto tab_pendencias), por isso o
# mapa por nome guarda a primeira ocorrencia (a do plugin).
declared_all: list[tuple[str, list[str]]] = []
exec_blocks = 0
for event, groups in (hj.get("hooks") or {}).items():
    for group in groups:
        for h in group.get("hooks", []):
            if h.get("type") != "command":
                continue
            exec_blocks += 1
            cmd = h.get("command")
            args = h.get("args")
            # Asserção estrutural: forma EXEC, nao forma shell.
            # Interpretadores aceitos na forma exec: python3 (hooks do produto) e bash
            # (hook do shell, skills/eficacia/bin/hook_lider_dormindo.sh). Ambos com args[] literal.
            if cmd not in ("python3", "bash"):
                fail(f"hook em {event}: command esperado 'python3' ou 'bash' (forma exec), "
                     f"obtido {cmd!r}")
            if not isinstance(args, list) or not args:
                fail(f"hook em {event}: 'args' ausente/vazio - nao esta na forma exec")
                continue
            if "python3 " in (cmd or "") or any("python3 " in str(a) for a in args):
                fail(f"hook em {event}: string shell 'python3 ' embutida - "
                     f"esperado forma exec (command + args)")
            expanded = [_expand(cmd)] + [_expand(str(a)) for a in args]
            # O script referenciado (ultimo arg) tem de existir no disco.
            script_path = Path(expanded[-1])
            if not script_path.exists():
                fail(f"hook script ausente: {script_path}")
            declared.setdefault(script_path.name, expanded)
            declared_all.append((event, expanded))

EXPECTED_HOOKS = 11
if exec_blocks != EXPECTED_HOOKS:
    fail(f"esperados {EXPECTED_HOOKS} hooks type=command, encontrados {exec_blocks}")
print(f"  hooks type=command: {exec_blocks} (todos forma exec: command=python3|bash + args[])")

# 5. Executa os 6 hooks DISTINTOS com ambiente simulado, mas agora pela invocacao
#    REAL declarada no hooks.json ([command, *args]) - nao mais [sys.executable, script].
#    Isso exercita a string que o Claude Code de fato roda. Sao 4 de governanca
#    (session_init, reinforce, porte_reminder, tab_pendencias_reminder) + 2 de TDD
#    (tdd_guard, tdd_runner). tab_pendencias_reminder aparece em 2 eventos -> 7 blocos.
print("[5] Execucao dos hooks (invocacao real do hooks.json, env simulado)")
# BIGTECH_TAB_REMINDER=full: o smoke valida o contrato do plugin SOZINHO. Sem
# isso, numa maquina que tambem tem o produto standalone `tab_pendencias`
# registrado nas settings, o tab_pendencias_reminder cede a ele os gatilhos 1
# e 2 (anti-duplicacao) e o 5e abaixo falharia por um motivo que nao e defeito.
env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT), "BIGTECH_TAB_REMINDER": "full"}


def run_hook(script: str, payload: dict) -> tuple[int, str]:
    invocation = declared.get(script)
    if invocation is None:
        fail(f"hook '{script}' nao esta declarado em hooks.json (forma exec)")
        return 1, ""
    # Só no smoke: se python3 do hooks.json não resolve no PATH (runner Windows
    # sem alias), usa o interpretador desta sessão — espelha bin/python3.cmd.
    # hooks.json permanece com command=python3 (contrato Claude Code).
    if invocation and invocation[0] == "python3" and shutil.which("python3") is None:
        invocation = [sys.executable, *invocation[1:]]
    proc = subprocess.run(
        invocation,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
        cwd=SMOKE_TMP,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")

# 5a. session_init: docs-bootstrap deve citar docs/ e ORG
rc, out = run_hook("bigtech_session_init.py", {"hook_event_name": "SessionStart"})
if rc != 0:
    fail(f"bigtech_session_init exit {rc} (deveria ser 0/silent-fail)")
if "docs" not in out or "ORG" not in out:
    fail("bigtech_session_init: additionalContext nao cita os manuais (docs/ORG)")
else:
    print("  session_init: docs-bootstrap OK (cita os manuais)")

# 5b. reinforce: prompt de ativacao deve rotear para /bigtech
rc, out = run_hook(
    "bigtech_reinforce.py",
    {"prompt": "montar o time c-level bigtech", "cwd": SMOKE_TMP},
)
if rc != 0:
    fail(f"bigtech_reinforce exit {rc} (deveria ser 0)")
if "bigtech" not in out.lower():
    fail("bigtech_reinforce: nao roteou para /bigtech no prompt de ativacao")
else:
    print("  reinforce: roteamento para /bigtech OK")

# 5c. porte_reminder: silent-fail em dir sem marcador
rc, _ = run_hook("bigtech_porte_reminder.py", {"hook_event_name": "SessionStart"})
if rc != 0:
    fail(f"bigtech_porte_reminder exit {rc} (deveria ser 0)")
else:
    print("  porte_reminder: exit 0 (silent) OK")

# 5d. tdd_guard: sem config de TDD, deve liberar (exit 0)
rc, _ = run_hook(
    "tdd_guard.py",
    {
        "tool_name": "Edit",
        "tool_input": {"file_path": SMOKE_TMP_FILE},
        "cwd": SMOKE_TMP,
    },
)
if rc not in (0,):
    fail(f"tdd_guard exit {rc} sem config (deveria liberar com 0)")
else:
    print("  tdd_guard: fail-open sem config OK")

# 5e. lembrete unico da tabela de pendencias, pela invocacao declarada no
#     hooks.json: repo git com .bigtech-porte e sem TODO.md. Os hooks de
#     SessionStart que tocam tab_pendencias (plugin + produto) devem emitir
#     UMA mensagem de criacao, citando /bigtech:tab_pendencias, e nenhuma
#     mensagem pode citar o comando sem o prefixo bigtech:.
with tempfile.TemporaryDirectory(prefix="bigtech-smoke-") as tmp:
    repo = Path(tmp)
    (repo / ".bigtech-porte").write_text("porte=early\n", encoding="utf-8")
    # NAO criamos TODO.md de proposito: e a condicao que arma o gatilho.
    # Repo git: o CRIAR do produto exige git (is_git).
    git_env = {**os.environ, "GIT_AUTHOR_NAME": "smoke", "GIT_AUTHOR_EMAIL": "s@s",
               "GIT_COMMITTER_NAME": "smoke", "GIT_COMMITTER_EMAIL": "s@s"}
    subprocess.run(["git", "init", "-q"], cwd=repo, env=git_env, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, env=git_env, check=True)
    subprocess.run(["git", "commit", "-qm", "boot", "--allow-empty"], cwd=repo,
                   env=git_env, check=True)
    criacoes = 0
    sem_prefixo = False
    for event, invocation in declared_all:
        if event != "SessionStart" or "tab_pendencias" not in " ".join(invocation):
            continue
        proc = subprocess.run(
            invocation,
            input=json.dumps({"hook_event_name": "SessionStart", "cwd": str(repo),
                              "session_id": "smoke-5e"}),
            capture_output=True, text=True, env=env, timeout=30, cwd=str(repo),
        )
        if proc.returncode != 0:
            fail(f"tab_pendencias ({invocation[-1]}) exit {proc.returncode} (deveria ser 0)")
        for m in re.findall(r'"additionalContext": "((?:[^"\\]|\\.)*)"', proc.stdout):
            if "--create" in m:
                criacoes += 1
            if re.search(r"(?<!bigtech:)/tab_pendencias(?![\w/])", m):
                sem_prefixo = True
    if criacoes != 1:
        fail(f"lembrete de criacao: {criacoes} mensagens com --create (esperada 1)")
    elif sem_prefixo:
        fail("lembrete de tab_pendencias cita o comando sem o prefixo bigtech:")
    else:
        print("  tab_pendencias: lembrete de criacao unico, com prefixo bigtech: OK")

# 5f. tdd_runner: payload minimo, projeto sem .claude/tdd-guard.json -> nao roda
#     a suite e nunca quebra o fluxo (exit 0).
rc, _ = run_hook(
    "tdd_runner.py",
    {
        "tool_name": "Write",
        "tool_input": {"file_path": SMOKE_TMP_FILE},
        "cwd": SMOKE_TMP,
    },
)
if rc != 0:
    fail(f"tdd_runner exit {rc} sem config (deveria ser 0/inerte)")
else:
    print("  tdd_runner: inerte sem config (exit 0) OK")

print()
if fails:
    print(f"RESULTADO: FAIL ({len(fails)} problema(s))")
    sys.exit(1)
print("RESULTADO: PASS - plugin carregavel; hooks executam e se comportam como esperado.")
sys.exit(0)
