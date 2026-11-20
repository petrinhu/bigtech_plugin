"""Testes do gate ZERO-ORFAOS (scripts/validate_plugin.py), CONS-03.

Contrato publico testado:
  - `run(root)` devolve (dimensoes, exit_code, n_md); exit_code 0 ou 1;
  - o CLI `python3 scripts/validate_plugin.py --root DIR` sai 0 ou 1.

Cada teste monta uma arvore minima em tmp_path e nao depende do inventario
vivo do repo. Os asserts usam o par (dimensao, caminho relativo) da violacao.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_plugin as vp

VALIDATOR = SCRIPTS / "validate_plugin.py"

SKILL_LIMPA = "---\nname: demo\n---\n\nSkill de exemplo sem referencias pessoais.\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _base(root: Path) -> None:
    """Arvore minima valida: uma skill .md limpa."""
    _write(root / "skills/demo/SKILL.md", SKILL_LIMPA)


def _exit_code(root: Path) -> int:
    return vp.run(root)[1]


def _violacoes(root: Path) -> set[tuple[str, str]]:
    results, _code, _n = vp.run(root)
    return {(d.name, v.path) for d in results for v in d.violations}


def _relatorio(root: Path) -> str:
    results, _code, _n = vp.run(root)
    return "\n".join(
        f"[{d.status()}] {d.name}: " + "; ".join(str(v) for v in d.violations)
        for d in results
    )


# --- 1. Lista de excluidos revogada em 20/11/2026 -----------


@pytest.mark.parametrize(
    "rel,content",
    [
        (
            "agents/dr-advogado.md",
            "---\nname: dr-advogado\n---\n\n# dr-advogado\n\nAgente de pericia.\n",
        ),
        (
            "skills/proj_jogo/SKILL.md",
            "---\nname: proj_jogo\n---\n\nUse /proj_jogo para projetos de jogo.\n",
        ),
        (
            "skills/pericia-medica/SKILL.md",
            "---\nname: pericia-medica\n---\n\nUse /pericia-medica.\n",
        ),
        (
            "docs/guias/mapa.md",
            "Ver o agent game-producer e o level-designer.\n",
        ),
    ],
)
def test_aceita_mencao_a_agent_que_agora_entra_no_plugin(tmp_path, rel, content):
    _base(tmp_path)
    _write(tmp_path / rel, content)

    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


# --- 2. Termos pessoais novos (markdown) -------------------------------------


@pytest.mark.parametrize(
    "termo",
    [
        "gusworld",
        "GusWorld",
        "glintfx",
        "GlintFx",
        "drpetrus",
        "Justiça Federal",
        "justica federal",
        "JUSTIÇA FEDERAL",
    ],
)
def test_reprova_termo_pessoal_novo_em_markdown(tmp_path, termo):
    _base(tmp_path)
    _write(tmp_path / "agents/gameplay.md", f"Projeto de referencia: {termo}.\n")

    assert _exit_code(tmp_path) == 1, _relatorio(tmp_path)


# --- 3. Dimensoes 2 e 3 leem .py, .sh e .json de skills/ ---------------------


@pytest.mark.parametrize(
    "arquivo",
    ["skills/demo/tool.py", "skills/demo/run.sh", "skills/demo/config.json"],
)
@pytest.mark.parametrize(
    "termo,dimensao",
    [("/home/petrus/projetos", "local_paths"), ("GusWorld", "personal")],
)
def test_reprova_caminho_local_ou_termo_pessoal_em_codigo_de_skill(
    tmp_path, arquivo, termo, dimensao
):
    _base(tmp_path)
    _write(tmp_path / arquivo, f"# ref: {termo}\n")

    assert (dimensao, arquivo) in _violacoes(tmp_path), _relatorio(tmp_path)


def test_nao_aplica_regra_de_wikilink_a_codigo_de_skill(tmp_path):
    """Guarda contra falso positivo: `[[ ]]` de shell nao e wikilink."""
    _base(tmp_path)
    _write(
        tmp_path / "skills/demo/run.sh",
        "#!/usr/bin/env bash\nif [[ -f arquivo ]]; then echo ok; fi\n",
    )

    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


def test_mantem_wikilink_proibido_em_markdown_de_skill(tmp_path):
    """Regressao: a dimensao 1 continua valendo para .md dentro de skills/."""
    _write(tmp_path / "skills/demo/SKILL.md", "Veja [[Projects/x]].\n")

    assert ("wikilinks", "skills/demo/SKILL.md") in _violacoes(tmp_path)


# --- 4. Varredura vazia reprova (fail-closed) ---------------------------------------


def test_reprova_raiz_vazia(tmp_path):
    assert _exit_code(tmp_path) == 1, _relatorio(tmp_path)
    assert "varredura vazia reprova (fail-closed)" in _relatorio(tmp_path)


def test_reprova_raiz_sem_nenhum_md_so_com_codigo_de_skill(tmp_path):
    _write(tmp_path / "skills/demo/tool.py", "print('ok')\n")

    assert _exit_code(tmp_path) == 1, _relatorio(tmp_path)


def test_cli_reprova_raiz_inexistente(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(tmp_path / "nao-existe")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_cli_reprova_termo_pessoal_com_exit_1(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "agents/x.md", "Autor: GusWorld\n")

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1, proc.stdout + proc.stderr


# --- 5. Arvore limpa passa (guarda contra falso positivo) --------------------


def test_aceita_arvore_limpa_com_agent_skill_e_codigo(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "agents/demo-agent.md", "# demo-agent\n\nAgente de exemplo.\n")
    _write(tmp_path / "skills/demo/tool.py", "VERSAO = '1'\n")

    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


# --- 4. Fornecedor de hospedagem numa lista generica (incluido em 2026-11-20) -


def test_aceita_fornecedor_de_hospedagem_em_lista_generica(tmp_path):
    _base(tmp_path)
    _write(
        tmp_path / "docs/guias/infra.md",
        "Cloud (AWS/GCP/Azure) ou VPS (Hetzner, Hostinger) ou shared hosting.\n",
    )

    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


def test_reprova_termo_pessoal_na_mesma_lista_de_fornecedores(tmp_path):
    _base(tmp_path)
    _write(
        tmp_path / "docs/guias/infra.md",
        "Cloud (AWS/GCP/Azure) ou VPS (Hetzner, GusWorld) ou shared hosting.\n",
    )

    assert _exit_code(tmp_path) == 1, _relatorio(tmp_path)


# --- 6. Escopo: so arquivos versionados pelo git (CONS-03B) ------------------


def _git_init(root: Path) -> None:
    """Cria um repo git descartavel em `root` (sem commit: so o index importa)."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def _git_add(root: Path, *rels: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "--", *rels], check=True)


