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


# ---------------------------------------------------------------------------
# Ramp sequencial: a parte que quebra o desperdicio de tiros fixos.
# Para cedo quando a barra fecha, em vez de gastar 4096 tiros por hipotese.
# ---------------------------------------------------------------------------
import math

VEREDITOS = (1, 0, "REFUSED")


def llr_bernoulli(sucessos, falhas, p0, p1):
    """Log-verossimilhanca acumulada de Wald para H0: p<=p0 contra H1: p>=p1."""
    if not (0.0 < p0 < p1 < 1.0):
        raise ValueError("exige 0 < p0 < p1 < 1")
    return sucessos * math.log(p1 / p0) + falhas * math.log((1.0 - p1) / (1.0 - p0))


def limites_sprt(alpha=0.05, beta=0.05):
    """Fronteiras de Wald. Acima de A decide 1, abaixo de B decide 0."""
    if not (0.0 < alpha < 1.0 and 0.0 < beta < 1.0):
        raise ValueError("alpha e beta em (0, 1)")
    return math.log((1.0 - beta) / alpha), math.log(beta / (1.0 - alpha))


def raio_hoeffding(n, alpha=0.05):
    """Meia-largura da sequencia de confianca de Hoeffding para variavel em [0,1]."""
    if n <= 0:
        return 1.0
    return math.sqrt(math.log(2.0 / alpha) / (2.0 * n))


def decidir_sequencial(amostras, p0, p1, alpha=0.05, beta=0.05, max_shots=4096,
                       regra="sprt"):
    """Consome observacoes 0/1 e para assim que a decisao fecha.

    Devolve {"verdict": 1|0|"REFUSED", "shots", "regra", "llr" ou "raio"}.

    Duas regras, com poderes diferentes, e a diferenca importa:
    - "sprt" compara duas hipoteses simples (p<=p0 contra p>=p1). Se a taxa real
      cair entre as duas, a caminhada aleatoria acaba cruzando uma fronteira e o
      teste ESCOLHE um lado, mesmo sem evidencia. SPRT so devolve REFUSED quando
      o orcamento de tiros acaba. Para decisao binaria, e o teste certo.
    - "hoeffding" usa sequencia de confianca e mantem uma faixa indecidivel entre
      p0 e p1. E a unica das duas que sustenta o terceiro valor por merito, nao
      por falta de tiros. Para veredito trivalente, use esta.
    """
    if regra not in ("sprt", "hoeffding"):
        raise ValueError("regra deve ser 'sprt' ou 'hoeffding'")
    A, B = limites_sprt(alpha, beta)
    sucessos = falhas = 0
    llr = 0.0
    usados = 0
    for obs in amostras:
        if usados >= max_shots:
            break
        usados += 1
        if obs:
            sucessos += 1
            llr += math.log(p1 / p0)
        else:
            falhas += 1
            llr += math.log((1.0 - p1) / (1.0 - p0))
        if regra == "sprt":
            if llr >= A:
                return {"verdict": 1, "shots": usados, "regra": "sprt", "llr": round(llr, 6)}
            if llr <= B:
                return {"verdict": 0, "shots": usados, "regra": "sprt", "llr": round(llr, 6)}
        else:
            taxa = sucessos / usados
            eps = raio_hoeffding(usados, alpha)
            if taxa - eps >= p1:
                return {"verdict": 1, "shots": usados, "regra": "hoeffding",
                        "raio": round(eps, 6), "taxa": round(taxa, 6)}
            if taxa + eps <= p0:
                return {"verdict": 0, "shots": usados, "regra": "hoeffding",
                        "raio": round(eps, 6), "taxa": round(taxa, 6)}
    return {"verdict": "REFUSED", "shots": usados, "regra": regra,
            "motivo": "ISTH-BUDGET", "llr": round(llr, 6)}


def decidir_dos_counts(counts, p0, p1, alpha=0.05, beta=0.05, max_shots=4096,
                        target_key="1", regra="sprt"):
    """Decide a partir de contagens ja agregadas.

    Contagem agregada perde a ordem das observacoes, e a ordem muda o ponto de
    parada. Entao devolvemos a faixa honesta: parada otimista (sucessos primeiro)
    e pessimista (falhas primeiro). O veredito nao depende da ordem, so a parada.
    """
    total = sum(counts.values())
    if total == 0:
        raise ValueError("contagens vazias")
    if total > max_shots:
        raise Refusal("ISTH-BUDGET", f"{total} tiros acima do orcamento de {max_shots}")
    sucessos = counts.get(target_key, 0)
    falhas = total - sucessos
    llr = llr_bernoulli(sucessos, falhas, p0, p1)
    A, B = limites_sprt(alpha, beta)
    taxa = sucessos / total
    if regra == "hoeffding":
        # faixa indecidivel preservada: so decide se o intervalo inteiro cai de um lado
        eps = raio_hoeffding(total, alpha)
        if taxa - eps >= p1:
            veredito = 1
        elif taxa + eps <= p0:
            veredito = 0
        else:
            veredito = "REFUSED"
    else:
        veredito = 1 if llr >= A else (0 if llr <= B else "REFUSED")

    def parada(sucesso_primeiro):
        s = f = 0
        acumulado = 0.0
        for i in range(total):
            vira_sucesso = (i < sucessos) if sucesso_primeiro else (i >= falhas)
            if vira_sucesso:
                s += 1
                acumulado += math.log(p1 / p0)
            else:
                f += 1
                acumulado += math.log((1.0 - p1) / (1.0 - p0))
            if acumulado >= A or acumulado <= B:
                return i + 1
        return None

    p1_cedo, p0_cedo = parada(True), parada(False)
    candidatos = [x for x in (p1_cedo, p0_cedo) if x is not None]
    return {
        "verdict": veredito,
        "taxa": round(sucessos / total, 6),
        "llr": round(llr, 6),
        "shots_declarados": total,
        "parada_min": min(candidatos) if candidatos else None,
        "parada_max": max(candidatos) if candidatos else None,
        "parada_se_sucessos_primeiro": p1_cedo,
        "parada_se_falhas_primeiro": p0_cedo,
        "economia_contra_4096": round(1.0 - total / 4096.0, 4),
        "regra": regra,
        "aviso": ("SPRT escolhe entre duas hipoteses simples: veredito 0 significa "
                  "'p=0.85 mais verossimil que p=0.95', NAO significa 'p<=0.85'"
                  if regra == "sprt" else "faixa indecidivel respeitada"),
    }
