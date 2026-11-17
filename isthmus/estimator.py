# -*- coding: utf-8 -*-
"""Estimator com Alignment Two: duas rodadas, e a diferenca decide."""
from .errors import Refusal


def estimate_two_rounds(round_fn, band):
    r1 = float(round_fn(1))
    r2 = float(round_fn(2))
    gap = abs(r1 - r2)
    if gap > band:
        raise Refusal("ISTH-ALIGNMENT-DRIFT", f"|{r1:.4f}-{r2:.4f}|={gap:.4f} > {band}")
    return {"estimate": (r1 + r2) / 2, "rounds": [r1, r2], "gap": gap, "band": band}
