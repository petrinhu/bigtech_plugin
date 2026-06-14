#!/usr/bin/env python3
"""Gate ZERO-ORFAOS (spec 4.1) do plugin bigtech — validador reutilizavel.

Valida, sobre `agents/`, `skills/` e `docs/` (EXCETO `docs/superpowers/`, que e
material de processo e contem exemplos legitimos de `[[wikilinks]]` no template de
higienizacao), o criterio-mae de aceitacao da secao 4.1 da spec:

  1. ZERO wikilinks `[[ ]]` fora de blocos/trechos de codigo. A unica excecao
     legitima sao atributos C++ ([[nodiscard]], [[likely]], [[maybe_unused]], ...)
     dentro de uma fence de codigo (``` ... ```) ou de inline-code (`...`).
  2. ZERO paths locais (`/home/petrus`, `~/.claude`).
  3. ZERO termos pessoais do autor-soberano (petrus, petrinhu, kaiser, hostinger,
     e-mail do autor). NOTA: "lider supremo / soberano" aplicado AO USUARIO que
     instala e uma feature de produto (transferencia de titulo, spec 4.2) e NAO e
     violacao; por isso nao entra nesta lista.
  4. ZERO referencias aos 20 agents/skills excluidos (jogo, pericia, sobreposicao,
     pessoal) nem as skills `/proj_jogo` e `/pericia-medica`.
  5. ZERO links Markdown relativos `.md` apontando para arquivo inexistente
     (checagem ativa de orfaos; ignora http(s)://, mailto: e ancoras `#`).

Uso:
    python3 scripts/validate_plugin.py [--root DIR] [--quiet]

Saida:
    - relatorio por dimensao (PASS/FAIL com contagem e localizacao das violacoes);
    - exit code 0 se tudo PASS, 1 se qualquer dimensao FAIL.

Reaproveitado no pre-CI (TST-T15) e como DoD incremental de itens de texto.
So usa a stdlib (sem dependencias externas).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracao do escopo e das regras (fonte: spec 4.1 + Apendice A).
# ---------------------------------------------------------------------------

# Diretorios validados (relativos a raiz do repo).
SCAN_DIRS = ("agents", "skills", "docs")

# Subarvores ignoradas: processo, nao produto. docs/superpowers contem a spec e o
# template de higienizacao (exibem `[[ ]]` como EXEMPLO); docs/auditoria e o dossie
# de auditoria; docs/submission e o material de submissao ao marketplace. Todos
# gitignored, material de processo local, fora do produto distribuido.
EXCLUDED_SUBTREES = ("docs/superpowers", "docs/auditoria", "docs/submission")

# Extensoes de texto validadas.
TEXT_SUFFIXES = (".md",)

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
    r"hostinger",
    r"petrinhu@yahoo\.com\.br",
    r"yahoo\.com\.br",
)

# Paths locais proibidos.
LOCAL_PATHS = (
    r"/home/petrus",
    r"~/\.claude",
)

# Os 20 agents/skills excluidos + 2 skills excluidas (spec 2.2 / Apendice A cat. 9).
# Ordenados por especificidade; usados como \b...\b para reduzir falso-positivo.
EXCLUDED_REFS = (
    # Jogo (10 agents)
    r"3d-artist-rigger",
    r"audio-designer-composer",
    r"economy-designer",
    r"engine-graphics-programmer",
    r"game-animator",
    r"gameplay_engineer",
    r"game-producer",
    r"lead-game-designer",
    r"level-designer",
    r"narrative-designer",
    # Pericia/forense (4 agents)
    r"dr-advogado",
    r"dr-medico-perito",
    r"dr-medico-psiquiatra",
    r"dr-medico-trabalho",
    r"dr-medico",  # cobre qualquer dr-medico-* nao listado
    # Pessoal/literario/pedagogico (4 agents)
    r"narrative-writer",
    r"revisor-textual",
    r"learning-designer",
    r"linux-diag",
    # Sobreposicao (2 agents)
    r"engineering-coach",
    r"product-marketing-manager",
    # Skills excluidas (2)
    r"proj_jogo",
    r"pericia-medica",
)

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
RE_PERSONAL = re.compile("|".join(PERSONAL_TERMS), re.IGNORECASE)
RE_LOCAL_PATH = re.compile("|".join(LOCAL_PATHS), re.IGNORECASE)
RE_EXCLUDED = re.compile(
    "|".join(rf"\b{term}\b" for term in EXCLUDED_REFS), re.IGNORECASE
)


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


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for scan_dir in SCAN_DIRS:
        base = root / scan_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in TEXT_SUFFIXES:
                continue
            rel = path.relative_to(root)
            if is_in_excluded_subtree(rel):
                continue
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
            resolved = (src_dir / path_part).resolve()
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


def run(root: Path) -> tuple[list[DimensionResult], int, int]:
    files = collect_files(root)

    dims = {
        "wikilinks": DimensionResult(
            "wikilinks",
            "ZERO `[[ ]]` fora de codigo (excecao: atributos C++ em fence)",
        ),
        "local_paths": DimensionResult(
            "local_paths", "ZERO paths locais (/home/petrus, ~/.claude)"
        ),
        "personal": DimensionResult(
            "personal", "ZERO termos pessoais do autor (petrus, kaiser, hostinger, e-mail)"
        ),
        "excluded": DimensionResult(
            "excluded", "ZERO refs aos 20 excluidos + /proj_jogo + /pericia-medica"
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

        dims["wikilinks"].violations.extend(check_wikilinks(rel, lines, code_flags))
        dims["local_paths"].violations.extend(
            check_regex_dim(rel, lines, RE_LOCAL_PATH)
        )
        dims["personal"].violations.extend(check_regex_dim(rel, lines, RE_PERSONAL))
        dims["excluded"].violations.extend(check_regex_dim(rel, lines, RE_EXCLUDED))
        dims["orphan_links"].violations.extend(
            check_orphan_links(rel_path, root, lines, code_flags)
        )

    results: list[DimensionResult] = []
    for dim in dims.values():
        dim.violations = filter_whitelist(dim.name, dim.violations)
        results.append(dim)

    exit_code = 0 if all(d.ok for d in results) else 1
    return results, exit_code, len(files)


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
    results, exit_code, n_files = run(root)

    print("== Gate ZERO-ORFAOS (spec 4.1) -- plugin bigtech ==")
    print(f"raiz: {root}")
    print(f"escopo: {', '.join(SCAN_DIRS)} (exceto {', '.join(EXCLUDED_SUBTREES)})")
    print(f"arquivos .md validados: {n_files}")
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
        print(f"RESULTADO: {overall} — todas as 5 dimensoes do gate 4.1 limpas.")
    else:
        print(f"RESULTADO: {overall} — dimensoes com violacao: {', '.join(failed)}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
