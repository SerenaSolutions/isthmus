# -*- coding: utf-8 -*-
"""STH e a derivada: sela, verifica e encadeia. Nao decide."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import isthmus as I
from isthmus import sth
from isthmus.errors import Refusal


class AbreviacaoTest(unittest.TestCase):
    def test_isth_e_a_abreviacao_de_isthmus(self):
        self.assertEqual(I.ABBREV, ("ISTH",))
        self.assertEqual(I.abbrev_name(), "ISTH")

    def test_sth_declarada_como_derivada(self):
        self.assertEqual(sth.NAME, "STH")
        self.assertEqual(sth.DERIVED_FROM, "ISTH")


class STHNaoDecideTest(unittest.TestCase):
    def test_decide_recusa_com_codigo_proprio(self):
        with self.assertRaises(Refusal) as ctx:
            sth.decide()
        self.assertEqual(ctx.exception.code, "ISTH-STH-NOT-ALLOWED")

    def test_selar_sem_veredito_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            sth.seal({"p0": 0.9, "n": 4})
        self.assertEqual(ctx.exception.code, "ISTH-STH-NOT-ALLOWED")


class STHSelaTest(unittest.TestCase):
    def _payload(self, seed=1, p0=0.9):
        return {"p0": p0, "n": 4, "shots": 512, "seed": seed, "mode": "sim",
                "error_bound": 0.05, "verdict": 1}

    def test_sela_e_verifica(self):
        rec = sth.seal(self._payload())
        self.assertEqual(sth.verify(rec)["stage"], "fine")

    def test_adulteracao_recusada(self):
        rec = sth.seal(self._payload())
        rec["payload"]["verdict"] = 0
        with self.assertRaises(Refusal) as ctx:
            sth.verify(rec)
        self.assertEqual(ctx.exception.code, "ISTH-FINE-SEAL")

    def test_encadeia_dois_elos(self):
        r1 = sth.seal(self._payload(seed=1))
        r2 = sth.seal(dict(self._payload(seed=2), prev_seal=r1["seal"]))
        self.assertEqual(sth.chain([r1, r2])["links"], 2)

    def test_cadeia_rompida(self):
        r1 = sth.seal(self._payload(seed=1))
        r2 = sth.seal(dict(self._payload(seed=2), prev_seal=r1["seal"]))
        r3 = sth.seal(dict(self._payload(seed=3), prev_seal=r2["seal"]))
        forged = sth.seal(dict(self._payload(seed=2, p0=0.1), verdict=0, prev_seal=r1["seal"]))
        with self.assertRaises(Refusal) as ctx:
            sth.chain([r1, forged, r3])
        self.assertEqual(ctx.exception.code, "ISTH-CHAIN-SHOWER")


if __name__ == "__main__":
    unittest.main()
