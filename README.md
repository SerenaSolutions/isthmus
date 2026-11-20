# ISTHMUS

Sub-linguagem híbrida de interoperabilidade, controle e verificação do ecossistema
ZEPHIRUM/ZYQL. Abreviações: **ISTH** e **STH**.

Quatorze algoritmos em três camadas, recibo com duas etapas de verificação, zero
dependência externa.

Versão 0.1.1 · 42 testes · Apache-2.0

## Instalar

```bash
pip install -e .
```

## Rodar em trinta segundos

```bash
python3 -m unittest discover -s tests -v      # 42 testes, todos passando
isth    decide --p0 0.9 --shots 512 > r.json
sth     verify r.json                          # {"state":"ok","stage":"fine"}
```

Os três comandos `isthmus`, `isth` e `ist` são equivalentes e decidem.
`sth` é a derivada: sela, verifica e encadeia, e **não decide**.

Alterar `verdict` no `r.json` e repetir a verificação devolve
`{"state":"refused","code":"ISTH-FINE-SEAL"}` com saída de código 1.

## ISTH e STH

| | ISTH | STH |
|---|---|---|
| decide | sim | **não** |
| sela payload já decidido | sim | sim |
| verifica recibo e cadeia | sim | sim |
| tem Ramp, Shutter, banda, oráculo | sim | não |

```bash
isth decide --p0 0.9 --shots 512 > r.json   # decide e sela
sth  seal   payload.json                     # sela payload cru, exige campo verdict
sth  verify r.json                           # confere
sth  chain  r1.json r2.json r3.json          # confere a cadeia
sth  decide                                  # recusa: ISTH-STH-NOT-ALLOWED
```

`sth seal` recebe um payload cru, não um recibo. O mínimo é:

```json
{"p0": 0.9, "n": 4, "shots": 512, "seed": 1, "mode": "sim", "error_bound": 0.05, "verdict": 1}
```

Recibo emitido sob ISTH verifica sob STH. É o sentido da derivação: quem só
confere não precisa da camada que decide.

## O que existe

| Camada | Algoritmos | Estado |
|---|---|---|
| Clássico puro | Ramp, Shutter, Canonize, Fringe, Refase | implementado e testado |
| Híbrido | Sampler, Estimator com Alignment Two, Mitigation audit, Budget, Transpile audit | implementado como contrato |
| Ponta quântica | Prepare, Evolve, Measure, Reset, Flow, Characterize | implementado como fluxo local |
| Ponte com backend real | as cinco responsabilidades híbridas | **planejado** |

A ponte com QPU e simulador externo não está implementada. Nenhum adaptador foi
conectado, e este README não afirma o contrário.

## As duas etapas do verificador

1. **Grossa**: esquema, versão de gramática e campos obrigatórios. Barata, falha cedo.
2. **Fina**: selo SHA3-256 sobre os bytes canônicos. Cara, falha tarde.

A cadeia tem verificação própria: um elo re-selado passa sozinho e só
`verify_chain` o denuncia, que é a diferença entre dano contíguo (*snowball*) e
dano distribuído (*shower*).

## Servidor MCP, para qualquer agente

O Isthmus fala o Model Context Protocol em stdlib pura, sem dependência. Um agente
qualquer, inclusive de outra empresa, chama o verificador como ferramenta:

```bash
isthmus-mcp          # transporte stdio, JSON-RPC 2.0
```

| ferramenta | faz |
|---|---|
| `isthmus_decide` | decide com banda declarada e devolve recibo selado |
| `isthmus_seal` | sela payload já decidido, exige o campo `verdict` |
| `isthmus_verify` | verifica recibo, fase grossa e fase fina |
| `isthmus_verify_chain` | verifica cadeia e distingue dano contíguo de distribuído |
| `isthmus_nomenclature` | devolve fases, contratos e códigos de recusa |

Recusa chega ao agente como `isError` com código `ISTH-*`, nunca como traceback. O
manifesto de registro está em `server.json`, e nove testes falam o protocolo por
subprocesso em `tests/test_mcp.py`.

## Vocabulário de verificação, adaptado à linguagem

