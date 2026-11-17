# ERRATA

Correções de nomenclatura. O histórico do git não é reescrito: commit antigo fica
como foi escrito, e a correção entra aqui com data, commit e alcance.

## E-001: IST e STH tratados como sinônimos

**Quando entrou**: commit `5756eb2`, primeira publicação do pacote (17/11/2026).
**O que estava errado**: o README e o `NAMING.md` apresentavam `IST` e `STH` como
duas abreviações equivalentes da mesma linguagem, e os três comandos
(`isthmus`, `ist`, `sth`) faziam exatamente a mesma coisa.
**Correto**: `ISTH` é a abreviação de Isthmus. `STH` é uma **sublinguagem derivada**,
menor por construção, que sela, verifica e encadeia mas não decide.
**Corrigido em**: commit `0527eb1`, com `isthmus/sth.py`, CLI própria e 10 testes.

### O que mudou na prática

| antes | depois |
|---|---|
| `isthmus`, `ist`, `sth` decidiam igual | decidem `isthmus`, `isth` e `ist` |
| `sth decide` funcionava | `sth decide` recusa com `ISTH-STH-NOT-ALLOWED` |
| STH sem semântica própria | STH exige payload já com `verdict`, senão recusa |

### O que continua valendo

O prefixo `ISTH-` nos códigos de recusa não muda, em nenhuma das duas. Recibo
emitido sob `ISTH` continua verificável sob `STH`, e é isso que a derivação
significa: quem só confere não precisa da camada que decide.

### O que não dá para corrigir sem reescrever história

A mensagem do commit `5756eb2` diz "abreviacoes oficiais IST e STH". Reescrever
exigiria force-push e invalidaria o hash citado em qualquer laudo já emitido.
Fica registrado aqui, que é o lugar certo.
