"""Testes do gate 4 do preci: paridade de versao entre os manifestos (CONS-16).

Cada caso monta um plugin descartavel em tmp_path e roda o script por subprocess,
do mesmo jeito que o preci.sh roda. Codigos de saida: 0 igual, 1 divergente,
2 ausente ou ilegivel (reprova).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
RAIZ_REAL = SCRIPTS.parent
GATE = SCRIPTS / "check_paridade_versao.py"

# Decisao D1 (2026-11-20): pubmed saiu do bundle (retirado do marketplace life-sciences).
DEPENDENCIAS_ESPERADAS = {
    "bigtech",
    "playwright@claude-plugins-official",
    "superpowers@claude-plugins-official",
    "frontend-design@claude-plugins-official",
}
MARKETPLACES_ESPERADOS = {"claude-plugins-official"}


def _grava(caminho: Path, dados: object) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def _monta(
    raiz: Path,
    *,
    nucleo: str = "2.0.0",
    entrada_nucleo: str = "2.0.0",
    entrada_bundle: str = "2.0.0",
    bundle: str = "2.0.0",
) -> Path:
    _grava(raiz / ".claude-plugin" / "plugin.json", {"name": "bigtech", "version": nucleo})
    _grava(
        raiz / ".claude-plugin" / "marketplace.json",
        {
            "name": "petrinhu",
            "plugins": [
                {"name": "bigtech", "source": "./", "version": entrada_nucleo},
                {
                    "name": "bigtech-completo",
                    "source": "./bundles/bigtech-completo",
                    "version": entrada_bundle,
                },
            ],
        },
    )
    _grava(
        raiz / "bundles" / "bigtech-completo" / ".claude-plugin" / "plugin.json",
        {"name": "bigtech-completo", "version": bundle},
    )
    return raiz


def _roda(raiz: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(raiz)],
        capture_output=True,
        text=True,
        check=False,
    )


def _saida(proc: subprocess.CompletedProcess[str]) -> str:
    return proc.stdout + proc.stderr


def test_versoes_iguais_passam(tmp_path: Path) -> None:
    proc = _roda(_monta(tmp_path))
    assert proc.returncode == 0, _saida(proc)


def test_bundle_divergente_reprova_e_nomeia_o_bundle(tmp_path: Path) -> None:
    proc = _roda(_monta(tmp_path, bundle="1.9.0"))
    assert proc.returncode == 1, _saida(proc)
    assert "bundles/bigtech-completo" in _saida(proc)


def test_segunda_entrada_do_marketplace_divergente_reprova(tmp_path: Path) -> None:
    # Caso que o gate antigo deixava passar: lia so plugins[0] (a entrada do nucleo).
    proc = _roda(_monta(tmp_path, entrada_bundle="1.9.0"))
    assert proc.returncode == 1, _saida(proc)


def test_entrada_do_nucleo_divergente_reprova(tmp_path: Path) -> None:
    proc = _roda(_monta(tmp_path, entrada_nucleo="1.0.0"))
    assert proc.returncode == 1, _saida(proc)


def test_manifesto_do_bundle_ausente_da_erro(tmp_path: Path) -> None:
    raiz = _monta(tmp_path)
    (raiz / "bundles" / "bigtech-completo" / ".claude-plugin" / "plugin.json").unlink()
    proc = _roda(raiz)
    assert proc.returncode == 2, _saida(proc)


def test_entrada_bigtech_completo_ausente_da_erro(tmp_path: Path) -> None:
    raiz = _monta(tmp_path)
    _grava(
        raiz / ".claude-plugin" / "marketplace.json",
        {"name": "petrinhu", "plugins": [{"name": "bigtech", "version": "2.0.0"}]},
    )
    proc = _roda(raiz)
    assert proc.returncode == 2, _saida(proc)


def test_versao_vazia_da_erro(tmp_path: Path) -> None:
    proc = _roda(_monta(tmp_path, nucleo=""))
    assert proc.returncode == 2, _saida(proc)


def test_json_ilegivel_da_erro(tmp_path: Path) -> None:
    raiz = _monta(tmp_path)
    (raiz / ".claude-plugin" / "plugin.json").write_text("{nao e json", encoding="utf-8")
    proc = _roda(raiz)
    assert proc.returncode == 2, _saida(proc)


def test_repositorio_real_tem_versoes_casadas() -> None:
    proc = _roda(RAIZ_REAL)
    assert proc.returncode == 0, _saida(proc)


def test_bundle_declara_exatamente_os_recomendados() -> None:
    bundle = json.loads(
        (RAIZ_REAL / "bundles" / "bigtech-completo" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    assert set(bundle["dependencies"]) == DEPENDENCIAS_ESPERADAS


def test_allowlist_cobre_os_marketplaces_das_dependencias() -> None:
    market = json.loads(
        (RAIZ_REAL / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    bundle = json.loads(
        (RAIZ_REAL / "bundles" / "bigtech-completo" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    permitidos = set(market["allowCrossMarketplaceDependenciesOn"])
    externos = {dep.split("@", 1)[1] for dep in bundle["dependencies"] if "@" in dep}
    assert externos == MARKETPLACES_ESPERADOS
    assert externos <= permitidos
    assert "life-sciences" not in permitidos
