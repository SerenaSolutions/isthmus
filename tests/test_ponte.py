# -*- coding: utf-8 -*-
"""Bateria da ponte de vocabulario ZEPHIRUM x ISTHMUS."""
import random, unittest
import zephirum
import isthmus as I
from isthmus import ponte
from isthmus.errors import Refusal


class TestPonte(unittest.TestCase):
    def test_zephirum_para_isthmus_500(self):
        random.seed(11)
        for _ in range(500):
            shots = random.choice([100, 512, 1000, 4096])
            s = random.randint(0, shots)
            dz = zephirum.decidir({"000": s, "111": shots - s}, shots, 0.5, 0.05, "000")
            env = ponte.de_zephirum(dz)
            self.assertEqual(I.verify(env)["state"], "ok")
            self.assertEqual(ponte.verificar(env)["state"], "ok")
            self.assertEqual(env["payload"]["verdict"], dz["verdict"])
            self.assertEqual(env["payload"]["shots"], dz["shots"])

    def test_isthmus_para_zephirum_500(self):
        random.seed(12)
        for i in range(500):
            r = I.receipt.build(verdict=str(i % 2), p0=0.5, n=1000, shots=1000,
                                seed=i, mode="exact", error_bound=0.0247)
            z = ponte.de_isthmus(r)
            self.assertEqual(z["verdict"], r["payload"]["verdict"])
            self.assertEqual(z["receipt_hash"], r["seal"])
            self.assertEqual(ponte.verificar(z)["state"], "ok")

    def test_adulteracao_de_campo_mapedo(self):
        dz = zephirum.decidir({"000": 820, "111": 180}, 1000, 0.5, 0.05, "000")
        env = ponte.de_zephirum(dz)
        detectadas = 0
        for campo in ("verdict", "shots", "threshold", "epsilon"):
            ruim = {k: v for k, v in env["ponte"]["campos_origem"].items()}
            ruim[campo] = "X"
            e = dict(env); e["ponte"] = dict(env["ponte"]); e["ponte"]["campos_origem"] = ruim
            with self.assertRaises(Refusal):
                ponte.verificar(e)
            detectadas += 1
        self.assertEqual(detectadas, 4)

    def test_mapa_desconhecido(self):
        dz = zephirum.decidir({"000": 820, "111": 180}, 1000, 0.5, 0.05, "000")
        env = ponte.de_zephirum(dz)
        env["ponte"]["mapa"] = "ponte-9.9"
        with self.assertRaises(Refusal) as ctx:
            ponte.verificar(env)
        self.assertEqual(ctx.exception.code, "ISTH-BRIDGE-MAPA")

    def test_sem_ponte(self):
        with self.assertRaises(Refusal) as ctx:
            ponte.verificar({"verdict": "1"})
        self.assertEqual(ctx.exception.code, "ISTH-BRIDGE-AUSENTE")

    def test_determinismo(self):
        dz = zephirum.decidir({"000": 820, "111": 180}, 1000, 0.5, 0.05, "000")
        selos = {ponte.de_zephirum(dz)["seal"] for _ in range(200)}
        self.assertEqual(len(selos), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
