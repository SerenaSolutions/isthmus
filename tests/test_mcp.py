# -*- coding: utf-8 -*-
"""Teste de protocolo: fala MCP de verdade, por subprocesso e stdio."""
import json, os, subprocess, sys, unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MCPProtocoloTest(unittest.TestCase):
    def setUp(self):
        self.p = subprocess.Popen(
            [sys.executable, "-m", "isthmus_mcp.server"],
            cwd=RAIZ, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
            env={**os.environ, "PYTHONPATH": RAIZ})

    def tearDown(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()

    def _rpc(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())

    def test_initialize_declara_ferramentas(self):
        r = self._rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(r["id"], 1)
        self.assertIn("protocolVersion", r["result"])
        self.assertIn("tools", r["result"]["capabilities"])
        self.assertEqual(r["result"]["serverInfo"]["name"], "isthmus")

    def test_notificacao_nao_responde(self):
        self._rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.p.stdin.flush()
        r = self._rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(r["id"], 2)

    def test_lista_cinco_ferramentas_com_esquema(self):
        r = self._rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        nomes = [t["name"] for t in r["result"]["tools"]]
        self.assertEqual(nomes[:5], ["isthmus_decide", "isthmus_seal", "isthmus_verify",
                                     "isthmus_verify_chain", "isthmus_nomenclature"])
        self.assertIn("quanso_status", nomes)
        for t in r["result"]["tools"]:
            self.assertEqual(t["inputSchema"]["type"], "object")
            self.assertTrue(t["description"])

    def _call(self, nome, args, mid=10):
        return self._rpc({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
                          "params": {"name": nome, "arguments": args}})

    def test_decide_devolve_recibo_que_verifica(self):
        r = self._call("isthmus_decide", {"p0": 0.9, "shots": 512})
        dados = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(dados["verdict"], 1)
        self.assertEqual(dados["stage"]["stage"], "fine")
        v = self._call("isthmus_verify", {"receipt": dados["receipt"]}, 11)
        self.assertEqual(json.loads(v["result"]["content"][0]["text"])["state"], "ok")

    def test_verify_recusa_adulterado_com_codigo(self):
        r = self._call("isthmus_decide", {"p0": 0.9})
        rec = json.loads(r["result"]["content"][0]["text"])["receipt"]
        rec["payload"]["verdict"] = 0
        v = self._call("isthmus_verify", {"receipt": rec}, 12)
        self.assertTrue(v["result"]["isError"])
        self.assertEqual(json.loads(v["result"]["content"][0]["text"])["code"], "ISTH-FINE-SEAL")

    def test_seal_sem_verdict_recusa(self):
        r = self._call("isthmus_seal", {"payload": {"p0": 0.9}}, 13)
        self.assertTrue(r["result"]["isError"])
        self.assertEqual(json.loads(r["result"]["content"][0]["text"])["code"], "ISTH-STH-NOT-ALLOWED")

    def test_cadeia_de_dois_elos(self):
        a = json.loads(self._call("isthmus_decide", {"p0": 0.9, "seed": 1}, 14)["result"]["content"][0]["text"])
        b = json.loads(self._call("isthmus_decide", {"p0": 0.1, "seed": 2}, 15)["result"]["content"][0]["text"])
        b2 = dict(b["receipt"])
        b2["payload"] = dict(b2["payload"], prev_seal=a["receipt"]["seal"])
        import isthmus as I
        b2 = I.build(**{k: b2["payload"][k] for k in ("p0", "n", "shots", "seed", "mode", "error_bound", "verdict")},
                     prev_seal=a["receipt"]["seal"])
        r = self._call("isthmus_verify_chain", {"receipts": [a["receipt"], b2]}, 16)
        self.assertEqual(json.loads(r["result"]["content"][0]["text"])["links"], 2)

    def test_ferramenta_inexistente_da_erro_de_protocolo(self):
        r = self._call("nao_existe", {}, 17)
        self.assertEqual(r["error"]["code"], -32602)

    def test_nomenclatura_publica_o_vocabulario(self):
        r = self._call("isthmus_nomenclature", {}, 18)
        d = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(len(d["fases"]), 7)
        self.assertTrue(d["validacao"]["ok"])


if __name__ == "__main__":
    unittest.main()


class ExternoTest(unittest.TestCase):
    """Projeto externo vira ferramenta por CLI, sem tocar no servidor."""

    def test_provider_desativado_nao_aparece(self):
        from isthmus_mcp import externo
        provs = [{"project": "X", "tool": "x", "enabled": False, "command": ["x"]}]
        self.assertEqual(externo.especificacoes(provs), [])
        self.assertEqual(externo.despachos(provs), {})

    def test_provider_habilitado_roda_comando(self):
        from isthmus_mcp import externo
        provs = [{"project": "Eco", "tool": "eco", "enabled": True,
                  "command": [sys.executable, "-c", "print('ok-do-projeto')"]}]
        specs = externo.especificacoes(provs)
        self.assertEqual(specs[0]["name"], "eco")
        r = externo.despachos(provs)["eco"]({})
        self.assertEqual(r["saida"], "ok-do-projeto")

    def test_comando_ausente_vira_codigo(self):
        from isthmus_mcp import externo
        provs = [{"project": "Fantasma", "tool": "fantasma", "enabled": True,
                  "command": ["binario-que-nao-existe-xyz"]}]
        with self.assertRaises(externo.FalhaExterna) as ctx:
            externo.despachos(provs)["fantasma"]({})
        self.assertEqual(ctx.exception.codigo, "ISTH-MCP-EXT-AUSENTE")

    def test_quanso_declarado_uma_vez_so(self):
        from isthmus_mcp import externo
        provs = externo.carregar()
        alvo = [p for p in provs if p.get("project") == "QuanSo"]
        self.assertEqual(len(alvo), 1, "QuanSo precisa estar declarado exatamente uma vez")


class QuanSoProviderTest(unittest.TestCase):
    """QuanSo integrado como ferramenta MCP declarada."""

    def test_quanso_ativo_com_comando_correto(self):
        from isthmus_mcp import externo
        alvo = [p for p in externo.carregar() if p.get("project") == "QuanSo"]
        self.assertEqual(len(alvo), 1)
        self.assertTrue(alvo[0]["enabled"], "QuanSo precisa estar ativo")
        self.assertEqual(alvo[0]["command"], ["python3", "-m", "boot"])
        self.assertEqual(alvo[0]["fixed_args"], ["classico"])

    def test_quanso_vira_ferramenta_listada(self):
        from isthmus_mcp import externo
        specs = externo.especificacoes(externo.carregar())
        nomes = [s["name"] for s in specs]
        self.assertIn("quanso_status", nomes)

    def test_argumentos_posicionais_entram_antes_das_flags(self):
        from isthmus_mcp import externo
        prov = {"project": "P", "tool": "p", "enabled": True,
                "command": [sys.executable, "-c",
                            "import sys; print('|'.join(sys.argv[1:]))"],
                "fixed_args": ["classico"]}
        r = externo.executar(prov, {"modo": "sim"})
        self.assertEqual(r["saida"], "classico|--modo|sim")
