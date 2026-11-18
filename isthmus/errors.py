# -*- coding: utf-8 -*-
"""Codigos de recusa do Isthmus. Um codigo por motivo, e o motivo vem declarado."""

CODES = {
    "ISTH-PROFILE": "perfil de canonizacao desconhecido",
    "ISTH-SHUTTER": "campo, tipo ou tamanho fora do contrato",
    "ISTH-RAMP-SHORT": "serie insuficiente para ajuste de rampa",
    "ISTH-RAMP-BREAK": "serie nao monotona: rampa quebrada",
    "ISTH-REFASE-BAND": "deslocamento de fase acima da banda declarada",
    "ISTH-BUDGET": "orcamento de tiros ou chamadas esgotado",
    "ISTH-SHOTS": "tiros executados diferentes dos declarados",
    "ISTH-ALIGNMENT-DRIFT": "duas rodadas de alinhamento divergem alem da banda",
    "ISTH-MITIG-UNDECLARED": "mitigacao aplicada sem declaracao",
    "ISTH-TRANSPILE-LOSS": "perda na ida e volta do circuito",
    "ISTH-FLOW": "sequencia de ciclo invalida",
    "ISTH-BAND-OPTIMISM": "banda declarada mais estreita que o ruido medido",
    "ISTH-COARSE-SCHEMA": "fase grossa: esquema invalido",
    "ISTH-COARSE-GRAMATICA": "fase grossa: versao de gramatica invalida",
    "ISTH-COARSE-CAMPO": "fase grossa: campo obrigatorio ausente",
    "ISTH-FINE-SEAL": "fase fina: selo nao confere",
    "ISTH-CHAIN-SHOWER": "cadeia rompida: dano distribuido",
    "ISTH-SIG-ALG": "assinatura: algoritmo declarado desconhecido",
    "ISTH-SIG-FALHA": "assinatura: nao confere com a chave",
    "ISTH-SIG-AUSENTE": "assinatura: recibo declara algoritmo e nao traz assinatura",
    "ISTH-BRIDGE-AUSENTE": "ponte: bloco de origem ausente",
    "ISTH-BRIDGE-MAPA": "ponte: versao de mapa desconhecida",
    "ISTH-BRIDGE-SELO": "ponte: selo de origem nao recomputa",
    "ISTH-BRIDGE-ORIGEM": "ponte: formato de origem desconhecido",
    "ISTH-BRIDGE-FORMA": "ponte: recibo de origem fora de forma",
    "ISTH-BRIDGE-CAMPO": "ponte: campo mapeavel ausente",
    "ISTH-STH-NOT-ALLOWED": "STH nao decide: derivada so sela, verifica e encadeia",
}


class Refusal(Exception):
    """Recusa declarada: sempre com codigo do catalogo."""

    def __init__(self, code, detail=""):
        if code not in CODES:
            raise ValueError(f"codigo fora do catalogo: {code}")
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)
