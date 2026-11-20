# SPDX-License-Identifier: Apache-2.0
"""Testes do endurecimento da escrita de estado do tab_pendencias (CONS-05S).

Contrato testado: antes de gravar, o diretorio-alvo e conferido com lstat.
Symlink e diretorio de outro dono sao recusados com erro claro e nada e
gravado. O temporario vem de mkstemp, nunca de um nome previsivel
(`<arquivo>.tmp`), entao um `.tmp` plantado como symlink nao e seguido.

Os casos de dono simulam outro usuario com monkeypatch de os.getuid. Todo
diretorio de teste mora em tmp_path (repo git descartavel); nada e escrito
fora dele.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[2] / "skills" / "tab_pendencias" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import concurrent_inbox as CI
import intake_journal as IJ
import todo_lock as TL
import todo_sync as TS

pytestmark = pytest.mark.skipif(
    not hasattr(os, "getuid"), reason="dono de diretorio so existe em POSIX"
)

VICTIM_TEXT = "CONTEUDO ORIGINAL DO ALVO, NAO PODE MUDAR\n"


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _outro_uid(monkeypatch) -> None:
    """Faz o processo parecer outro usuario: todo dono existente diverge."""
    uid_real = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: uid_real + 1)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd, check=True, capture_output=True, text=True,
    )


def _repo_com_commit(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "init")
    return repo


# ---------------------------------------------------------------------------
# concurrent_inbox
# ---------------------------------------------------------------------------

_TS = "20261120-120000"


def test_inbox_symlink_para_fora_e_recusado(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    fora = tmp_path / "fora"
    fora.mkdir()
    (repo / "inbox").symlink_to(fora, target_is_directory=True)

    with pytest.raises(CI.ConcurrentInboxError):
        CI.write_discovery(str(repo), "s1", "achado", "corpo\n", timestamp=_TS)

    assert list(fora.iterdir()) == [], "nada pode ser gravado no alvo do symlink"


def test_tmp_plantado_como_symlink_nao_e_seguido(tmp_path):
    repo = tmp_path / "repo"
    (repo / "inbox").mkdir(parents=True)
    victim = tmp_path / "victim.md"
    victim.write_text(VICTIM_TEXT, encoding="utf-8")
    md5_antes = _md5(victim)
    # nome que a versao antiga usava: <path>.tmp, previsivel pelo timestamp
    previsivel = repo / "inbox" / f"{_TS}-s1-achado.md.tmp"
    previsivel.symlink_to(victim)

    path = CI.write_discovery(str(repo), "s1", "achado", "corpo\n", timestamp=_TS)

    assert _md5(victim) == md5_antes, "o alvo do .tmp plantado nao pode ser tocado"
    assert Path(path).read_text(encoding="utf-8") == "corpo\n"


def test_inbox_de_outro_dono_e_recusado(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "inbox").mkdir(parents=True)

    _outro_uid(monkeypatch)
    with pytest.raises(CI.ConcurrentInboxError):
        CI.write_discovery(str(repo), "s1", "achado", "corpo\n", timestamp=_TS)

    assert [p for p in (repo / "inbox").iterdir()] == []


# ---------------------------------------------------------------------------
# intake_journal
# ---------------------------------------------------------------------------

def test_journal_symlink_para_fora_e_recusado(tmp_path):
    fora = tmp_path / "fora"
    fora.mkdir()
    journal = tmp_path / "journal"
    journal.symlink_to(fora, target_is_directory=True)

    with pytest.raises(IJ.IntakeJournalError):
        IJ.write_candidate("cand-1", source="test", description="d",
                           journal_dir=str(journal))

    assert list(fora.iterdir()) == [], "nada pode ser gravado no alvo do symlink"


def test_journal_de_outro_dono_e_recusado(tmp_path, monkeypatch):
    journal = tmp_path / "journal"
    journal.mkdir()

    _outro_uid(monkeypatch)
    with pytest.raises(IJ.IntakeJournalError):
        IJ.write_candidate("cand-1", source="test", description="d",
                           journal_dir=str(journal))

    assert list(journal.iterdir()) == []


# ---------------------------------------------------------------------------
# todo_lock
# ---------------------------------------------------------------------------

def test_lock_dir_symlink_para_fora_e_recusado(tmp_path):
    repo = _repo_com_commit(tmp_path)
    fora = tmp_path / "fora"
    fora.mkdir()
    (repo / ".git" / "tab-pendencias").symlink_to(fora, target_is_directory=True)
    todo = repo / "TODO.md"
    todo.write_text("x\n", encoding="utf-8")

    with pytest.raises(TL.TodoLockError):
        TL.default_lock_path(str(todo))

    assert list(fora.iterdir()) == [], "o lock nao pode nascer no alvo do symlink"


def test_lock_dir_de_outro_dono_e_recusado(tmp_path, monkeypatch):
    repo = _repo_com_commit(tmp_path)
    todo = repo / "TODO.md"
    todo.write_text("x\n", encoding="utf-8")

    _outro_uid(monkeypatch)
    with pytest.raises(TL.TodoLockError):
        TL.default_lock_path(str(todo))


# ---------------------------------------------------------------------------
# todo_sync
# ---------------------------------------------------------------------------

def test_ref_plantado_como_symlink_nao_e_seguido(tmp_path):
    repo = _repo_com_commit(tmp_path)
    victim = tmp_path / "victim.txt"
    victim.write_text(VICTIM_TEXT, encoding="utf-8")
    md5_antes = _md5(victim)
    (repo / ".git" / "todo-sync-ref").symlink_to(victim)

    TS._save_sync_ref(str(repo))

    assert _md5(victim) == md5_antes, "o alvo do symlink do ref nao pode ser tocado"


def test_ref_de_git_dir_de_outro_dono_nao_e_gravado(tmp_path, monkeypatch):
    repo = _repo_com_commit(tmp_path)
    ref = repo / ".git" / "todo-sync-ref"

    _outro_uid(monkeypatch)
    TS._save_sync_ref(str(repo))

    assert not ref.exists(), "com dono alheio nada pode ser gravado"
