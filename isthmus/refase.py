# -*- coding: utf-8 -*-
"""Refase: alinha fase entre duas medicoes antes de comparar."""
from .errors import Refusal


def refase(a, b, band):
    n = min(len(a), len(b))
    if n < 3:
        raise Refusal("ISTH-REFASE-BAND", "series curtas")
    best, best_custo = 0, None
    for k in range(n):
        custo = sum((a[i] - b[(i - k) % n]) ** 2 for i in range(n)) / n
        if best_custo is None or custo < best_custo:
            best, best_custo = k, custo
    if best_custo ** 0.5 > band:
        raise Refusal("ISTH-REFASE-BAND", f"residuo {best_custo ** 0.5:.4f} > {band}")
    return {"shift": best, "residual": best_custo ** 0.5, "band": band}
