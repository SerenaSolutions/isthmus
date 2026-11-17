---
title: ISTHMUS 1.3 — inventário de algoritmos
summary: Inventário dos catorze algoritmos em três camadas, com o artefato real de cada um no repositório, estado verificado, teste de aceite e a ordem de construção começando pela Ramp.
---

# ISTHMUS 1.3 — inventário de algoritmos

Correção de nomenclatura aplicada em todo o documento. `isthmus` é pacote e identificador: minúsculo, sem acento, importável. *Isthmus* é o nome de exibição, e só isso.

*Estímulos* entra no registro como erro de transcrição de áudio, não como decisão de projeto. Nenhuma seção deste documento usa a palavra.

17/11/2026 · Serena Solutions

---

## 1. As três camadas

| Camada | O que decide | O que não faz |
|---|---|---|
| Clássico puro | bytes, forma, tempo de leitura | não toca hardware |
| Híbrido | amostragem, orçamento, transporte | não julga veredito |
| Ponta quântica | prepara, evolui, mede, caracteriza | não interpreta resultado |

A regra da passagem continua valendo: nenhuma camada lê o resultado da outra e reescreve a própria declaração. O que entra é declarado antes.

---

## 2. Camada clássica pura

### Canonize

*Faz*: aplica o perfil de canonização e devolve os bytes canônicos mais o identificador do perfil.

*No repositório*: `src/zqea_canon.py`. Existe.

*Teste*: mesmo payload sob `profile canon-v1` gera bytes idênticos em duas execuções; perfil desconhecido recusa com `ISTH-PROFILE`.

### Fringe

*Faz*: compara duas canonizações e reporta onde divergem, posição e tipo. É o dispersed fringe sensing aplicado a bytes.

*No repositório*: não existe. `fringe` retorna zero arquivo.

*Teste*: para o par (`\b`, `\u0008`) reporta divergência na posição do escape e o tipo `control-escape`; para entradas idênticas reporta `no-drift`.

### Shutter

*Faz*: decide o que não entra. Portão de admissão de campo, que recusa chave, tipo ou tamanho fora do contrato antes de qualquer selo.

*No repositório*: não existe.

*Teste*: recibo com campo não declarado é barrado antes do selo, com `ISTH-SHUTTER`; recibo válido passa sem custo mensurável.

### Ramp

*Faz*: aquisição não destrutiva de contagens em rampa. Lê a série de amostras e ajusta a reta, em vez de esperar o valor final.

*No repositório*: não existe, e é a primeira a construir.

*Teste*: mesma série de amostras produz a mesma contagem corrigida e a mesma inclinação; série com queda abrupta no meio é marcada com `ISTH-RAMP-BREAK` em vez de aceita.

### Refase

*Faz*: corrige a fase entre duas medições do mesmo estado antes de comparar.

*No repositório*: não existe.

*Teste*: duas medições do mesmo estado com fase relativa deslocada convergem após refase; deslocamento maior que a banda declarada resulta em `REFUSED`.

---

## 3. Camada híbrida

### Sampler

*Faz*: coleta contagens de um backend declarado, com `shots` fixado antes.

*No repositório*: usado pelos adaptadores, `src/qroute/hardware.py` e `src/zyql_auditkit.py`. Existe como consumo, não como componente próprio.

*Teste*: `shots` do recibo igual ao `shots` do job; divergência recusa com `ISTH-SHOTS`.

### Estimator, com Alignment Two

*Faz*: estima valor esperado com duas rodadas de alinhamento, a primeira para a estrutura e a segunda em campo múltiplo.

*No repositório*: `estimator` aparece só em documentação de cronograma.

*Teste*: estimativa com uma rodada e com duas diferem apenas dentro da banda declarada; se a diferença exceder a banda, o resultado é `REFUSED`, nunca média silenciosa.

### Mitigation audit

*Faz*: registra qual mitigação foi aplicada, com que parâmetros, e qual seria o resultado sem ela.

*No repositório*: `src/zyql_zne.py`. Existe, como ZNE.

