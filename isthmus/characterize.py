# -*- coding: utf-8 -*-
"""Characterize: mede o dispositivo e impede banda mais otimista que o ruido."""
from .errors import Refusal


def characterize(error_rate, coherence_us, backend, measured_at):
    return {"error_rate": float(error_rate), "coherence_us": float(coherence_us),
            "backend": backend, "measured_at": measured_at}


def check_band(band, profile):
    if float(band) < float(profile["error_rate"]):
        raise Refusal("ISTH-BAND-OPTIMISM",
                      f"banda {band} < ruido {profile['error_rate']}")
    return {"band": float(band), "noise": float(profile["error_rate"]), "state": "coerente"}
