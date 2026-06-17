"""Testes do hook UserPromptSubmit `bigtech_reinforce.py` (AUD-F08).

Exercita as funções puras importáveis (TRIGGER_RE de roteamento, read_porte) com
asserts de VALOR, mais os dois modos mutuamente exclusivos de `main()` (reforço
em projeto classificado vs. roteamento por gatilho de linguagem) e um contrato
via subprocess (exit 0 + JSON parseável).

Invariante-chave testada: os modos NUNCA disparam juntos, e projeto sem marcador
com prompt que não casa gatilho fica em silêncio (anti-ruído).
"""
import io
import json
import os
import subprocess
import sys

import bigtech_reinforce as r

MARKER = r.MARKER     # ".bigtech-porte"


# ---------------------------------------------------------------------------
# TRIGGER_RE: gatilhos de "quero a constelação C-level" (pt-br e inglês).
# ---------------------------------------------------------------------------
def test_trigger_re_casa_termos_da_constelacao():
    for prompt in (
        "monta o time c-level",
        "preciso de c-levels",
        "ativar a constelacao bigtech",
        "big tech mode, por favor",
        "quero montar o time",
        "build the team agora",
        "chamar o chief of staff",
        "preciso do Cosimo pra orquestrar",
        "gerenciar o projeto inteiro",
        "monte a equipe de agentes dev",
    ):
        assert r.TRIGGER_RE.search(prompt), f"deveria casar: {prompt!r}"


def test_trigger_re_nao_casa_prompt_neutro():
    for prompt in (
        "corrige esse bug no parser",
        "explica como funciona o cache",
        "roda os testes unitarios",
        "",
    ):
        assert not r.TRIGGER_RE.search(prompt), f"NÃO deveria casar: {prompt!r}"


# ---------------------------------------------------------------------------
# TRIGGER_RE: termos genericos NAO podem disparar fora de contexto de
# equipe/projeto (falsos positivos achados na auditoria), mas os verdadeiros
# positivos (incl. montar/montar/criar o time/empresa/agentes) devem manter.
# ---------------------------------------------------------------------------
def test_trigger_re_nao_casa_falsos_positivos_genericos():
    for prompt in (
        "gestão de memória",
        "manage the connection pool",
        "constellation pattern",
        "orquestrador de containers",
        # variacoes proximas que tambem nao sao sobre o time/projeto:
        "preciso gerenciar a memória do processo",
        "coordinate the threads no pool",
        "design a constellation of microservices",
    ):
        assert not r.TRIGGER_RE.search(prompt), f"NÃO deveria casar: {prompt!r}"


def test_trigger_re_casa_generico_so_com_contexto_de_equipe():
    # O mesmo verbo generico que NAO casa sozinho deve casar perto do contexto.
    for prompt in (
        "gerenciar o projeto inteiro",
        "preciso coordenar a equipe de agentes",
        "quem orquestra o time?",
        "gestão do produto e da empresa",
    ):
        assert r.TRIGGER_RE.search(prompt), f"deveria casar: {prompt!r}"


def test_trigger_re_corrige_falso_negativo_de_montagem():
    # Antes so casava 'montar'/'monta'; agora cobre monte/criar + alvo, e
    # tambem 'montar a empresa' / 'agentes C-level'.
    for prompt in (
        "monte o time de produto",
        "monte a equipe agora",
        "criar agentes C-level",
        "montar a empresa",
        "estruturar o time de engenharia",
        "organize a equipe por favor",
    ):
        assert r.TRIGGER_RE.search(prompt), f"deveria casar: {prompt!r}"


# ---------------------------------------------------------------------------
# read_porte: extrai 'porte=<x>' da primeira linha do marcador; fallback seguro.
# ---------------------------------------------------------------------------
def test_read_porte_extrai_valor(tmp_path):
    mk = tmp_path / MARKER
    mk.write_text("porte=bigtech\noutras coisas\n")
    assert r.read_porte(str(mk)) == "bigtech"


def test_read_porte_normaliza_caixa(tmp_path):
    mk = tmp_path / MARKER
    mk.write_text("porte = EARLY\n")
    assert r.read_porte(str(mk)) == "early"


def test_read_porte_fallback_sem_campo(tmp_path):
    mk = tmp_path / MARKER
    mk.write_text("conteudo sem o campo\n")
    assert r.read_porte(str(mk)) == "classificado"


def test_read_porte_fallback_arquivo_inexistente(tmp_path):
    assert r.read_porte(str(tmp_path / "nao-existe")) == "classificado"