def test_ignora_termo_pessoal_em_node_modules_nao_versionado(tmp_path):
    """Caso do bug: node_modules presente no disco, ignorado pelo git, nao reprova."""
    _git_init(tmp_path)
    _write(tmp_path / "skills/demo/SKILL.md", SKILL_LIMPA)
    _git_add(tmp_path, "skills/demo/SKILL.md")
    _write(tmp_path / "skills/demo/node_modules/x.json", '{"autor": "GusWorld"}\n')

    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


def test_reprova_mesmo_termo_pessoal_em_arquivo_versionado(tmp_path):
    _git_init(tmp_path)
    _write(tmp_path / "skills/demo/SKILL.md", SKILL_LIMPA)
    _write(tmp_path / "skills/demo/config.json", '{"autor": "GusWorld"}\n')
    _git_add(tmp_path, "skills/demo/SKILL.md", "skills/demo/config.json")

    assert ("personal", "skills/demo/config.json") in _violacoes(tmp_path), _relatorio(
        tmp_path
    )


def test_repo_git_sem_arquivo_versionado_no_escopo_reprova(tmp_path):
    """Lista vazia reprova (fail-closed): agente nao aprova por silencio."""
    _git_init(tmp_path)
    _write(tmp_path / "agents/nao-add.md", "# nao versionado\n")

    assert _exit_code(tmp_path) == 1, _relatorio(tmp_path)


def test_cli_fora_de_git_avisa_que_varre_disco(tmp_path):
    _base(tmp_path)

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "fora de git: varredura de disco" in proc.stdout, proc.stdout + proc.stderr


def test_cli_em_repo_git_avisa_que_usa_git_ls_files(tmp_path):
    _git_init(tmp_path)
    _write(tmp_path / "skills/demo/SKILL.md", SKILL_LIMPA)
    _git_add(tmp_path, "skills/demo/SKILL.md")

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "git ls-files" in proc.stdout, proc.stdout + proc.stderr
    assert "fora de git" not in proc.stdout, proc.stdout


# --- CONS-13. Dimensao 5 varre docs/house sem excecao e resolve ${CLAUDE_PLUGIN_ROOT} ---


def test_reprova_link_quebrado_plantado_em_docs_house(tmp_path):
    """Dimensao 5 (links orfaos) vale tambem para a copia de docs/house."""
    _base(tmp_path)
    _write(tmp_path / "docs/house/ORG.md", "Veja [falta](nao_existe.md).\n")
    assert ("orphan_links", "docs/house/ORG.md") in _violacoes(tmp_path), _relatorio(tmp_path)


def test_aceita_link_valido_entre_arquivos_de_docs_house(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/house/ORG.md", "Veja [irmao](CONTRACT.md).\n")
    _write(tmp_path / "docs/house/CONTRACT.md", "# c\n")
    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


def test_resolve_claude_plugin_root_em_agent(tmp_path):
    """`${CLAUDE_PLUGIN_ROOT}/docs/house/X.md` resolve contra a raiz do plugin."""
    _base(tmp_path)
    _write(tmp_path / "docs/house/CONTRACT.md", "# c\n")
    _write(
        tmp_path / "agents/demo-agent.md",
        "Manual: [contrato](${CLAUDE_PLUGIN_ROOT}/docs/house/CONTRACT.md).\n",
    )
    assert _exit_code(tmp_path) == 0, _relatorio(tmp_path)


def test_reprova_claude_plugin_root_apontando_para_alvo_inexistente(tmp_path):
    _base(tmp_path)
    _write(
        tmp_path / "agents/demo-agent.md",
        "Manual: [sumiu](${CLAUDE_PLUGIN_ROOT}/docs/house/MANUAL_QUE_NAO_EXISTE.md).\n",
    )
    assert ("orphan_links", "agents/demo-agent.md") in _violacoes(tmp_path), _relatorio(tmp_path)
