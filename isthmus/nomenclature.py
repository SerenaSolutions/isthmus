# -*- coding: utf-8 -*-
"""Vocabulario formal do Isthmus, adaptado da engenharia de alinhamento do JWST.

Sete fases de execucao, tres contratos e dois artefatos hostis. Cada fase aponta
para o alvo real no codigo, e `validate()` confere que o alvo existe: nome sem
funcao por tras e enfeite, e enfeite nao passa no teste.
"""
import importlib

# fase, o que faz no Isthmus, alvo real (modulo, atributo)
PHASES = (
    ("Deployment", "declaracao: band, oracle, shots e deny antes de executar",
     ("isthmus.budget", "Budget")),
    ("Wavefront Sensing", "aquisicao nao destrutiva em rampa",
     ("isthmus.ramp", "fit")),
    ("Segment Alignment", "admissao de campos e forma canonica",
     ("isthmus.shutter", "shutter")),
    ("Image Stacking", "acumulo de contagens ate os tiros declarados",
     ("isthmus.sampler", "sample")),
    ("Coarse Phasing", "esquema, versao de gramatica e campos obrigatorios",
     ("isthmus.receipt", "coarse_phasing")),
    ("Fine Phasing", "selo SHA3-256 sobre os bytes canonicos",
     ("isthmus.receipt", "fine_phasing")),
    ("Wavefront Control", "correcao de fase entre duas medicoes",
     ("isthmus.refase", "refase")),
)

CONTRACTS = (
    ("Backplane", "contrato de serializacao canonica", ("isthmus.canon", "canonize")),
    ("CRDS", "registro versionado de regras, declarado no recibo como profile",
     ("isthmus.canon", "PROFILES")),
    ("Trim tab", "constante declarada do emissor", ("isthmus.receipt", "build")),
    ("Dispersed fringe sensing", "medida da divergencia entre duas canonizacoes",
     ("isthmus.fringe", "fringe")),
)

ARTIFACTS = (
    ("Snowball", "dano contiguo, pego pela fase fina de um recibo", "ISTH-FINE-SEAL"),
    ("Shower", "dano distribuido, pego pela verificacao de cadeia", "ISTH-CHAIN-SHOWER"),
)

ORDER = tuple(name for name, _, _ in PHASES)


def stage_index(name):
    """Posicao da fase no pipeline, com erro claro se o nome nao existir."""
    if name not in ORDER:
        raise KeyError(f"fase fora do vocabulario: {name}")
    return ORDER.index(name)


def artifact_of(code):
    """Classifica um codigo de recusa como Snowball, Shower ou None."""
    for name, _, codigo in ARTIFACTS:
        if codigo == code:
            return name
    return None


def table():
    """Linhas prontas para documento: fase, funcao, alvo."""
    return [{"fase": n, "faz": d, "alvo": f"{m}.{a}"} for n, d, (m, a) in PHASES]


def validate():
    """Confere que todo nome tem alvo importavel. Nome sem funcao reprova."""
    faltando = []
    for grupo in (PHASES, CONTRACTS):
        for name, _, (mod, attr) in grupo:
            try:
                if not hasattr(importlib.import_module(mod), attr):
                    faltando.append(f"{name}: {mod}.{attr} inexistente")
            except ImportError as e:
                faltando.append(f"{name}: modulo {mod} nao importa ({e})")
    return {"ok": not faltando, "fases": len(PHASES), "contratos": len(CONTRACTS),
            "artefatos": len(ARTIFACTS), "faltando": faltando}
