# Fuzz: 40 mil casos, dois defeitos reais encontrados

Cada família rodou 10 mil casos, semente fixa 20261117, reprodutível.

1. *Canonize*: mesma entrada com ordem de chave trocada, com ida e volta por JSON, e perfil inexistente
2. *Ramp*: hipóteses sorteadas, tiros sorteados, veredito conferido contra a regra de Hoeffding calculada à parte
3. *Alignment*: distância em [0,1], simetria e identidade
4. *Recibo*: adulteração de um campo sorteado, exigindo recusa declarada

## Defeito 1: perfil não textual estourava exceção crua

Adulterar o campo `profile` de um recibo com dicionário ou lista produzia `TypeError`, porque `profile not in PROFILES` exige hash. O auditor recebia stack trace em vez de `ISTH-PROFILE`.

Corrigido em `canon.py` com verificação de tipo antes da consulta ao catálogo de perfis.

## Defeito 2: distância de variação total passava de 1

Uma em 10 mil distribuições devolveu `1.0000000000000002`. Soma de ponto flutuante estoura por um ULP, e distância acima de 1 não existe. Numa comparação de fronteira, isso muda o veredito.

Corrigido com saturação em [0, 1], e teste de regressão com 2 mil distribuições sorteadas exige o intervalo fechado.

## Depois das correções

40 mil casos, nenhum contraexemplo. Suíte de unidade em 77 testes, todos passando.

## Como repetir

```
python tools/fuzz_isthmus.py
```
