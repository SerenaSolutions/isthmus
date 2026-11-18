# -*- coding: utf-8 -*-
"""Criptoagilidade: sig_alg declarado, despacho por algoritmo, legado intacto."""
import copy, unittest
import isthmus as I
from isthmus import assinatura as A
from isthmus.errors import Refusal

BASE = dict(verdict="1", p0=0.5, n=1000, shots=1000, seed=0, mode="exact", error_bound=0.0247)


class TestAssinatura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pk, cls.sk = A.gerar_chave()
        cls.r = I.receipt.build(**BASE)
        cls.ra = A.assinar(cls.r, cls.sk)

    def test_assina_e_verifica(self):
        self.assertEqual(self.ra["sig_alg"], "ml-dsa-44")
        self.assertEqual(I.verify(self.ra)["state"], "ok")
        out = A.verificar_assinatura(self.ra, self.pk)
        self.assertTrue(out["assinado"])

    def test_selo_cobre_sig_alg(self):
        self.assertEqual(self.ra["payload"]["sig_alg"], "ml-dsa-44")
        self.assertNotEqual(self.ra["seal"], self.r["seal"])

    def test_payload_adulterado_quebra_selo(self):
        ruim = copy.deepcopy(self.ra)
        ruim["payload"]["verdict"] = "0"
        with self.assertRaises(Refusal) as ctx:
            I.verify(ruim)
        self.assertEqual(ctx.exception.code, "ISTH-FINE-SEAL")

    def test_assinatura_adulterada(self):
        ruim = copy.deepcopy(self.ra)
        ruim["sig"] = "A" * 200
        with self.assertRaises(Refusal) as ctx:
            A.verificar_assinatura(ruim, self.pk)
        self.assertEqual(ctx.exception.code, "ISTH-SIG-FALHA")

    def test_algoritmo_desconhecido(self):
        ruim = copy.deepcopy(self.ra)
        ruim["sig_alg"] = "rsa-2048"
        with self.assertRaises(Refusal) as ctx:
            A.verificar_assinatura(ruim, self.pk)
        self.assertEqual(ctx.exception.code, "ISTH-SIG-ALG")

    def test_declara_alg_e_nao_traz_assinatura(self):
        ruim = copy.deepcopy(self.ra)
        ruim["sig"] = None
        with self.assertRaises(Refusal) as ctx:
            A.verificar_assinatura(ruim, self.pk)
        self.assertEqual(ctx.exception.code, "ISTH-SIG-AUSENTE")

    def test_legado_sem_sig_alg_continua_verificando(self):
        self.assertNotIn("sig_alg", self.r["payload"])
        self.assertEqual(I.verify(self.r)["state"], "ok")
        out = A.verificar_assinatura(self.r, self.pk)
        self.assertEqual(out["alg"], "none")
        self.assertFalse(out["assinado"])

    def test_selo_deterministico_assinatura_nao(self):
        a = A.assinar(self.r, self.sk)
        b = A.assinar(self.r, self.sk)
        self.assertEqual(a["seal"], b["seal"])          # selo: deterministico
        self.assertEqual(A.verificar_assinatura(a, self.pk)["state"], "ok")
        self.assertEqual(A.verificar_assinatura(b, self.pk)["state"], "ok")
        # assinatura ML-DSA-44 e randomizada: ambas validas, bytes podem diferir

    def test_chave_errada_nao_verifica(self):
        outro_pk, _ = A.gerar_chave()
        with self.assertRaises(Refusal):
            A.verificar_assinatura(self.ra, outro_pk)

    def test_verificar_completo(self):
        out = A.verificar_completo(self.ra, self.pk)
        self.assertEqual(out["selo"]["state"], "ok")
        self.assertEqual(out["assinatura"]["alg"], "ml-dsa-44")


if __name__ == "__main__":
    unittest.main(verbosity=2)
