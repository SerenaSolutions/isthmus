# Ramp sequencial — implementação e primeira medição em QPU real

## O que foi implementado

`isthmus.ramp` ganhou a parte sequencial, que é a razão de a Ramp vir primeiro: parar quando a decisão fecha, em vez de gastar 4096 tiros fixos.

1. `llr_bernoulli` e `limites_sprt`: teste sequencial de Wald para duas hipóteses simples
2. `raio_hoeffding`: sequência de confiança para variável em [0,1]
3. `decidir_sequencial`: consome observações e para no primeiro cruzamento, devolvendo 1, 0 ou REFUSED
4. `decidir_dos_counts`: decide a partir de contagens agregadas e devolve a faixa de parada, mínima e máxima, porque ordem de chegada muda o ponto de parada e não muda o veredito

## As duas regras não são equivalentes, e isso importa

O SPRT compara `p ≤ p0` com `p ≥ p1`. Quando a taxa real cai **entre** as duas hipóteses, a caminhada aleatória acaba cruzando uma fronteira e o teste escolhe um lado por construção. O veredito `0` ali significa "p0 é mais verossímil que p1", **não** "p ≤ p0". Ler como a segunda coisa produz afirmação falsa.

A sequência de confiança mantém uma faixa indecidível entre `p0` e `p1`. É a única das duas que sustenta o terceiro valor por mérito, e não por falta de tiros.

## Medição em hardware real

Job `dbu3i2c9po4c73cegl3g`, QPU `ibm_marrakesh`, Bell com 1 CZ, 2048 tiros, sampler V2.

| Regra | Taxa observada | Veredito | Leitura correta do veredito |
|---|---|---|---|
| sprt | 0,9009 | 0 | "p=0,85 mais verossímil que p=0,95" — **não** "p ≤ 0,85", que seria falso |
| hoeffding | 0,9009 | REFUSED | a taxa cai na faixa entre 0,85 e 0,95, e o sistema não afirma nada |

Hipóteses declaradas: `p0 = 0,85`, `p1 = 0,95`, `alpha = beta = 0,05`.

## Achado que mudou o código

A primeira versão de `decidir_dos_counts` aceitava o parâmetro `regra` e devolvia o veredito do LLR de qualquer jeito, ou seja, `hoeffding` e `sprt` davam o mesmo resultado. O bug escondia exatamente o caso perigoso, em que as duas regras discordam. Corrigido, com teste de regressão que exige vereditos diferentes nesse cenário.

## Recomendação

1. Veredito trivalente usa `hoeffding` por padrão. O recibo declara a regra usada, porque regra diferente é resposta diferente
2. SPRT fica disponível para decisão binária, com o significado do `0` declarado no recibo, nunca apresentado como limite de `p`
3. A economia contra 4096 tiros é medida na parada, não no orçamento: a faixa de parada aparece no recibo
