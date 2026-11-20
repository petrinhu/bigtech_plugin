#!/usr/bin/env python3
"""Sincroniza os manuais do vault para `docs/house/` (CONS-04B).

Autoridade: o vault (fonte). A copia do plugin recebe SOMENTE transformacoes de
privacidade e estruturais, todas declaradas em TRANSFORMACOES e identificadas
por id (T1, T2, ...) no cabecalho gerado e na tabela do README.

  T1 wikilink-privado : sai a linha que contem `[[Projects/` ou `[[Areas/`
                        (nomes de projetos e areas pessoais; a linha inteira sai).
  T2 autoridade-pessoal: a linha que comeca com `**O usuário (<nome>)` vira o
                        paragrafo padrao do plugin (sem nome nem titulos pessoais).
  T3a caminho-do-vault: caminho em "cuja CWD esteja dentro de <caminho>" vira
                        "na raiz do vault" (frase do CLAUDE.md do vault).
  T3 caminho-local    : caminho que comeca na raiz de usuario (prefixo montado em
                        PREFIXO_HOME) vira `<caminho local removido>`.
  T4 dominio-producao : linha "- Dominio previsto em producao:" vira o placeholder
                        `{{DOMINIO_PRODUCAO}}` (o dominio pessoal sai).
  T5 link-externo     : link markdown relativo cujo alvo nao existe em docs/house
                        vira so o nome do arquivo, sem link (marca "link-externo",
                        separada das de privacidade).

Nenhuma transformacao nomeia um termo privado: casam por estrutura. Termos
privados extras ficam fora deste arquivo, no validador local.

Seguranca (oraculo): o sha256 do texto ANTES da redacao NUNCA e publicado. Como
as linhas removidas tem pouca entropia, um hash cru deixaria testar palpites.
A versao do vault e autenticada por HMAC-SHA256 com chave local fora do repo
(`~/.config/bigtech/sync_house.key`, modo 600, gerada por --gerar-chave). O hash
publicado do corpo usa prefixo de dominio e reflete o que esta no arquivo.

Uso:
    python3 scripts/sync_house.py --gerar-chave              (uma vez, na maquina)
    python3 scripts/sync_house.py --vault DIR --write        (exige a chave)
    python3 scripts/sync_house.py --vault DIR --check        (confere vault e arquivos)
    Caminho do vault, nesta ordem: --vault, BIGTECH_VAULT, depois o arquivo local
    ~/.config/bigtech/vault_path (uma linha, modo 600, nunca versionado).
    BIGTECH_SYNC_KEY_FILE substitui o caminho da chave.

Saidas: 0 em dia; 1 divergencia; 2 uso ou erro; 3 check sem chave local, isto e,
o corpo foi conferido mas a versao do vault NAO foi autenticada.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import os
import posixpath
import re
import secrets
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

MANUAIS: tuple[str, ...] = (
    "CONTRACT",
    "TESTES",
    "TOOLING",
    "pipeline_release_1.0",
    "DEPLOY_CHECKLIST",
    "lideranca_pipeline_release",
    "ORG",
    "Standards",
    "AGILE",
    "AUDITORIAS",
    "audit-seo",
    "CLAUDE",
)

# Nome do arquivo em docs/house quando ele difere do nome no vault. O CLAUDE.md do
# vault NAO pode virar CLAUDE.md dentro de docs/house: o Claude Code carrega CLAUDE.md
# de subpasta sozinho quando um arquivo dela e lido, e este texto e do vault, nao do
# plugin. O nome CLAUDE-vault.md nao e carregado de forma automatica.
DESTINO_EM_HOUSE: dict[str, str] = {"CLAUDE": "CLAUDE-vault"}


def nome_destino(nome: str) -> str:
    """Nome (sem .md) do arquivo em docs/house para o manual `nome` do vault."""
    return DESTINO_EM_HOUSE.get(nome, nome)


# Arquivos que existem em docs/house depois do sync: os manuais e o README. Conjunto
# declarado, nao lido do disco: o --write numa pasta vazia e o --check seguinte
# precisam decidir igual.
DESTINOS_HOUSE: frozenset[str] = frozenset(
    {f"{nome_destino(n)}.md" for n in MANUAIS} | {"README.md"}
)

FRASE_PRECEDENCIA_LONGA = (
    "As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que "
    "eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin "
    "em qualquer conflito. Onde divergirem, siga as do usuário."
)

REGRA_VAULT = (
    "Se o usuário tiver o vault, o vault prevalece em conflito material; "
    "senão use esta cópia."
)

PARAGRAFO_AUTORIDADE = (
    "Quem opera este plugin é o líder supremo e soberano desta organização."
)

CAMINHO_REMOVIDO = "<caminho local removido>"

MARCA_INICIO = "<!-- sync:tabela inicio -->"
MARCA_FIM = "<!-- sync:tabela fim -->"

# Prefixo de dominio do hash do corpo: impede que o hash de um manual sem redacao
# coincida com o sha256 cru do vault (oraculo).
DOMINIO_CORPO = b"corpo-transformado\n"

# Prefixo montado em partes: o literal nao aparece no fonte (guarda de privacidade).
PREFIXO_HOME = "/" + "home" + "/"
RE_T1 = re.compile(r"\[\[(?:Projects|Areas)/")
RE_T2 = re.compile(r"^\*\*O usuário \([^)\n]*\)[^\n]*$", re.MULTILINE)
RE_T3 = re.compile(re.escape(PREFIXO_HOME) + r"[^\s`)\]]+")
# Frase de CWD do CLAUDE do vault: o caminho inteiro vira o rotulo generico.
RE_T3A = re.compile(
    r"(?<=cuja CWD esteja )dentro de `" + re.escape(PREFIXO_HOME) + r"[^`]*`"
)
# Linha ancorada no rotulo do dominio: o valor vira o placeholder.
RE_T4 = re.compile(r"^(- Dominio previsto em producao:) .*$", re.MULTILINE)
# Link markdown [texto](alvo); wikilink [[X]] fica de fora pelo lookbehind.
RE_T5 = re.compile(r"(?<!\[)\[([^\[\]\n]*)\]\(([^)\s]+)\)")
RE_ESQUEMA = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
RE_LINHA_README = re.compile(
    r"^\| ([^|\s]+\.md) \| `[^`]*` \| `([0-9a-f]{64})` \|", re.MULTILINE
)

CHAVE_MIN_BYTES = 32


class ErroSync(RuntimeError):
    """Falha de uso ou de estrutura que impede a sincronizacao."""


def _t1(corpo: str) -> tuple[str, int]:
    linhas = corpo.splitlines(keepends=True)
    mantidas = [ln for ln in linhas if not RE_T1.search(ln)]
    return "".join(mantidas), len(linhas) - len(mantidas)


def _t2(corpo: str) -> tuple[str, int]:
    return RE_T2.subn(PARAGRAFO_AUTORIDADE, corpo)


def _t3a(corpo: str) -> tuple[str, int]:
    return RE_T3A.subn("na raiz do vault", corpo)


def _t3(corpo: str) -> tuple[str, int]:
    return RE_T3.subn(CAMINHO_REMOVIDO, corpo)


def _t4(corpo: str) -> tuple[str, int]:
    return RE_T4.subn(r"\1 {{DOMINIO_PRODUCAO}}", corpo)


def _alvo_externo(alvo: str) -> bool:
    """True quando o alvo relativo nao existe em docs/house. URL, ancora e caminho absoluto ficam."""
    if alvo.startswith(("#", "/")) or RE_ESQUEMA.match(alvo):
        return False
    caminho = alvo.split("#", 1)[0]
    return posixpath.normpath(caminho) not in DESTINOS_HOUSE


def _t5(corpo: str) -> tuple[str, int]:
    """Link para fora de docs/house vira so o nome do arquivo, sem link."""
    contagem = 0

    def troca(m: re.Match[str]) -> str:
        nonlocal contagem
        alvo = m.group(2)
        if not _alvo_externo(alvo):
            return m.group(0)
        contagem += 1
        nome = posixpath.basename(alvo.split("#", 1)[0].rstrip("/"))
        return nome or m.group(1)

    return RE_T5.sub(troca, corpo), contagem


@dataclass(frozen=True)
class Transformacao:
    id: str
    descricao: str
    aplicar: Callable[[str], tuple[str, int]]
    marca: str = "privacidade"


# Ordem importa: T3a (frase de CWD) roda antes da T3 generica.
TRANSFORMACOES: tuple[Transformacao, ...] = (
    Transformacao("T1", "sai a linha com wikilink de Projects/ ou Areas/", _t1),
    Transformacao("T2", "linha de autoridade pessoal vira o paragrafo padrao", _t2),
    Transformacao("T3a", "caminho do vault na frase de CWD vira 'na raiz do vault'", _t3a),
    Transformacao("T3", "caminho de raiz de usuário vira marcador neutro", _t3),
    Transformacao("T4", "dominio de producao pessoal vira o placeholder", _t4),
    Transformacao(
        "T5",
        "link markdown para fora de docs/house vira o nome do arquivo, sem link",
        _t5,
        marca="link-externo",
    ),
)


def aplicar_transformacoes(corpo: str) -> tuple[str, dict[str, int]]:
    """Aplica as transformacoes em ordem e devolve (corpo, contagem por id)."""
    contagem: dict[str, int] = {}
    for t in TRANSFORMACOES:
        corpo, n = t.aplicar(corpo)
        contagem[t.id] = n
    return corpo, contagem


# ---------------------------------------------------------------------------
# Chave local e autenticacao da versao do vault
# ---------------------------------------------------------------------------


def _modo_posix() -> bool:
    """Bits de modo POSIX so existem fora do Windows (CONS-R11). No Windows a
    chave fica no perfil do usuario, protegida pelo ACL, e o modo 600 nao se aplica."""
    return hasattr(os, "getuid")


def _diretorio_pessoal() -> Path:
    """HOME (ou USERPROFILE, no Windows). Sem ele e erro de uso (2), nunca RuntimeError.

    Path.home() levanta RuntimeError quando nenhuma das duas variaveis existe,
    o que derrubava o gate com traceback no runner Windows (CONS-R11).
    """
    home = os.path.expanduser("~")
    if home == "~" or not os.path.isabs(home):
        raise ErroSync("nao foi possivel determinar o diretorio pessoal (HOME ou USERPROFILE)")
    return Path(home)


def caminho_chave() -> Path:
    env = os.environ.get("BIGTECH_SYNC_KEY_FILE")
    if env:
        return Path(env).expanduser()
    return _diretorio_pessoal() / ".config" / "bigtech" / "sync_house.key"


def caminho_vault_local() -> Path:
    """Arquivo local, fora do repo, com o caminho do vault em uma linha (CONS-10A)."""
    return _diretorio_pessoal() / ".config" / "bigtech" / "vault_path"


def ler_vault_local(arq: Path) -> Path | None:
    """Caminho do vault lido do arquivo local, ou None quando o arquivo nao existe.

    O arquivo tem de ter exatamente uma linha com o caminho. Vazio ou com mais de
    uma linha e erro: nunca cai calado para outra fonte.
    """
    if not arq.is_file():
        return None
    linhas = [ln.strip() for ln in arq.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(linhas) != 1:
        raise ErroSync(f"{arq} deve ter exatamente uma linha com o caminho do vault")
    return Path(linhas[0]).expanduser()


def resolver_vault(flag: Path | None) -> Path | None:
    """Precedencia: --vault, depois BIGTECH_VAULT, depois o arquivo local. Sem nenhum: None."""
    if flag is not None:
        return flag
    env = os.environ.get("BIGTECH_VAULT")
    if env:
        return Path(env)
    return ler_vault_local(caminho_vault_local())


def gerar_chave(path: Path) -> None:
    """Cria a chave uma vez, com modo 600. Nunca sobrescreve."""
    if path.exists():
        raise ErroSync(f"chave ja existe em {path}; nao sobrescrevo")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(secrets.token_hex(32) + "\n")


def carregar_chave(path: Path) -> bytes | None:
    """Chave local, ou None quando o arquivo nao existe. Recusa permissao aberta."""
    if not path.is_file():
        return None
    if _modo_posix() and path.stat().st_mode & 0o077:
        raise ErroSync(f"permissao aberta na chave {path}; use chmod 600")
    try:
        chave = bytes.fromhex(path.read_text(encoding="utf-8").strip())
    except ValueError as exc:
        raise ErroSync(f"chave malformada em {path}") from exc
    if len(chave) < CHAVE_MIN_BYTES:
        raise ErroSync(f"chave curta demais em {path}")
    return chave


def hmac_vault(texto_vault: str, chave: bytes) -> str:
    return hmac.new(chave, texto_vault.encode("utf-8"), hashlib.sha256).hexdigest()


def _hash_corpo(corpo: str) -> str:
    return hashlib.sha256(DOMINIO_CORPO + corpo.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Geracao de manual e cabecalho
# ---------------------------------------------------------------------------


def _cabecalho(nome: str, data: str, autenticador: str, contagem: dict[str, int]) -> str:
    transf = " ".join(f"{k}={v}" for k, v in contagem.items())
    return (
        "<!--\n"
        "  docs/house sync\n"
        f"  origem: vault claudebrain / {nome}.md\n"
        f"  sync_date: {data}\n"
        f"  hmac_vault_sha256: {autenticador}\n"
        f"  transformacoes: {transf}\n"
        f"  regra: {FRASE_PRECEDENCIA_LONGA} {REGRA_VAULT}\n"
        "  sem segredos: não incluir tokens/credenciais\n"
        "-->\n"
    )


@dataclass(frozen=True)
class Preparado:
    texto: str
    autenticador: str
    sha_corpo: str
    contagem: dict[str, int]


def _preparar(texto_vault: str, nome: str, data: str, chave: bytes | None) -> Preparado:
    corpo, contagem = aplicar_transformacoes(texto_vault)
    autenticador = hmac_vault(texto_vault, chave) if chave is not None else "sem-chave-local"
    texto = _cabecalho(nome, data, autenticador, contagem) + corpo
    return Preparado(texto, autenticador, _hash_corpo(corpo), contagem)


def gerar_manual(texto_vault: str, nome: str, data: str, chave: bytes | None = None) -> str:
    return _preparar(texto_vault, nome, data, chave).texto


def extrair_data(texto_house: str) -> str:
    m = re.search(r"^  sync_date: (\S+)$", texto_house, re.MULTILINE)
    if m is None:
        raise ErroSync("cabecalho sem sync_date")
    return m.group(1)


def _corpo_apos_cabecalho(texto: str) -> str:
    return texto[texto.find("-->\n") + 4 :]


def _ids_aplicados(contagem: dict[str, int]) -> tuple[str, ...]:
    return tuple(k for k, v in contagem.items() if v > 0)


# ---------------------------------------------------------------------------
# README e sincronizacao em disco
# ---------------------------------------------------------------------------


def renderizar_readme(
    readme: str, entradas: Sequence[tuple[str, str, str, tuple[str, ...]]]
) -> str:
    """Substitui o conteudo entre as marcas pela tabela das entradas.

    Cada entrada: (arquivo, hmac_vault_sha256, sha256_corpo_transformado, ids_aplicados).
    """
    if MARCA_INICIO not in readme or MARCA_FIM not in readme:
        raise ErroSync("README sem as marcas de tabela sync:tabela inicio/fim")
    linhas = [
        "| Arquivo | hmac_vault_sha256 (chave local) | sha256_corpo_transformado | Transformações aplicadas |",
        "|---|---|---|---|",
    ]
    for arquivo, autent, sha_c, ids in entradas:
        aplicadas = ", ".join(ids) if ids else "nenhuma"
        linhas.append(f"| {arquivo} | `{autent}` | `{sha_c}` | {aplicadas} |")
    tabela = "\n".join(linhas)
    antes, resto = readme.split(MARCA_INICIO, 1)
    _, depois = resto.split(MARCA_FIM, 1)
    return f"{antes}{MARCA_INICIO}\n{tabela}\n{MARCA_FIM}{depois}"


def _ler_vault(vault: Path, nome: str) -> str:
    arq = vault / f"{nome}.md"
    if not arq.is_file():
        raise ErroSync(f"manual ausente no vault: {nome}.md")
    # Vault salvo com CRLF (Windows) tem de comparar igual ao manual gerado em LF.
    return arq.read_bytes().decode("utf-8").replace("\r\n", "\n")


@dataclass
class ResultadoSync:
    divergentes: list[str]
    nao_conferido: bool = False
    motivo: str = ""


MOTIVO_SEM_CHAVE = "a chave local nao esta na maquina"
MOTIVO_SEM_VAULT = "sem vault: so o corpo e a tabela do README foram conferidos"


def _sha_corpo_no_readme(readme: str) -> dict[str, str]:
    """Mapa arquivo -> sha256_corpo_transformado, lido da tabela do README."""
    return {m.group(1): m.group(2) for m in RE_LINHA_README.finditer(readme)}


def conferir_sem_vault(house: Path) -> ResultadoSync:
    """Sem vault (CI): confere cada manual contra o hash do corpo gravado no README.

    Nao autentica a versao do vault (isso exige HMAC com a chave). Por isso o
    resultado e sempre nao_conferido: a verificacao e parcial e nao vira PASS.
    """
    readme = house / "README.md"
    if not readme.is_file():
        raise ErroSync("docs/house/README.md ausente")
    shas = _sha_corpo_no_readme(readme.read_text(encoding="utf-8"))
    divergentes: list[str] = []
    for nome in MANUAIS:
        arq = house / f"{nome_destino(nome)}.md"
        if not arq.is_file():
            divergentes.append(arq.name)
            continue
        corpo = _corpo_apos_cabecalho(arq.read_text(encoding="utf-8"))
        if shas.get(arq.name) != _hash_corpo(corpo):
            divergentes.append(arq.name)
    return ResultadoSync(divergentes, True, MOTIVO_SEM_VAULT)


def _checar_manual(
    vault_text: str, nome: str, atual: str, chave: bytes | None
) -> tuple[bool, Preparado | None]:
    """Devolve (divergente, preparado). Sem chave, confere so o corpo."""
    try:
        data_cab = extrair_data(atual)
    except ErroSync:
        return True, None  # cabecalho removido ou reescrito a mao
    prep = _preparar(vault_text, nome, data_cab, chave)
    if _corpo_apos_cabecalho(atual) != _corpo_apos_cabecalho(prep.texto):
        return True, prep
    if chave is not None and prep.texto != atual:
        return True, prep
    return False, prep


def sincronizar(
    vault: Path, house: Path, data: str | None, modo: str, chave: bytes | None
) -> ResultadoSync:
    """Grava (modo 'write') ou confere (modo 'check') os manuais e o README."""
    if modo not in ("write", "check"):
        raise ErroSync(f"modo invalido: {modo}")
    if modo == "write" and chave is None:
        raise ErroSync("--write exige a chave local; rode --gerar-chave antes")
    data_hoje = data or dt.date.today().isoformat()
    divergentes: list[str] = []
    entradas: list[tuple[str, str, str, tuple[str, ...]]] = []
    for nome in MANUAIS:
        texto_vault = _ler_vault(vault, nome)
        arq = house / f"{nome_destino(nome)}.md"
        if modo == "write":
            prep = _preparar(texto_vault, nome, data_hoje, chave)
            house.mkdir(parents=True, exist_ok=True)
            arq.write_text(prep.texto, encoding="utf-8", newline="\n")
        else:
            if not arq.is_file():
                divergentes.append(arq.name)
                continue
            atual = arq.read_text(encoding="utf-8")
            divergente, prep_opt = _checar_manual(texto_vault, nome, atual, chave)
            if divergente:
                divergentes.append(arq.name)
            if prep_opt is None:
                continue
            prep = prep_opt
        entradas.append((arq.name, prep.autenticador, prep.sha_corpo, _ids_aplicados(prep.contagem)))

    readme = house / "README.md"
    if not readme.is_file():
        raise ErroSync("docs/house/README.md ausente")
    atual_readme = readme.read_text(encoding="utf-8")
    novo_readme = renderizar_readme(atual_readme, entradas)
    if modo == "write":
        readme.write_text(novo_readme, encoding="utf-8", newline="\n")
        return ResultadoSync([], False)
    if chave is None:
        # Sem chave a tabela do README (com HMAC) nao e reproduzivel; so o corpo foi conferido.
        return ResultadoSync(divergentes, True, MOTIVO_SEM_CHAVE)
    if novo_readme != atual_readme:
        divergentes.append(readme.name)
    return ResultadoSync(divergentes, False)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--vault", type=Path, default=None, help="raiz do vault (ou BIGTECH_VAULT)")
    parser.add_argument(
        "--house",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "docs" / "house",
        help="pasta de destino (default: docs/house do plugin)",
    )
    parser.add_argument("--data", default=None, help="sync_date AAAA-MM-DD (default: hoje)")
    parser.add_argument("--gerar-chave", action="store_true", help="cria a chave local (uma vez)")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--write", action="store_const", const="write", dest="modo")
    grupo.add_argument("--check", action="store_const", const="check", dest="modo")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    try:
        if args.gerar_chave:
            gerar_chave(caminho_chave())
            print(f"chave local criada em {caminho_chave()} (modo 600); nao versionar")
            return 0
        if args.modo is None:
            print("erro: informe --write, --check ou --gerar-chave", file=sys.stderr)
            return 2
        vault = resolver_vault(args.vault)
        if vault is None:
            # Sem vault so vale o --check de CI (sem chave): confere corpo e README.
            # Com chave na maquina, a conferencia exige o vault: erro 2, nunca 3.
            if args.modo != "check" or caminho_chave().is_file():
                print(
                    "erro: informe --vault ou BIGTECH_VAULT (a conferencia com chave local exige o vault)",
                    file=sys.stderr,
                )
                return 2
            res = conferir_sem_vault(args.house)
        else:
            chave = carregar_chave(caminho_chave())
            res = sincronizar(vault.resolve(), args.house, args.data, args.modo, chave)
    except ErroSync as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2

    if args.modo == "write":
        print(f"docs/house gravado: {len(MANUAIS)} manuais e README")
        return 0
    if res.divergentes:
        print("divergentes: " + ", ".join(res.divergentes))
        return 1
    if res.nao_conferido:
        print(
            f"NAO CONFERIDO: {res.motivo}. A versao do vault nao foi autenticada "
            "(HMAC); a conferencia completa roda na maquina com vault e chave local."
        )
        return 3
    print("docs/house em dia com o vault (versao autenticada por HMAC)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
