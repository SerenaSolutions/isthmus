# -*- coding: utf-8 -*-
"""O vocabulario e parte da linguagem: cada nome tem alvo, fase e teste."""
import os, re, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import isthmus as I
from isthmus import nomenclature as N
from isthmus.errors import Refusal


class PipelineTest(unittest.TestCase):
    def test_sete_fases_na_ordem(self):
        self.assertEqual(len(N.ORDER), 7)
        self.assertEqual(N.ORDER[0], "Deployment")
        self.assertEqual(N.ORDER[-1], "Wavefront Control")

    def test_indice_da_fase(self):
        self.assertEqual(N.stage_index("Wavefront Sensing"), 1)
        self.assertEqual(N.stage_index("Coarse Phasing"), 4)
        self.assertLess(N.stage_index("Coarse Phasing"), N.stage_index("Fine Phasing"))

    def test_fase_inexistente_recusa(self):
        with self.assertRaises(KeyError):
            N.stage_index("Warp Drive")

    def test_todo_nome_tem_alvo_importavel(self):
        v = N.validate()
        self.assertTrue(v["ok"], v["faltando"])
        self.assertEqual(v["fases"], 7)
        self.assertEqual(v["contratos"], 4)
        self.assertEqual(v["artefatos"], 2)


class FasesSeparadasTest(unittest.TestCase):
    def _rec(self, **kw):
        base = dict(p0=0.9, n=4, shots=512, seed=1, mode="sim", error_bound=0.05, verdict=1)
        base.update(kw)
        return I.build(**base)

    def test_coarse_passa_e_fine_passa(self):
        rec = self._rec()
        self.assertEqual(I.coarse_phasing(rec)["stage"], "coarse_phasing")
        self.assertEqual(I.fine_phasing(rec)["stage"], "fine_phasing")

    def test_coarse_falha_antes_do_selo(self):
        rec = self._rec()
        rec["payload"]["gramatica"] = "9.9"
        with self.assertRaises(Refusal) as ctx:
            I.coarse_phasing(rec)
        self.assertEqual(ctx.exception.code, "ISTH-COARSE-GRAMATICA")
        # a fase fina diria apenas "selo nao confere": menos especifica.
        # e por isso que a grossa roda primeiro.
        with self.assertRaises(Refusal) as ctx2:
            I.fine_phasing(rec)
        self.assertEqual(ctx2.exception.code, "ISTH-FINE-SEAL")

    def test_fine_pega_adulteracao_que_coarse_deixa_passar(self):
        rec = self._rec()
        rec["payload"]["verdict"] = 0
        self.assertEqual(I.coarse_phasing(rec)["state"], "ok")
        with self.assertRaises(Refusal) as ctx:
            I.fine_phasing(rec)
        self.assertEqual(ctx.exception.code, "ISTH-FINE-SEAL")


class ArtefatoTest(unittest.TestCase):
    def test_snowball_e_shower(self):
        self.assertEqual(N.artifact_of("ISTH-FINE-SEAL"), "Snowball")
        self.assertEqual(N.artifact_of("ISTH-CHAIN-SHOWER"), "Shower")
        self.assertIsNone(N.artifact_of("ISTH-BUDGET"))

    def test_codigos_dos_artefatos_existem_no_catalogo(self):
        for nome, _, codigo in N.ARTIFACTS:
            self.assertIn(codigo, I.CODES)


class DriftDoReadmeTest(unittest.TestCase):
    def test_readme_cita_todas_as_fases(self):
        txt = open(os.path.join(RAIZ, "README.md"), encoding="utf-8").read()
        faltando = [f for f in N.ORDER if f not in txt]
        self.assertEqual(faltando, [], f"fases ausentes no README: {faltando}")

    def test_readme_cita_os_contratos(self):
        txt = open(os.path.join(RAIZ, "README.md"), encoding="utf-8").read()
        for nome, _, _ in N.CONTRACTS:
            self.assertIn(nome, txt, f"contrato ausente no README: {nome}")


if __name__ == "__main__":
    unittest.main()
