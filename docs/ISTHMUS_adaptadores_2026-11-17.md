# Adaptadores: qBraid e IBM, os dois medidos

## O que existe agora

`isthmus/adaptadores.py` entrega duas pontes reais, com uma regra comum: credencial ausente, saldo zerado ou dispositivo fora do ar viram recusa declarada, nunca exceção crua e nunca resultado inventado.

1. `qbraid_simulador(portoes, shots)`: simulador gratuito `qbraid:qbraid:sim:qir-sv`. Medido: Bell de 256 tiros devolveu `00` = 136 e `11` = 120
2. `ibm_dispositivos()`: lê os QPUs online da instância
3. `ibm_executar(qasm, backend, shots)`: submete OpenQASM 3 ao QPU, acompanha o job e extrai as contagens
4. `ibm_executar_circuito(qc, backend, shots)`: transpila para os portões nativos do alvo e chama o anterior

## Medição em QPU real

Job `dbu4u8gvv3fc73c0qd1g`, `ibm_kingston`, 512 tiros, Bell com 1 CZ:

| Resultado | Contagem |
|---|---|
| 00 | 275 |
| 11 | 216 |
| 10 | 12 |
| 01 | 9 |

Concordância entre bits: 95,90%. Recusa assimétrica: 12 em `10` contra 9 em `01`.

## Ponto de atenção declarado

Falha de autenticação hoje cai no código `ISTH-BUDGET`, que é de orçamento, não de credencial. O catálogo é fechado e tem 17 códigos, todos com teste. Criar um código próprio de credencial é mudança de catálogo, e fica como decisão separada, não como atalho.

## Como rodar os testes ao vivo

```
ISTHMUS_LIVE=1 QBRAID_API_KEY=... IBM_API_KEY=... python -m unittest tests.test_adaptadores
```
