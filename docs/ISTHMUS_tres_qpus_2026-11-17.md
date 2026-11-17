# Três QPUs, mesmo circuito, mesma regra

Critério de lançamento: mínimo três QPUs distintos. Cumprido.

| Backend | Bell, 1 CZ | GHZ-6, 5 CZ | Veredito Isthmus |
|---|---|---|---|
| ibm_marrakesh | 92,48% | 78,91% | REFUSED nos dois |
| ibm_kingston | 95,80% | 93,26% | REFUSED nos dois |
| ibm_fez | 94,43% | 84,77% | REFUSED nos dois |

1024 tiros por circuito, hipóteses declaradas antes: Bell com p0 = 0,85 e p1 = 0,95; GHZ-6 com p0 = 0,70 e p1 = 0,90. Todos os recibos verificam.

## O que os três juntos mostram

1. A dispersão entre QPUs do mesmo tamanho é grande: 92,48% a 95,80% no Bell, e 78,91% a 93,26% no GHZ-6. Escolher backend muda o resultado mais do que muita otimização de circuito
2. A faixa indecidível fez o trabalho dela: com a taxa entre as hipóteses, nenhum dos seis casos virou afirmação. Não houve veredito heroico
3. GHZ-6 é o circuito sensível: 5 CZ acumulam erro, e a diferença entre o melhor e o pior backend chega a 14 pontos percentuais
