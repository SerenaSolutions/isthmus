# CUDA-Q como segundo lado e Alignment Two medido

## O que foi feito

1. `isthmus/alignment.py`: distância de variação total, tolerância declarada, veredito `1` ou `REFUSED`, e `alinhar_recibos`, que amarra dois recibos pelos selos e não faz chamada nenhuma
2. CUDA-Q 0.17.0 instalado e rodado localmente no alvo `qpp-cpu`, como implementação independente
3. Medição real: CUDA-Q contra QPU `ibm_marrakesh` na mesma entrada, 2048 tiros de cada lado
4. 57 testes passando

## A contradição, resolvida sem redefinir palavra

Alignment Two precisa de dois lados. "Uma chamada de oráculo por decisão" continua valendo: cada lado é uma decisão própria, com recibo próprio, e o alinhamento é um **registro derivado** que só carrega os dois selos. Ninguém faz chamada nova para auditar; quem audita recalcula com os dois recibos na mão. Não foi preciso afrouxar a regra nem tirar o instrumento.

## Medição

| Lado | 00 | 01 | 10 | 11 |
|---|---|---|---|---|
| CUDA-Q qpp-cpu | 1018 | 0 | 0 | 1030 |
| IBM marrakesh | 1019 | 192 | 11 | 826 |

Distância de variação total: **0,0996**.

Com tolerância 0,10 o alinhamento passa, por 0,0004. Com 0,05 ele **recusa**. O mesmo par de dados, duas tolerâncias, duas respostas: a tolerância declarada é parte do veredito, não detalhe.

## Achado de hardware

O erro não é simétrico: 192 eventos em `01` contra 11 em `10`. Ruído direcional, típico de leitura e de acoplamento, e não ruído branco. Modelo que trata os dois como iguais erra a previsão de onde a decisão vai quebrar.

## NVIDIA: o que existe e onde o Isthmus entra

1. *CUDA-Q* é a plataforma aberta da NVIDIA, com Python e C++, compilador `nvq++`, dialeto MLIR próprio, e integração declarada com qualquer QPU. Roda aqui, versão 0.17.0
2. *cuQuantum* acelera simulação de vetor de estado e tensor network em GPU. É o músculo do `Estimator`, não uma linguagem
3. *QIR* é o formato de intercâmbio de baixo nível. O simulador `qbraid:qbraid:sim:qir-sv` já consome QIR, e CUDA-Q compila para QIR/MLIR

Três portas de entrada, da mais barata à mais cara:

1. *OpenQASM 3*: o Isthmus já exporta. CUDA-Q aceita, e a comparação acima foi feita nesse caminho
2. *QIR*: exportar QIR põe o Isthmus em qualquer runtime QIR, incluindo GPU
3. *Alvo próprio do CUDA-Q*: registrar um target que despacha para a camada de decisão. É o que coloca o projeto dentro do ecossistema de verdade, e não apenas como consumidor

Limite honesto: sem GPU neste ambiente, `cuQuantum` não foi medido aqui. E CUDA-Q exige kernel em arquivo `.py`, não aceita kernel definido no interpretador interativo.
