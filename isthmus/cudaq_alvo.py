# -*- coding: utf-8 -*-
"""Alvo externo do CUDA-Q para o Isthmus.

Segue o modelo publico de integracao externa do CUDA-Q (issue 4619): o pacote
anuncia o alvo, entrega a configuracao do alvo e entrega o runtime que executa.
Nada aqui toca o repositorio da NVIDIA, nao copia interno deles e nao pede nada
a ninguem: usa a superficie de extensao declarada.

O alvoNAO e uma QPU. Ele e um portao de decisao: recebe a entrada, decide com a
Ramp, emite recibo, e so o que sobrevive vira execucao no alvo de verdade.
"""

DESCRITOR = {
    "nome": "isthmus-decide",
    "descricao": ("portao de decisao: decide antes de executar, emite recibo selado "
                  "e deixa passar so o que a decisao autorizou"),
    "tipo": "gate",
    "simulador": False,
    "qubits": "qualquer",
    "entrada": ["cudaq-kernel", "contagens"],
    "saida": ["receipt", "contagens"],
    "modelo_de_integracao": "pacote externo, sem copiar ativo para dentro do CUDA-Q",
}

PORTAS_SUPORTADAS = ("H", "X", "CNOT")


def configuracao_alvo():
    """Configuracao declarada do alvo, no formato que o integrador externo entrega."""
    return {
        "alvos": [DESCRITOR["nome"]],
        "configuracao": {
            "qubits": DESCRITOR["qubits"],
            "portoes": list(PORTAS_SUPORTADAS),
            "medicao": "terminal",
            "shots_padrao": 1024,
        },
        "runtime": "isthmus.cudaq_alvo:AlvoIsthmus",
        "requisitos": ["cudaq>=0.17 (opcional, so para execucao local)"],
    }


def rodar_no_cudaq(portoes, shots=1024, alvo="qpp-cpu"):
    """Executa uma lista de portoes no CUDA-Q e devolve contagens.

    Exemplo de entrada: [("H", 0), ("CNOT", 0, 1)].
    """
    try:
        import cudaq
    except ImportError:
        from .errors import Refusal
        raise Refusal("ISTH-BUDGET", "cudaq ausente no ambiente")
    cudaq.set_target(alvo)
    n = 1 + max(max(p[1:] or (0,)) for p in portoes)
    kernel = cudaq.make_kernel()
    q = kernel.qalloc(n)
    for porta in portoes:
        nome = porta[0].upper()
        if nome == "H":
            kernel.h(q[porta[1]])
        elif nome == "X":
            kernel.x(q[porta[1]])
        elif nome == "CNOT":
            kernel.cx(q[porta[1]], q[porta[2]])
        else:
            raise ValueError(f"porta fora do conjunto suportado: {nome}")
    kernel.mz(q)
    resultado = cudaq.sample(kernel, shots_count=shots)
    return {formato(chave, n): int(valor) for chave, valor in resultado.items()}


def formato(chave, n):
    """Normaliza a chave do CUDA-Q para cadeia de bits do mesmo tamanho."""
    if chave.isdigit() and len(chave) <= n:
        return chave.zfill(n)
    return chave


def decidir_e_selar(contagens, p0, p1, target_key=None, shots=None,
                    alpha=0.05, beta=0.05, max_shots=4096, regra="hoeffding",
                    alvo="qpp-cpu"):
    """Roda a Ramp sobre as contagens e devolve decisao mais recibo selado."""
    from . import ramp, receipt
    total = shots or sum(contagens.values())
    chave = target_key or max(contagens, key=contagens.get)
    decisao = ramp.decidir_dos_counts(contagens, p0, p1, alpha=alpha, beta=beta,
                                      max_shots=max_shots, target_key=chave, regra=regra)
    recibo = receipt.build(
        verdict=decisao["verdict"],
        p0=p0,
        n=1,
        shots=total,
        seed=0,
        mode="hardware" if alvo not in ("qpp-cpu", "nvidia") else "sim",
        error_bound=alpha,
        regra=regra,
        alvo=alvo,
        contagens=contagens,
        distancia_ou_llr=decisao.get("llr"),
    )
    return {"contagens": contagens, "decisao": decisao, "recibo": recibo}


class AlvoIsthmus:
    """O runtime que o pacote externo entrega ao CUDA-Q."""

    nome = DESCRITOR["nome"]

    def __init__(self, alvo="qpp-cpu"):
        self.alvo = alvo

    def configuracao(self):
        return configuracao_alvo()

    def executar(self, portoes, p0, p1, shots=1024, **kwargs):
        contagens = rodar_no_cudaq(portoes, shots=shots, alvo=self.alvo)
        return decidir_e_selar(contagens, p0, p1, shots=shots, alvo=self.alvo, **kwargs)
