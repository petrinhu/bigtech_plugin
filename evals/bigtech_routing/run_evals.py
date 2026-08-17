#!/usr/bin/env python3
"""Evals determinísticos de roteamento /bigtech (BT-8).

Harness OFFLINE de política de classificação pós-BT-5:
  - perfil canônico: early | scale | bigtech
  - piso early; nunca emitir profile=solo
  - headcount/capacity com peso 0 no score de perfil
  - criticidade/compliance elevam agents (e às vezes o porte)

Não substitui eval LLM real da skill; só trava a política.
Stdlib only. Exit 0 se todos pass; 1 se fail.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "cases.json"

VALID_PROFILES = ("early", "scale", "bigtech")
PROFILE_RANK = {"early": 0, "scale": 1, "bigtech": 2}
DEPRECATED_PROFILE_ALIASES = {"solo": "early"}

# Dimensões de ESCALA/COMPLEXIDADE do porte (0..3 cada).
# criticality/compliance NÃO entram no score de porte sozinhas: elevam agents
# (CISO/CLO) e só empurram o porte quando coexistem com sinais sistêmicos
# (multi-repo, multi-produto, etc.)  -  espelha Cosimo pós-BT-5 / CASE-C.
PROFILE_DIMS = (
    "blast_radius",
    "coupling",
    "reversibility",
    "complexity",
    "distribution",
    "maintenance",
)

# Dimensões de risco (elevam governança; peso 0 no score de porte isolado).
RISK_DIMS = ("criticality", "compliance")

# Faixas da soma PROFILE_DIMS (6 × 0..3 = 0..18).
# 0..8 early | 9..15 scale | 16+ bigtech
SUM_EARLY_MAX = 8
SUM_SCALE_MAX = 15

# Agents base por porte (hints de constelação; não é o mapa completo da skill).
BASE_AGENTS: dict[str, list[str]] = {
    "early": ["celso-ceo", "caetano-cto"],
    "scale": [
        "celso-ceo",
        "capitolino-cpo",
        "caetano-cto",
        "camilo-cmo",
        "cosmo-coo",
        "narciso-ciso",
    ],
    "bigtech": [
        "celso-ceo",
        "capitolino-cpo",
        "caetano-cto",
        "camilo-cmo",
        "cosmo-coo",
        "narciso-ciso",
        "candido-cdo",
        "caio-caio",
        "confucio-cfo",
        "cicero-cro",
        "claudio-clo",
    ],
}


def _clamp_dim(value: Any) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(3, n))


def normalize_profile_hint(raw: Any) -> str | None:
    """Normaliza hint legado; solo → early. Desconhecido → None."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    if s in DEPRECATED_PROFILE_ALIASES:
        return DEPRECATED_PROFILE_ALIASES[s]
    if s in VALID_PROFILES:
        return s
    return None


def score_signals(signals: dict[str, Any]) -> int:
    """Soma das dimensões de porte (escala/complexidade). headcount peso 0."""
    total = 0
    for dim in PROFILE_DIMS:
        total += _clamp_dim(signals.get(dim, 0))
    return total


def risk_score(signals: dict[str, Any]) -> int:
    """Soma criticality+compliance (só governança / elevação de agents)."""
    total = 0
    for dim in RISK_DIMS:
        total += _clamp_dim(signals.get(dim, 0))
    return total


