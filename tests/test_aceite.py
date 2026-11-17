# -*- coding: utf-8 -*-
"""Testes de aceite do ISTHMUS, um por criterio do inventario 1.3."""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import isthmus as I
from isthmus.errors import Refusal


def backend(p=0.9):
    def f(shots, seed):
        k = int(round(p * shots))
        return {"1": k, "0": shots - k}
    return f


class CanonizeTest(unittest.TestCase):
    def test_deterministico_e_com_perfil(self):
        a = I.canonize({"b": 1, "a": {"d": 2, "c": 3}})
        b = I.canonize({"a": {"c": 3, "d": 2}, "b": 1})
        self.assertEqual(a["bytes"], b["bytes"])
        self.assertEqual(a["profile"], "canon-v1")
        self.assertEqual(len(a["sha3"]), 64)

    def test_perfil_desconhecido_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            I.canonize({"a": 1}, profile="canon-v9")
        self.assertEqual(ctx.exception.code, "ISTH-PROFILE")

    def test_dois_perfis_mesmo_payload(self):
        a = I.canonize({"s": "x\by"}, "canon-v1")
        b = I.canonize({"s": "x\by"}, "canon-u0008")
        self.assertNotEqual(a["sha3"], b["sha3"])


class FringeTest(unittest.TestCase):
    def test_sem_deriva(self):
        a = I.canonize({"a": 1})
        self.assertEqual(I.fringe(a, a)["state"], "no-drift")

    def test_escape_de_controle(self):
        a = I.canonize({"s": "x\by"}, "canon-v1")
        b = I.canonize({"s": "x\by"}, "canon-u0008")
        d = I.fringe(a, b)
        self.assertEqual(d["state"], "drift")
        self.assertEqual(d["kind"], "control-escape")


class ShutterTest(unittest.TestCase):
    def test_recusa_campo_nao_declarado(self):
        with self.assertRaises(Refusal) as ctx:
            I.shutter({"p0": 0.9, "extra": 1}, required=("p0",))
        self.assertEqual(ctx.exception.code, "ISTH-SHUTTER")

    def test_admite_valido(self):
        self.assertEqual(I.shutter({"p0": 0.9}, required=("p0",))["state"], "admitted")


class RampTest(unittest.TestCase):
    def test_ajusta_taxa(self):
        samples = [(i, 100 + 20 * i) for i in range(8)]
        r = I.ramp_fit(samples)
        self.assertAlmostEqual(r["rate"], 20.0, places=6)
        self.assertLess(r["sigma"], 1e-9)

    def test_quebra_detectada(self):
        samples = [(i, 100 + 20 * i) for i in range(4)] + [(i, 180 + 1 * i) for i in range(4, 9)]
        with self.assertRaises(Refusal) as ctx:
            I.ramp_fit(samples)
        self.assertEqual(ctx.exception.code, "ISTH-RAMP-BREAK")

    def test_serie_curta(self):
        with self.assertRaises(Refusal) as ctx:
            I.ramp_fit([(0, 1), (1, 2)])
        self.assertEqual(ctx.exception.code, "ISTH-RAMP-SHORT")


class RefaseTest(unittest.TestCase):
    def test_alinhamento(self):
        a = [0.1, 0.2, 0.3, 0.4, 0.5]
        b = a[2:] + a[:2]
        r = I.refase(a, b, band=0.01)
        self.assertEqual(r["shift"], 2)
        self.assertLess(r["residual"], 1e-9)

    def test_banda_estourada(self):
        with self.assertRaises(Refusal) as ctx:
            I.refase([0.1] * 4, [0.9] * 4, band=0.01)
        self.assertEqual(ctx.exception.code, "ISTH-REFASE-BAND")


class BudgetTest(unittest.TestCase):
    def test_recusa_ao_estourar(self):
        b = I.Budget(shots=1000, oracle_calls=1)
        b.spend(shots=600, oracle=1)
        with self.assertRaises(Refusal) as ctx:
            b.spend(shots=600)
        self.assertEqual(ctx.exception.code, "ISTH-BUDGET")
        with self.assertRaises(Refusal) as ctx2:
            b.spend(oracle=1)
        self.assertEqual(ctx2.exception.code, "ISTH-BUDGET")


class SamplerTest(unittest.TestCase):
    def test_tiros_declarados(self):
        b = I.Budget(shots=1024, oracle_calls=1)
        r = I.sample(backend(), shots=512, budget=b)
        self.assertEqual(sum(r["counts"].values()), 512)
        self.assertEqual(r["budget"]["oracle_used"], 1)

    def test_divergencia_de_tiros(self):
        with self.assertRaises(Refusal) as ctx:
            I.sample(lambda shots, seed: {"1": shots - 1}, shots=512)
        self.assertEqual(ctx.exception.code, "ISTH-SHOTS")


class EstimatorTest(unittest.TestCase):
    def test_duas_rodadas_dentro_da_banda(self):
        r = I.estimate_two_rounds(lambda r: 0.80 + 0.001 * r, band=0.01)
        self.assertEqual(len(r["rounds"]), 2)
        self.assertAlmostEqual(r["estimate"], 0.8015, places=6)

    def test_deriva_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            I.estimate_two_rounds(lambda r: 0.5 + 0.2 * r, band=0.01)
        self.assertEqual(ctx.exception.code, "ISTH-ALIGNMENT-DRIFT")


