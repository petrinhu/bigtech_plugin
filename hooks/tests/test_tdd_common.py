import json
import os
import tdd_common as c


def test_glob_match_star_is_single_segment():
    assert c.glob_match("src/app.py", "src/*.py")
    assert not c.glob_match("src/sub/app.py", "src/*.py")


def test_glob_match_double_star_crosses_directories():
    assert c.glob_match("a/b/test_x.py", "**/test_*.py")
    assert c.glob_match("test_x.py", "**/test_*.py")
    assert c.glob_match("tests/sub/x.py", "tests/**")


def test_glob_match_no_false_positive():
    assert not c.glob_match("src/app.py", "tests/**")
    assert not c.glob_match("readme.md", "**/*.py")


def test_resolve_config_expands_preset():
    cfg = c.resolve_config({"preset": "python-pytest"})
    assert cfg["test_command"] == "pytest -x -q"
    assert "**/test_*.py" in cfg["test_globs"]
    assert cfg["strict"] is True           # default
    assert cfg["timeout_sec"] == 120       # default


def test_resolve_config_override_wins_over_preset():
    cfg = c.resolve_config({"preset": "python-pytest",
                            "test_command": "pytest -q meu/",
                            "strict": False})
    assert cfg["test_command"] == "pytest -q meu/"
    assert cfg["strict"] is False


def test_resolve_config_unknown_preset_raises():
    import pytest
    with pytest.raises(ValueError):
        c.resolve_config({"preset": "nao-existe"})


def test_resolve_config_without_preset_uses_raw_globs():
    cfg = c.resolve_config({"test_globs": ["t/**"], "production_globs": ["s/**"]})
    assert cfg["test_globs"] == ["t/**"]


def _make_project(tmp_path, raw_config):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "tdd-guard.json").write_text(json.dumps(raw_config))
    return tmp_path


def test_find_project_root_walks_up(tmp_path):
    root = _make_project(tmp_path, {"preset": "python-pytest"})
    deep = root / "src" / "a" / "b"
    deep.mkdir(parents=True)
    assert c.find_project_root(str(deep)) == os.path.realpath(str(root))


def test_find_project_root_none_when_absent(tmp_path):
    assert c.find_project_root(str(tmp_path)) is None


def test_load_config_returns_root_and_resolved(tmp_path):
    root = _make_project(tmp_path, {"preset": "python-pytest"})
    got_root, cfg = c.load_config(str(root / "src"))
    assert got_root == os.path.realpath(str(root))
    assert cfg["test_command"] == "pytest -x -q"


def test_load_config_disabled_returns_none(tmp_path):
    root = _make_project(tmp_path, {"preset": "python-pytest", "enabled": False})
    got_root, cfg = c.load_config(str(root))
    assert got_root is None and cfg is None


def test_load_config_no_project_returns_none(tmp_path):
    got_root, cfg = c.load_config(str(tmp_path))
    assert got_root is None and cfg is None


def test_classify_precedence():
    cfg = c.resolve_config({
        "preset": "python-pytest",
        "exclude_globs": ["prototypes/**"],
    })
    assert c.classify("tests/test_foo.py", cfg) == "test"
    assert c.classify("src/foo.py", cfg) == "production"
    assert c.classify("prototypes/foo.py", cfg) == "excluded"
    assert c.classify("README.md", cfg) == "ignored"


def test_classify_exclude_beats_production():
    cfg = c.resolve_config({"preset": "python-pytest",
                            "exclude_globs": ["src/legacy/**"]})
    assert c.classify("src/legacy/old.py", cfg) == "excluded"


def test_classify_test_beats_production():
    # test_*.py tambem casa **/*.py (producao), mas teste tem precedencia
    cfg = c.resolve_config({"preset": "python-pytest"})
    assert c.classify("pkg/test_x.py", cfg) == "test"


def test_classify_conftest_nested_is_test_not_production():
    # BUG: o glob "conftest.py" so casava na raiz, entao um conftest.py
    # aninhado (pkg/conftest.py) caia em producao e o guard bloquearia.
    # Com "**/conftest.py", aninhado e raiz ambos sao TESTE.
    cfg = c.resolve_config({"preset": "python-pytest"})
    assert c.classify("conftest.py", cfg) == "test"            # raiz
    assert c.classify("pkg/conftest.py", cfg) == "test"        # aninhado 1 nivel
    assert c.classify("a/b/c/conftest.py", cfg) == "test"      # aninhado fundo
    # sanidade: arquivo de producao comum continua producao
    assert c.classify("pkg/core.py", cfg) == "production"


def test_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))   # isola o diretorio de estado
    root = "/proj/exemplo"
    assert c.read_state(root) is None           # ausente -> None
    c.write_state(root, {"ran": True, "has_red": True})
    got = c.read_state(root)
    assert got["ran"] is True and got["has_red"] is True