*Teste*: recibo carrega o método e os fatores; recibo sem campo de mitigação quando houve mitigação recusa com `ISTH-MITIG-UNDECLARED`.

### Budget

*Faz*: contabiliza tiros e chamadas gastos, e recusa antes de estourar o declarado.

*No repositório*: `src/qroute/core.py` e `src/qroute/cli.py`. Existe.

*Teste*: orçamento estourado no meio recusa com `ISTH-BUDGET` e emite recibo de recusa, não recibo parcial.

### Transpile audit

*Faz*: registra a transformação do circuito até o dialeto do backend, e verifica round-trip.

*No repositório*: `src/oq3.py` e `src/qroute/core.py`, com OpenQASM 3 em ida e volta. Existe.

*Teste*: circuito que sobrevive ao round-trip tem a mesma profundidade declarada; qualquer perda recusa com `ISTH-TRANSPILE-LOSS`.

---

## 4. Ponta quântica

### Prepare, Evolve, Measure, Reset, Flow

*Fazem*: as cinco operações de ciclo: preparar o estado, evoluir, medir, reinicializar e encadear a sequência. `qif` entra aqui como ramo sem colapso.

*No repositório*: `evolve` e `measure` existem dispersos em `src/qroute/graph.py`, `src/oq3.py` e `src/qroute/hardware.py`; `prepare` e `reset` só em documentação. Não há componente único.

*Teste*: um Flow de quatro passos (Prepare, Evolve, Measure, Reset) produz recibo único com as quatro etapas declaradas; Reset sem Prepare seguinte recusa com `ISTH-FLOW`.

### Characterize

*Faz*: mede o dispositivo antes da decisão: taxas de erro, coerência, ruído de leitura.

*No repositório*: não existe.

*Teste*: caracterização declara os parâmetros medidos com data e backend; decisão que usa banda menor que a caracterização recusa com `ISTH-BAND-OPTIMISM`, que é nome feio para um erro feio: banda mais estreita que o ruído medido.

---

## 5. Estado verificado, sem enfeite

| Algoritmo | Artefato | Estado |
|---|---|---|
| Canonize | `src/zqea_canon.py` | implementado, sem teste de perfil |
| Sampler | `src/qroute/hardware.py` | implementado como consumo |
| Mitigation audit | `src/zyql_zne.py` | implementado como ZNE |
| Budget | `src/qroute/core.py` | implementado |
| Transpile audit | `src/oq3.py` | implementado com round-trip |
| Prepare/Evolve/Measure/Reset/Flow | dispersos | parcial |
| Estimator + Alignment Two | só documentação | planejado |
| Fringe | ausente | planejado |
| Shutter | ausente | planejado |
| Ramp | ausente | planejado, primeiro da fila |
| Refase | ausente | planejado |
| Characterize | ausente | planejado |

---

## 6. Ordem de construção, começando pela Ramp

1. *Ramp*. Sem aquisição não destrutiva correta, todo número acima é leitura de valor final, e a banda de erro não tem base
2. *Shutter*. Barato, e impede que os seguintes recebam lixo
3. *Canonize com perfil declarado*. Fecha o buraco do `profile` e faz a CRDS existir de fato
4. *Fringe*. Só faz sentido depois de haver dois perfis para comparar
5. *Refase*. Corrige fase entre medições, sem a qual Sampler compara coisas diferentes
6. *Sampler e Estimator com Alignment Two*. Primeiro o consumo com `shots` auditado, depois o estimador com duas rodadas
7. *Characterize*. Antes de qualquer decisão que use banda estreita
8. *Budget e Transpile audit*. Já existem; entram na ordem para ganhar teste de aceite, não código
9. *Prepare/Evolve/Measure/Reset/Flow*. Unificar o que hoje está disperso

A ordem tem uma lógica só: cada passo entrega o instrumento que o seguinte usa para provar que funciona.

---

## 7. O que este documento não afirma

Não afirma que os implementados passam nos testes de aceite: os testes estão escritos aqui pela primeira vez. Não afirma que os planejados têm código. E não mede tempo de nada, porque ainda não há o que medir.
