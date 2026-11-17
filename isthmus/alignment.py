# -*- coding: utf-8 -*-
"""Alignment Two: acordo entre duas implementacoes na mesma entrada.

O ponto delicado, declarado no vocabulario: uma decisao, uma chamada de oraculo.
Alignment Two precisa de dois lados, entao ele NAO e uma decisao sozinho. Ele e uma
relacao entre dois recibos ja emitidos, cada um com sua chamada, e o resultado sai
num terceiro registro derivado que nao pede oraculo nenhum: quem audita recalcula
so com os dois recibos na mao.
"""
from .errors import Refusal

METRICAS = ("tv",)


def variacao_total(contagens_a, contagens_b):
    """Distancia de variacao total entre duas distribuicoes empiricas, em [0, 1]."""
    if not contagens_a or not contagens_b:
        raise ValueError("as duas distribuicoes precisam de ao menos uma contagem")
    total_a = sum(contagens_a.values())
    total_b = sum(contagens_b.values())
    if total_a <= 0 or total_b <= 0:
        raise ValueError("contagens nao podem somar zero")
    chaves = set(contagens_a) | set(contagens_b)
    return 0.5 * sum(abs(contagens_a.get(k, 0) / total_a - contagens_b.get(k, 0) / total_b)
                     for k in chaves)


def alinhar(contagens_a, contagens_b, tolerancia=0.10, rotulo_a="A", rotulo_b="B",
            metrica="tv"):
    """Compara dois lados. Devolve 1 se cabe na tolerancia, REFUSED se passa dela.

    Nunca devolve media das duas distribuicoes: discordar e resultado, nao ruido a
    ser suavizado.
    """
    if metrica not in METRICAS:
        raise ValueError(f"metrica deve ser uma de {METRICAS}")
    if not (0.0 < tolerancia <= 0.5):
        raise ValueError("tolerancia declarada deve ficar em (0, 0.5]")
    distancia = variacao_total(contagens_a, contagens_b)
    cabe = distancia <= tolerancia
    return {
        "verdict": 1 if cabe else "REFUSED",
        "metrica": metrica,
        "distancia": round(distancia, 6),
        "tolerancia": tolerancia,
        "folga": round(tolerancia - distancia, 6),
        "lado_a": {"rotulo": rotulo_a, "tiros": sum(contagens_a.values())},
        "lado_b": {"rotulo": rotulo_b, "tiros": sum(contagens_b.values())},
        "motivo": None if cabe else "ISTH-ALIGNMENT-DRIFT",
    }


def alinhar_recibos(recibo_a, recibo_b, tolerancia=0.10, metrica="tv"):
    """Registro derivado: amarra dois recibos pelos selos, sem nova chamada de oraculo."""
    for nome, recibo in (("a", recibo_a), ("b", recibo_b)):
        if not isinstance(recibo, dict) or "seal" not in recibo:
            raise Refusal("ISTH-FINE-SEAL", f"recibo {nome} sem selo")
    contagens_a = recibo_a.get("payload", {}).get("counts") or recibo_a.get("counts")
    contagens_b = recibo_b.get("payload", {}).get("counts") or recibo_b.get("counts")
    if not contagens_a or not contagens_b:
        raise ValueError("recibos precisam trazer contagens para o alinhamento")
    resultado = alinhar(contagens_a, contagens_b, tolerancia, metrica=metrica)
    resultado["selo_a"] = recibo_a["seal"]
    resultado["selo_b"] = recibo_b["seal"]
    resultado["regra"] = "alignment-two-v1"
    return resultado
