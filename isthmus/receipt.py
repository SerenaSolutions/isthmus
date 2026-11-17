# -*- coding: utf-8 -*-
"""Recibo: fase grossa, fase fina, perfil declarado e cadeia."""
import hashlib
from .canon import canonize
from .errors import Refusal

REQUIRED = ("schema", "gramatica", "profile", "verdict", "p0", "n", "shots",
            "seed", "mode", "error_bound", "coarse", "trim")
SCHEMA = "1.0.0"
GRAMATICA = "1.5.0"


def _seal(payload):
    return hashlib.sha3_256(canonize(payload, payload.get("profile", "canon-v1"))["bytes"]).hexdigest()


def build(prev_seal=None, **fields):
    payload = dict(fields)
    payload.setdefault("schema", SCHEMA)
    payload.setdefault("gramatica", GRAMATICA)
    payload.setdefault("profile", "canon-v1")
    payload.setdefault("coarse", {"schema": "ok", "gramatica": "ok", "campos": "ok"})
    payload.setdefault("trim", {"constante": 0.0, "declarada_por": "emissor"})
    if prev_seal:
        payload["prev_seal"] = prev_seal
    return {"payload": payload, "seal": _seal(payload)}


def verify(rec):
    """Grossa primeiro, fina depois. Grossa barata e falha cedo."""
    payload = rec.get("payload") if isinstance(rec, dict) else None
    if not isinstance(payload, dict):
        raise Refusal("ISTH-COARSE-SCHEMA", "sem payload")
    if payload.get("schema") != SCHEMA:
        raise Refusal("ISTH-COARSE-SCHEMA", str(payload.get("schema")))
    if payload.get("gramatica") != GRAMATICA:
        raise Refusal("ISTH-COARSE-GRAMATICA", str(payload.get("gramatica")))
    for k in REQUIRED:
        if k not in payload:
            raise Refusal("ISTH-COARSE-CAMPO", k)
    if _seal(payload) != rec.get("seal"):
        raise Refusal("ISTH-FINE-SEAL", "selo nao confere")
    return {"state": "ok", "stage": "fine", "profile": payload["profile"]}


def verify_chain(recs):
    """Snowball cai no verify; shower so aparece aqui."""
    for r in recs:
        verify(r)
    for i in range(1, len(recs)):
        if recs[i]["payload"].get("prev_seal") != recs[i - 1]["seal"]:
            raise Refusal("ISTH-CHAIN-SHOWER", f"elo {i} rompido")
    return {"state": "ok", "links": len(recs)}
