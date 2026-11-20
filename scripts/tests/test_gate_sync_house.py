"""Testes da trava de CI e do preci para o sync de docs/house (CONS-10).

Prova as saidas reais por subprocess: 0 conferido, 3 nao conferido (nunca PASS),
1 reprovado e 2 erro de uso (reprova). Usa chave e vault descartaveis em tmp.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_house as sh

GATE = SCRIPTS / "gate_sync_house.py"
CHAVE = b"\x03" * 32


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    for nome in sh.MANUAIS:
        (vault / f"{nome}.md").write_text(
            f"# {nome}\n\nTexto sem nada a remover.\n", encoding="utf-8"
        )
    return vault


def _house_gravada(tmp_path: Path, vault: Path) -> Path:
    house = tmp_path / "house"
    house.mkdir()
    (house / "README.md").write_text(
        "# docs/house\n\n<!-- sync:tabela inicio -->\n<!-- sync:tabela fim -->\n",
        encoding="utf-8",
    )
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    return house


def _chave(tmp_path: Path) -> Path:
    arq = tmp_path / "sync_house.key"
    arq.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    arq.chmod(0o600)
    return arq


def _rodar(tmp_path: Path, args: list[str], chave: Path, ci: bool = False) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": "",
        "BIGTECH_SYNC_KEY_FILE": str(chave),
        # HOME descartavel: sem ele o gate leria ~/.config/bigtech/vault_path da maquina (CONS-10A).
        "HOME": str(tmp_path / "home_descartavel"),
        # Windows: o perfil sai de USERPROFILE; sem ele Path.home() falha (CONS-R11).
        "USERPROFILE": str(tmp_path / "home_descartavel"),
    }
    if ci:
        env["GITHUB_ACTIONS"] = "true"
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
        check=False,
    )


def test_saida_0_conferido_mostra_pass(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    house = _house_gravada(tmp_path, vault)
    r = _rodar(tmp_path, ["--vault", str(vault), "--house", str(house), "--check"], _chave(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_saida_1_vault_alterado_reprova(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    house = _house_gravada(tmp_path, vault)
    (vault / "ORG.md").write_text("mudou no vault\n", encoding="utf-8")
    r = _rodar(tmp_path, ["--vault", str(vault), "--house", str(house), "--check"], _chave(tmp_path))
    assert r.returncode == 1
    assert "REPROVADO" in r.stdout
    assert "PASS" not in r.stdout


def test_saida_3_sem_vault_e_sem_chave_nao_conferido_e_nunca_pass(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    house = _house_gravada(tmp_path, vault)
    ausente = tmp_path / "nao_existe.key"
    r = _rodar(tmp_path, ["--house", str(house), "--check"], ausente, ci=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NAO CONFERIDO" in r.stdout
    assert "::warning::" in r.stdout
    assert "PASS" not in r.stdout


def test_saida_3_sem_chave_com_vault_nao_conferido(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    house = _house_gravada(tmp_path, vault)
    ausente = tmp_path / "nao_existe.key"
    r = _rodar(tmp_path, ["--vault", str(vault), "--house", str(house), "--check"], ausente)
    assert r.returncode == 0
    assert "NAO CONFERIDO" in r.stdout
    assert "PASS" not in r.stdout


def test_saida_2_erro_de_uso_reprova(tmp_path: Path) -> None:
    # Com chave e sem vault, a conferencia exige o vault: erro 2, que a trava reprova.
    vault = _vault(tmp_path)
    house = _house_gravada(tmp_path, vault)
    r = _rodar(tmp_path, ["--house", str(house), "--check"], _chave(tmp_path))
    assert r.returncode == 1
    assert "REPROVADO" in r.stdout
    assert "PASS" not in r.stdout


@pytest.mark.parametrize("codigo", [0, 1, 2, 3])
def test_mapa_fechado_de_codigos(codigo: int, monkeypatch: pytest.MonkeyPatch) -> None:
    import gate_sync_house as gate

    monkeypatch.setattr(gate.sh, "main", lambda argv=None: codigo)
    rc = gate.main(["--check"])
    esperado = {0: 0, 1: 1, 2: 1, 3: 0}[codigo]
    assert rc == esperado
