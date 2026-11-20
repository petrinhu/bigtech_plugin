"""Utilidades compartilhadas pelos hooks do bigtech (CONS-15c).

`nome_evento`: o nome do evento vem do stdin (`hook_event_name`), que o host
informa no payload. O valor padrao do hook vale so quando o campo falta, nao e
texto ou nao e um identificador simples (letras, 1 a 40 caracteres).
"""
import re

_EVENTO_RE = re.compile(r"[A-Za-z]{1,40}")


def nome_evento(data, padrao: str) -> str:
    """Nome do evento vindo do payload, ou `padrao` se ausente ou invalido."""
    nome = data.get("hook_event_name") if isinstance(data, dict) else None
    if isinstance(nome, str) and _EVENTO_RE.fullmatch(nome):
        return nome
    return padrao
