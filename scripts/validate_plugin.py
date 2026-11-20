#!/usr/bin/env python3
"""Gate ZERO-ORFAOS (spec 4.1) do plugin bigtech — validador reutilizavel.

Valida, sobre `agents/`, `skills/` e `docs/` (exceto as subarvores em
`EXCLUDED_SUBTREES` - processo e campanha), o criterio-mae de
aceitacao da secao 4.1 da spec:

  1. ZERO wikilinks `[[ ]]` fora de blocos/trechos de codigo. A unica excecao
     legitima sao atributos C++ ([[nodiscard]], [[likely]], [[maybe_unused]], ...)
     dentro de uma fence de codigo (``` ... ```) ou de inline-code (`...`).
  2. ZERO paths locais (`/home/petrus`, `~/.claude`). Vale para `.md` e, dentro
     de `skills/`, tambem para `.py`, `.sh` e `.json`.
  3. ZERO termos pessoais do autor e de projetos privados (ver PERSONAL_TERMS).
     Vale para `.md` e, dentro de `skills/`, tambem para `.py`, `.sh` e `.json`.
     NOTA: "lider supremo / soberano" aplicado AO USUARIO que instala e uma
     feature de produto (transferencia de titulo, spec 4.2) e NAO e violacao;
     por isso nao entra nesta lista.
  4. ZERO links Markdown relativos `.md` apontando para arquivo inexistente
     (checagem ativa de orfaos; ignora http(s)://, mailto: e ancoras `#`).
  Em `docs/house/` (copia do vault, CONS-04B) valem so as dimensoes 2 e 3: a
  dimensao 2 fica restrita a caminho `/home/`, e a 3 recebe os termos privados
  extras lidos do arquivo local (ver `carregar_termos_privados`).
  5. Varredura nao vazia: ao menos um `.md` no escopo. Varredura vazia reprova
     (fail-closed): uma raiz sem nada a validar nao pode aprovar por silencio.

Lista de arquivos (CONS-03B): dentro de repo git, so o que o git versiona
(`git ls-files`); `node_modules/` nao rastreado fica de fora. Fora de git, varredura
de disco, com aviso na saida.

Agents de jogo, pericia, pedagogia e sobreposicao ENTRAM no plugin (lista de excluidos
revogada em 20/11/2026): nao ha mais lista de refs excluidas.

Uso:
    python3 scripts/validate_plugin.py [--root DIR] [--quiet]

Termos privados extras (projetos e areas pessoais) ficam num arquivo LOCAL e
nao versionado: `$BIGTECH_TERMOS_PRIVADOS` ou `~/.config/bigtech/termos_privados.txt`.
Sem o arquivo, a saida avisa que rodou so com a lista publica.

Saida:
    - relatorio por dimensao (PASS/FAIL com contagem e localizacao das violacoes);
    - exit code 0 se tudo PASS, 1 se qualquer dimensao FAIL.

Reaproveitado no pre-CI (TST-T15) e como DoD incremental de itens de texto.
So usa a stdlib (sem dependencias externas).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracao do escopo e das regras (fonte: spec 4.1 + Apendice A).
# ---------------------------------------------------------------------------

# Diretorios validados (relativos a raiz do repo).
SCAN_DIRS = ("agents", "skills", "docs")

# Subarvores ignoradas: processo / nao produto distribuido ao instalador.
# - docs/superpowers: spec + template de higienizacao (exibem `[[ ]]` como EXEMPLO)
# - docs/auditoria: dossie de auditoria
# - docs/submission: material de submissao ao marketplace
# - docs/campanha: snapshots e metricas da campanha de melhoria (paths, nomes)
# - docs/house: copia canônica do vault para quem nao tem vault; contem wikilinks
#   e nomes de papel por desenho. Este gate zero-orfaos NAO re-higieniza o vault:
#   a higiene do produto distribuido continua em agents/, skills/ e no restante
#   de docs/ (manuais higienizados em docs/house/, principles, etc.).
EXCLUDED_SUBTREES = (
    "docs/superpowers",
    "docs/auditoria",
    "docs/submission",
    "docs/campanha",
)

# Copia do vault (CONS-04B). Entra no escopo so para as dimensoes 2 (caminho local)
# e 3 (termo pessoal). Wikilink e link orfao NAO valem aqui: os manuais preservam
# a sintaxe do vault (ver CONS-10).
HOUSE_SUBTREE = "docs/house"

# Variavel que o Claude Code troca pela raiz do plugin nos corpos de agents e skills.
PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}/"

# Extensoes de texto validadas em todo o escopo (wikilink e link orfao: so .md).
TEXT_SUFFIXES = (".md",)

# Extensoes de codigo e configuracao varridas SO em skills/, para as dimensoes
# de caminho local e termo pessoal (CONS-03). Wikilink e link orfao NAO valem
# aqui: `[[ -f x ]]` em shell e sintaxe, nao wikilink.
SKILL_CODE_SUFFIXES = (".py", ".sh", ".json")

# Atributos C++ que NAO sao wikilinks. So sao tolerados dentro de codigo; um
# `[[nodiscard]]` em prosa corrida ainda seria reportado (defensivo).
CPP_ATTRIBUTES = {
    "nodiscard",
    "likely",
    "unlikely",
    "maybe_unused",
    "fallthrough",
    "noreturn",
    "deprecated",
    "carries_dependency",
    "no_unique_address",
    "assume",
}

# Termos pessoais do autor-soberano. Determinístico e conservador: so o que prende
# o produto a IDENTIDADE/INFRA do autor. "soberano/lider supremo" isolado NAO entra
# (é a transferencia de titulo ao usuario, spec 4.2 — feature, nao vazamento).
PERSONAL_TERMS = (
    r"petrus",
    r"petrinhu",
    r"kaiser",
    r"petrinhu@yahoo\.com\.br",
    r"yahoo\.com\.br",
    # Projetos e pessoas privados (CONS-03, incluido em 20/11/2026).
    r"gusworld",
    r"glintfx",
    r"drpetrus",
    r"justi[cç]a federal",
)

# Paths locais proibidos.
LOCAL_PATHS = (
    r"/home/petrus",
    r"~/\.claude",
)

# Em docs/house a dimensao 2 vale so para caminho de home de qualquer usuario:
# `~/.claude` e convencao publica do plugin, nao dado pessoal.
HOUSE_LOCAL_PATHS = (r"/home/",)

# Arquivo LOCAL com termos privados extras (um por linha, `#` comenta). Nao versionado.
TERMOS_PRIVADOS_ENV = "BIGTECH_TERMOS_PRIVADOS"

# Whitelist explicita de violacoes conhecidas-e-aceitas. Cada entrada precisa de
# justificativa; nenhuma deveria existir no estado limpo. Formato:
#   (dimensao, path_relativo, lineno_ou_None, justificativa)
# Mantida vazia de proposito: o estado-alvo do produto e zero violacoes reais.
WHITELIST: tuple[tuple[str, str, int | None, str], ...] = ()


# ---------------------------------------------------------------------------
# Regexes pre-compilados.
# ---------------------------------------------------------------------------

RE_WIKILINK = re.compile(r"\[\[([^\]\n]+?)\]\]")
RE_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
RE_INLINE_CODE = re.compile(r"`[^`\n]*`")
RE_MD_LINK = re.compile(r"\]\(\s*([^)\s]+?)\s*\)")
RE_LOCAL_PATH = re.compile("|".join(LOCAL_PATHS), re.IGNORECASE)
RE_HOUSE_LOCAL_PATH = re.compile("|".join(HOUSE_LOCAL_PATHS), re.IGNORECASE)


def padrao_pessoal(termos_extra: tuple[str, ...] = ()) -> re.Pattern[str]:
    """Regex dos termos pessoais: lista publica + termos locais (com fronteira de palavra)."""
    extras = tuple(r"(?<!\w)" + re.escape(t) + r"(?!\w)" for t in termos_extra)
    return re.compile("|".join(PERSONAL_TERMS + extras), re.IGNORECASE)


def termos_privados_path() -> Path:
    """Arquivo local de termos privados: variavel de ambiente ou caminho padrao do usuario."""
    import os

    env = os.environ.get(TERMOS_PRIVADOS_ENV)
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config" / "bigtech" / "termos_privados.txt"


def carregar_termos_privados(path: Path) -> tuple[str, ...] | None:
    """Le os termos extras. None quando o arquivo nao existe (rodar so com a lista publica)."""
    if not path.is_file():
        return None
    termos: list[str] = []
    for linha in path.read_text(encoding="utf-8").splitlines():
        limpo = linha.strip()
        if limpo and not limpo.startswith("#"):
            termos.append(limpo)
    return tuple(termos)


@dataclass
class Violation:
    path: str  # relativo a raiz do repo
    line: int
    snippet: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.snippet.strip()[:200]}"


@dataclass
class DimensionResult:
    name: str
    description: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    def status(self) -> str:
        return "PASS" if self.ok else "FAIL"


# ---------------------------------------------------------------------------
# Coleta de arquivos.
# ---------------------------------------------------------------------------


def is_in_excluded_subtree(rel_path: Path) -> bool:
    posix = rel_path.as_posix()
    return any(
        posix == sub or posix.startswith(sub + "/") for sub in EXCLUDED_SUBTREES
    )


def scanned_suffixes(scan_dir: str) -> tuple[str, ...]:
    """Extensoes varridas em cada diretorio do escopo."""
    if scan_dir == "skills":
        return TEXT_SUFFIXES + SKILL_CODE_SUFFIXES
    return TEXT_SUFFIXES


def repo_git_raiz(root: Path) -> bool:
    """True quando `root` e a raiz de um repo git (nao apenas um diretorio dentro dele)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=False,
        )
    except OSError:  # git ausente
        return False
    if proc.returncode != 0:
        return False
    topo = Path(proc.stdout.decode("utf-8", errors="replace").strip())
    return topo.resolve() == root.resolve()


