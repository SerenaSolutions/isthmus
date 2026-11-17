# Naming

| forma | papel | uso |
|---|---|---|
| **Isthmus** | nome de exibição | texto, capa, titulo de secao |
| `isthmus` | nome canonico | pacote, import, URL do repositorio |
| **ISTH** | abreviacao oficial de Isthmus | etiqueta, tabela, versao |
| **STH** | sublinguagem **derivada** | quem so sela, verifica e encadeia |

## ISTH

Abreviacao oficial. Tres comandos equivalentes, todos decidem:

```
isthmus decide --p0 0.9 --shots 512
isth    decide --p0 0.9 --shots 512
ist     decide --p0 0.9 --shots 512
```

```python
>>> import isthmus
>>> isthmus.ABBREV
('ISTH',)
```

## STH, a derivada

STH nao e apelido de Isthmus. E uma sublinguagem menor, derivada de ISTH, restrita
a transportar e conferir: sela payload ja decidido, verifica recibo, verifica
cadeia. Nao decide.

```
sth seal   payload.json    # exige campo verdict
sth verify recibo.json
sth chain  r1.json r2.json r3.json
sth decide                 # recusa com ISTH-STH-NOT-ALLOWED
```

A derivacao e por subtracao: STH nao tem Ramp, Shutter, Estimator, banda nem
oraculo. Quem precisa de qualquer um deles usa ISTH.

```python
>>> from isthmus import sth
>>> sth.NAME, sth.DERIVED_FROM
('STH', 'ISTH')
```

## Prefixo dos codigos

`ISTH-`, a raiz de `ISTH` e de `STH`. Trocar o prefixo quebraria recibo ja
emitido, entao ele nao muda.
