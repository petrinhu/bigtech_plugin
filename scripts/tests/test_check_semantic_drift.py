"""Testes do gate de drift semântico (BT-7).

Usa árvore mínima em tmp_path — não depende do inventário vivo do repo
para os casos de falha; o caso de integração roda contra a raiz real.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

# Importa o módulo sob teste a partir de scripts/
SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_semantic_drift as drift


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _minimal_plugin(
    root: Path,
    *,
    n_agents: int | None = None,
    agent_names: list[tuple[str, str]] | None = None,
    skill_name: str | None = "demo",
    hook_script_exists: bool = True,
    extra_files: dict[str, str] | None = None,
) -> Path:
    """Monta um plugin mínimo sob root."""
    n = n_agents if n_agents is not None else drift.EXPECTED_AGENT_COUNT
    if agent_names is None:
        agent_names = [(f"agent-{i:02d}", f"agent-{i:02d}") for i in range(n)]

    for stem, name in agent_names:
        _write(
            root / "agents" / f"{stem}.md",
            f"""\
            ---
            name: {name}
            description: test
            ---
            # {name}
            """,
        )

    if skill_name is not None:
        body = f"""\
        ---
        name: {skill_name}
        description: skill test
        ---
        # skill
        """
        if skill_name == "":
            body = """\
            ---
            description: sem name
            ---
            # skill
            """
        _write(root / "skills" / "demo" / "SKILL.md", body)

    hook_py = root / "hooks" / "dummy_hook.py"
    if hook_script_exists:
        _write(hook_py, "print('ok')\n")
    hooks_payload = {
        "hooks": {
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3",
                            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/dummy_hook.py"],
                        }
                    ]
                }
            ]
        }
    }
    _write(root / "hooks" / "hooks.json", json.dumps(hooks_payload, indent=2) + "\n")

    # README mínimo para o scanner de produto ter algo.
    _write(root / "README.md", "# demo\n")

    if extra_files:
        for rel, content in extra_files.items():
            _write(root / rel, content)

    return root


def test_clean_minimal_tree_passes(tmp_path: Path) -> None:
    root = _minimal_plugin(tmp_path)
    report = drift.run(root)
    assert report.ok, [f.message for f in report.findings]


def test_agent_name_mismatch_fails(tmp_path: Path) -> None:
    names = [(f"agent-{i:02d}", f"agent-{i:02d}") for i in range(drift.EXPECTED_AGENT_COUNT)]
    names[0] = ("agent-00", "wrong-name")
    root = _minimal_plugin(tmp_path, agent_names=names)
    report = drift.run(root)
    assert not report.ok
    assert any(f.check == "agent-name" for f in report.findings)


def test_agent_name_duplicate_fails(tmp_path: Path) -> None:
    names = [(f"agent-{i:02d}", f"agent-{i:02d}") for i in range(drift.EXPECTED_AGENT_COUNT)]
    names[1] = ("agent-01", "agent-00")  # duplica name do agent-00
    root = _minimal_plugin(tmp_path, agent_names=names)
    report = drift.run(root)
    assert any("duplicado" in f.message for f in report.findings)


def test_agent_count_mismatch_fails(tmp_path: Path) -> None:
    root = _minimal_plugin(tmp_path, n_agents=3)
    report = drift.run(root)
    assert any(f.check == "agent-count" for f in report.findings)


def test_skill_missing_name_fails(tmp_path: Path) -> None:
    root = _minimal_plugin(tmp_path, skill_name="")
    report = drift.run(root)
    assert any(f.check == "skill-name" for f in report.findings)


def test_missing_hook_script_fails(tmp_path: Path) -> None:
    root = _minimal_plugin(tmp_path, hook_script_exists=False)
    report = drift.run(root)
    assert any(f.check == "hooks-scripts" for f in report.findings)


def test_codeberg_in_readme_fails(tmp_path: Path) -> None:
    host = "codeberg" + ".org"
    root = _minimal_plugin(
        tmp_path,
        extra_files={"README.md": f"mirror of https://{host}/foo/bar\n"},
    )
    report = drift.run(root)
    assert any(f.check == "codeberg" for f in report.findings)


def test_solo_peer_porte_fails(tmp_path: Path) -> None:
    # early | solo | scale como peers (sem alias/deprec na linha).
    peer = "early | " + "so" + "lo" + " | scale | bigtech"
    root = _minimal_plugin(
        tmp_path,
        extra_files={"docs/ORG.md": f"Porte: {peer}\n"},
    )
    report = drift.run(root)
    assert any(f.check == "porte-solo" for f in report.findings)


def test_solo_deprecated_alias_allowed(tmp_path: Path) -> None:
    solo = "so" + "lo"
    root = _minimal_plugin(
        tmp_path,
        extra_files={
            "docs/ORG.md": (
                f"Alias deprecado: `--porte {solo}` normaliza para early. "
                f"Não grave porte={solo} em marcadores novos.\n"
            ),
        },
    )
    report = drift.run(root)
    assert report.ok, [f.message for f in report.findings]


def test_main_exit_codes(tmp_path: Path) -> None:
    root = _minimal_plugin(tmp_path)
    assert drift.main(["--root", str(root), "--quiet"]) == 0

    host = "codeberg" + ".org"
    bad = _minimal_plugin(
        tmp_path / "bad",
        extra_files={"README.md": f"see {host}/x\n"},
    )
    assert drift.main(["--root", str(bad), "--quiet"]) == 1


def test_repo_root_integration() -> None:
    """Integração: o repo vivo do plugin deve passar no gate."""
    repo = Path(__file__).resolve().parent.parent.parent
    report = drift.run(repo)
    assert report.ok, [(f.check, f.path, f.message) for f in report.findings]
    agents = list((repo / "agents").glob("*.md"))
    assert len(agents) == drift.EXPECTED_AGENT_COUNT