def fonte_da_lista(root: Path) -> str:
    """Rotulo da origem da lista de arquivos (aparece na saida do CLI)."""
    if repo_git_raiz(root):
        return "git ls-files (somente arquivos versionados)"
    return "fora de git: varredura de disco"


def _candidatos_git(root: Path) -> list[str]:
    """Caminhos relativos (posix) versionados pelo git, sem node_modules nao rastreado."""
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [
        p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p
    ]


def _candidatos_disco(root: Path) -> list[str]:
    """Caminhos relativos (posix) de todo o disco nas pastas do escopo (fallback fora de git)."""
    out: list[str] = []
    for scan_dir in SCAN_DIRS:
        base = root / scan_dir
        if base.is_dir():
            out.extend(
                path.relative_to(root).as_posix()
                for path in base.rglob("*")
                if path.is_file()
            )
    return out


def collect_files(root: Path) -> list[Path]:
    """Arquivos do escopo: versionados (git ls-files) ou, fora de git, varredura de disco.

    Aplica depois o mesmo filtro de pastas, extensoes e subarvores excluidas nos dois casos.
    """
    candidatos = _candidatos_git(root) if repo_git_raiz(root) else _candidatos_disco(root)
    files: list[Path] = []
    for rel in sorted(candidatos):
        rel_path = Path(rel)
        if not rel_path.parts or rel_path.parts[0] not in SCAN_DIRS:
            continue
        if rel_path.suffix not in scanned_suffixes(rel_path.parts[0]):
            continue
        if is_in_excluded_subtree(rel_path):
            continue
        path = root / rel_path
        if path.is_file():
            files.append(path)
    return files