Os nomes das fases vêm da engenharia de alinhamento do telescópio espacial James
Webb, onde alinhar o espelho é medir, corrigir e medir de novo em duas escalas.
No Isthmus eles não são metáfora de documento: são o pipeline declarado em
`isthmus/nomenclature.py`, e cada nome aponta para a função que o executa.

| fase | o que faz no Isthmus | alvo no código |
|---|---|---|
| Deployment | declara band, oracle, shots e deny antes de executar | `budget.Budget` |
| Wavefront Sensing | aquisição não destrutiva em rampa | `ramp.fit` |
| Segment Alignment | admissão de campos e forma canônica | `shutter.shutter` |
| Image Stacking | acúmulo de contagens até os tiros declarados | `sampler.sample` |
| Coarse Phasing | esquema, versão de gramática e campos | `receipt.coarse_phasing` |
| Fine Phasing | selo SHA3-256 sobre os bytes canônicos | `receipt.fine_phasing` |
| Wavefront Control | correção de fase entre duas medições | `refase.refase` |

Quatro contratos e dois artefatos completam o vocabulário:

| nome | papel | onde |
|---|---|---|
| Backplane | contrato de serialização canônica | `canon.canonize` |
| CRDS | registro versionado de regras, o campo `profile` do recibo | `canon.PROFILES` |
| Trim tab | constante declarada do emissor | `receipt.build` |
| Dispersed fringe sensing | medida da divergência entre duas canonizações | `fringe.fringe` |
| Snowball | dano contíguo, pego pela fase fina | `ISTH-FINE-SEAL` |
| Shower | dano distribuído, pego pela cadeia | `ISTH-CHAIN-SHOWER` |

O vocabulário é executável, não decorativo:

```python
>>> import isthmus
>>> isthmus.nomenclature.validate()
{'ok': True, 'fases': 7, 'contratos': 4, 'artefatos': 2, 'faltando': []}
>>> isthmus.coarse_phasing(recibo)      # só a fase grossa
>>> isthmus.fine_phasing(recibo)        # só a fase fina
>>> isthmus.nomenclature.artifact_of("ISTH-CHAIN-SHOWER")
'Shower'
```

`validate()` importa cada alvo: nome sem função por trás reprova. E um teste de
drift confere que toda fase do vocabulário aparece neste README, para documento e
código não se separarem.

Duas ressalvas de fonte, que valem mais que o nome bonito: no JWST o *backplane
não é berílio*, é compósito de grafite, e quem é berílio são os 18 segmentos do
espelho; e *coarse/fine phasing* medem fase óptica, não bytes. A analogia é de
método, não de física.

Detalhamento com teste de aceite por termo: `docs/ISTHMUS_1.2_vocabulario_verificacao_2026-11-17.md`.

## Testado com simulador, não com hardware

A integração já rodada usa Qiskit Aer, simulador local: circuito de Bell, duas
rodadas de 1.024 tiros, p0 de 0,4951 e 0,5020, recibo e cadeia verificando,
adulteração recusada com `ISTH-FINE-SEAL`. Nenhum hardware foi usado.

## Contradição aberta

Alignment Two exige duas rodadas; a regra do projeto diz uma chamada de oráculo por
decisão. `Budget` recebe `oracle_calls` declarado em vez de fingir que é sempre um.
As três saídas possíveis estão em `docs/ISTHMUS_1.4_implementacao_2026-11-17.md`.

## Documentação

- `docs/ISTHMUS_prompt_mestre_2026-11-17.md`: especificação e prompt mestre
- `docs/ISTHMUS_v1.1_ponte_hibrida_2026-11-17.md`: ponte híbrida e maturidade
- `docs/ISTHMUS_1.2_vocabulario_verificacao_2026-11-17.md`: vocabulário e testes de aceite
- `docs/ISTHMUS_1.3_inventario_algoritmos_2026-11-17.md`: inventário e ordem de construção
- `docs/ISTHMUS_1.4_implementacao_2026-11-17.md`: primeira implementação, com medições
- `NAMING.md`: nome canônico, abreviações ISTH e STH
- `docs/ERRATA.md`: correções de nomenclatura, inclusive as que já foram para o histórico
- `CHANGELOG.md`: versões, mudanças e quebras
- `docs/radar/`: material externo lido pela equipe, com fonte e o que não foi verificado

## Licença

Apache-2.0.
