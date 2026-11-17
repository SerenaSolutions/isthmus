---
title: ISTHMUS 1.2 — vocabulário de verificação
summary: Adendo à especificação com os seis termos do vocabulário de engenharia do Webb, cada um preso a um teste de aceite, mais o registro versionado de regras de canonização e três correções verificadas na fonte.
---

# ISTHMUS 1.2 — vocabulário de verificação

Adendo à especificação. Seis nomes vindos da engenharia do telescópio Webb, cada um convertido em peça verificável do verificador. Com as correções que a fonte primária exigiu.

17/11/2026 · Serena Solutions

---

## 1. Antes dos nomes: três correções

*Correção 1, material.* O backplane do Webb *não é berílio*. Os 18 segmentos do espelho são berílio banhado a ouro; a estrutura que os sustenta é composta de grafite, como a documentação do STScI descreve. [FONTE] A frase boa continua valendo ("não é o espelho, é o que impede o espelho de mentir"), só o material muda.

*Correção 2, o Rust não existe.* Procurei no repositório: não há verificador em Rust. O que existe é `cpp/zyql_verdict.cpp`, com 22 linhas, sem `schema`, sem `payload`, sem `sha3`. É esboço de núcleo de veredito, não verificador.

*Correção 3, e é a que muda o diagnóstico.* O `esquema=9.9` *não* passaria no Python: `tools/zyql_verificar_recibo.py` já confere em duas etapas, linha 35 exige `schema == "1.0.0"` e linha 37 exige `gramatica == "1.5.0"`. Ou seja, a fase grossa existe. O defeito real é outro, e é pior: *existe uma implementação só*. Não há segunda porta para discordar da primeira, então "acordo entre implementações" é hoje uma afirmação sem teste.

[OPINIÃO] Isso não desmonta o seu mapeamento, fortalece. Coarse e fine phasing continuam sendo os dois nomes certos para as duas etapas; o que muda é que a urgência não é escrever a etapa grossa, é escrever a segunda porta.

---

## 2. Os seis nomes, com teste de aceite

### Backplane — o contrato de serialização

*No Webb*: a estrutura estável onde os segmentos são montados, medida em escala micrométrica, que impede o espelho de deformar.

*No Zephirum*: o contrato que define bytes canônicos. Não é o payload, é o que garante que o payload não deforme ao atravessar linguagem.

*Teste*: mesmo payload lógico, duas implementações independentes, mesmos bytes. Falha hoje, porque só há uma implementação.

### Coarse phasing e fine phasing — as duas etapas do verificador

*No Webb*: primeiro se acerta a estrutura, depois a fase fina. Nenhuma das duas basta sozinha.

*No Zephirum*: coarse confere esquema, versão de gramática e conjunto de campos obrigatórios; fine confere byte a byte contra o selo.

*Teste*: recibo com `schema 9.9` deve falhar em coarse com código `V-COARSE-SCHEMA`, sem nunca chegar ao fine. Recibo íntegro passa nas duas. Recibo com campo faltando falha em coarse. Recibo com um byte trocado passa em coarse e falha em fine.

### Dispersed fringe sensing — o diff entre duas canonizações

*No Webb*: mede o erro de pistão dos 18 segmentos dispersando franjas, em vez de comparar posições.

*No Zephirum*: não compara texto, calcula a diferença entre duas canonizações e aponta onde divergem. É o instrumento que mostra `\b` virando `\u0008`.

*Teste*: para o mesmo payload, produzir o par (implementação A, implementação B) e reportar posição e tipo da divergência. Sem esse relatório, "as duas concordam" é palpite.

### CRDS — o registro versionado de regras

*No Webb*: sistema de dados de referência calibrada, que diz qual verdade vale para qual dado, versionado.

*No Zephirum*: registro das regras de canonização, versionado, e o recibo declara qual versão aplicou. É o campo que falta para o veredito ser auditável depois, quando as regras mudarem.

*Teste*: um recibo emitido sob `profile v1` continua verificável depois que `v2` entra em vigor, e o verificador informa `verificado sob perfil v1, atual v2`. Recibo sem `profile` é tratado como perfil legado, e o verificador avisa.

### Trim tab — a constante declarada do emissor

*No Webb*: aba passiva que absorve o empuxo da luz solar, em vez de gastar combustível corrigindo.

*No Zephirum*: constante pública e declarada do emissor que absorve a não-determinação conhecida, sem custar correção ativa. Declarada, nunca inferida.

*Teste*: recibo traz a constante e a declara; verificador rejeita constante não declarada com `V-TRIM-UNDECLARED`.

### Snowball e shower — os dois artefatos hostis

*No Webb*: dois artefatos de raio cósmico no MIRI, catalogados por nome. Um atinge um bloco compacto, o outro deixa rastro vertical de carga.

*No Zephirum*: as duas classes de corrupção de recibo. *Snowball*: dano contíguo, um campo ou bloco. *Shower*: dano distribuído ao longo da cadeia, que só aparece quando se verifica o encadeamento inteiro.

*Teste*: snowball é pego pelo fine phasing de um recibo; shower só é pego por `verify_chain`. Um verificador que só faz fine em recibo isolado não detecta shower, e é por isso que a cadeia precisa ser verificável como cadeia.

---

## 3. O que entra no recibo

Três campos novos, todos declarados, nenhum inferido:

```
profile    "canon-v1"        ; versao das regras de canonizacao aplicadas
coarse     {schema, gramatica, campos_obrigatorios: ok}
trim       {constante, declarada_por}
```

`coarse` registra o resultado da fase grossa *dentro* do recibo, para que um auditor saiba que ela rodou, e não apenas que o selo confere.

---

## 4. Ordem de execução, e por que ela importa

1. Coarse: esquema, gramática, campos. Barato, falha cedo, mensagem clara
2. Fine: bytes contra selo. Caro, falha tarde, mensagem específica
3. Perfil: qual CRDS valeu na emissão
4. Cadeia: shower só aparece aqui
5. Veredito: `1`, `0` ou `REFUSED` com motivo declarado

Inverter 3 e 1 permite que um recibo antigo pareça inválido por causa de regra nova. É o erro que a CRDS existe para evitar.

---

## 5. O que este adendo não faz

Não implementa nada, e não afirma que algo funciona. Cada seção tem teste de aceite porque o estado atual é: uma implementação, sem segunda porta, com três campos declarados ausentes. Depois dos testes, o documento muda de tempo verbal.
