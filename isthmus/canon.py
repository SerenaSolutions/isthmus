# -*- coding: utf-8 -*-
"""Canonize: forma canonica, com perfil declarado e versionado."""
import json, hashlib
from .errors import Refusal


def _dump(payload):
    try:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as e:
        raise Refusal("ISTH-CANON-TIPO", f"{type(e).__name__}: {e}") from e


def canon_v1(payload):
    """Perfil 1: escapa controle no estilo curto (\\b, \\f)."""
    return _dump(payload).encode("utf-8")


def canon_u0008(payload):
    """Perfil alternativo: escapa controle em forma unicode explicita."""
    s = _dump(payload).replace("\\b", "\\u0008").replace("\\f", "\\u000c")
    return s.encode("utf-8")


PROFILES = {"canon-v1": canon_v1, "canon-u0008": canon_u0008}


def canonize(payload, profile="canon-v1"):
    # achado do fuzz: profile nao textual (dict, lista) estourava TypeError cru
    if not isinstance(profile, str) or profile not in PROFILES:
        raise Refusal("ISTH-PROFILE", str(profile))
    raw = PROFILES[profile](payload)
    return {"bytes": raw, "sha3": hashlib.sha3_256(raw).hexdigest(), "profile": profile}
