"""README-tdd.md ensina a apontar test_command para um executor isolado (Q-M6).

O tdd_runner roda test_command no host com timeout, mas sem limite de
processos. A documentação precisa mostrar o executor isolado com limite e
dizer que teste dinâmico não roda na sessão viva do usuário.
"""
import json
import os

import pytest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(HOOKS_DIR, "README-tdd.md")


@pytest.fixture(scope="module")
def texto():
    with open(README, encoding="utf-8") as fh:
        return fh.read()


def _secao(texto, titulo):
    """Corpo da seção `titulo` (do cabeçalho ao próximo de mesmo nível ou maior)."""
    linhas = texto.splitlines()
    inicio = next(i for i, l in enumerate(linhas) if l.strip() == titulo)
    nivel = len(titulo) - len(titulo.lstrip("#"))
    corpo = []
    for linha in linhas[inicio + 1:]:
        if linha.startswith("#") and (len(linha) - len(linha.lstrip("#"))) <= nivel:
            break
        corpo.append(linha)
    return "\n".join(corpo)


def test_secao_de_executor_isolado_existe(texto):
    assert "## Executor isolado e limite de processos" in texto


def test_secao_traz_exemplo_de_test_command_com_limite_de_processos(texto):
    secao = _secao(texto, "## Executor isolado e limite de processos")
    assert "--pids-limit" in secao, "o exemplo precisa de limite de processos"
    assert "--memory" in secao, "o exemplo precisa de limite de memória"
    bloco = secao.split("```json", 1)[1].split("```", 1)[0]
    config = json.loads(bloco)
    assert "--pids-limit" in config["test_command"]
    assert config["timeout_sec"] > 0


def test_secao_diz_que_teste_dinamico_nao_roda_na_sessao_viva(texto):
    secao = _secao(texto, "## Executor isolado e limite de processos")
    assert "sessão viva" in secao
    assert "janela" in secao or "foco" in secao


SECAO_USUARIO = "## Para o usuário (não para o modelo)"


def _sem_secao(texto, titulo):
    """Texto sem a seção `titulo` (cabeçalho e corpo), para ver só o corpo."""
    linhas = texto.splitlines()
    inicio = next(i for i, l in enumerate(linhas) if l.strip() == titulo)
    nivel = len(titulo) - len(titulo.lstrip("#"))
    fim = len(linhas)
    for i in range(inicio + 1, len(linhas)):
        l = linhas[i]
        if l.startswith("#") and (len(l) - len(l.lstrip("#"))) <= nivel:
            fim = i
            break
    return "\n".join(linhas[:inicio] + linhas[fim:])


def test_secao_para_o_usuario_existe(texto):
    assert SECAO_USUARIO in texto


def test_secao_para_o_usuario_explica_as_valvulas(texto):
    secao = _secao(texto, SECAO_USUARIO)
    assert "TDD_GUARD=off" in secao
    assert "TDD_PHASE=refactor" in secao


def test_corpo_nao_ensina_o_modelo_a_desligar_o_guard(texto):
    corpo = _sem_secao(texto, SECAO_USUARIO)
    assert "TDD_GUARD" not in corpo
    assert "TDD_PHASE" not in corpo


def test_corpo_manda_pedir_ao_usuario_para_sair_do_ciclo(texto):
    corpo = _sem_secao(texto, SECAO_USUARIO)
    assert "para sair do ciclo, peça ao usuário" in corpo
