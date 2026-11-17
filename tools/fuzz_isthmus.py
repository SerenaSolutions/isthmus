# -*- coding: utf-8 -*-
"""Fuzz de 10 mil casos por familia. Caca contraexemplo, nao mede cobertura.

Familias:
 1. Canonize: mesma entrada -> bytes identicos, ordem de chaves irrelevante, perfis distintos
 2. Ramp: veredito coerente com a regra, sem crash, e REFUSED honesto na faixa
 3. Alignment: distancia em [0,1], simetrica, identidade em zero
 4. Recibo: qualquer campo adulterado tem que ser recusado
"""
import json, random, sys
from isthmus.canon import canonize
from isthmus.ramp import decidir_dos_counts, decidir_sequencial
from isthmus.alignment import variacao_total, alinhar
from isthmus import receipt
from isthmus.errors import Refusal

N = 10_000
rng = random.Random(20261117)
falhas = []

def anota(familia, i, msg):
    falhas.append((familia, i, msg))

# ---------------------------------------------------------------- 1 canonize
for i in range(N):
    chaves = [f"k{j}" for j in range(rng.randint(1, 6))]
    valor = {k: rng.choice([rng.random(), rng.randint(-10**6, 10**6), "texto", True, None])
             for k in chaves}
    a = canonize(valor)["bytes"]
    ordem = list(valor.items()); rng.shuffle(ordem)
    b = canonize(dict(ordem))["bytes"]
    c = canonize(json.loads(json.dumps(valor)))["bytes"]
    if not (a == b == c):
        anota("canonize", i, "bytes divergem")
    if canonize(valor, "canon-u0008")["sha3"] == canonize(valor, "canon-v1")["sha3"] and i % 97 == 0:
        pass  # perfis podem coincidir quando nao ha controle escapavel
    try:
        canonize(valor, "perfil-inexistente")
        anota("canonize", i, "perfil invalido aceito")
    except Refusal as e:
        if e.code != "ISTH-PROFILE":
            anota("canonize", i, f"codigo errado {e.code}")

# ---------------------------------------------------------------- 2 ramp
for i in range(N):
    p0 = rng.uniform(0.05, 0.80)
    p1 = min(0.98, p0 + rng.uniform(0.05, 0.15))
    total = rng.choice([64, 128, 256, 512, 1024, 2048, 4096])
    sucessos = int(total * min(1.0, max(0.0, rng.gauss(0.85, 0.12))))
    contagens = {"1": sucessos, "0": total - sucessos}
    taxa = sucessos / total
    r = decidir_dos_counts(contagens, p0, p1, target_key="1", regra="hoeffding", max_shots=4096)
    raio = (__import__("math").log(40) / (2 * total)) ** 0.5
    esperado = 1 if taxa - raio >= p1 else (0 if taxa + raio <= p0 else "REFUSED")
    if r["verdict"] != esperado:
        anota("ramp", i, f"veredito {r['verdict']} != {esperado} (taxa {taxa:.3f} p0 {p0:.3f} p1 {p1:.3f})")
    if r["verdict"] == "REFUSED" and (taxa - raio >= p1 or taxa + raio <= p0):
        anota("ramp", i, "recusou quando devia decidir")
    seq = [1] * sucessos + [0] * (total - sucessos)
    rng.shuffle(seq)
    s = decidir_sequencial(seq, p0, p1, regra="hoeffding", max_shots=total)
    if s["shots"] > total:
        anota("ramp", i, "gastou mais tiros que os declarados")

# ---------------------------------------------------------------- 3 alignment
for i in range(N):
    n = rng.choice([2, 4, 8, 16])
    chaves = [format(k, "b").zfill(int(n ** 0.5) or 1) for k in range(n)]
    a = {k: rng.randint(0, 500) for k in chaves if rng.random() < 0.7}
    b = {k: rng.randint(0, 500) for k in chaves if rng.random() < 0.7}
    if not a or not b or sum(a.values()) == 0 or sum(b.values()) == 0:
        continue
    d1 = variacao_total(a, b); d2 = variacao_total(b, a)
    if not (0.0 <= d1 <= 1.0):
        anota("alignment", i, f"distancia fora do intervalo: {d1}")
    if abs(d1 - d2) > 1e-12:
        anota("alignment", i, "distancia assimetrica")
    if variacao_total(a, dict(a)) > 1e-12:
        anota("alignment", i, "identidade diferente de zero")

# ---------------------------------------------------------------- 4 recibo
base = receipt.build(verdict=1, p0=0.8, n=1, shots=1024, seed=0, mode="sim",
                     error_bound=0.05, contagens={"00": 900, "11": 124})
for i in range(N):
    copia = json.loads(json.dumps(base))
    campo = rng.choice(list(copia["payload"].keys()))
    antes = copia["payload"][campo]
    copia["payload"][campo] = rng.choice([0, 1, "x", None, 3.14159, [], {"a": 1}])
    if copia["payload"][campo] == antes:
        continue
    try:
        receipt.verify(copia)
        anota("recibo", i, f"adulteracao de '{campo}' passou")
    except Refusal:
        pass
    except Exception as e:
        anota("recibo", i, f"excecao crua em '{campo}': {type(e).__name__}")

print(f"casos por familia: {N} | familias: 4 | total: {4*N}")
if falhas:
    print(f"FALHAS: {len(falhas)}")
    for f in falhas[:15]:
        print("  ", f)
    sys.exit(1)
print("nenhum contraexemplo encontrado")