def test_state_path_is_per_project(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert c.state_path("/proj/a") != c.state_path("/proj/b")


def test_read_state_corrupt_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    p = c.state_path("/proj/x")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write("{ nao eh json")
    assert c.read_state("/proj/x") is None


# --- BUG: read_state deve DISTINGUIR ausente/corrompido (None) de erro de
#     I/O (propaga OSError), para o guard poder FAIL-OPEN em vez de bloquear ---

def test_read_state_io_error_propagates(tmp_path, monkeypatch):
    # open() falhando por I/O (ex.: HOME read-only, sem permissao) NAO pode
    # virar None silencioso: deve propagar OSError para o chamador decidir.
    monkeypatch.setenv("HOME", str(tmp_path))

    def boom(*a, **k):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr("builtins.open", boom)
    import pytest
    with pytest.raises(OSError):
        c.read_state("/proj/x")


def test_read_state_generic_oserror_propagates(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    def boom(*a, **k):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr("builtins.open", boom)
    import pytest
    with pytest.raises(OSError):
        c.read_state("/proj/x")


def test_extract_file_path():
    data = {"tool_name": "Write", "tool_input": {"file_path": "/x/a.py"}}
    assert c.extract_file_path(data) == "/x/a.py"
    assert c.extract_file_path({}) == ""
    assert c.extract_file_path({"tool_input": {}}) == ""


def test_parse_totals_pytest():
    t = c.parse_totals("=== 3 passed, 1 failed in 0.2s ===")
    assert t == {"passed": 3, "failed": 1}


def test_parse_totals_phpunit():
    t = c.parse_totals("Tests: 5, Assertions: 9, Failures: 2.")
    assert t.get("failed") == 2


def test_parse_totals_empty():
    assert c.parse_totals("nada relevante") == {}


# --- BUG C1/C2: glob ** nao deve casar substring ---

def test_glob_match_double_star_does_not_match_substring():
    # 'contest_results' contem 'test_' como substring, mas NAO eh teste
    assert not c.glob_match("src/contest_results.py", "**/test_*.py")
    assert not c.glob_match("src/protest_handler.py", "**/test_*.py")
    # de verdade teste:
    assert c.glob_match("src/test_foo.py", "**/test_*.py")
    assert c.glob_match("test_foo.py", "**/test_*.py")


def test_glob_match_double_star_middle_anchors_segment():
    assert c.glob_match("a/b/c.py", "a/**/c.py")
    assert c.glob_match("a/c.py", "a/**/c.py")
    assert not c.glob_match("a/XYZ_c.py", "a/**/c.py")


def test_glob_match_bare_double_star_matches_all():
    assert c.glob_match("qualquer/coisa.py", "**")
    assert c.glob_match("x", "**")


# --- BUG I1: load_config silencia config malformada ---

def test_load_config_malformed_warns(tmp_path, capsys):
    d = tmp_path / ".claude"
    d.mkdir()
    (d / "tdd-guard.json").write_text("{ nao eh json")
    root, cfg = c.load_config(str(tmp_path))
    assert root is None and cfg is None
    assert "tdd" in capsys.readouterr().err.lower()


def test_load_config_bad_preset_warns(tmp_path, capsys):
    d = tmp_path / ".claude"
    d.mkdir()
    (d / "tdd-guard.json").write_text(json.dumps({"preset": "python_pytest"}))  # typo
    root, cfg = c.load_config(str(tmp_path))
    assert root is None and cfg is None
    assert capsys.readouterr().err != ""


# --- BUG I3/M3: parse_totals ---

def test_parse_totals_pytest_error_counts_as_failed():
    assert c.parse_totals("=== 1 error in 0.1s ===").get("failed") == 1


def test_parse_totals_phpunit_zero_failures_omits_failed():
    assert "failed" not in c.parse_totals("Tests: 3, Assertions: 3, Failures: 0.")


def test_extract_file_path_non_dict_tool_input():
    assert c.extract_file_path({"tool_input": [1, 2]}) == ""
    assert c.extract_file_path({"tool_input": None}) == ""


# --- OS-2: separador de path Windows ('\') deve casar globs POSIX ('/') ---
# No Windows os.path.relpath devolve 'src\app.py'; os globs sao 'src/*.py'.
# Sem normalizar, nada casaria e classify() retornaria sempre 'ignored',
# deixando guard/runner inertes. Estes testes simulam o rel path do Windows.

def test_glob_match_normalizes_backslash_separator():
    # caminho estilo Windows casa o mesmo glob POSIX
    assert c.glob_match("src\\app.py", "src/*.py")
    assert c.glob_match("a\\b\\test_x.py", "**/test_*.py")
    assert c.glob_match("tests\\sub\\x.py", "tests/**")
    # e nao gera falso positivo: '\' aninhado nao casa glob de unico segmento
    assert not c.glob_match("src\\sub\\app.py", "src/*.py")


def test_glob_match_backslash_matches_same_as_slash():
    # paridade: o mesmo caminho com '\' e com '/' classifica igual
    for sep_path in ("a/b/c.py", "a\\b\\c.py"):
        assert c.glob_match(sep_path, "a/**/c.py")
        assert not c.glob_match(sep_path, "x/**/c.py")


def test_classify_with_windows_separator():
    # classify deve funcionar mesmo recebendo rel path com '\' (Windows):
    # sem o fix, todos cairiam em 'ignored' e o TDD ficaria inerte.
    cfg = c.resolve_config({
        "preset": "python-pytest",
        "exclude_globs": ["prototypes/**"],
    })
    assert c.classify("tests\\test_foo.py", cfg) == "test"
    assert c.classify("src\\foo.py", cfg) == "production"
    assert c.classify("prototypes\\foo.py", cfg) == "excluded"
    assert c.classify("a\\b\\c\\conftest.py", cfg) == "test"


def test_classify_linux_separator_still_correct():
    # sanidade: no Linux/mac (sep '/') a normalizacao e no-op e nada quebra.
    cfg = c.resolve_config({"preset": "python-pytest"})
    assert c.classify("tests/test_foo.py", cfg) == "test"
    assert c.classify("src/foo.py", cfg) == "production"
    assert c.classify("README.md", cfg) == "ignored"
