#!/usr/bin/env python3
"""Lib compartilhada dos hooks de TDD (guard + runner)."""
import hashlib
import json
import os
import re
import sys


def _glob_to_regex(pattern: str) -> str:
    pattern = pattern.strip("/")
    out, i, n = [], 0, len(pattern)
    while i < n:
        ch = pattern[i]
        if ch == "*":
            if i + 1 < n and pattern[i + 1] == "*":  # '**'
                j = i + 2
                if j < n and pattern[j] == "/":
                    out.append(r"(?:.*/)?")   # '**/' -> zero+ segmentos ancorados em '/'
                    j += 1
                else:
                    out.append(".*")          # '**' final -> casa tudo
                i = j
                continue
            out.append("[^/]*")  # '*' fica num unico segmento
            i += 1
        elif ch == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(ch))
            i += 1
    return "^" + "".join(out) + "$"


def glob_match(rel_path: str, pattern: str) -> bool:
    return re.match(_glob_to_regex(pattern), rel_path.strip("/")) is not None


PRESETS = {
    "python-pytest": {
        "test_command": "pytest -x -q",
        "production_globs": ["**/*.py"],
        "test_globs": ["tests/**", "**/test_*.py", "**/*_test.py", "conftest.py"],
    },
    "php-phpunit": {
        "test_command": "vendor/bin/phpunit",
        "production_globs": ["**/*.php"],
        "test_globs": ["tests/**", "**/*Test.php"],
    },
    "node-vitest": {
        "test_command": "npx vitest run",
        "production_globs": ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"],
        "test_globs": ["**/*.test.js", "**/*.test.ts", "**/*.test.jsx",
                       "**/*.test.tsx", "**/*.spec.js", "**/*.spec.ts"],
    },
    "node-jest": {
        "test_command": "npx jest",
        "production_globs": ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"],
        "test_globs": ["__tests__/**", "**/*.test.js", "**/*.test.ts"],
    },
    "go-test": {
        "test_command": "go test ./...",
        "production_globs": ["**/*.go"],
        "test_globs": ["**/*_test.go"],
    },
    "cpp-ctest": {
        "test_command": "ctest --output-on-failure",
        "production_globs": ["**/*.cpp", "**/*.cc", "**/*.cxx", "**/*.h", "**/*.hpp"],
        "test_globs": ["tests/**", "**/test_*.cpp", "**/*_test.cpp"],
    },
    "dotnet-test": {
        "test_command": "dotnet test",
        "production_globs": ["**/*.cs"],
        "test_globs": ["**/*Tests.cs", "**/*Test.cs"],
    },
}

_DEFAULTS = {
    "enabled": True,
    "strict": True,
    "timeout_sec": 120,
    "fast_command": None,
    "exclude_globs": [],
    "production_globs": [],
    "test_globs": [],
    "test_command": None,
}


def resolve_config(raw: dict) -> dict:
    cfg = dict(_DEFAULTS)
    preset = raw.get("preset")
    if preset:
        if preset not in PRESETS:
            raise ValueError(f"preset desconhecido: {preset}")
        cfg.update(PRESETS[preset])
    cfg.update({k: v for k, v in raw.items() if k != "preset"})
    return cfg


def find_project_root(start_dir: str):
    d = os.path.realpath(start_dir)
    while True:
        if os.path.isfile(os.path.join(d, ".claude", "tdd-guard.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load_config(start_dir: str):
    root = find_project_root(start_dir)
    if root is None:
        return None, None
    config_path = os.path.join(root, ".claude", "tdd-guard.json")
    try:
        with open(config_path) as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        print(f"tdd-guard: JSON invalido em {config_path}: {e}", file=sys.stderr)
        return None, None
    except Exception:
        return None, None
    if raw.get("enabled") is False:
        return None, None
    try:
        cfg = resolve_config(raw)
    except ValueError as e:
        print(f"tdd-guard: {e}", file=sys.stderr)
        return None, None
    return root, cfg


def classify(rel_path: str, cfg: dict) -> str:
    for g in cfg.get("exclude_globs", []):
        if glob_match(rel_path, g):
            return "excluded"
    for g in cfg.get("test_globs", []):
        if glob_match(rel_path, g):
            return "test"
    for g in cfg.get("production_globs", []):
        if glob_match(rel_path, g):
            return "production"
    return "ignored"


def state_path(project_root: str) -> str:
    h = hashlib.sha256(os.path.realpath(project_root).encode()).hexdigest()[:16]
    base = os.path.join(os.path.expanduser("~"), ".claude", "state", "tdd-guard", h)
    return os.path.join(base, "last-run.json")


def read_state(project_root: str):
    try:
        with open(state_path(project_root)) as f:
            return json.load(f)
    except Exception:
        return None


def write_state(project_root: str, state: dict) -> None:
    p = state_path(project_root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, p)   # escrita atomica


def extract_file_path(data: dict) -> str:
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    return ti.get("file_path", "") or ""


def parse_totals(text: str) -> dict:
    totals = {}
    m = re.search(r"(\d+) passed", text)
    if m:
        totals["passed"] = int(m.group(1))
    m = re.search(r"(\d+) failed", text)
    if m:
        totals["failed"] = int(m.group(1))
    m = re.search(r"(\d+) error", text)         # pytest: coleta/fixture error
    if m:
        totals["failed"] = totals.get("failed", 0) + int(m.group(1))
    m = re.search(r"Failures:\s*(\d+)", text)   # phpunit
    if m and int(m.group(1)) > 0:
        totals["failed"] = int(m.group(1))
    return totals
