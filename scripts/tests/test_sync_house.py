"""Testes do sync_house.py (CONS-04B): transformacoes, cabecalho e verificacao.

Contrato testado:
  - aplicar_transformacoes(corpo) -> (corpo_novo, contagem_por_id)
  - gerar_manual(texto_vault, nome, data, chave=None) -> arquivo completo
  - sincronizar(vault, house, data, modo, chave) -> ResultadoSync
      .divergentes: arquivos que nao batem com o vault
      .nao_conferido: True quando faltou a chave e o vault nao foi autenticado
  - main(argv) -> 0 ok, 1 divergencia, 2 uso/erro, 3 check sem chave (nao conferido)

Seguranca: o cabecalho NUNCA publica sha256 do texto do vault (antes da redacao).
A autenticacao da versao do vault e HMAC-SHA256 com chave local fora do repo.
Os termos privados aparecem aqui so por concatenacao.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_house as sh

CHAVE = b"\x01" * 32  # chave de teste; a real nunca entra no repo

FRASE_LONGA = (
    "As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que "
    "eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin "
    "em qualquer conflito. Onde divergirem, siga as do usuário."
)

LINHA_AUTORIDADE = (
    "**O usuário (" + "pet" + "rus) é o líder supremo e soberano de todos os projetos "
    "desta máquina.** Títulos: " + "Kai" + "ser, Presidente, Rei."
)

LINHA_WIKI_PROJETO = "- Alvos Web: [[Projects/" + "site_" + "consultorio]] · [[Projects/my_comp]]"
LINHA_WIKI_AREA = "- Áreas: [[Areas/" + "clinica]] · [[Areas/financas]]"

VAULT_EXEMPLO = (
    "# ORG — exemplo\n"
    "\n"
    "Texto livre sem nada a remover.\n"
    f"{LINHA_AUTORIDADE}\n"
    "- [[Projects]] · [[Areas]] · [[Resources]]\n"
    f"{LINHA_WIKI_PROJETO}\n"
    f"{LINHA_WIKI_AREA}\n"
    "Caminho de exemplo: /home/" + "pet" + "rus/IDrive/arquivo.md\n"
)


def _corpo_apos_cabecalho(texto: str) -> str:
    return texto[texto.find("-->\n") + 4 :]


def _vault_com(tmp_path: Path, nomes: tuple[str, ...] = sh.MANUAIS) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    for nome in nomes:
        (vault / f"{nome}.md").write_text(VAULT_EXEMPLO, encoding="utf-8")
    return vault


def _house(tmp_path: Path) -> Path:
    house = tmp_path / "house"
    house.mkdir()
    readme = "# docs/house\n\n<!-- sync:tabela inicio -->\n<!-- sync:tabela fim -->\n"
    (house / "README.md").write_text(readme, encoding="utf-8")
    return house


@pytest.fixture(autouse=True)
def _home_descartavel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """HOME e vault da maquina do dono nunca entram nos testes (CONS-10A)."""
    home = tmp_path / "home_descartavel"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))  # Windows: o perfil sai daqui (CONS-R11)
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    return home


# ---------------------------------------------------------------------------
# Cabecalho de sync
# ---------------------------------------------------------------------------


def test_cabecalho_leva_a_frase_longa_de_precedencia() -> None:
    assert sh.FRASE_PRECEDENCIA_LONGA == FRASE_LONGA
    saida = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    assert FRASE_LONGA in saida[: saida.find("-->\n")]


def test_cabecalho_nao_tem_caminho_local_nem_path_vault() -> None:
    saida = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    cabecalho = saida[: saida.find("-->\n")]
    assert "path_vault" not in cabecalho
    assert "/home/" not in cabecalho


def test_cabecalho_registra_data_e_hmac_do_vault() -> None:
    saida = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    assert "sync_date: 2026-11-20" in saida
    assert "hmac_vault_sha256:" in saida


def test_nenhum_arquivo_gerado_contem_o_sha256_do_texto_do_vault() -> None:
    # Oraculo: o sha256 do texto ANTES da redacao nao pode aparecer em lugar nenhum.
    # Sem chave, a saida nao tem HMAC; ainda assim o sha256 cru nao pode vazar.
    sha_vault = hashlib.sha256(VAULT_EXEMPLO.encode("utf-8")).hexdigest()
    assert sha_vault not in sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20")
    assert sha_vault not in sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)


def test_nenhum_arquivo_do_sync_contem_o_sha256_do_vault(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    sha_vault = hashlib.sha256(VAULT_EXEMPLO.encode("utf-8")).hexdigest()
    for arq in house.glob("*.md"):
        assert sha_vault not in arq.read_text(encoding="utf-8"), arq.name


def test_manual_sem_transformacao_nao_publica_o_sha_do_vault() -> None:
    # Sem redacao o corpo e igual ao vault; o hash do corpo nao pode ser o do vault.
    limpo = "# Titulo\n\nSem nada a remover.\n"
    sha_vault = hashlib.sha256(limpo.encode("utf-8")).hexdigest()
    assert sha_vault not in sh.gerar_manual(limpo, "TESTES", "2026-11-20", CHAVE)


# ---------------------------------------------------------------------------
# Transformacoes (todas de privacidade ou estruturais)
# ---------------------------------------------------------------------------


def test_t1_remove_linha_com_wikilink_de_projeto_ou_area() -> None:
    corpo, cont = sh.aplicar_transformacoes(VAULT_EXEMPLO)
    assert "[[Projects/" not in corpo
    assert "[[Areas/" not in corpo
    assert cont["T1"] == 2


def test_t1_preserva_wikilink_de_indice_sem_barra() -> None:
    corpo, _ = sh.aplicar_transformacoes(VAULT_EXEMPLO)
    assert "- [[Projects]] · [[Areas]] · [[Resources]]" in corpo


def test_t2_troca_linha_de_autoridade_pessoal_pelo_paragrafo_padrao() -> None:
    corpo, cont = sh.aplicar_transformacoes(VAULT_EXEMPLO)
    assert LINHA_AUTORIDADE not in corpo
    assert "Quem opera este plugin é o líder supremo e soberano desta organização." in corpo
    assert cont["T2"] == 1


def test_t3_troca_caminho_home_no_corpo() -> None:
    corpo, cont = sh.aplicar_transformacoes(VAULT_EXEMPLO)
    assert "/home/" not in corpo
    assert cont["T3"] == 1


DOMINIO_PESSOAL = "drpet" + "rus.top"
LINHA_DOMINIO = (
    "- Dominio previsto em producao: {{DOMINIO_PRODUCAO}} = https://" + DOMINIO_PESSOAL
)
LINHA_CWD_VAULT = (
    "Auto-carrega em qualquer sessão Claude Code cuja CWD esteja dentro de `"
    + "/" + "home/" + "pet" + "rus/IDrive/Documentos/projetos_claudebrain/"
    + "`. Conteúdo em docs separados."
)


def test_marcas_das_transformacoes_sao_as_declaradas() -> None:
    # T1 a T4 sao de privacidade; a T5 (link para fora de docs/house) tem marca propria.
    marcas = {t.id: t.marca for t in sh.TRANSFORMACOES}
    assert marcas == {
        "T1": "privacidade",
        "T2": "privacidade",
        "T3a": "privacidade",
        "T3": "privacidade",
        "T4": "privacidade",
        "T5": "link-externo",
    }


def test_t3a_caminho_do_vault_em_frase_de_cwd_vira_a_raiz_do_vault() -> None:
    corpo, cont = sh.aplicar_transformacoes(LINHA_CWD_VAULT + "\n")
    assert corpo == (
        "Auto-carrega em qualquer sessão Claude Code cuja CWD esteja na raiz do vault. "
        "Conteúdo em docs separados.\n"
    )
    assert cont["T3a"] == 1
    assert cont["T3"] == 0


def test_t4_troca_dominio_pessoal_pelo_placeholder_ancorado_no_rotulo() -> None:
    corpo, cont = sh.aplicar_transformacoes(LINHA_DOMINIO + "\n")
    assert corpo == "- Dominio previsto em producao: {{DOMINIO_PRODUCAO}}\n"
    assert cont["T4"] == 1
    assert "drpet" + "rus" not in corpo


def test_t5_link_para_fora_de_house_vira_so_o_nome_do_arquivo() -> None:
    entrada = "Veja [`docs/claude/perfil.md`](docs/claude/perfil.md) (perfil).\n"
    corpo, cont = sh.aplicar_transformacoes(entrada)
    assert corpo == "Veja perfil.md (perfil).\n"
    assert cont["T5"] == 1


def test_t5_link_com_ancora_e_caminho_relativo_para_fora_vira_texto() -> None:
    corpo, cont = sh.aplicar_transformacoes("Ver [regra](../CONTRACT.md#secao-2).\n")
    assert corpo == "Ver CONTRACT.md.\n"
    assert cont["T5"] == 1


def test_t5_link_para_manual_da_house_continua_link() -> None:
    entrada = "[ORG](ORG.md) e [CONTRATO](./CONTRACT.md#regra) e [README](README.md)\n"
    corpo, cont = sh.aplicar_transformacoes(entrada)
    assert corpo == entrada
    assert cont["T5"] == 0


def test_t5_nao_mexe_em_url_ancora_nem_caminho_absoluto_nem_esquema() -> None:
    entrada = (
        "[site](https://exemplo.org/x) [topo](#inicio) "
        "[mail](mailto:contato@exemplo.org) [raiz](/indice)\n"
    )
    corpo, cont = sh.aplicar_transformacoes(entrada)
    assert corpo == entrada
    assert cont["T5"] == 0


def test_t5_nao_mexe_em_wikilink() -> None:
    entrada = "Indice: [[Projects]] e [[ORG]].\n"
    corpo, cont = sh.aplicar_transformacoes(entrada)
    assert corpo == entrada
    assert cont["T5"] == 0


def test_nome_do_claude_do_vault_no_plugin_nao_e_claude_md() -> None:
    assert "CLAUDE" in sh.MANUAIS
    assert "audit-seo" in sh.MANUAIS
    assert len(sh.MANUAIS) == 12
    assert sh.nome_destino("CLAUDE") == "CLAUDE-vault"
    assert sh.nome_destino("ORG") == "ORG"


def test_corpo_sem_transformacao_e_byte_identico_ao_vault() -> None:
    limpo = "# Titulo\n\nParagrafo com [[Projects]] e `[[nodiscard]]`.\n"
    corpo, cont = sh.aplicar_transformacoes(limpo)
    assert corpo == limpo
    assert cont == {"T1": 0, "T2": 0, "T3a": 0, "T3": 0, "T4": 0, "T5": 0}


def test_gerar_manual_e_deterministico() -> None:
    a = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    b = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    assert a == b


def test_gerar_manual_corpo_sai_depois_do_cabecalho() -> None:
    saida = sh.gerar_manual(VAULT_EXEMPLO, "ORG", "2026-11-20", CHAVE)
    corpo, _ = sh.aplicar_transformacoes(VAULT_EXEMPLO)
    assert _corpo_apos_cabecalho(saida) == corpo


# ---------------------------------------------------------------------------
# Verificacao: --check detecta mudanca do vault com chave, avisa sem chave
# ---------------------------------------------------------------------------


def test_write_grava_arquivos_e_check_com_chave_passa(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    assert sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE).divergentes == []
    assert (house / "ORG.md").exists()
    res = sh.sincronizar(vault, house, None, "check", CHAVE)
    assert res.divergentes == [] and res.nao_conferido is False


def test_check_com_chave_detecta_mudanca_do_vault(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    (vault / "ORG.md").write_text(VAULT_EXEMPLO + "Linha nova no vault.\n", encoding="utf-8")
    res = sh.sincronizar(vault, house, None, "check", CHAVE)
    assert "ORG.md" in res.divergentes


def test_check_com_chave_detecta_hmac_trocado_mesmo_com_corpo_igual(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    outra = b"\x02" * 32
    res = sh.sincronizar(vault, house, None, "check", outra)
    assert "ORG.md" in res.divergentes


def test_check_sem_chave_avisa_nao_conferido_e_nao_falha_calado(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    res = sh.sincronizar(vault, house, None, "check", None)
    assert res.divergentes == []
    assert res.nao_conferido is True


def test_check_sem_chave_ainda_detecta_corpo_alterado(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    (vault / "ORG.md").write_text(VAULT_EXEMPLO + "Mudanca.\n", encoding="utf-8")
    res = sh.sincronizar(vault, house, None, "check", None)
    assert "ORG.md" in res.divergentes


def test_write_sem_chave_recusa(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    with pytest.raises(sh.ErroSync):
        sh.sincronizar(vault, house, "2026-11-20", "write", None)


def test_check_usa_a_data_do_cabecalho_e_nao_a_data_do_dia(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2020-01-01", "write", CHAVE)
    assert sh.extrair_data((house / "ORG.md").read_text(encoding="utf-8")) == "2020-01-01"
    assert sh.sincronizar(vault, house, None, "check", CHAVE).divergentes == []


def test_header_removido_a_mao_vira_divergencia(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    (house / "ORG.md").write_text("adulterado\n", encoding="utf-8")
    assert "ORG.md" in sh.sincronizar(vault, house, None, "check", CHAVE).divergentes


# ---------------------------------------------------------------------------
# main: codigos de saida e chave local
# ---------------------------------------------------------------------------


def _chave_em(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, chave: bytes | None) -> Path:
    arq = tmp_path / "k.key"
    if chave is not None:
        arq.write_text(chave.hex() + "\n", encoding="utf-8")
        arq.chmod(0o600)
    else:
        arq.unlink(missing_ok=True)  # scratch do pytest, nunca a chave real
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(arq))
    return arq


def test_main_write_sem_vault_sai_2(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    _chave_em(tmp_path, monkeypatch, None)
    assert sh.main(["--write", "--house", str(_house(tmp_path))]) == 2


def test_main_check_sem_vault_sem_chave_confere_corpo_e_sai_3(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # CI: sem vault e sem chave. So o corpo e o README sao conferidos; nao e PASS.
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    _chave_em(tmp_path, monkeypatch, CHAVE)
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    _chave_em(tmp_path, monkeypatch, None)
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    assert sh.main(["--check", "--house", str(house)]) == 3


def test_main_check_sem_vault_sem_chave_detecta_corpo_adulterado_sai_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    _chave_em(tmp_path, monkeypatch, CHAVE)
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    arq = house / "ORG.md"
    arq.write_text(arq.read_text(encoding="utf-8") + "Linha inserida a mao.\n", encoding="utf-8")
    _chave_em(tmp_path, monkeypatch, None)
    assert sh.main(["--check", "--house", str(house)]) == 1


def test_main_check_sem_vault_com_chave_sai_2_nunca_3(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Na maquina do lider (com chave), sem vault a conferencia nao pode virar NAO CONFERIDO.
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    _chave_em(tmp_path, monkeypatch, CHAVE)
    assert sh.main(["--check", "--house", str(_house(tmp_path))]) == 2


def test_conferir_sem_vault_marca_nao_conferido_e_aponta_divergencia(tmp_path: Path) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    limpo = sh.conferir_sem_vault(house)
    assert limpo.divergentes == [] and limpo.nao_conferido is True
    (house / "ORG.md").write_text("adulterado\n", encoding="utf-8")
    assert "ORG.md" in sh.conferir_sem_vault(house).divergentes


def test_main_check_com_mudanca_sai_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    chave = tmp_path / "k.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o600)
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(chave))
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    (vault / "ORG.md").write_text("mudou\n", encoding="utf-8")
    assert sh.main(["--vault", str(vault), "--house", str(house), "--check"]) == 1


def test_main_check_sem_chave_sai_3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    chave = tmp_path / "k.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o600)
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(chave))
    sh.main(["--vault", str(vault), "--house", str(house), "--write"])
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(tmp_path / "ausente.key"))
    assert sh.main(["--vault", str(vault), "--house", str(house), "--check"]) == 3


@pytest.mark.skipif(sys.platform == "win32",
                    reason="modo 600 e POSIX; no Windows a chave fica no perfil, protegida pelo ACL")
def test_gerar_chave_cria_600_e_nao_sobrescreve(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    chave = tmp_path / "sync_house.key"
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(chave))
    assert sh.main(["--gerar-chave"]) == 0
    assert chave.stat().st_mode & 0o777 == 0o600
    assert len(chave.read_text(encoding="utf-8").strip()) == 64
    conteudo = chave.read_text(encoding="utf-8")
    assert sh.main(["--gerar-chave"]) == 2
    assert chave.read_text(encoding="utf-8") == conteudo


@pytest.mark.skipif(sys.platform == "win32",
                    reason="recusa por modo 644 e POSIX; no Windows o modo nao existe (ACL do perfil)")
def test_chave_com_permissao_aberta_recusa(tmp_path: Path) -> None:
    chave = tmp_path / "aberta.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o644)
    with pytest.raises(sh.ErroSync):
        sh.carregar_chave(chave)


# ---------------------------------------------------------------------------
# README: tabela regenerada entre marcadores
# ---------------------------------------------------------------------------


def test_readme_tabela_entre_marcadores_e_regenerada() -> None:
    readme = (
        "# titulo\n\n<!-- sync:tabela inicio -->\nvelha\n<!-- sync:tabela fim -->\n\nfim\n"
    )
    entradas = [("ORG.md", "a" * 64, "b" * 64, ("T1", "T2"))]
    novo = sh.renderizar_readme(readme, entradas)
    assert "velha" not in novo
    assert "| ORG.md |" in novo
    assert "T1, T2" in novo
    assert novo.endswith("fim\n")


# ---------------------------------------------------------------------------
# Guarda de privacidade do proprio codigo
# ---------------------------------------------------------------------------

TERMOS_PROIBIDOS_NO_CODIGO = (
    "pet" + "rus",
    "kai" + "ser",
    "cl" + "inica",
    "site_" + "consultorio",
    "gus" + "world",
    "glint" + "fx",
    "drpet" + "rus",
    "/" + "home" + "/",
)


def test_codigo_do_sync_nao_tem_termo_privado_literal() -> None:
    fonte = (SCRIPTS / "sync_house.py").read_text(encoding="utf-8").lower()
    achados = [t for t in TERMOS_PROIBIDOS_NO_CODIGO if t in fonte]
    assert achados == []


# ---------------------------------------------------------------------------
# Caminho do vault: --vault > BIGTECH_VAULT > ~/.config/bigtech/vault_path (CONS-10A)
# ---------------------------------------------------------------------------


def _chave_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    chave = tmp_path / "chave_de_teste.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o600)
    monkeypatch.setenv("BIGTECH_SYNC_KEY_FILE", str(chave))


def _vault_path_local(home: Path, conteudo: str) -> None:
    arq = home / ".config" / "bigtech" / "vault_path"
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(conteudo, encoding="utf-8")


def test_arquivo_local_resolve_o_vault_sem_flag_nem_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _home_descartavel: Path
) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    _chave_local(tmp_path, monkeypatch)
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    _vault_path_local(_home_descartavel, str(vault) + "\n")
    assert sh.main(["--house", str(house), "--check"]) == 0


def test_env_vence_o_arquivo_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _home_descartavel: Path
) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    _chave_local(tmp_path, monkeypatch)
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    _vault_path_local(_home_descartavel, str(tmp_path / "nao_existe") + "\n")
    monkeypatch.setenv("BIGTECH_VAULT", str(vault))
    assert sh.main(["--house", str(house), "--check"]) == 0


def test_flag_vence_env_e_arquivo_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _home_descartavel: Path
) -> None:
    vault = _vault_com(tmp_path)
    house = _house(tmp_path)
    _chave_local(tmp_path, monkeypatch)
    assert sh.main(["--vault", str(vault), "--house", str(house), "--write"]) == 0
    _vault_path_local(_home_descartavel, str(tmp_path / "nao_existe_1") + "\n")
    monkeypatch.setenv("BIGTECH_VAULT", str(tmp_path / "nao_existe_2"))
    assert sh.main(["--vault", str(vault), "--house", str(house), "--check"]) == 0


def test_sem_nenhuma_fonte_do_vault_com_chave_segue_erro_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    house = _house(tmp_path)
    _chave_local(tmp_path, monkeypatch)
    assert sh.main(["--house", str(house), "--check"]) == 2


@pytest.mark.parametrize("conteudo", ["", "\n", "/a/um\n/a/dois\n"])
def test_arquivo_local_malformado_e_erro_2_nunca_fallback(
    conteudo: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _home_descartavel: Path,
) -> None:
    house = _house(tmp_path)
    _chave_local(tmp_path, monkeypatch)
    _vault_path_local(_home_descartavel, conteudo)
    assert sh.main(["--house", str(house), "--check"]) == 2


# ---------------------------------------------------------------------------
# CONS-R11: Windows (CRLF, sem bits POSIX, sem diretorio pessoal)
# ---------------------------------------------------------------------------

_README_BASE = "# docs/house\n\n<!-- sync:tabela inicio -->\n<!-- sync:tabela fim -->\n"


def test_vault_com_crlf_confere_igual_ao_lf(tmp_path: Path) -> None:
    """Um vault salvo com CRLF (Windows) nao pode divergir do manual gerado."""
    vault = tmp_path / "vault"
    vault.mkdir()
    for nome in sh.MANUAIS:
        (vault / f"{nome}.md").write_bytes(f"# {nome}\r\n\r\nTexto.\r\n".encode())
    house = tmp_path / "house"
    house.mkdir()
    (house / "README.md").write_text(_README_BASE, encoding="utf-8")
    sh.sincronizar(vault, house, "2026-11-20", "write", CHAVE)
    res = sh.sincronizar(vault, house, "2026-11-20", "check", CHAVE)
    assert res.divergentes == []


def test_chave_com_modo_aberto_nao_e_recusada_fora_do_posix(tmp_path: Path, monkeypatch) -> None:
    """Sem bits POSIX (Windows), a chave nao e recusada por modo: fica no perfil do usuario."""
    monkeypatch.setattr(sh, "_modo_posix", lambda: False)
    chave = tmp_path / "sem_modo.key"
    chave.write_text(CHAVE.hex() + "\n", encoding="utf-8")
    chave.chmod(0o644)
    assert sh.carregar_chave(chave) == CHAVE


def test_sem_diretorio_pessoal_sai_2_sem_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Sem HOME nem USERPROFILE (Windows sem perfil), o erro e de uso (2), nunca RuntimeError."""
    monkeypatch.delenv("BIGTECH_VAULT", raising=False)
    monkeypatch.delenv("BIGTECH_SYNC_KEY_FILE", raising=False)
    monkeypatch.setattr(sh.os.path, "expanduser", lambda p: p)

    def sem_home(cls):
        raise RuntimeError("Could not determine home directory.")

    monkeypatch.setattr(sh.Path, "home", classmethod(sem_home))
    house = tmp_path / "house"
    house.mkdir()
    assert sh.main(["--house", str(house), "--check"]) == 2
    assert "erro" in capsys.readouterr().err
