# Naming

| forma | papel | uso |
|---|---|---|
| **Isthmus** | nome de exibição | texto, capa, título de seção |
| `isthmus` | nome canônico | pacote, import, URL do repositório |
| **IST** | abreviação oficial | sufixo de versão, etiqueta, tabela |
| **STH** | abreviação oficial | idem, forma curta de quatro letras |

As duas abreviações são equivalentes e ambas aceitas. `IST` é a que aparece em
documento; `STH` é a que aparece onde o espaço é curto, cabeçalho de tabela e
nome de arquivo.

## Implementadas, não só declaradas

Os três nomes de comando existem e fazem a mesma coisa:

```
isthmus decide --p0 0.9 --shots 512
ist      decide --p0 0.9 --shots 512
sth      decide --p0 0.9 --shots 512
```

E as abreviações são exportadas pelo pacote:

```python
>>> import isthmus
>>> isthmus.ABBREV
('IST', 'STH')
>>> isthmus.abbrev_name()
'IST|STH'
```

## Prefixo dos códigos

Códigos de recusa usam `ISTH-`, que é a raiz comum às duas abreviações: `IST` mais
o `H` que sobrevive em `STH`. Trocar o prefixo quebraria recibos já emitidos, então
ele não muda.