class MitigationTest(unittest.TestCase):
    def test_metodo_sem_fatores(self):
        with self.assertRaises(Refusal) as ctx:
            I.mitigation_audit("ZNE", [], 0.81, 0.76)
        self.assertEqual(ctx.exception.code, "ISTH-MITIG-UNDECLARED")

    def test_mudanca_sem_metodo(self):
        with self.assertRaises(Refusal) as ctx:
            I.mitigation_audit(None, [], 0.81, 0.76)
        self.assertEqual(ctx.exception.code, "ISTH-MITIG-UNDECLARED")

    def test_declarado_passa(self):
        r = I.mitigation_audit("ZNE", [1, 3], 0.81, 0.76)
        self.assertAlmostEqual(r["delta"], 0.05, places=6)


class TranspileTest(unittest.TestCase):
    def test_roundtrip_identico(self):
        self.assertEqual(I.transpile_audit(["h", "cx"], lambda o: o)["ops"], 2)

    def test_perda_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            I.transpile_audit(["h", "cx"], lambda o: o[:1])
        self.assertEqual(ctx.exception.code, "ISTH-TRANSPILE-LOSS")


class FlowTest(unittest.TestCase):
    def test_flow_valido(self):
        f = I.Flow().add("prepare").add("evolve").add("measure").add("reset").add("prepare")
        self.assertEqual(f.run()["count"], 5)

    def test_reset_sem_prepare(self):
        with self.assertRaises(Refusal) as ctx:
            I.Flow().add("prepare").add("reset").add("measure").run()
        self.assertEqual(ctx.exception.code, "ISTH-FLOW")


class CharacterizeTest(unittest.TestCase):
    def test_banda_otimista_recusa(self):
        prof = I.characterize(0.02, 120.0, "sim", "2026-11-17")
        with self.assertRaises(Refusal) as ctx:
            I.check_band(0.01, prof)
        self.assertEqual(ctx.exception.code, "ISTH-BAND-OPTIMISM")

    def test_coerencia_ausente_nao_quebra(self):
        prof = I.characterize(0.008, backend="aer_simulator")
        self.assertIsNone(prof["coherence_us"])
        self.assertEqual(I.check_band(0.03, prof)["state"], "coerente")

    def test_taxa_de_erro_ausente_recusa(self):
        with self.assertRaises(Refusal) as ctx:
            I.characterize(None)
        self.assertEqual(ctx.exception.code, "ISTH-BAND-OPTIMISM")

    def test_banda_coerente(self):
        prof = I.characterize(0.02, 120.0, "sim", "2026-11-17")
        self.assertEqual(I.check_band(0.05, prof)["state"], "coerente")


class ReceiptTest(unittest.TestCase):
    def _rec(self, **kw):
        base = dict(p0=0.9, n=4, shots=512, seed=1, mode="sim", error_bound=0.05, verdict=1)
        base.update(kw)
        return I.build(**base)

    def test_grossa_antes_da_fina(self):
        rec = self._rec()
        rec["payload"]["schema"] = "9.9"
        with self.assertRaises(Refusal) as ctx:
            I.verify(rec)
        self.assertEqual(ctx.exception.code, "ISTH-COARSE-SCHEMA")

    def test_campo_ausente(self):
        rec = self._rec()
        del rec["payload"]["shots"]
        with self.assertRaises(Refusal) as ctx:
            I.verify(rec)
        self.assertEqual(ctx.exception.code, "ISTH-COARSE-CAMPO")

    def test_gramatica_invalida(self):
        rec = self._rec()
        rec["payload"]["gramatica"] = "9.9"
        with self.assertRaises(Refusal) as ctx:
            I.verify(rec)
        self.assertEqual(ctx.exception.code, "ISTH-COARSE-GRAMATICA")

    def test_snowball_detectado(self):
        rec = self._rec()
        rec["payload"]["verdict"] = 0
        with self.assertRaises(Refusal) as ctx:
            I.verify(rec)
        self.assertEqual(ctx.exception.code, "ISTH-FINE-SEAL")

    def test_recibo_intacto(self):
        self.assertEqual(I.verify(self._rec())["stage"], "fine")

    def test_shower_detectado_na_cadeia(self):
        r1 = self._rec()
        r2 = I.build(prev_seal=r1["seal"], p0=0.9, n=4, shots=512, seed=2, mode="sim",
                     error_bound=0.05, verdict=1)
        r3 = I.build(prev_seal=r2["seal"], p0=0.9, n=4, shots=512, seed=3, mode="sim",
                     error_bound=0.05, verdict=1)
        self.assertEqual(I.verify_chain([r1, r2, r3])["links"], 3)
        # re-sela o elo do meio: cada recibo continua valido, a cadeia nao
        forged = I.build(prev_seal=r1["seal"], p0=0.1, n=4, shots=512, seed=2, mode="sim",
                         error_bound=0.05, verdict=0)
        I.verify(forged)
        with self.assertRaises(Refusal) as ctx:
            I.verify_chain([r1, forged, r3])
        self.assertEqual(ctx.exception.code, "ISTH-CHAIN-SHOWER")


if __name__ == "__main__":
    unittest.main(verbosity=2)
