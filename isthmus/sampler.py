# -*- coding: utf-8 -*-
"""Sampler: coleta contagens com tiros declarados antes."""
from .errors import Refusal


def sample(backend, shots, budget=None, seed=0, oracle=1):
    if budget is not None:
        budget.spend(shots=shots, oracle=oracle)
    try:
        counts = backend(shots=shots, seed=seed)
    except Exception as e:
        raise Refusal("ISTH-SAMPLER-FAIL", f"{type(e).__name__}: {e}") from e
    if not isinstance(counts, dict) or not counts:
        raise Refusal("ISTH-SAMPLER-FORMATO", f"contagens ausentes ou {type(counts).__name__}")
    limpos = {}
    for k, v in counts.items():
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise Refusal("ISTH-SAMPLER-FORMATO", f"{k}={v!r} nao e inteiro nao negativo")
        limpos[str(k)] = v
    counts = limpos
    total = sum(counts.values())
    if total != shots:
        raise Refusal("ISTH-SHOTS", f"executados {total}, declarados {shots}")
    return {"counts": dict(counts), "shots": shots, "seed": seed,
            "budget": budget.snapshot() if budget else None}
