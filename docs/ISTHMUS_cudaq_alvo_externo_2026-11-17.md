# Alvo externo do CUDA-Q: o caminho difícil e aceitável

## A escolha

O caminho fácil seria copiar um alvo para dentro do repositório da NVIDIA, ou pendurar um patch que só funciona no nosso clone. Isso atravessa muro alheio: o repositório deles tem processo, licença e marca. O caminho aceitável é o que eles próprios declararam na issue 4619, "Enable External Backend Integration": um pacote externo anuncia o alvo, entrega a configuração e entrega o runtime, sem copiar ativo para dentro da instalação do CUDA-Q.

`isthmus/cudaq_alvo.py` faz exatamente isso, no nosso repositório, com Apache-2.0 e sem tocar em código de terceiro.

## O que o pacote declara

1. *Alvo anunciado*: `isthmus-decide`, tipo `gate`, não simulador
2. *Configuração*: qubits qualquer, portões `H`, `X`, `CNOT`, medição terminal, 1024 tiros padrão
3. *Runtime*: `isthmus.cudaq_alvo:AlvoIsthmus`, com `configuracao()` e `executar()`

## O que o alvo é, e o que ele não é

É um portão de decisão. Recebe a entrada, decide com a Ramp, emite recibo selado e deixa passar só o que a decisão autorizou.

Não é uma QPU. Não despacha para hardware real ainda. Quem executa hoje é o alvo `qpp-cpu` do CUDA-Q, e o teste de execução real roda de verdade, com 256 tiros, gerando recibo que verifica.

## Limites declarados

1. O adaptador é Python. Construir a extensão C++ `quantum_platform` exigiria compilar a biblioteca do CUDA-Q, que não é o caso deste ambiente
2. Nenhum PR foi aberto no repositório da NVIDIA. Quando for, segue o guia de contribuição deles, e isso é decisão separada
3. Marca: dizer "integra com CUDA-Q" é fato. Dizer que a NVIDIA endossa não é, e não faremos

## Verificação

63 testes passando no total, sendo 6 deste módulo, um deles executando CUDA-Q de verdade.
