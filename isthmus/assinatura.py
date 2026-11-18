# -*- coding: utf-8 -*-
"""Criptoagilidade: o recibo declara o algoritmo, a verificacao despacha por ele.

O selo (SHA3-256) cobre o payload inteiro, inclusive sig_alg. A assinatura cobre
o selo e fica fora dele, porque nenhuma assinatura pode assinar a si mesma.
Recibos antigos, sem sig_alg, continuam verificando: ausencia significa 'none'.
"""
import base64
from .errors import Refusal
from .receipt import _seal, verify as verify_isthmus

ALGORITMOS = ("none", "ml-dsa-44")


def _ml_dsa():
    try:
        from dilithium_py.ml_dsa import ML_DSA_44
        return ML_DSA_44
    except Exception:
        raise Refusal("ISTH-SIG-ALG", "ml-dsa-44 indisponivel neste ambiente")


def gerar_chave(alg="ml-dsa-44"):
    if alg != "ml-dsa-44":
        raise Refusal("ISTH-SIG-ALG", alg)
    return _ml_dsa().keygen()


def assinar(rec, chave_privada, alg="ml-dsa-44"):
    """Sela com sig_alg declarado e assina o selo."""
    if alg not in ALGORITMOS:
        raise Refusal("ISTH-SIG-ALG", alg)
    payload = dict(rec["payload"])
    payload["sig_alg"] = alg
    selo = _seal(payload)
    if alg == "none":
        return {"payload": payload, "seal": selo, "sig_alg": "none", "sig": None}
    assinatura = _ml_dsa().sign(chave_privada, selo.encode())
    return {"payload": payload, "seal": selo, "sig_alg": alg,
            "sig": base64.b64encode(assinatura).decode()}


def verificar_assinatura(rec, chave_publica):
    """Despacha pelo algoritmo declarado. Recusa o que nao sabe ler."""
    alg = rec.get("sig_alg") or rec.get("payload", {}).get("sig_alg") or "none"
    if alg not in ALGORITMOS:
        raise Refusal("ISTH-SIG-ALG", str(alg))
    if alg == "none":
        return {"state": "ok", "alg": "none", "assinado": False}
    if not rec.get("sig"):
        raise Refusal("ISTH-SIG-AUSENTE", alg)
    ok = _ml_dsa().verify(chave_publica, rec["seal"].encode(),
                          base64.b64decode(rec["sig"]))
    if not ok:
        raise Refusal("ISTH-SIG-FALHA", alg)
    return {"state": "ok", "alg": alg, "assinado": True}


def verificar_completo(rec, chave_publica=None):
    """Fase grossa e fina do selo, depois a assinatura."""
    estado = verify_isthmus(rec)
    assin = verificar_assinatura(rec, chave_publica) if chave_publica else {"state": "nao_verificada"}
    return {"selo": estado, "assinatura": assin}
