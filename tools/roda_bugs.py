# -*- coding: utf-8 -*-
"""Rodada de inducao de defeitos no isthmus.

Conta como BUG qualquer excecao que nao seja Refusal (TypeError, KeyError,
AttributeError, ValueError, RecursionError, OverflowError...). Recusa declarada
nao e bug: e contrato.

Uso: python3 tools/roda_bugs.py [--por-familia 400] [--seed 2026]
"""
import argparse, json, math, os, random, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import isthmus as I
from isthmus import sth
from isthmus.errors import Refusal

VALORES = [None, True, False, 0, -1, 1, 1.5, "", "x", [], {}, (), b"", float("nan"),
           float("inf"), -float("inf"), 10**30, "0" * 5000, {"a": {"b": {}}}]


def rec_valido(**kw):
    base = dict(p0=0.9, n=4, shots=512, seed=1, mode="sim", error_bound=0.05, verdict=1)
    base.update(kw)
    return I.build(**base)


def fam_recibo(rnd, n):
    """Muta campo do recibo: tipo trocado, removido, injetado, duplicado profundo."""
    bugs = 0
    for _ in range(n):
        rec = rec_valido()
        modo = rnd.choice(["tipo", "remover", "injetar", "aninhar", "seal"])
        campo = rnd.choice(list(rec["payload"]))
        if modo == "tipo":
            rec["payload"][campo] = rnd.choice(VALORES)
        elif modo == "remover":
            rec["payload"].pop(campo, None)
        elif modo == "injetar":
            rec["payload"]["extra_" + str(rnd.randint(0, 9))] = rnd.choice(VALORES)
        elif modo == "aninhar":
            rec["payload"][campo] = {"x": [1, {"y": rnd.choice(VALORES)}]}
        else:
            rec["seal"] = rnd.choice(VALORES)
        try:
            I.verify(rec)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG recibo/{modo}/{campo}: {type(e).__name__}: {e}")
    return bugs


def fam_canon(rnd, n):
    bugs = 0
    for _ in range(n):
        payload = rnd.choice([{}, {"s": "\b\f\n\t"}, {"s": "\u0000\u001f"},
                              {"n": float("nan")}, {"n": float("inf")},
                              {"deep": eval("[" * 40 + "]" * 40)},
                              {"big": "x" * rnd.randint(1, 5000)},
                              {"u": "\U0001F600" * 3}, {"k": {str(i): i for i in range(50)}}])
        perfil = rnd.choice(["canon-v1", "canon-u0008", None, 1, [], {}, "canon-v9", ""])
        try:
            I.canonize(payload, profile=perfil)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG canon/perfil={perfil!r}: {type(e).__name__}: {e}")
    return bugs


def fam_ramp(rnd, n):
    bugs = 0
    for _ in range(n):
        k = rnd.randint(0, 6)
        amostras = []
        for i in range(k):
            t = rnd.choice([i, i, i * 0.5, float("nan"), float("inf"), -i])
            c = rnd.choice([100 + 20 * i, float("nan"), -5, 10**12, 0])
            amostras.append((t, c))
        try:
            I.ramp_fit(amostras)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG ramp/{amostras}: {type(e).__name__}: {e}")
    return bugs


def fam_refase(rnd, n):
    bugs = 0
    for _ in range(n):
        a = [rnd.choice([0.1, 0.5, float("nan"), 1e9]) for _ in range(rnd.randint(0, 5))]
        b = [rnd.choice([0.1, 0.9, float("nan")]) for _ in range(rnd.randint(0, 5))]
        band = rnd.choice([0.01, 0, -1, float("nan"), float("inf")])
        try:
            I.refase(a, b, band)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG refase/band={band}: {type(e).__name__}: {e}")
    return bugs


def fam_budget(rnd, n):
    bugs = 0
    for _ in range(n):
        limite = rnd.choice([0, 1, 512, -5, 1.5, 10**9])
        try:
            b = I.Budget(shots=limite, oracle_calls=rnd.choice([0, 1, -1, 2.5]))
            b.spend(shots=rnd.choice([0, 1, -1, 512, 10**9]), oracle=rnd.choice([0, 1, -1]))
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG budget/limite={limite}: {type(e).__name__}: {e}")
    return bugs


def fam_sampler(rnd, n):
    bugs = 0
    backends = [
        lambda shots, seed: {"1": shots},
        lambda shots, seed: {"1": -5},
        lambda shots, seed: {"1": shots - 1},
        lambda shots, seed: {},
        lambda shots, seed: None,
        lambda shots, seed: {"1": "500"},
        lambda shots, seed: (_ for _ in ()).throw(RuntimeError("backend caiu")),
    ]
    for _ in range(n):
        try:
            I.sample(rnd.choice(backends), shots=rnd.choice([0, 1, 512, -1]), seed=rnd.randint(0, 9))
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG sampler: {type(e).__name__}: {e}")
    return bugs


def fam_cadeia(rnd, n):
    bugs = 0
    for _ in range(n):
        r1 = rec_valido(seed=1)
        r2 = rec_valido(seed=2, **{"prev_seal": r1["seal"]}) if False else I.build(
            prev_seal=r1["seal"], p0=0.9, n=4, shots=512, seed=2, mode="sim", error_bound=0.05, verdict=1)
        casos = [[], [r1], [r2], [r1, r2], [r1, r1], [r1, r2, r1],
                 [r1, {"payload": {}}, r2], [None, r1], [r1, None]]
        recs = rnd.choice(casos)
        try:
            I.verify_chain(recs)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG cadeia/{len(recs)}: {type(e).__name__}: {e}")
    return bugs


def fam_sth(rnd, n):
    bugs = 0
    for _ in range(n):
        payload = rnd.choice([
            {}, {"p0": 0.9}, {"verdict": 1}, {"p0": 0.9, "verdict": None},
            {"p0": 0.9, "verdict": "1"}, {"p0": float("nan"), "verdict": 1},
            {"p0": 0.9, "verdict": 1, "n": -1},
            {"p0": 0.9, "verdict": 1, "shots": "muitos"},
        ])
        try:
            rec = sth.seal(payload)
            sth.verify(rec)
        except Refusal:
            pass
        except Exception as e:
            bugs += 1
            print(f"BUG sth/{payload}: {type(e).__name__}: {e}")
    return bugs


FAMILIAS = [("recibo", fam_recibo), ("canonize", fam_canon), ("ramp", fam_ramp),
            ("refase", fam_refase), ("budget", fam_budget), ("sampler", fam_sampler),
            ("cadeia", fam_cadeia), ("sth", fam_sth)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--por-familia", type=int, default=400)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    total = 0
    por = {}
    for nome, fn in FAMILIAS:
        bugs = fn(rnd, a.por_familia)
        por[nome] = bugs
        total += bugs
    casos = a.por_familia * len(FAMILIAS)
    print("\n=== RESUMO ===")
    for nome, b in por.items():
        print(f"{nome:<10} {b:>4} bugs em {a.por_familia} casos")
    print(f"TOTAL: {total} bugs em {casos} casos | seed {a.seed}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
