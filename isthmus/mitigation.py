# -*- coding: utf-8 -*-
"""Mitigation audit: registra o que foi aplicado e o que seria sem isso."""
from .errors import Refusal


def audit(method, factors, mitigated, unmitigated):
    if method and not factors:
        raise Refusal("ISTH-MITIG-UNDECLARED", "metodo sem fatores declarados")
    if not method and mitigated != unmitigated:
        raise Refusal("ISTH-MITIG-UNDECLARED", "valor mitigado sem metodo declarado")
    delta = None
    if mitigated is not None and unmitigated is not None:
        delta = float(mitigated) - float(unmitigated)
    return {"method": method, "factors": list(factors or []),
            "mitigated": mitigated, "unmitigated": unmitigated, "delta": delta}
