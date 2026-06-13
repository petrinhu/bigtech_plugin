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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails: list[str] = []


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
    except Exception as e:  # noqa: BLE001
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

# 4. hooks.json: cada script referenciado existe
print("[4] hooks.json (scripts resolviveis)")
hj = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
refs = re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"\\]+)", json.dumps(hj))
for rel in sorted(set(refs)):
    if not (ROOT / rel).exists():
        fail(f"hook script ausente: {rel}")
print(f"  scripts referenciados: {len(set(refs))}")

# 5. Executa os hooks de governanca com ambiente simulado
print("[5] Execucao dos hooks (env simulado)")
env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT)}


def run_hook(script: str, payload: dict) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "hooks" / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
        cwd="/tmp",
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
rc, out = run_hook("bigtech_reinforce.py", {"prompt": "montar o time c-level bigtech", "cwd": "/tmp"})
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
rc, _ = run_hook("tdd_guard.py", {"tool_name": "Edit", "tool_input": {"file_path": "/tmp/x.py"}, "cwd": "/tmp"})
if rc not in (0,):
    fail(f"tdd_guard exit {rc} sem config (deveria liberar com 0)")
else:
    print("  tdd_guard: fail-open sem config OK")

print()
if fails:
    print(f"RESULTADO: FAIL ({len(fails)} problema(s))")
    sys.exit(1)
print("RESULTADO: PASS - plugin carregavel; hooks executam e se comportam como esperado.")
sys.exit(0)
