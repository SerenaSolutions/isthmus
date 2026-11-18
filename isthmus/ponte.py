# -*- coding: utf-8 -*-
"""Ponte de vocabulário entre ZEPHIRUM e ISTHMUS.

Nao finge equivalencia: declara o mapa, preserva a origem e recusa quando o
campo nao tem correspondencia. Quem verifica recomputa o selo da origem.
"""
import hashlib
from .errors import Refusal
from .receipt import build, verify as verify_isthmus

MAPA_VERSAO = "ponte-1.0"

# campo do Zephirum -> campo do payload do Isthmus
Z_PARA_I = {
    "verdict": "verdict",
    "shots": "shots",
    "threshold": "p0",
    "epsilon": "error_bound",
}
# campo do payload do Isthmus -> campo do Zephirum
I_PARA_Z = {v: k for k, v in Z_PARA_I.items()}

SEM_CORRESPONDENCIA = {
    "zephirum": ["delta", "p_hat", "exact_interval", "target_key", "rule"],
    "isthmus": ["schema", "gramatica", "profile", "seed", "mode", "coarse", "trim"],
}


def _selo_zephirum(campos):
    """Mesma canonizacao do Zephirum: JSON compacto com chaves ordenadas."""
    import json
    base = {k: v for k, v in campos.items() if k != "receipt_hash"}
    corpo = json.dumps(base, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(corpo.encode()).hexdigest()


def de_zephirum(rec):
    """Envelope do Isthmus carregando um recibo do Zephirum."""
    if not isinstance(rec, dict) or "verdict" not in rec:
        raise Refusal("ISTH-BRIDGE-FORMA", "recibo do Zephirum sem verdict")
    campos = {k: rec[k] for k in ("verdict", "shots", "threshold", "epsilon") if k in rec}
    if len(campos) != 4:
        raise Refusal("ISTH-BRIDGE-CAMPO", "faltam campos mapeaveis")
    env = build(
        verdict=campos["verdict"],
        shots=int(campos["shots"]),
        n=int(campos["shots"]),
        p0=float(campos["threshold"]),
        error_bound=float(campos["epsilon"]),
        mode="bridge",
        seed=0,
    )
    env["ponte"] = {
        "mapa": MAPA_VERSAO,
        "origem": "zephirum",
        "selo_origem": rec.get("receipt_hash"),
        "campos_origem": {k: rec[k] for k in rec},
        "sem_correspondencia": SEM_CORRESPONDENCIA["zephirum"],
    }
    return env


def de_isthmus(rec):
    """Recibo do Zephirum carregando um recibo do Isthmus."""
    ok = verify_isthmus(rec)  # grossa e fina antes de qualquer traducao
    p = rec["payload"]
    out = {
        "verdict": p["verdict"],
        "shots": int(p["shots"]),
        "threshold": float(p["p0"]),
        "epsilon": float(p["error_bound"]),
        "rule": "ponte-1.0",
        "receipt_hash": rec["seal"],
    }
    out["ponte"] = {
        "mapa": MAPA_VERSAO,
        "origem": "isthmus",
        "selo_origem": rec["seal"],
        "campos_origem": dict(p),
        "sem_correspondencia": SEM_CORRESPONDENCIA["isthmus"],
        "estado_origem": ok,
    }
    return out


def verificar(rec):
    """Recomputa o selo da origem e confere o mapa declarado."""
    ponte = rec.get("ponte") if isinstance(rec, dict) else None
    if not isinstance(ponte, dict):
        raise Refusal("ISTH-BRIDGE-AUSENTE", "sem bloco ponte")
    if ponte.get("mapa") != MAPA_VERSAO:
        raise Refusal("ISTH-BRIDGE-MAPA", str(ponte.get("mapa")))
    campos = ponte.get("campos_origem") or {}
    if ponte.get("origem") == "zephirum":
        if _selo_zephirum(campos) != ponte.get("selo_origem"):
            raise Refusal("ISTH-BRIDGE-SELO", "selo de origem nao recomputa")
    elif ponte.get("origem") == "isthmus":
        ver = verify_isthmus({"payload": campos, "seal": ponte.get("selo_origem")})
        if ver.get("state") != "ok":
            raise Refusal("ISTH-BRIDGE-SELO", str(ver))
    else:
        raise Refusal("ISTH-BRIDGE-ORIGEM", str(ponte.get("origem")))
    return {"state": "ok", "mapa": MAPA_VERSAO, "origem": ponte["origem"],
            "sem_correspondencia": len(ponte.get("sem_correspondencia") or [])}