# ---------------------------------------------------------------------------
# Logica de "esta dentro de codigo?".
# ---------------------------------------------------------------------------


def code_line_flags(lines: list[str]) -> list[bool]:
    """Retorna, por linha (1-based-friendly em indice 0), se ela esta dentro de
    uma fence de codigo (``` ... ``` ou ~~~ ... ~~~). A linha da propria cerca e
    considerada codigo (nao ha [[ ]] de prosa nela)."""
    in_fence = False
    fence_marker = ""
    flags: list[bool] = []
    for line in lines:
        m = RE_FENCE.match(line)
        if m:
            marker = m.group(1)[0]  # ` ou ~
            if not in_fence:
                in_fence = True
                fence_marker = marker
                flags.append(True)
                continue
            # ja dentro: so fecha se o marcador casar
            if marker == fence_marker:
                in_fence = False
                fence_marker = ""
                flags.append(True)
                continue
            flags.append(True)
            continue
        flags.append(in_fence)
    return flags


def strip_inline_code(text: str) -> str:
    """Remove trechos `inline code` para que [[X]] dentro deles nao conte."""
    return RE_INLINE_CODE.sub("", text)


def is_cpp_attribute(token: str) -> bool:
    """`token` e o conteudo entre [[ ]]. C++ atributo: identificador simples
    (opcionalmente com namespace `gnu::const`) e sem espacos, conhecido na lista."""
    cleaned = token.strip()
    # atributos podem vir como `gnu::const`, `nodiscard("motivo")`, etc.
    head = re.split(r"[(\s]", cleaned, maxsplit=1)[0]
    head = head.split("::")[-1]
    return head in CPP_ATTRIBUTES


