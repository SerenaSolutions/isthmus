---
title: ISTHMUS 1.4 — primeira implementação executável
summary: O pacote isthmus v0.1.0 rodando, com 32 testes de aceite passando, os 17 códigos de recusa exercitados, as correções da auditoria aplicadas e uma contradição que só a dona do projeto pode resolver.
---

# ISTHMUS 1.4 — primeira implementação executável

Deixa de ser especificação. `isthmus` v0.1.0 existe, roda, e tem teste para cada algoritmo do inventário.

17/11/2026 · Serena Solutions

---

## 1. O que passou a existir

Oito módulos na camada clássica, cinco no híbrido, dois na ponta quântica, mais recibo e CLI. Zero dependência externa: só stdlib, para que qualquer auditor rode sem instalar nada.

| Módulo | Algoritmo | Ordem de construção |
|---|---|---|
| `ramp.py` | Ramp | 1º |
| `shutter.py` | Shutter | 2º |
| `canon.py` | Canonize, com perfil `canon-v1` e `canon-u0008` | 3º |
| `fringe.py` | Fringe | 4º |
| `refase.py` | Refase | 5º |
| `sampler.py` | Sampler | 6º |
| `estimator.py` | Estimator + Alignment Two | 6º |
| `characterize.py` | Characterize | 7º |
| `budget.py` | Budget de tiros e chamadas | 8º |
| `transpile.py` | Transpile audit | 8º |
| `quantum.py` | Prepare/Evolve/Measure/Reset/Flow | 9º |
| `mitigation.py` | Mitigation audit | — |
| `receipt.py` | recibo, fase grossa, fase fina, cadeia | — |
| `cli.py` | `decide` e `verify` | — |

---

## 2. Medição

[DADO] Ambiente: container do workspace, Python 3.11, sem dependências externas, 17/11/2026.

```
Ran 32 tests in 0.002s
OK
```

1. *32 testes, 32 passando*, 0,002 s no total, cerca de 0,06 ms por teste
2. *17 de 17 códigos do catálogo exercitados*: cada erro tem teste que provoca o erro
3. *633 linhas* entre módulos e testes
4. *Zero dependência*: `import isthmus` não puxa nada de terceiros

O número que importa não é a velocidade, é o segundo: *nenhum código de recusa existe só no papel*. Cada um tem uma entrada que o provoca e uma asserção que confere.

---

## 3. O que a auditoria obrigou a corrigir

O parecer independente reprovou a especificação em cinco pontos. Todos entraram no código:

1. *Códigos ISTH-\* agora existem de verdade*. Eram vocabulário proposto; viraram `errors.py` com catálogo fechado, e código fora do catálogo levanta erro na hora de construir a recusa
2. *Budget passou a ser de tiros e chamadas*, não de dinheiro. O `budget` do qroute mede outra coisa e o nome estava sendo emprestado indevidamente
3. *A fase grossa vem antes da fina e falha primeiro*, testada com esquema `9.9` e gramática `9.9` separadamente. É o coarse phasing que faltava
4. *A cadeia tem teste próprio*: reclinar um elo e re-selar o meio faz cada recibo passar sozinho, e só `verify_chain` pega. Esse é o shower, e agora existe um teste que prova a diferença
5. *O perfil vai declarado no recibo*, e dois perfis de escape produzem selos diferentes para o mesmo payload, com o Fringe apontando o índice e a natureza da divergência

---

## 4. Contradição aberta, e não sou eu que resolvo

*Alignment Two exige duas rodadas. "Uma chamada de oráculo por decisão" proíbe a segunda.*

O auditor achou a contradição no próprio teste do projeto. Não escondi: `Budget` recebe `oracle_calls` declarado, e o padrão é 1. Mas o estimador com duas rodadas precisa de 2, e aí uma das três coisas é verdade:

1. Alignment Two são *duas decisões* e dois recibos, encadeados. Coerente com a regra, mais caro
2. A regra passa a ser "chamadas declaradas antes", e não "uma chamada". Mais honesto, menos vendável
3. Alignment Two não pertence ao Isthmus

[OPINIÃO] A segunda opção é a única que sobrevive a auditoria externa, porque a primeira é uma redefinição de palavra e a terceira joga fora o melhor instrumento de estimativa. Mas a decisão é sua, e enquanto não for tomada o código declara o número em vez de fingir que é sempre um.

---

## 5. O que não está feito, e não vou dizer que está

1. Nenhum adaptador real foi conectado: não há chamada a QPU ou simulador externo, então *interoperabilidade híbrida continua planejada*
2. Não há teste de integração com Qiskit, pela mesma razão
3. Não foi publicado no PyPI: `isthmus` existe como pasta, não como pacote instalável
4. `Characterize` mede o que recebe, não conversa com backend nenhum
5. A segunda porta do verificador de recibos do Zephirum continua sendo trabalho separado

A tabela de maturidade de Isthmus fica assim: clássico puro *implementado e testado*, híbrido *implementado no papel de contrato*, ponta quântica *implementada como fluxo local*, ponte com backend *planejada*.

---

## 6. Como verificar em trinta segundos

```
unzip isthmus_v0.1.0.zip && cd isthmus_dev
python3 -m unittest discover -s tests -v    # 32 testes
python3 -m isthmus decide --p0 0.9 --shots 512 > r.json
python3 -m isthmus verify r.json            # {"state":"ok","stage":"fine"}
```

Alterar `verdict` no `r.json` e repetir o último comando devolve `ISTH-FINE-SEAL`.
