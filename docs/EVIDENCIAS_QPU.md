# Evidências de execução em QPU real

Documento de apoio ao preprint `ISTHMUS_paper_cientifico_comercial_v0.1`.
Existe porque o texto do preprint afirma que os testes foram feitos em simulador
(Qiskit Aer) e que adaptadores de QPU não estão implementados. O repositório
contém registros de execuções em hardware IBM, com `job_id` verificável na conta
da Serena Solutions.

## O que está registrado no repositório

### `experiments/ibm_2026_11_17/resultado.json`

| Campo | Valor |
| --- | --- |
| Data | 2026-11-17 |
| Backend | `ibm_marrakesh` |
| Job | `dbu3i2c9po4c73cegl3g` |
| Shots | 2048 |
| Concordam | 1845 |
| Discordam | 203 |
| Taxa | 0,900879 |
| Regra | SPRT, `verdict` 0, LLR −17,806998 |
| Hipóteses | p0 = 0,85 · p1 = 0,95 |

### `experiments/ibm_2026_11_17/terceiro_qpu.json`

Backend `ibm_fez`, três circuitos com recibo e selo:

| Circuito | Job | Shots | Concordam | Taxa | Veredito | Recibo |
| --- | --- | --- | --- | --- | --- | --- |
| `bell` | `dbu5pfhjbrss73a7ac7g` | 1024 | 967 | 0,9443 | REFUSED | ok, selo `de3759b6850acac2` |
| `ghz6` | `dbu5piqe8crs738b41kg` | 1024 | 868 | 0,8477 | REFUSED | ok |

### `experiments/ibm_2026_11_17/rodada2_isthmus_zephirum.json`

Registro de segunda rodada, integrando ISTHMUS e ZEPHIRUM. Detalhes no próprio arquivo.

## O que isso muda na redação do preprint

1. A frase "testes com Qiskit Aer, não com hardware quântico" precisa ser corrigida:
   há execução em QPU IBM documentada, com `job_id`.
2. A frase "adaptadores para QPUs ainda não implementados" também precisa de ajuste:
   existe caminho de execução em hardware registrado no repositório.
3. O que continua verdadeiro: não há teste de integração ponta a ponta automatizado
   para os três alvos (IBM, qBraid, CUDA-Q), nem suíte de CI que os exercite.

## O que ainda falta para sustentar alegação científica

1. Teste de integração reproduzível por terceiro, com token próprio.
2. Registro de calibração do backend no dia da execução.
3. Comparação entre QPU e simulador no mesmo circuito e mesmas shots.
4. Análise de incerteza sobre a taxa de concordância, não apenas o ponto estimado.

## Verificação

Os `job_id` podem ser consultados na IBM Quantum Platform pela conta que os submeteu.
Sem acesso à conta, a verificação possível é a integridade do registro: os arquivos
trazem recibo selado em SHA3-256, e a cadeia de recibos é verificável pelo próprio
ISTHMUS com `isthmus verify`.
