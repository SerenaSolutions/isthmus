# -*- coding: utf-8 -*-
"""Shutter: portao de admissao. Recusa antes de qualquer selo."""
import json
from .errors import Refusal


def shutter(payload, required=(), optional=(), max_bytes=65536):
    if not isinstance(payload, dict):
        raise Refusal("ISTH-SHUTTER", "payload nao e objeto")
    allowed = set(required) | set(optional)
    extra = sorted(set(payload) - allowed)
    if extra:
        raise Refusal("ISTH-SHUTTER", f"campo nao declarado: {extra[0]}")
    falta = [k for k in required if k not in payload]
    if falta:
        raise Refusal("ISTH-SHUTTER", f"campo obrigatorio ausente: {falta[0]}")
    size = len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    if size > max_bytes:
        raise Refusal("ISTH-SHUTTER", f"{size} bytes acima de {max_bytes}")
    return {"state": "admitted", "bytes": size, "fields": len(payload)}
