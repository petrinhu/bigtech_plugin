"""Roteamento derivado da prosa (CONS-R5).

Deriva do disco o conjunto esperado (71 agents e 15 skills, sem github-gossips,
que sai do plugin pela CONS-R7) e confere, na prosa de
agents/cosimo-chief-of-staff.md e skills/bigtech/SKILL.md, que cada um é roteável.
A raiz é parametrizável por BIGTECH_ROOT, para rodar numa cópia (sabotagem).
"""
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("BIGTECH_ROOT", Path(__file__).resolve().parents[2]))
PROSA = [ROOT / "agents" / "cosimo-chief-of-staff.md", ROOT / "skills" / "bigtech" / "SKILL.md"]
SKILLS_FORA_DO_PLUGIN = {"github-gossips"}
TOTAL_AGENTS = 71
TOTAL_SKILLS = 15


def _prosa():
    return "\n".join(p.read_text(encoding="utf-8") for p in PROSA)


def _agents():
    return sorted(p.stem for p in (ROOT / "agents").glob("*.md"))


def _skills():
    nomes = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    return [s for s in nomes if s not in SKILLS_FORA_DO_PLUGIN]


def _roteavel_agent(nome, texto):
    # bigtech:x conta; /bigtech:x NÃO conta para o agent x (é a skill). Nome curto conta
    # só fora de "bigtech:" e de "/" (evita casar a skill homônima).
    forma_prefixada = rf"(?<![/\w-])bigtech:{re.escape(nome)}(?![\w-])"
    forma_curta = rf"(?<![\w:/-]){re.escape(nome)}(?![\w-])"
    return re.search(forma_prefixada, texto) or re.search(forma_curta, texto)


def _roteavel_skill(nome, texto):
    return re.search(rf"/bigtech:{re.escape(nome)}(?![\w-])", texto)


def test_conjunto_esperado_do_disco():
    # Piso: varredura vazia reprova (não passa por zero).
    assert len(_agents()) == TOTAL_AGENTS, f"agents no disco: {len(_agents())}"
    assert len(_skills()) == TOTAL_SKILLS, f"skills no disco (sem github-gossips): {len(_skills())}"


def test_todo_agent_e_roteavel_pela_prosa():
    texto = _prosa()
    sem_rota = [a for a in _agents() if not _roteavel_agent(a, texto)]
    assert not sem_rota, f"agents sem rota na prosa: {sem_rota}"


def test_toda_skill_e_roteavel_pela_prosa():
    texto = _prosa()
    sem_rota = [s for s in _skills() if not _roteavel_skill(s, texto)]
    assert not sem_rota, f"skills sem rota na prosa: {sem_rota}"
