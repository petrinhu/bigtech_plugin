#!/usr/bin/env python3
# tools/intake_agent_bridge.py -- ponte agentiva sem LLM (Fase 5 / TAB-CONC-001)
# SPDX-License-Identifier: Apache-2.0
# Licença: Apache-2.0 (ver NOTICE na raiz do plugin).
# Derivado do projeto standalone tab_pendencias, do mesmo autor, relicenciado sob Apache-2.0.
"""
intake_agent_bridge -- parse mecanico de DISCOVERED_WORK + heuristica de flags.

Fronteira de responsabilidade (ADR-0002 / plano Fase 5):
  - O AGENTE (LLM) julga prosa e preenche o bloco DISCOVERED_WORK.
  - Este modulo NAO faz NLP/semantica: so parseia chaves estruturadas e
    mapeia blast_radius -> flags booleanas de WorkCandidate.
  - O MOTOR (`todo_intake.run_intake`) persiste a rota mecanica.

Formato (plano TAB-CONC-001)::

    DISCOVERED_WORK
    source_item: <ID atual>
    description: <trabalho descoberto>
    evidence: <arquivo:linha/teste/log>
    known_dependencies: <IDs ou unknown>
    blast_radius: <local/component/system/unknown>

stdlib only.
"""
from __future__ import annotations

import hashlib
import re

_BLOCK_START = re.compile(r"(?m)^DISCOVERED_WORK\s*$")
_FIELD = re.compile(
    r"(?m)^(source_item|description|evidence|known_dependencies|"
    r"blast_radius|item_id|candidate_id|acceptance)\s*:\s*(.*)$"
)

VALID_BLAST = frozenset({"local", "component", "system", "unknown"})


def parse_discovered_work(block: str) -> list[dict]:
    """Extrai zero ou mais blocos DISCOVERED_WORK de um texto.

    Cada item e um dict com as chaves do formato (strings; ausentes = "").
    Blocos sem `description` nao-vazia sao ignorados.
    """
    text = block or ""
    starts = [m.start() for m in _BLOCK_START.finditer(text)]
    if not starts:
        # permite um unico bloco "nu" com as chaves sem cabecalho
        one = _parse_fields(text)
        if (one.get("description") or "").strip():
            return [one]
        return []

    chunks: list[str] = []
    for i, start in enumerate(starts):
        # conteudo apos a linha DISCOVERED_WORK
        line_end = text.find("\n", start)
        body_start = line_end + 1 if line_end >= 0 else len(text)
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        chunks.append(text[body_start:end])

    out: list[dict] = []
    for chunk in chunks:
        d = _parse_fields(chunk)
        if (d.get("description") or "").strip():
            out.append(d)
    return out


def _parse_fields(chunk: str) -> dict:
    found: dict[str, str] = {}
    for m in _FIELD.finditer(chunk or ""):
        key = m.group(1)
        val = (m.group(2) or "").strip()
        # primeira ocorrencia vence (estavel)
        if key not in found:
            found[key] = val
    return {
        "source_item": found.get("source_item", ""),
        "description": found.get("description", ""),
        "evidence": found.get("evidence", ""),
        "known_dependencies": found.get("known_dependencies", ""),
        "blast_radius": found.get("blast_radius", "unknown"),
        "item_id": found.get("item_id", ""),
        "candidate_id": found.get("candidate_id", ""),
        "acceptance": found.get("acceptance", ""),
    }


def _split_deps(raw: str) -> list[str]:
    s = (raw or "").strip()
    if not s or s.casefold() in ("unknown", "-", "—", "--", "none", "n/a"):
        return []
    out = []
    for part in re.split(r"[,;]", s):
        p = part.strip()
        if p and p.casefold() not in ("unknown",):
            out.append(p)
    return out


def _default_candidate_id(d: dict) -> str:
    if d.get("candidate_id"):
        return str(d["candidate_id"])
    basis = f"{d.get('source_item','')}|{d.get('description','')}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"disc-{digest}"


def judgment_from_discovered(d: dict) -> dict:
    """Heuristica documentada: DISCOVERED_WORK dict -> WorkCandidate-ish dict.

    Mapa blast_radius (mecanico, sem NLP sobre description):
      local     -> is_local=True, fields_complete=True
      component -> is_scoped=True, fields_complete=True
      system    -> is_foundation=True, fields_complete=True
      unknown   -> fields_complete=False (NEEDS_TRIAGE no motor)
      outro     -> igual unknown

    known_dependencies vira lista `dependencies` (tokens); token `unknown`
    sozinho nao adiciona deps e nao forca incompleto alem do blast.

    Nao atribui WSJF. item_id so se vier no bloco.
    """
    if not isinstance(d, dict):
        raise TypeError("judgment_from_discovered espera dict")
    blast = (d.get("blast_radius") or "unknown").strip().casefold()
    if blast not in VALID_BLAST:
        blast = "unknown"

    deps = _split_deps(d.get("known_dependencies") or "")
    desc = (d.get("description") or "").strip()
    fields_complete = blast != "unknown" and bool(desc)
    is_local = blast == "local"
    is_scoped = blast == "component"
    is_foundation = blast == "system"

    return {
        "candidate_id": _default_candidate_id(d),
        "description": desc,
        "source": "agent",
        "evidence": (d.get("evidence") or "").strip(),
        "source_item": (d.get("source_item") or "").strip(),
        "dependencies": deps,
        "item_id": (d.get("item_id") or "").strip(),
        "acceptance": (d.get("acceptance") or "").strip(),
        "fields_complete": fields_complete,
        "authority_ok": True,
        "is_local": is_local,
        "is_scoped": is_scoped,
        "is_foundation": is_foundation,
        "blast_radius": blast,
    }
