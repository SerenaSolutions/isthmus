# -*- coding: utf-8 -*-
"""Servidor MCP (Model Context Protocol) do Isthmus, em stdlib pura.

Transporte stdio, JSON-RPC 2.0, mensagens delimitadas por linha. Zero dependência:
o Isthmus não pede instalação para ser chamado por um agente.

Ferramentas expostas:
    isthmus_decide         decide com banda declarada e devolve recibo selado
    isthmus_seal           sela um payload já decidido
    isthmus_verify         verifica um recibo, fase grossa e fase fina
    isthmus_verify_chain   verifica uma cadeia de recibos
    isthmus_nomenclature   devolve o vocabulário e os códigos de recusa
"""
import json
import sys

import isthmus as I
from isthmus.errors import Refusal

PROTOCOLO = "2025-06-18"
NOME = "isthmus"
VERSAO = I.__version__

FERRAMENTAS = [
    {
        "name": "isthmus_decide",
        "description": ("Decide com veredito trivalente (1, 0) e emite recibo selado "
                        "com SHA3-256. A banda de erro é declarada, nunca inferida."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "p0": {"type": "number", "description": "probabilidade medida, entre 0 e 1"},
                "n": {"type": "integer", "description": "número de qubits", "default": 4},
                "shots": {"type": "integer", "description": "tiros declarados", "default": 512},
                "seed": {"type": "integer", "description": "semente declarada", "default": 1},
                "error_bound": {"type": "number", "description": "banda declarada", "default": 0.05},
            },
            "required": ["p0"],
        },
    },
    {
        "name": "isthmus_seal",
        "description": "Sela um payload já decidido e devolve o recibo com selo.",
        "inputSchema": {
            "type": "object",
            "properties": {"payload": {"type": "object", "description": "payload com o campo verdict"}},
            "required": ["payload"],
        },
    },
    {
        "name": "isthmus_verify",
        "description": ("Verifica um recibo: fase grossa (esquema, gramática, campos) e fase "
                        "fina (selo). Recusa com código ISTH-* em vez de levantar exceção."),
        "inputSchema": {
            "type": "object",
            "properties": {"receipt": {"type": "object", "description": "recibo completo"}},
            "required": ["receipt"],
        },
    },
    {
        "name": "isthmus_verify_chain",
        "description": "Verifica uma cadeia de recibos e distingue dano contíguo de distribuído.",
        "inputSchema": {
            "type": "object",
            "properties": {"receipts": {"type": "array", "items": {"type": "object"}}},
            "required": ["receipts"],
        },
    },
    {
        "name": "isthmus_nomenclature",
        "description": "Devolve as sete fases, os contratos e os códigos de recusa do Isthmus.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _texto(obj, erro=False):
    return {"content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False, indent=2)}],
            "isError": erro}


def _decide(a):
    p0 = float(a["p0"])
    banda = float(a.get("error_bound", 0.05))
    verdict = 1 if abs(p0 - 0.5) > banda else 0
    rec = I.build(p0=p0, n=int(a.get("n", 4)), shots=int(a.get("shots", 512)),
                  seed=int(a.get("seed", 1)), mode="sim", error_bound=banda, verdict=verdict)
    return {"verdict": verdict, "receipt": rec, "stage": I.verify(rec)}


def _seal(a):
    payload = dict(a["payload"])
    if "verdict" not in payload:
        raise Refusal("ISTH-STH-NOT-ALLOWED", "payload sem verdict: o servidor nao decide por voce")
    return I.build(**payload)


def _verify(a):
    return I.verify(a["receipt"])


def _chain(a):
    return I.verify_chain(a["receipts"])


def _nomenclatura(_a):
    return {"fases": list(I.nomenclature.ORDER),
            "tabela": I.nomenclature.table(),
            "validacao": I.nomenclature.validate(),
            "codigos": sorted(I.CODES)}


DESPACHO = {"isthmus_decide": _decide, "isthmus_seal": _seal,
            "isthmus_verify": _verify, "isthmus_verify_chain": _chain,
            "isthmus_nomenclature": _nomenclatura}


def tratar(msg):
    """Trata uma mensagem JSON-RPC. Devolve a resposta ou None para notificação."""
    metodo = msg.get("method")
    mid = msg.get("id")
    if metodo is None:
        return None
    if metodo == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOLO,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": NOME, "version": VERSAO}}}
    if metodo in ("notifications/initialized", "initialized"):
        return None
    if metodo == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if metodo == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": FERRAMENTAS}}
    if metodo == "tools/call":
        params = msg.get("params") or {}
        nome = params.get("name")
        args = params.get("arguments") or {}
        fn = DESPACHO.get(nome)
        if fn is None:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"ferramenta desconhecida: {nome}"}}
        try:
            return {"jsonrpc": "2.0", "id": mid, "result": _texto(fn(args))}
        except Refusal as e:
            return {"jsonrpc": "2.0", "id": mid,
                    "result": _texto({"state": "refused", "code": e.code, "detail": e.detail}, erro=True)}
        except Exception as e:  # nunca deixar o agente ver traceback cru
            return {"jsonrpc": "2.0", "id": mid,
                    "result": _texto({"state": "refused", "code": "ISTH-MCP-FALHA",
                                      "detail": f"{type(e).__name__}: {e}"}, erro=True)}
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"metodo nao suportado: {metodo}"}}


def main(argv=None):
    """Loop principal: lê uma linha JSON por vez e responde no stdout."""
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError as e:
            out = {"jsonrpc": "2.0", "id": None,
                   "error": {"code": -32700, "message": f"JSON invalido: {e}"}}
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()
            continue
        resp = tratar(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
