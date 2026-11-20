# -*- coding: utf-8 -*-
"""Integração de projetos externos como ferramentas MCP, por CLI declarada.

Qualquer projeto que tenha linha de comando vira ferramenta sem tocar no servidor:
basta uma entrada em mcp_providers.json. A saída do processo é devolvida como
texto; falha vira recusa com código, nunca traceback.
"""
import json
import os
import shlex
import subprocess

CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "mcp_providers.json")
LIMITE_S = 20


class FalhaExterna(Exception):
    def __init__(self, codigo, detalhe):
        self.codigo = codigo
        self.detalhe = detalhe
        super().__init__(f"{codigo}: {detalhe}")


def carregar(caminho=None):
    caminho = caminho or CONFIG
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as fh:
        dados = json.load(fh)
    return dados.get("providers", [])


def especificacoes(providers):
    """Só provedores habilitados viram ferramenta exposta ao agente."""
    specs = []
    for p in providers:
        if not p.get("enabled"):
            continue
        specs.append({
            "name": p["tool"],
            "description": p.get("description", ""),
            "inputSchema": p.get("inputSchema") or {"type": "object", "properties": {}},
        })
    return specs


def executar(provider, argumentos):
    comando = list(provider.get("command") or [])
    if not comando:
        raise FalhaExterna("ISTH-MCP-EXT", "provedor sem comando")
    for chave, valor in (argumentos or {}).items():
        comando.extend([f"--{chave.replace('_', '-')}", str(valor)])
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=LIMITE_S)
    except FileNotFoundError:
        raise FalhaExterna("ISTH-MCP-EXT-AUSENTE", comando[0])
    except subprocess.TimeoutExpired:
        raise FalhaExterna("ISTH-MCP-EXT-TEMPO", f"{LIMITE_S}s")
    if r.returncode != 0:
        raise FalhaExterna("ISTH-MCP-EXT-FALHA",
                           (r.stderr or r.stdout or "").strip()[:300] or f"saida {r.returncode}")
    return {"provider": provider.get("project", provider["tool"]), "saida": r.stdout.strip()}


def despachos(providers):
    return {p["tool"]: (lambda a, p=p: executar(p, a)) for p in providers if p.get("enabled")}