# ---------------------------------------------------------------------------
# Dimensoes de validacao.
# ---------------------------------------------------------------------------


def check_wikilinks(rel: str, lines: list[str], code_flags: list[bool]) -> list[Violation]:
    out: list[Violation] = []
    for idx, raw in enumerate(lines):
        if code_flags[idx]:
            # Dentro de fence de codigo: [[atributo]] C++ permitido; qualquer
            # outro [[X]] dentro de codigo tambem nao e wikilink Obsidian, mas
            # so toleramos atributos C++ conhecidos (defensivo). Reporta o resto.
            for m in RE_WIKILINK.finditer(raw):
                if not is_cpp_attribute(m.group(1)):
                    out.append(Violation(rel, idx + 1, raw))
            continue
        # Fora de fence: remover inline-code antes (um [[X]] em `code` nao conta).
        scrubbed = strip_inline_code(raw)
        for m in RE_WIKILINK.finditer(scrubbed):
            # tolerar atributo C++ tambem em inline (raro, mas consistente)
            if is_cpp_attribute(m.group(1)):
                continue
            out.append(Violation(rel, idx + 1, raw))
    return out


def check_regex_dim(
    rel: str, lines: list[str], pattern: re.Pattern[str]
) -> list[Violation]:
    out: list[Violation] = []
    for idx, raw in enumerate(lines):
        if pattern.search(raw):
            out.append(Violation(rel, idx + 1, raw))
    return out


def check_orphan_links(
    rel_path: Path, root: Path, lines: list[str], code_flags: list[bool]
) -> list[Violation]:
    """Resolve cada link Markdown relativo `.md` contra o filesystem.
    Ignora: URLs (http/https/mailto///), ancoras puras (#sec) e nao-.md."""
    out: list[Violation] = []
    src_dir = (root / rel_path).parent
    rel = rel_path.as_posix()
    for idx, raw in enumerate(lines):
        if code_flags[idx]:
            continue  # link dentro de bloco de codigo e ilustrativo
        scrubbed = strip_inline_code(raw)
        for m in RE_MD_LINK.finditer(scrubbed):
            target = m.group(1).strip()
            if not target:
                continue
            low = target.lower()
            if low.startswith(("http://", "https://", "mailto:", "//", "#")):
                continue
            # separa ancora (#) e querystring
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part.lower().endswith(".md"):
                continue
            if path_part.startswith(PLUGIN_ROOT_VAR):
                # `${CLAUDE_PLUGIN_ROOT}` e a raiz do plugin, que e a raiz do repo.
                alvo = root / path_part[len(PLUGIN_ROOT_VAR):]
            else:
                alvo = src_dir / path_part
            resolved = alvo.resolve()
            if not resolved.is_file():
                out.append(
                    Violation(rel, idx + 1, f"link orfao -> {target}  (resolve: {resolved})")
                )
    return out


# ---------------------------------------------------------------------------
# Aplicacao da whitelist.
# ---------------------------------------------------------------------------


def filter_whitelist(dim_name: str, violations: list[Violation]) -> list[Violation]:
    if not WHITELIST:
        return violations
    allowed = {
        (path, line)
        for (dname, path, line, _just) in WHITELIST
        if dname == dim_name
    }
    kept: list[Violation] = []
    for v in violations:
        if (v.path, v.line) in allowed or (v.path, None) in allowed:
            continue
        kept.append(v)
    return kept


# ---------------------------------------------------------------------------
# Orquestracao.
# ---------------------------------------------------------------------------


