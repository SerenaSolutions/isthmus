# -*- coding: utf-8 -*-
"""Ramp sequencial: prova de que para cedo sem inventar resposta."""
import random
import unittest

from isthmus.ramp import (decidir_dos_counts, decidir_sequencial, limites_sprt,
                          llr_bernoulli, raio_hoeffding)


def bernoulli(p, n, semente=1):
    r = random.Random(semente)
    return [1 if r.random() < p else 0 for _ in range(n)]


class TestRampSequencial(unittest.TestCase):
    def test_fronteiras_de_wald(self):
        A, B = limites_sprt(0.05, 0.05)
        self.assertGreater(A, 0)
        self.assertLess(B, 0)
        self.assertAlmostEqual(A, -B, places=6)

    def test_llr_cresce_com_sucesso(self):
        self.assertGreater(llr_bernoulli(10, 0, 0.75, 0.90),
                           llr_bernoulli(5, 5, 0.75, 0.90))

    def test_decide_1_e_para_cedo(self):
        r = decidir_sequencial(bernoulli(0.97, 4096), 0.75, 0.90)
        self.assertEqual(r["verdict"], 1)
        self.assertLess(r["shots"], 200, f"gastou {r['shots']} tiros")

    def test_decide_0_e_para_cedo(self):
        r = decidir_sequencial(bernoulli(0.50, 4096), 0.75, 0.90)
        self.assertEqual(r["verdict"], 0)
        self.assertLess(r["shots"], 200, f"gastou {r['shots']} tiros")

    def test_banda_intermediaria_recusa_com_hoeffding(self):
        """O terceiro valor e da sequencia de confianca, nao do SPRT."""
        r = decidir_sequencial(bernoulli(0.83, 4096), 0.75, 0.90, regra="hoeffding")
        self.assertEqual(r["verdict"], "REFUSED")
        self.assertEqual(r["motivo"], "ISTH-BUDGET")

    def test_sprt_escolhe_lado_na_banda_e_isso_esta_documentado(self):
        """SPRT nao tem zona morta: entre p0 e p1 ele acaba escolhendo um lado."""
        r = decidir_sequencial(bernoulli(0.83, 4096), 0.75, 0.90, regra="sprt")
        self.assertIn(r["verdict"], (0, 1))

    def test_respeita_orcamento_de_tiros(self):
        r = decidir_sequencial(bernoulli(0.83, 4096), 0.75, 0.90, max_shots=120,
                               regra="hoeffding")
        self.assertEqual(r["verdict"], "REFUSED")
        self.assertLessEqual(r["shots"], 120)

    def test_economia_media_contra_4096(self):
        gastos = [decidir_sequencial(bernoulli(0.96, 4096, s), 0.75, 0.90)["shots"]
                  for s in range(60)]
        media = sum(gastos) / len(gastos)
        self.assertLess(media, 4096 * 0.25, f"media {media:.0f} tiros")

    def test_erro_tipo_I_controlado(self):
        """Em p = p0, decidir 1 nao pode passar de alpha com folga estatistica."""
        falsos = sum(1 for s in range(300)
                     if decidir_sequencial(bernoulli(0.76, 4096, s), 0.75, 0.90)["verdict"] == 1)
        self.assertLessEqual(falsos / 300, 0.10, f"{falsos} falsos positivos em 300")

    def test_hoeffding_decide_e_recusa(self):
        r1 = decidir_sequencial(bernoulli(0.99, 4096), 0.75, 0.90, regra="hoeffding")
        self.assertEqual(r1["verdict"], 1)
        r2 = decidir_sequencial(bernoulli(0.83, 400), 0.75, 0.90, max_shots=400, regra="hoeffding")
        self.assertEqual(r2["verdict"], "REFUSED")

    def test_raio_encolhe_com_n(self):
        self.assertGreater(raio_hoeffding(10), raio_hoeffding(1000))

    def test_counts_da_faixa_de_parada(self):
        r = decidir_dos_counts({"1": 950, "0": 50}, 0.75, 0.90)
        self.assertEqual(r["verdict"], 1)
        self.assertLessEqual(r["parada_min"], r["parada_max"])
        self.assertGreater(r["economia_contra_4096"], 0.7)

    def test_regras_diferem_quando_a_taxa_fica_entre_as_hipoteses(self):
        """Regressao: a regra hoeffding chegou a devolver o mesmo que o SPRT."""
        contagens = {"1": 1845, "0": 203}          # taxa 0,9009 entre 0,85 e 0,95
        sprt = decidir_dos_counts(contagens, 0.85, 0.95, target_key="1", regra="sprt")
        hoeff = decidir_dos_counts(contagens, 0.85, 0.95, target_key="1", regra="hoeffding")
        self.assertEqual(sprt["verdict"], 0)
        self.assertEqual(hoeff["verdict"], "REFUSED")
        self.assertNotEqual(sprt["verdict"], hoeff["verdict"])

    def test_counts_acima_do_orcamento_recusa(self):
        from isthmus.errors import Refusal
        with self.assertRaises(Refusal):
            decidir_dos_counts({"1": 5000, "0": 10}, 0.75, 0.90, max_shots=4096)

    def test_deterministico(self):
        a = decidir_sequencial(bernoulli(0.96, 1000, 7), 0.75, 0.90)
        b = decidir_sequencial(bernoulli(0.96, 1000, 7), 0.75, 0.90)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
