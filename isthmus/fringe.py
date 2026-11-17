# -*- coding: utf-8 -*-
"""Fringe: mede a diferenca entre duas canonizacoes, sem comparar texto."""


def _b(x):
    return x["bytes"] if isinstance(x, dict) else (x.encode("utf-8") if isinstance(x, str) else x)


def fringe(a, b):
    a, b = _b(a), _b(b)
    if a == b:
        return {"state": "no-drift", "length": len(a)}
    lim = min(len(a), len(b))
    i = next((k for k in range(lim) if a[k] != b[k]), lim)
    if i >= lim:
        kind = "length"
    else:
        prev = a[i - 1] if i else None
        if prev == 0x5C or (i and b[i - 1] == 0x5C):
            kind = "control-escape"
        elif a[i] in b" \t\n\r" or b[i] in b" \t\n\r":
            kind = "whitespace"
        else:
            kind = "byte"
    return {"state": "drift", "index": i, "kind": kind,
            "left": a[max(0, i - 8):i + 12].decode("latin-1"),
            "right": b[max(0, i - 8):i + 12].decode("latin-1")}
