# -*- coding: utf-8 -*-
"""Ramp: aquisicao nao destrutiva em rampa. Ajusta a reta, nao espera o valor final."""
from .errors import Refusal


def _slope(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def fit(samples, min_slope_ratio=0.5, max_resid_sigma=3.0):
    """samples: [(t, counts)]. Devolve taxa, intercepto e dispersao."""
    n = len(samples)
    if n < 3:
        raise Refusal("ISTH-RAMP-SHORT", f"{n} amostras")
    ts = [float(t) for t, _ in samples]
    ys = [float(c) for _, c in samples]
    slope = _slope(ts, ys)
    inter = sum(ys) / n - slope * (sum(ts) / n)
    resid = [y - (inter + slope * t) for t, y in zip(ts, ys)]
    sigma = (sum(r * r for r in resid) / max(n - 2, 1)) ** 0.5

    h = n // 2
    s1, s2 = _slope(ts[:h], ys[:h]), _slope(ts[h:], ys[h:])
    if s1 > 0 and s2 < min_slope_ratio * s1:
        raise Refusal("ISTH-RAMP-BREAK", f"inclinacao {s1:.3f} -> {s2:.3f}")
    if sigma > 0 and max(abs(r) for r in resid) > max_resid_sigma * sigma:
        raise Refusal("ISTH-RAMP-BREAK", "residuo acima de 3 sigma")
    return {"rate": slope, "intercept": inter, "sigma": sigma, "samples": n}
