# -*- coding: utf-8 -*-
"""isthmus: sublinguagem hibrida de interoperabilidade, controle e verificacao."""
__version__ = "0.1.0"
ABBREV = ("ISTH",)


def abbrev_name():
    """Abreviacao oficial de Isthmus."""
    return ABBREV[0]

from .errors import Refusal, CODES
from .canon import canonize, PROFILES
from .fringe import fringe
from .shutter import shutter
from .ramp import fit as ramp_fit
from .refase import refase
from .budget import Budget
from .sampler import sample
from .estimator import estimate_two_rounds
from .mitigation import audit as mitigation_audit
from .transpile import audit as transpile_audit
from .quantum import Flow
from .characterize import characterize, check_band
from .receipt import build, verify, verify_chain, REQUIRED

__all__ = ["Refusal", "CODES", "canonize", "PROFILES", "fringe", "shutter", "ramp_fit",
           "refase", "Budget", "sample", "estimate_two_rounds", "mitigation_audit",
           "transpile_audit", "Flow", "characterize", "check_band", "build", "verify",
           "verify_chain", "REQUIRED", "__version__", "ABBREV", "abbrev_name"]
