#!/usr/bin/env python3
"""Gate de drift semântico do registry bigtech (BT-7).

Detecta inconsistências mínimas entre inventário de agents/skills, hooks.json
e política de porte/host. Offline, só stdlib.

Checks (hard fail):
  1. agents/*.md: frontmatter `name:` presente, único e == stem do arquivo
     (exceções documentadas em NAME_STEM_EXCEPTIONS).
  2. skills/*/SKILL.md: `name:` presente no frontmatter.
  3. hooks/hooks.json: scripts referenciados em args existem no disco.
  4. Contagem de agents == EXPECTED_AGENT_COUNT (bump intencional se inventário mudar).
  5. valor legado "solo" não é porte primário (peer de early/scale/bigtech) sem alias/deprec.
  6. Zero referências ao host legado Codeberg em paths de produto.

Uso:
    python3 scripts/check_semantic_drift.py [--root DIR] [--quiet]

Exit: 0 se limpo; 1 se qualquer check falhar.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Inventário e política
# ---------------------------------------------------------------------------

# Bump quando o inventário público de agents mudar de propósito (README/AGENTS).
EXPECTED_AGENT_COUNT = 51

# stem -> name permitido se diferente do stem. Vazio = sem exceções.
NAME_STEM_EXCEPTIONS: dict[str, str] = {}

# Paths de produto onde host legado e porte-primário "solo" são proibidos.
# docs/campanha = prova histórica (antes/depois); docs/house = espelho vault.
PRODUCT_FILE_GLOBS = (
    "README.md",
    "AGENTS.md",
    "SECURITY.md",
    "PRIVACY.md",
    "DEVELOPMENT.md",
    "CHANGELOG.md",
    "NOTICE",
    "LICENSE",
    ".claude-plugin/**/*",
    "agents/**/*.md",
    "skills/**/*",
    "hooks/*.py",
    "hooks/*.json",
    "hooks/*.md",
    "scripts/*.py",
    "scripts/*.sh",
    "bin/**/*",
    "docs/**/*.md",
)

PRODUCT_EXCLUDE_PREFIXES = (
    "docs/campanha/",
    "docs/house/",
    "docs/superpowers/",
    "docs/auditoria/",
    "docs/submission/",
    # Meta: o próprio gate e a suíte que o exercitam (evita auto-alarme).
    "scripts/check_semantic_drift.py",
    "scripts/tests/",
)

# Solo listado como peer de porte canônico (early/scale/bigtech) em enums/tabelas.
# Padrões montados em partes para o arquivo-fonte não conter o literal proibido
# em prosa de produto (o gate não se auto-exclui de forma perfeita em todos os
# hosts; a exclusão de path cobre o caso normal).
_SOLO = "so" + "lo"
RE_SOLO_PEER = re.compile(
    rf"(?:"
    rf"(?:early|scale|bigtech)\s*[|/]\s*{_SOLO}"
    rf"|\b{_SOLO}\s*[|/]\s*(?:early|scale|bigtech)"
    rf"|\bearly\s*[|,]\s*{_SOLO}\s*[|,]\s*scale"
    rf"|\b{_SOLO}\s*[|,]\s*early\s*[|,]\s*scale"
    rf")",
    re.IGNORECASE,
)

# Marcador / flag de porte com valor solo (alias deprecado só com contexto).
RE_PORTE_SOLO = re.compile(
    rf"(?:porte\s*=\s*{_SOLO}|--porte\s+{_SOLO})\b",
    re.IGNORECASE,
)

# Host legado proibido em produto (string montada para não auto-disparar no docstring).
RE_CODEBERG = re.compile(r"codeberg" + r"\.org", re.IGNORECASE)

# Contexto que autoriza menção a solo (alias deprecado / migração / normalização).
_DEPREC_MARKERS = (
    "deprec",
    "alias",
    "legado",
    "legacy",
    "normaliz",
    "migrat",
    "não grave",
    "nao grave",
    "não existe",
    "nao existe",
    "nunca grave",
    "lido como",
    "→ early",
    "-> early",
    "para early",
)


@dataclass
class Finding:
    check: str
    message: str
    path: str | None = None
    line: int | None = None


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def fail(
        self,
        check: str,
        message: str,
        path: str | None = None,
        line: int | None = None,
    ) -> None:
        self.findings.append(Finding(check=check, message=message, path=path, line=line))

    @property
    def ok(self) -> bool:
        return not self.findings


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    """Parse YAML-like frontmatter simples (chave: valor), stdlib only."""
    try:
        txt = path.read_text(encoding="utf-8")
    except OSError:
        return None  # caller reporta arquivo ilegível se precisar
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in txt[3:end].splitlines():
        m = re.match(r"([A-Za-z0-9_-]+):\s*(.*)", line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        data[key] = val
    return data


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _is_deprec_context(line: str) -> bool:
    low = line.lower()
    return any(m in low for m in _DEPREC_MARKERS)


def _iter_product_files(root: Path) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for pattern in PRODUCT_FILE_GLOBS:
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            rel = _rel(root, p)
            if any(rel == pref.rstrip("/") or rel.startswith(pref) for pref in PRODUCT_EXCLUDE_PREFIXES):
                continue
            # Só texto legível.
            if p.suffix.lower() not in {
                ".md",
                ".py",
                ".sh",
                ".json",
                ".toml",
                ".txt",
                ".cmd",
                "",
            } and p.name not in {"NOTICE", "LICENSE"}:
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            out.append(p)
    return sorted(out, key=lambda x: _rel(root, x))


def check_agents(root: Path, report: Report) -> None:
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        report.fail("agents", "diretório agents/ ausente")
        return

    files = sorted(agents_dir.glob("*.md"))
    count = len(files)
    report.notes.append(f"agents encontrados: {count} (esperado {EXPECTED_AGENT_COUNT})")

    if count != EXPECTED_AGENT_COUNT:
        report.fail(
            "agent-count",
            f"contagem de agents={count}, esperado EXPECTED_AGENT_COUNT={EXPECTED_AGENT_COUNT} "
            f"(atualize a constante se o inventário mudou de propósito)",
        )

    names: dict[str, str] = {}  # name -> rel path
    for path in files:
        rel = _rel(root, path)
        stem = path.stem
        fm = parse_frontmatter(path)
        if fm is None:
            report.fail("agent-name", "frontmatter ausente ou inválido", path=rel)
            continue
        name = fm.get("name")
        if not name:
            report.fail("agent-name", "campo name: ausente no frontmatter", path=rel)
            continue
        expected = NAME_STEM_EXCEPTIONS.get(stem, stem)
        if name != expected:
            report.fail(
                "agent-name",
                f"name={name!r} != stem/exception esperado {expected!r}",
                path=rel,
            )
        if name in names:
            report.fail(
                "agent-name",
                f"name duplicado {name!r} (também em {names[name]})",
                path=rel,
            )
        else:
            names[name] = rel


def check_skills(root: Path, report: Report) -> None:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        report.fail("skills", "diretório skills/ ausente")
        return

    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    report.notes.append(f"skills encontradas: {len(skill_files)}")
    if not skill_files:
        report.fail("skills", "nenhum skills/*/SKILL.md encontrado")
        return

    for path in skill_files:
        rel = _rel(root, path)
        fm = parse_frontmatter(path)
        if fm is None:
            report.fail("skill-name", "frontmatter ausente ou inválido", path=rel)
            continue
        if not fm.get("name"):
            report.fail("skill-name", "campo name: ausente no frontmatter", path=rel)


def check_hooks_scripts(root: Path, report: Report) -> None:
    hooks_json = root / "hooks" / "hooks.json"
    if not hooks_json.is_file():
        report.fail("hooks-json", "hooks/hooks.json ausente")
        return

    try:
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        report.fail("hooks-json", f"JSON inválido: {exc}", path="hooks/hooks.json")
        return

    seen_scripts: set[str] = set()
    n_blocks = 0
    for event, groups in (data.get("hooks") or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            for h in group.get("hooks") or []:
                if h.get("type") != "command":
                    continue
                n_blocks += 1
                args = h.get("args")
                if not isinstance(args, list):
                    report.fail(
                        "hooks-scripts",
                        f"evento {event}: args ausente ou não-lista",
                        path="hooks/hooks.json",
                    )
                    continue
                for arg in args:
                    s = str(arg)
                    if "${CLAUDE_PLUGIN_ROOT}" not in s and not s.endswith(".py"):
                        continue
                    expanded = s.replace("${CLAUDE_PLUGIN_ROOT}", str(root.resolve()))
                    sp = Path(expanded)
                    rel_script = _rel(root, sp) if sp.is_absolute() or sp.exists() else expanded
                    if not sp.is_file():
                        report.fail(
                            "hooks-scripts",
                            f"script referenciado inexistente (evento {event}): {s}",
                            path="hooks/hooks.json",
                        )
                    else:
                        seen_scripts.add(rel_script)

    report.notes.append(
        f"hooks type=command: {n_blocks}; scripts resolvidos: {len(seen_scripts)}"
    )


def check_solo_primary(root: Path, report: Report) -> None:
    """Falha se solo aparece como porte primário (peer early/scale) sem alias/deprec."""
    for path in _iter_product_files(root):
        rel = _rel(root, path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            peer = RE_SOLO_PEER.search(line)
            porte = RE_PORTE_SOLO.search(line)
            if not peer and not porte:
                continue
            if _is_deprec_context(line):
                continue
            # Janela curta: linha anterior/seguinte com deprec (listas multi-linha).
            lines = text.splitlines()
            window = []
            if lineno >= 2:
                window.append(lines[lineno - 2])
            if lineno < len(lines):
                window.append(lines[lineno])
            if any(_is_deprec_context(w) for w in window):
                continue
            kind = "peer early/scale" if peer else "marcador/flag de porte legado"
            report.fail(
                "porte-solo",
                f"valor legado 'solo' como porte primário ({kind}) sem alias/deprec: "
                f"{line.strip()[:120]}",
                path=rel,
                line=lineno,
            )


def check_codeberg(root: Path, report: Report) -> None:
    for path in _iter_product_files(root):
        rel = _rel(root, path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if RE_CODEBERG.search(line):
                report.fail(
                    "codeberg",
                    f"referência a host legado Codeberg em path de produto: "
                    f"{line.strip()[:120]}",
                    path=rel,
                    line=lineno,
                )


def run(root: Path) -> Report:
    report = Report()
    check_agents(root, report)
    check_skills(root, report)
    check_hooks_scripts(root, report)
    check_solo_primary(root, report)
    check_codeberg(root, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate de drift semântico (BT-7).")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz do plugin (default: pai de scripts/).",
    )
    parser.add_argument("--quiet", action="store_true", help="Só imprime falhas.")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    if not args.quiet:
        print("== Drift semântico (BT-7) ==")
        print(f"root: {root}")

    report = run(root)

    if not args.quiet:
        for note in report.notes:
            print(f"  · {note}")

    if report.ok:
        if not args.quiet:
            print("[PASS] drift semântico limpo (agents/skills/hooks/porte/host).")
        return 0

    print(f"[FAIL] {len(report.findings)} violação(ões) de drift semântico:", file=sys.stderr)
    for f in report.findings:
        loc = ""
        if f.path:
            loc = f" @ {f.path}"
            if f.line is not None:
                loc += f":{f.line}"
        print(f"  - [{f.check}]{loc}: {f.message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
