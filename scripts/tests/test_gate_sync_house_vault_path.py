"""Gate 11 do preci com o caminho do vault em arquivo local (CONS-10A).

Reproduz a maquina do dono sem tocar nela: HOME descartavel com
`.config/bigtech/sync_house.key` (modo 600) e `.config/bigtech/vault_path`
(uma linha). Sem BIGTECH_VAULT e sem --vault, o gate tem de conferir, e nao
sair 2 e reprovar.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_house as sh

GATE = SCRIPTS / "gate_sync_house.py"
CHAVE = b"\x04" * 32


def _maquina(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Devolve (home, vault, house). Chave e vault_path ficam no HOME descartavel."""
    home = tmp_path / "home"
    cfg = home / ".config" / "bigtech"
    cfg.mkdir(parents=True)
    chave = cfg / "sync_house.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o600)
    vault = tmp_path / "vault"
    vault.mkdir()
    for nome in sh.MANUAIS:
        (vault / f"{nome}.md").write_text(f"# {nome}\n\nTexto sem nada a remover.\n", encoding="utf-8")
    house = tmp_path / "house"
    house.mkdir()
    (house / "README.md").write_text(
        "# docs/house\n\n<!-- sync:tabela inicio -->\n<!-- sync:tabela fim -->\n", encoding="utf-8"
    )
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    return home, vault, house


def _gate(home: Path, tmp_path: Path, house: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": "", "HOME": str(home)}
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(GATE), "--check", "--house", str(house)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
        check=False,
    )


def test_arquivo_local_com_chave_no_padrao_confere_e_passa(tmp_path: Path) -> None:
    home, vault, house = _maquina(tmp_path)
    (home / ".config" / "bigtech" / "vault_path").write_text(f"{vault}\n", encoding="utf-8")
    r = _gate(home, tmp_path, house)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout
    assert "REPROVADO" not in r.stdout


def test_arquivo_local_com_manual_sabotado_reprova_com_1(tmp_path: Path) -> None:
    home, vault, house = _maquina(tmp_path)
    (home / ".config" / "bigtech" / "vault_path").write_text(f"{vault}\n", encoding="utf-8")
    (vault / "ORG.md").write_text("sabotado no vault\n", encoding="utf-8")
    r = _gate(home, tmp_path, house)
    assert r.returncode == 1
    assert "REPROVADO" in r.stdout
    assert "PASS" not in r.stdout


def test_variavel_de_ambiente_vence_o_arquivo_local(tmp_path: Path) -> None:
    home, vault, house = _maquina(tmp_path)
    (home / ".config" / "bigtech" / "vault_path").write_text(str(tmp_path / "nao_existe") + "\n", encoding="utf-8")
    r = _gate(home, tmp_path, house, {"BIGTECH_VAULT": str(vault)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_sem_vault_nenhum_e_com_chave_reprova_com_erro_de_uso(tmp_path: Path) -> None:
    home, _vault, house = _maquina(tmp_path)
    r = _gate(home, tmp_path, house)
    assert r.returncode == 1
    assert "REPROVADO" in r.stdout
    assert "PASS" not in r.stdout
