# ISTHMUS

Sub-linguagem híbrida de interoperabilidade, controle e verificação do ecossistema
ZEPHIRUM/ZYQL. Abreviação oficial: **ISTH**. Derivada: **STH**.

Quatorze algoritmos em três camadas, um recibo com duas etapas de verificação,
zero dependência externa.

## Instalar

```bash
pip install -e .
```

## Rodar em trinta segundos

```bash
python3 -m unittest discover -s tests -v      # 32 testes
isthmus decide --p0 0.9 --shots 512 > r.json
isthmus verify r.json                          # {"state":"ok","stage":"fine"}
```

`isthmus`, `isth` e `ist` são equivalentes e decidem. `sth` é a derivada que só sela, verifica e encadeia.

Alterar `verdict` no `r.json` e repetir a verificação devolve
`{"state":"refused","code":"ISTH-FINE-SEAL"}` com saída de código 1.

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
- `NAMING.md`: nome canônico, abreviação ISTH e a derivada STH
- `docs/ERRATA.md`: correções de nomenclatura, inclusive as que já foram para o histórico

## Licença

Apache-2.0.
