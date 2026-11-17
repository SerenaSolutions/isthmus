# -*- coding: utf-8 -*-
"""Alvo externo do CUDA-Q: declaracao, execucao e recibo."""
import unittest

from isthmus import receipt
from isthmus.alignment import alinhar
from isthmus.cudaq_alvo import (DESCRITOR, AlvoIsthmus, configuracao_alvo,
                                decidir_e_selar)
from isthmus.errors import Refusal


class TestAlvoExterno(unittest.TestCase):
    def test_configuracao_anuncia_alvo_runtime_e_portoes(self):
        cfg = configuracao_alvo()
        self.assertIn(DESCRITOR["nome"], cfg["alvos"])
        self.assertEqual(cfg["runtime"], "isthmus.cudaq_alvo:AlvoIsthmus")
        self.assertIn("H", cfg["configuracao"]["portoes"])

    def test_decisao_emite_recibo_que_verifica(self):
        r = decidir_e_selar({"00": 950, "11": 50}, 0.75, 0.90, target_key="00")
        self.assertEqual(r["decisao"]["verdict"], 1)
        self.assertTrue(receipt.verify(r["recibo"]))
        self.assertIn("contagens", r["recibo"]["payload"])

    def test_recibo_adulterado_e_recusado(self):
        r = decidir_e_selar({"00": 950, "11": 50}, 0.75, 0.90, target_key="00")
        ruim = r["recibo"]
        ruim["payload"]["verdict"] = 0
        with self.assertRaises(Refusal):
            receipt.verify(ruim)

    def test_banda_indecidivel_produz_refused(self):
        r = decidir_e_selar({"00": 900, "11": 100}, 0.85, 0.95, target_key="00")
        self.assertEqual(r["decisao"]["verdict"], "REFUSED")

    def test_alinhamento_entre_duas_rodadas(self):
        a = decidir_e_selar({"00": 500, "11": 500}, 0.40, 0.60, target_key="00")
        b = decidir_e_selar({"00": 505, "11": 495}, 0.40, 0.60, target_key="00")
        rel = alinhar(a["contagens"], b["contagens"], tolerancia=0.1)
        self.assertEqual(rel["verdict"], 1)

    def test_execucao_real_no_cudaq(self):
        try:
            import cudaq  # noqa: F401
        except ImportError:
            self.skipTest("cudaq ausente")
        alvo = AlvoIsthmus()
        r = alvo.executar([("H", 0), ("CNOT", 0, 1)], p0=0.40, p1=0.60, shots=256)
        self.assertEqual(sum(r["contagens"].values()), 256)
        self.assertTrue(receipt.verify(r["recibo"]))


if __name__ == "__main__":
    unittest.main()
