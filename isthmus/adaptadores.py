# -*- coding: utf-8 -*-
"""Adaptadores de execucao: a ponte que o Isthmus opera.

Dois lados, cada um com codigo de recusa proprio e nenhum silencio:
- qBraid: simulador gratuito (qir-sv), util como segundo lado do Alignment Two;
- IBM: QPU real pela API v1 da plataforma, com sampler V2.

Regra que vale para os dois: credencial ausente, saldo zero ou dispositivo offline
viram recusa declarada, nunca excecao crua e nunca resultado inventado.
"""
import json
import os
import subprocess

from .errors import Refusal

IBM_BASE = "https://quantum.cloud.ibm.com/api/v1"
# CRN da instancia de quantum-computing; pode ser sobrescrito por IBM_CRN
IBM_CRN_PADRAO = ("crn:v1:bluemix:public:quantum-computing:us-east:"
                  "a/95c41207c62e44b4836797c50afa51b8:52de7392-9adb-443b-9b46-ea0b88a0145f::")
IBM_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def _curl(metodo, url, cabecalhos, corpo=None, timeout=90):
    args = ["curl", "-s", "-w", "\n%{http_code}", "-m", str(timeout), "-X", metodo, url]
    for k, v in cabecalhos.items():
        args += ["-H", f"{k}: {v}"]
    if corpo is not None:
        args += ["-H", "content-type: application/json", "-d", json.dumps(corpo)]
    saida = subprocess.run(args, capture_output=True, text=True, timeout=timeout + 15)
    partes = saida.stdout.rsplit("\n", 1)
    texto = partes[0] if len(partes) == 2 else ""
    codigo = int(partes[1]) if len(partes) == 2 and partes[1].strip().isdigit() else 0
    try:
        return codigo, json.loads(texto or "{}")
    except json.JSONDecodeError:
        return codigo, {"bruto": texto[:300]}


# ----------------------------------------------------------------- qBraid
def qbraid_simulador(portoes, shots=1024, dispositivo="qbraid:qbraid:sim:qir-sv"):
    """Executa no simulador gratuito do qBraid. Sem credito, recusa ISTH-BUDGET."""
    chave = os.environ.get("QBRAID_API_KEY") or os.environ.get("QBRAID_CHAVE")
    if not chave:
        raise Refusal("ISTH-BUDGET", "QBRAID_API_KEY ausente")
    try:
        from qbraid.runtime import QbraidProvider
    except ImportError:
        raise Refusal("ISTH-BUDGET", "SDK do qBraid ausente")
    from qiskit import QuantumCircuit
    n = 1 + max(max(p[1:]) for p in portoes)
    qc = QuantumCircuit(n, n)
    for porta in portoes:
        nome = porta[0].upper()
        if nome == "H":
            qc.h(porta[1])
        elif nome == "X":
            qc.x(porta[1])
        elif nome == "CNOT":
            qc.cx(porta[1], porta[2])
        else:
            raise ValueError(f"porta fora do conjunto: {nome}")
    qc.measure(range(n), range(n))
    try:
        alvo = QbraidProvider(api_key=chave).get_device(dispositivo)
        resultado = alvo.run(qc, shots=shots).result()
    except Exception as e:
        texto = str(e)
        if "Insufficient qBraid credits" in texto:
            raise Refusal("ISTH-BUDGET", "saldo qBraid em zero")
        raise Refusal("ISTH-BUDGET", f"qbraid: {texto[:120]}")
    contagens = resultado.data.get_counts()
    return {k.replace(" ", ""): int(v) for k, v in contagens.items()}


# ----------------------------------------------------------------- IBM
def _ibm_token():
    chave = os.environ.get("IBM_API_KEY")
    if not chave:
        raise Refusal("ISTH-BUDGET", "IBM_API_KEY ausente")
    saida = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://iam.cloud.ibm.com/identity/token",
         "-H", "content-type: application/x-www-form-urlencoded",
         "--data-urlencode", "grant_type=urn:ibm:params:oauth:grant-type:apikey",
         "--data-urlencode", f"apikey={chave}",
         "--data-urlencode", "response_type=cloud_iam"],
        capture_output=True, text=True, timeout=60)
    try:
        token = json.loads(saida.stdout)["access_token"]
    except Exception:
        raise Refusal("ISTH-BUDGET", "credencial IBM recusada pelo IAM")
    return token


def _ibm(caminho, metodo="GET", corpo=None):
    token = _ibm_token()
    crn = os.environ.get("IBM_CRN") or IBM_CRN_PADRAO
    return _curl(metodo, f"{IBM_BASE}{caminho}",
                 {"Authorization": f"Bearer {token}", "Service-CRN": crn,
                  "IBM-API-Version": "2025-05-01", "Accept": "application/json",
                  "User-Agent": IBM_UA}, corpo)


def ibm_dispositivos():
    codigo, dados = _ibm("/backends")
    if codigo != 200:
        raise Refusal("ISTH-BUDGET", f"listagem IBM falhou: {codigo}")
    return [d["name"] for d in dados.get("devices", [])
            if d.get("status", {}).get("name") == "online"]


def ibm_executar(qasm, backend="ibm_kingston", shots=1024, timeout=600):
    """Submete um circuito OpenQASM 3 ao QPU real e devolve as contagens."""
    codigo, resp = _ibm("/jobs", "POST", {"program_id": "sampler", "backend": backend,
                                          "params": {"version": 2, "pubs": [[qasm, None, shots]]}})
    if codigo != 200 or "id" not in resp:
        raise Refusal("ISTH-BUDGET", f"submissao recusada: {codigo} {str(resp)[:120]}")
    job = resp["id"]
    import time
    for _ in range(max(1, timeout // 10)):
        _, st = _ibm(f"/jobs/{job}")
        estado = st.get("state") or st.get("status") or {}
        if isinstance(estado, dict):
            estado = estado.get("name") or estado.get("status")
        if str(estado).lower() == "completed":
            _, res = _ibm(f"/jobs/{job}/results")
            amostras = res["results"][0]["data"]["c"]["samples"]
            n = int(res["results"][0]["data"]["c"].get("num_bits", 0)) or _bits(qasm)
            contagens = {}
            for s in amostras:
                k = format(int(s, 16), f"0{n}b")
                contagens[k] = contagens.get(k, 0) + 1
            return {"job": job, "backend": backend, "contagens": contagens}
        if str(estado).lower() in ("failed", "error", "cancelled"):
            raise Refusal("ISTH-BUDGET", f"job {job} terminou em {estado}")
        time.sleep(10)
    raise Refusal("ISTH-BUDGET", f"job {job} nao terminou em {timeout}s")


def ibm_executar_circuito(circuito, backend="ibm_kingston", shots=1024, timeout=600):
    """Recebe um QuantumCircuit, transpila para os portoes nativos do alvo e executa."""
    from qiskit import transpile, qasm3
    codigo, conf = _ibm(f"/backends/{backend}/configuration")
    if codigo != 200:
        raise Refusal("ISTH-BUDGET", f"configuracao de {backend} indisponivel")
    base = [g for g in conf["basis_gates"] if g != "xslow"]   # xslow nao e portao padrao do Qiskit
    pronto = transpile(circuito, basis_gates=base, coupling_map=conf["coupling_map"],
                       optimization_level=1, seed_transpiler=17)
    return ibm_executar(qasm3.dumps(pronto), backend=backend, shots=shots, timeout=timeout)


def _bits(qasm):
    for linha in qasm.splitlines():
        if linha.strip().startswith("bit["):
            return int(linha.split("[")[1].split("]")[0])
    return 0
