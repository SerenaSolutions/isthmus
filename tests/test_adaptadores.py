# -*- coding: utf-8 -*-
"""Adaptadores: recusa declarada quando falta credencial, e nada de excecao crua."""
import os
import unittest

from isthmus import adaptadores
from isthmus.errors import Refusal


class TestRecusaSemCredencial(unittest.TestCase):
    def setUp(self):
        self.guarda = {k: os.environ.pop(k, None) for k in ("QBRAID_API_KEY", "QBRAID_CHAVE", "IBM_API_KEY")}

    def tearDown(self):
        for k, v in self.guarda.items():
            if v is not None:
                os.environ[k] = v

    def test_qbraid_sem_chave_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            adaptadores.qbraid_simulador([("H", 0)], shots=8)
        self.assertEqual(ctx.exception.code, "ISTH-BUDGET")

    def test_ibm_sem_chave_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            adaptadores.ibm_dispositivos()
        self.assertEqual(ctx.exception.code, "ISTH-BUDGET")

    def test_porta_desconhecida_e_erro_de_programa(self):
        os.environ["QBRAID_API_KEY"] = "chave-falsa-para-forcar-caminho"
        with self.assertRaises((ValueError, Refusal)):
            adaptadores.qbraid_simulador([("ROT", 0, 1)], shots=8)


@unittest.skipUnless(os.environ.get("ISTHMUS_LIVE") == "1",
                     "rodada ao vivo desligada; defina ISTHMUS_LIVE=1")
class TestAoVivo(unittest.TestCase):
    def test_qbraid_gratuito(self):
        contagens = adaptadores.qbraid_simulador([("H", 0), ("CNOT", 0, 1)], shots=128)
        self.assertEqual(sum(contagens.values()), 128)

    def test_ibm_qpu(self):
        from qiskit import QuantumCircuit
        qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
        r = adaptadores.ibm_executar_circuito(qc, shots=128, timeout=420)
        self.assertEqual(sum(r["contagens"].values()), 128)
        self.assertTrue(r["job"])


if __name__ == "__main__":
    unittest.main()