def is_house_path(rel: str) -> bool:
    return rel == HOUSE_SUBTREE or rel.startswith(HOUSE_SUBTREE + "/")


def run(
    root: Path, termos_extra: tuple[str, ...] = ()
) -> tuple[list[DimensionResult], int, int]:
    files = collect_files(root)
    md_count = 0
    re_pessoal = padrao_pessoal(termos_extra)

    dims = {
        "wikilinks": DimensionResult(
            "wikilinks",
            "ZERO `[[ ]]` fora de codigo (excecao: atributos C++ em fence)",
        ),
        "local_paths": DimensionResult(
            "local_paths", "ZERO paths locais (/home/petrus, ~/.claude)"
        ),
        "personal": DimensionResult(
            "personal", "ZERO termos pessoais do autor e de projetos privados (PERSONAL_TERMS)"
        ),
        "varredura": DimensionResult(
            "varredura", "varredura nao vazia: ao menos 1 .md no escopo"
        ),
        "orphan_links": DimensionResult(
            "orphan_links", "ZERO links Markdown relativos .md orfaos"
        ),
    }

    for path in files:
        rel_path = path.relative_to(root)
        rel = rel_path.as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        code_flags = code_line_flags(lines)

        house = is_house_path(rel)
        dims["local_paths"].violations.extend(
            check_regex_dim(rel, lines, RE_HOUSE_LOCAL_PATH if house else RE_LOCAL_PATH)
        )
        dims["personal"].violations.extend(check_regex_dim(rel, lines, re_pessoal))
        if path.suffix == ".md":
            # Dimensao 5 (links orfaos) vale tambem para docs/house (CONS-13): sem excecao.
            dims["orphan_links"].violations.extend(
                check_orphan_links(rel_path, root, lines, code_flags)
            )
        if path.suffix == ".md" and not house:
            md_count += 1
            dims["wikilinks"].violations.extend(
                check_wikilinks(rel, lines, code_flags)
            )

    if md_count == 0:
        dims["varredura"].violations.append(
            Violation(
                "(raiz)",
                0,
                f"nenhum .md em {', '.join(SCAN_DIRS)}: varredura vazia reprova (fail-closed)",
            )
        )

    results: list[DimensionResult] = []
    for dim in dims.values():
        dim.violations = filter_whitelist(dim.name, dim.violations)
        results.append(dim)

    exit_code = 0 if all(d.ok for d in results) else 1
    return results, exit_code, md_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Raiz do repo do plugin (default: pai de scripts/).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="So imprime FAIL e o resumo final.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"erro: raiz inexistente: {root}", file=sys.stderr)
        return 1
    caminho_termos = termos_privados_path()
    termos_extra = carregar_termos_privados(caminho_termos)
    results, exit_code, n_files = run(root, termos_extra or ())

    print("== Gate ZERO-ORFAOS (spec 4.1) -- plugin bigtech ==")
    print(f"raiz: {root}")
    print(f"escopo: {', '.join(SCAN_DIRS)} (exceto {', '.join(EXCLUDED_SUBTREES)})")
    print(f"lista de arquivos: {fonte_da_lista(root)}")
    if termos_extra is None:
        print(
            f"AVISO: sem arquivo de termos privados ({caminho_termos}); "
            "rodou so com a lista publica"
        )
    else:
        print(f"termos privados locais: {len(termos_extra)} carregados")
    print(f"arquivos .md validados: {n_files}")
    print("codigo de skills (.py, .sh, .json) varrido nas dimensoes de caminho e termo")
    print("-" * 72)

    for dim in results:
        n = len(dim.violations)
        line = f"[{dim.status()}] {dim.name:<13} {dim.description}"
        if dim.ok:
            if not args.quiet:
                print(line + "  (0 ocorrencias)")
        else:
            print(line + f"  ({n} VIOLACOES)")
            for v in dim.violations:
                print(f"        - {v}")

    print("-" * 72)
    overall = "PASS" if exit_code == 0 else "FAIL"
    failed = [d.name for d in results if not d.ok]
    if exit_code == 0:
        print(f"RESULTADO: {overall}: todas as 5 dimensoes do gate 4.1 limpas.")
    else:
        print(f"RESULTADO: {overall}: dimensoes com violacao: {', '.join(failed)}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