def classify(signals: dict[str, Any]) -> dict[str, Any]:
    """Classifica porte + hints de agents de forma determinística (pós-BT-5)."""
    signals = dict(signals or {})
    legacy = normalize_profile_hint(signals.get("legacy_porte_hint"))
    score = score_signals(signals)
    risk = risk_score(signals)

    criticality = _clamp_dim(signals.get("criticality", 0))
    compliance = _clamp_dim(signals.get("compliance", 0))
    blast = _clamp_dim(signals.get("blast_radius", 0))
    coupling = _clamp_dim(signals.get("coupling", 0))
    distribution = _clamp_dim(signals.get("distribution", 0))
    complexity = _clamp_dim(signals.get("complexity", 0))
    maintenance = _clamp_dim(signals.get("maintenance", 0))
    multi_product = bool(signals.get("multi_product"))
    domain = str(signals.get("domain") or "").lower()

    # Score de escala → porte base (risco isolado não sobe cerimônia).
    if score <= SUM_EARLY_MAX:
        profile = "early"
    elif score <= SUM_SCALE_MAX:
        profile = "scale"
    else:
        profile = "bigtech"

    # Elevacoes sistemicas (nao headcount).
    # Multi-repo / ecossistema com consumidores: no minimo scale.
    if (
        blast >= 3
        and (coupling >= 2 or distribution >= 2)
        and PROFILE_RANK[profile] < PROFILE_RANK["scale"]
    ):
        profile = "scale"
    # Multi-produto + risco no teto → bigtech.
    if multi_product and criticality >= 3 and compliance >= 3:
        profile = "bigtech"
    # Ecossistema no teto + complexidade/manutenção altas → bigtech.
    if (
        blast >= 3
        and coupling >= 3
        and distribution >= 3
        and (multi_product or (complexity >= 3 and maintenance >= 3))
    ):
        profile = "bigtech"

    # Garantia: perfil sempre canônico; solo nunca.
    if profile not in VALID_PROFILES or profile == "solo":
        profile = "early"
    # legacy solo→early só reforça piso; não rebaixa scale/bigtech.
    _ = legacy

    agents = list(BASE_AGENTS[profile])

    # Early-stage com usuarios reais (distribution>=2): Pipeline-Lean + CPO.
    if profile == "early" and distribution >= 2 and "capitolino-cpo" not in agents:
        agents.append("capitolino-cpo")

    # Criticidade eleva agents de segurança/jurídico sem forçar bigtech.
    if criticality >= 3 or compliance >= 3 or domain in {
        "health-pii",
        "health",
        "payments",
        "finance",
    }:
        for a in ("narciso-ciso", "claudio-clo"):
            # CLO quando compliance regulado (saúde) ou compliance==3.
            if a == "claudio-clo" and compliance < 3 and domain not in {
                "health-pii",
                "health",
            }:
                continue
            if a not in agents:
                agents.append(a)
    elif (criticality >= 2 or compliance >= 2) and "narciso-ciso" not in agents:
        agents.append("narciso-ciso")

    if domain in {"payments", "finance"} and "narciso-ciso" not in agents:
        agents.append("narciso-ciso")

    # IA como capability central → CAIO + applied-ai-engineer em qualquer porte.
    if signals.get("ai_central_capability"):
        for a in ("caio-caio", "applied-ai-engineer"):
            if a not in agents:
                agents.append(a)

    pipeline = {
        "early": "Pipeline-Early",
        "scale": "Pipeline-Padrão",
        "bigtech": "Pipeline-Completo",
    }[profile]
    if profile == "early" and (
        distribution >= 2 or "capitolino-cpo" in agents
    ):
        pipeline = "Pipeline-Lean"

    return {
        "profile": profile,
        "score": score,
        "risk_score": risk,
        "pipeline": pipeline,
        "agents": agents,
        "legacy_normalized": legacy,
        # Exposto para auditoria do harness: headcount lido e IGNORADO.
        "headcount_ignored": signals.get("headcount"),
        "capacity_ignored": signals.get("capacity"),
    }


def _check_case(case: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    signals = case.get("signals") or {}
    result = classify(signals)
    profile = result["profile"]
    reasons: list[str] = []

    # Nunca solo
    if profile == "solo" or profile not in VALID_PROFILES:
        reasons.append(f"profile invalido {profile!r} (piso early; sem solo)")

    forbidden = set(case.get("forbidden_profiles") or [])
    forbidden.add("solo")  # invariante global
    if profile in forbidden:
        reasons.append(f"profile={profile} esta em forbidden={sorted(forbidden)}")

    allowed = case.get("allowed_profiles")
    expected = case.get("expected_profile")
    if allowed is not None and profile not in set(allowed):
        reasons.append(f"profile={profile} fora de allowed={allowed}")
    elif expected is not None and profile != expected:
        reasons.append(f"profile={profile} != expected={expected}")

    # Min agents (hints)
    min_agents = case.get("expected_min_agents") or []
    got = set(result["agents"])
    missing = [a for a in min_agents if a not in got]
    if missing:
        reasons.append(f"agents faltando: {missing}")

    # Headcount não pode ser a única razão de scale/bigtech: se todas as
    # dims de score são 0 e headcount alto, perfil deve ser early.
    if (
        score_signals(signals) == 0
        and _clamp_dim(signals.get("headcount", 0)) == 0
        and int(signals.get("headcount") or 0) > 10
        and profile != "early"
    ):
        reasons.append("headcount alto promoveu porte (peso deve ser 0)")

    ok = not reasons
    msg = "OK" if ok else "; ".join(reasons)
    return ok, msg, result


def load_cases(path: Path = CASES_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def run(path: Path = CASES_PATH) -> int:
    data = load_cases(path)
    cases = data.get("cases") or []
    if not cases:
        print("Nenhum case em", path, file=sys.stderr)
        return 1

    # Colunas da tabela
    rows: list[tuple[str, str, str, str, str]] = []
    failed = 0
    for case in cases:
        ok, msg, result = _check_case(case)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        rows.append(
            (
                str(case.get("id", "?")),
                status,
                str(result.get("profile")),
                str(case.get("expected_profile") or case.get("allowed_profiles")),
                msg,
            )
        )

    # Larguras
    headers = ("ID", "STATUS", "GOT", "EXPECTED", "DETAIL")
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    print(f"bigtech routing evals  -  {path}")
    # ASCII-safe: Windows CI default (cp1252) cannot encode U+2192.
    print(
        f"policy: profiles={list(VALID_PROFILES)} "
        f"floor=early solo->early headcount_weight=0"
    )
    print()
    print(fmt(headers))
    print(fmt(tuple("-" * w for w in widths)))
    for row in rows:
        print(fmt(row))
    print()
    total = len(rows)
    passed = total - failed
    print(f"resultado: {passed}/{total} PASS, {failed} FAIL")
    return 0 if failed == 0 else 1


def _ensure_utf8_stdio() -> None:
    """Windows runners often use cp1252; reconfigure when the host allows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdio()
    argv = list(sys.argv[1:] if argv is None else argv)
    path = CASES_PATH
    if argv:
        path = Path(argv[0])
    try:
        return run(path)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"erro ao rodar evals: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
