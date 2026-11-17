# -*- coding: utf-8 -*-
"""Alignment Two: discordar tem que aparecer como resultado, nao como media."""
import unittest

from isthmus.alignment import alinhar, alinhar_recibos, variacao_total
from isthmus.errors import Refusal


class TestAlignmentTwo(unittest.TestCase):
    def test_distribuicoes_iguais(self):
        self.assertAlmostEqual(variacao_total({"00": 50, "11": 50}, {"00": 500, "11": 500}), 0.0)

    def test_distancia_no_intervalo(self):
        for a, b in [({"00": 100}, {"11": 100}), ({"00": 60, "11": 40}, {"00": 10, "11": 90})]:
            self.assertGreaterEqual(variacao_total(a, b), 0.0)
            self.assertLessEqual(variacao_total(a, b), 1.0)

    def test_aceita_quando_cabe_na_tolerancia(self):
        r = alinhar({"00": 497, "11": 503}, {"00": 510, "11": 490}, tolerancia=0.10)
        self.assertEqual(r["verdict"], 1)
        self.assertIsNone(r["motivo"])

    def test_recusa_quando_passa_da_tolerancia(self):
        r = alinhar({"00": 1000}, {"00": 500, "01": 500}, tolerancia=0.10)
        self.assertEqual(r["verdict"], "REFUSED")
        self.assertEqual(r["motivo"], "ISTH-ALIGNMENT-DRIFT")

    def test_tolerancia_invalida_e_recusada(self):
        for ruim in (0, -0.1, 0.9):
            with self.assertRaises(ValueError):
                alinhar({"00": 1}, {"00": 1}, tolerancia=ruim)

    def test_medicao_real_cudaq_contra_ibm(self):
        """Regressao da medicao de 17/11/2026, gravada em docs."""
        cudaq = {"00": 1018, "11": 1030}
        ibm = {"00": 1019, "11": 826, "01": 192, "10": 11}
        r10 = alinhar(cudaq, ibm, tolerancia=0.10, rotulo_a="cudaq-qpp", rotulo_b="ibm_marrakesh")
        self.assertEqual(r10["verdict"], 1)              # 0,0996 cabe em 0,10 por pouco
        self.assertAlmostEqual(r10["distancia"], 0.0996, places=4)
        r05 = alinhar(cudaq, ibm, tolerancia=0.05)
        self.assertEqual(r05["verdict"], "REFUSED")      # com 0,05 o mesmo par ja recusa

    def test_recibos_sem_selo_recusam(self):
        with self.assertRaises(Refusal):
            alinhar_recibos({"payload": {"counts": {"00": 1}}}, {"seal": "x", "counts": {"00": 1}})

    def test_cadeia_amarra_os_dois_selos(self):
        a = {"seal": "aaa", "payload": {"counts": {"00": 50, "11": 50}}}
        b = {"seal": "bbb", "payload": {"counts": {"00": 52, "11": 48}}}
        r = alinhar_recibos(a, b, tolerancia=0.10)
        self.assertEqual(r["verdict"], 1)
        self.assertEqual((r["selo_a"], r["selo_b"]), ("aaa", "bbb"))
        self.assertEqual(r["regra"], "alignment-two-v1")


if __name__ == "__main__":
    unittest.main()
