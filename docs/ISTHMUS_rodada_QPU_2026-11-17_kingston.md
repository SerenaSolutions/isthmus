# Rodada em QPU com Isthmus na frente — 17/11/2026

Job `dbu4fts9po4c73cei1b0`, QPU `ibm_kingston`, primitiva `sampler` V2, circuitos transpilados para os portões nativos do alvo, 1024 tiros por circuito.

## Sintaxe que dá o start

1. Submissão: `POST /api/v1/jobs` com `{"program_id": "sampler", "backend": "ibm_kingston", "params": {"version": 2, "pubs": [[qasm, None, 1024], ...]}}`
2. Acompanhamento: `GET /api/v1/jobs/{id}`
3. Resultado: `GET /api/v1/jobs/{id}/results`
4. Isthmus na frente: `decidir_e_selar(contagens, p0, p1, regra="hoeffding")` devolve decisão e recibo selado
5. ZEPHIRUM em paralelo: `decidir(contagens, shots, threshold)` devolve veredito e `receipt_hash`

## Resultado medido

| Circuito | Concordância | Isthmus (faixa) | ZEPHIRUM (limiar) | Recibos |
|---|---|---|---|---|
| Bell, 1 CZ | 95,80% | REFUSED | 1 | os dois verificam |
| GHZ-6, 5 CZ | 93,26% | REFUSED | 1 | os dois verificam |

Alignment Two contra o ideal do CUDA-Q: **TV = 0,0420**, dentro da tolerância declarada de 0,10.

## Por que as duas respostas diferem, e por que nenhuma está errada

ZEPHIRUM faz pergunta unilateral: a taxa está acima do limiar declarado? Com 95,80% e limiar 0,90, sim.

Isthmus trabalha com duas hipóteses e mantém faixa indecidível. Com `p0 = 0,85` e `p1 = 0,95`, o raio de Hoeffding em 1024 tiros é 0,0424: o limite inferior fica em 0,9156, abaixo de `p1`. A taxa pode ser 0,90, então o sistema não afirma que chega a 0,95.

Mesmo dado, instrumentos diferentes, respostas diferentes. O recibo de cada um declara a regra usada, então a divergência é auditável e não ambígua.

## Achado de backend

| Backend | Concordância no Bell |
|---|---|
| ibm_marrakesh (rodada 1) | 92,48% |
| ibm_kingston (rodada 2) | 95,80% |

Três pontos percentuais de diferença entre QPUs do mesmo tamanho. Rodada de calibração não é detalhe: é escolha que muda o veredito quando a taxa está na fronteira.
