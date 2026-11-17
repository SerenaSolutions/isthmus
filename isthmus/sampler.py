# -*- coding: utf-8 -*-
"""Sampler: coleta contagens com tiros declarados antes."""
from .errors import Refusal


def sample(backend, shots, budget=None, seed=0, oracle=1):
    if budget is not None:
        budget.spend(shots=shots, oracle=oracle)
    counts = backend(shots=shots, seed=seed)
    total = sum(int(v) for v in counts.values())
    if total != shots:
        raise Refusal("ISTH-SHOTS", f"executados {total}, declarados {shots}")
    return {"counts": dict(counts), "shots": shots, "seed": seed,
            "budget": budget.snapshot() if budget else None}
