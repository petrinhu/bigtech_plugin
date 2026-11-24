#!/usr/bin/env python3
# limpa_texto.py - sanitizador UNICO da skill eficacia (filtro stdin -> stdout).
# Descarta todo caractere de categoria unicode que comeca com "C" (controles Cc,
# formato Cf como os overrides bidi, codigos privados Co, nao atribuidos Cn),
# exceto \t e \n. Assim escape de terminal (ESC, BEL, CSI C1 U+009B) e bidi (U+202E)
# nunca chegam a fila, as decisoes, os desvios nem a tela do acordar.
import sys
import unicodedata


def limpa(texto):
    return "".join(c for c in texto if c in "\t\n" or not unicodedata.category(c).startswith("C"))


def main():
    dados = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    sys.stdout.buffer.write(limpa(dados).encode("utf-8"))


if __name__ == "__main__":
    main()