# ---------------------------------------------------------------------------
# Helper para main() in-process.
# ---------------------------------------------------------------------------
def _run_main(monkeypatch, payload):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = r.main()
    return rc, captured.getvalue()


# --- MODO 1: reforço por turno em projeto classificado ----------------------

def test_main_reforco_quando_classificado(tmp_path, monkeypatch):
    (tmp_path / MARKER).write_text("porte=scale\n")
    # Prompt neutro: o reforço acontece pelo marcador, não pelo gatilho.
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path), "prompt": "ajusta o lint"})
    assert rc == 0
    obj = json.loads(out)
    hso = obj["hookSpecificOutput"]
    assert hso["hookEventName"] == "UserPromptSubmit"
    assert "porte=scale" in hso["additionalContext"]
    assert "BIGTECH ATIVO" in hso["additionalContext"]


# --- MODO 2: roteamento por gatilho em projeto NÃO classificado -------------

def test_main_roteamento_quando_prompt_pede_constelacao(tmp_path, monkeypatch):
    # Sem .bigtech-porte + prompt com gatilho -> aponta para /bigtech.
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path), "prompt": "montar o time c-level"})
    assert rc == 0
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "/bigtech" in ctx
    assert "Cosimo" in ctx


# --- Anti-ruído: silêncio sem marcador e sem gatilho ------------------------

def test_main_silencia_sem_marcador_e_sem_gatilho(tmp_path, monkeypatch):
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path), "prompt": "corrige o bug X"})
    assert rc == 0
    assert out == ""


def test_main_cwd_inexistente_exit_0_silencioso(tmp_path, monkeypatch):
    rc, out = _run_main(
        monkeypatch,
        {"cwd": str(tmp_path / "fantasma"), "prompt": "montar o time c-level"},
    )
    assert rc == 0
    assert out == ""


def test_main_modos_sao_mutuamente_exclusivos(tmp_path, monkeypatch):
    # Marcador presente + prompt com gatilho: deve emitir SÓ o reforço (modo 1),
    # nunca os dois. Uma única linha de JSON é impressa.
    (tmp_path / MARKER).write_text("porte=early\n")
    rc, out = _run_main(monkeypatch, {"cwd": str(tmp_path), "prompt": "montar o time c-level"})
    assert rc == 0
    linhas = [ln for ln in out.splitlines() if ln.strip()]
    assert len(linhas) == 1
    assert "BIGTECH ATIVO" in linhas[0]   # modo 1 venceu, não o roteamento


# ---------------------------------------------------------------------------
# Contrato end-to-end via subprocess: exit 0 + JSON parseável.
# ---------------------------------------------------------------------------
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_subprocess_roteamento_exit_0_json(tmp_path):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_reinforce.py")],
        input=json.dumps({"cwd": str(tmp_path), "prompt": "montar o time c-level bigtech"}),
        text=True, capture_output=True,
    )
    assert proc.returncode == 0
    obj = json.loads(proc.stdout)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "/bigtech" in obj["hookSpecificOutput"]["additionalContext"]


def test_subprocess_stdin_invalido_exit_0(tmp_path):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_reinforce.py")],
        input="nao eh json", text=True, capture_output=True,
    )
    assert proc.returncode == 0


# ---------------------------------------------------------------------------
# FAIL-OPEN: stdin com JSON VALIDO porem NAO-dict (null, [], "x", 12).
# Antes do fix, data.get(...) lancava AttributeError -> exit 1 (bloqueava).
# ---------------------------------------------------------------------------
import pytest   # noqa: E402

NON_DICT_JSON = ("null", "[]", '"x"', "12", "[1, 2, 3]", "true", "3.14")


def _run_main_raw(monkeypatch, raw_text):
    """Como _run_main, mas injeta o texto bruto de stdin (sem json.dumps)."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(raw_text))
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = r.main()
    return rc, captured.getvalue()


@pytest.mark.parametrize("raw", NON_DICT_JSON)
def test_main_json_valido_nao_dict_exit_0(tmp_path, monkeypatch, raw):
    # Payload nao e dict: cai no os.getcwd() (dir sem marcador) e prompt vazio
    # -> silencio, e o essencial: NAO quebra (exit 0).
    monkeypatch.chdir(tmp_path)
    rc, out = _run_main_raw(monkeypatch, raw)
    assert rc == 0
    assert out == ""


@pytest.mark.parametrize("raw", NON_DICT_JSON)
def test_subprocess_json_valido_nao_dict_exit_0(raw):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, "bigtech_reinforce.py")],
        input=raw, text=True, capture_output=True,
    )
    assert proc.returncode == 0
