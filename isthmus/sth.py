# -*- coding: utf-8 -*-
"""STH: sublinguagem derivada de Isthmus, restrita a sela, verifica e encadeia.

STH nao decide. Quem precisa decidir usa Isthmus (ISTH). Quem so precisa
transportar e conferir um recibo ja emitido usa STH, que e menor por construcao:
sem Ramp, sem Shutter, sem Estimator, sem banda.
"""
from .canon import canonize
from .errors import Refusal
from . import receipt as _receipt

NAME = "STH"
DERIVED_FROM = "ISTH"


def seal(payload, profile="canon-v1"):
    """Sela um payload ja decidido. Nao avalia merito, nao escolhe veredito."""
    if "verdict" not in payload:
        raise Refusal("ISTH-STH-NOT-ALLOWED", "payload sem verdict: STH nao decide")
    return _receipt.build(**payload)


def verify(rec):
    return _receipt.verify(rec)


def chain(recs):
    return _receipt.verify_chain(recs)


def decide(*_a, **_k):
    """Existe para recusar com nome proprio, e nao com AttributeError."""
    raise Refusal("ISTH-STH-NOT-ALLOWED", "use isthmus (ISTH) para decidir")
