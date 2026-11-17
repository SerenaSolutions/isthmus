# -*- coding: utf-8 -*-
"""Transpile audit: ida e volta ate o dialeto do backend, com conferencia."""
from .errors import Refusal


def audit(ops, roundtrip):
    before = list(ops)
    after = list(roundtrip(before))
    if after != before:
        raise Refusal("ISTH-TRANSPILE-LOSS", f"profundidade {len(before)} -> {len(after)}")
    return {"ops": len(before), "roundtrip": "identico"}
