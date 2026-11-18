# -*- coding: utf-8 -*-
"""Regressao dos defeitos achados na rodada de inducao (tools/roda_bugs.py)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import isthmus as I
from isthmus.errors import Refusal


def rec(**kw):
    base = dict(p0=0.9, n=4, shots=512, seed=1, mode="sim", error_bound=0.05, verdict=1)
    base.update(kw)
    return I.build(**base)


class PayloadNaoSerializavelTest(unittest.TestCase):
    """Antes: TypeError cru. Depois: ISTH-CANON-TIPO."""

    def test_bytes_no_payload_recusa_com_codigo(self):
        r = rec()
        r["payload"]["n"] = b"\x00\x01"
        with self.assertRaises(Refusal) as ctx:
            I.verify(r)
        self.assertEqual(ctx.exception.code, "ISTH-CANON-TIPO")

    def test_bytes_em_campo_injetado(self):
        r = rec()
        r["payload"]["extra"] = b"x"
        with self.assertRaises(Refusal) as ctx:
            I.verify(r)
        self.assertEqual(ctx.exception.code, "ISTH-CANON-TIPO")

    def test_canonize_direto_tambem_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            I.canonize({"x": {1, 2}})
        self.assertEqual(ctx.exception.code, "ISTH-CANON-TIPO")


class SamplerHostilTest(unittest.TestCase):
    """Antes: AttributeError e RuntimeError. Depois: codigos proprios."""

    def test_backend_que_estoura(self):
        def boom(shots, seed):
            raise RuntimeError("QPU caiu")
        with self.assertRaises(Refusal) as ctx:
            I.sample(boom, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FAIL")

    def test_backend_devolve_none(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: None, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FORMATO")

    def test_backend_devolve_vazio(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: {}, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FORMATO")

    def test_contagem_negativa(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: {"1": -5, "0": shots + 5}, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FORMATO")

    def test_contagem_booleana(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: {"1": True}, shots=1)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FORMATO")

    def test_contagem_em_texto(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: {"1": "512"}, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SAMPLER-FORMATO")

    def test_contagem_valida_segue(self):
        r = I.sample(lambda shots, seed: {1: 300, 2: 212}, shots=512)
        self.assertEqual(r["counts"], {"1": 300, "2": 212})


if __name__ == "__main__":
    unittest.main()
