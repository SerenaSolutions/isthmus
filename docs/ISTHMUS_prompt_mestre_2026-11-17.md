---
title: ISTHMUS — prompt mestre da sublinguagem de Zephirum
summary: Especificação da sublinguagem Isthmus derivada da gramática real do ZYQL v2 e do contrato da API C, com prompt pronto para o outro agente e 12 testes de aceitação.
---

# ISTHMUS

**Sub-linguagem de Zephirum para travessia entre contagem e veredito.**
Documento de especificação e prompt mestre. Versão 1.0, 17/11/2026.
Autoria: Ravi dos Anjos · Serena Solutions.

---

## 1. Por que esse nome, e por que ele é bom

*Isthmus* é a faixa estreita de terra que liga duas massas maiores. Em Zephirum, as duas massas são a máquina quântica, de um lado, e o veredito selado, do outro. Isthmus é a única passagem autorizada entre as duas, e passagem estreita por construção: o que não couber nela não atravessa.

Isso resolve um problema de projeto, não de estilo. Hoje o ZYQL v2 aceita formas arbitrárias, e o Zephyron v1.4.3 aceita circuitos inteiros. Uma pessoa pode escrever qualquer coisa e chamar de decisão. Isthmus inverte a lógica: o programa **só** existe para atravessar, e o compilador recusa o que não atravessa.

---

## 2. O que este documento herda do livro

1. *Cinco termos canônicos* do léxico decidido: Teletransportador (protocolo), Katra (não-clonagem), IDIC (espaço de estados), Defletor (banda de erro declarada), Tradutor universal (transpilador)
2. *O princípio que fica*: recibo que só o emissor confere não é recibo, é corrente
3. *A medição do defeito de forma canônica*: o mesmo payload serializado como `\b` e como `\u0008` gera hashes diferentes, `d596f6381c2dbaa2` contra `6bc64e1a412adce4`. Python e Node concordam entre si, então a divergência nasce de escape feito à mão numa porta
4. *A taxonomia de evidência* aplicada a cada afirmação: [DADO] verificado em fonte primária, [FONTE] terceiro nomeado, [INFERÊNCIA] dedução, [OPINIÃO] juízo, [DESCONHECIDO] não apurado

---

## 3. O que existe hoje, verificado no repositório

[DADO] Gramática formal em `docs/grammar/zyql.ebnf`, derivada de `src/zyql_lisp.py`, sintaxe Lisp, arquivos `.zph`:

```
program      = { form } ;
form         = atom | list ;
list         = "(", { form }, ")" ;
atom         = symbol | number | string | boolean | decision ;
decision     = "1" | "0" | "REFUSED" ;
define       = "(", "define", symbol, form, ")" ;
decision-form= "(", "decide", { clause }, ")" ;
clause       = condition | otherwise ;
condition    = "(", "if", form, form, ")" ;
otherwise    = "(", "otherwise", form, ")" ;
receipt-form = "(", "emit", "receipt", { field }, ")" ;
field        = symbol, form ;
comment      = ";;", { any-char - newline } ;
```

[DADO] Front-end Zephyron v1.4.3 em `docs/language.md`: blocos `circuit NAME { }`, `qubit[N] q;`, `zyqbit` com cópia proibida por tipo (não-clonagem), `qif`, portas H, X, Y, Z, S, T, RX, RY, RZ, CNOT, CZ, SWAP, TOFFOLI, `zyql_rag "pergunta";`, e round-trip OpenQASM 3 por `src/oq3.py`.

[DADO] Contrato da API C em `src/zephirum.h`: uma chamada de oráculo por decisão, banda de ruído declarada, recibo racional canônico (num/den) selado com SHA3-256, assinatura ML-DSA-44 como camada opcional de roadmap.

[Opinião] Isthmus nasce como *subconjunto estrito* do ZYQL v2 que compila 1:1 para esse contrato C. Não é linguagem nova, é fronteira nova.

---

## 4. As sete leis de Isthmus

1. *Banda antes de execução.* Nenhum `decide` sem `band` declarada antes do `oracle`. Sem Defletor, não há veredito
2. *Trivalência irredutível.* `0` e `REFUSED` nunca colapsam. Ausência de evidência não é reprovação
3. *Um oráculo por decisão.* Exatamente uma chamada por `decide`, sem laço, sem adaptação depois de observar
4. *Katra.* Nenhum estado quântico é copiado, porque não há primitiva de cópia
5. *Recibo canônico.* Serialização por RFC 8785, números racionais, selo SHA3-256 sobre os bytes canônicos
6. *Emissor identificado.* Todo recibo carrega `emissor` e fingerprint de chave. Chave sozinha não prova nada: o verificador precisa da lista de chaves confiáveis
7. *Estreiteza verificada.* O compilador rejeita qualquer forma fora do conjunto abaixo. Erro de sintaxe em Isthmus é recusa, não exceção

---

## 5. Gramática formal de Isthmus

Extensão da EBNF do ZYQL v2, subconjunto estrito mais três formas novas.

```
(* ISTHMUS 1.0 — subconjunto estrito de ZYQL v2 · Apache-2.0 *)
(* Arquivo .isth · compila para o contrato C de src/zephirum.h *)

isthmus-program = "(", "isthmus", symbol, { decl }, decide-form, receipt-form, ")" ;
decl            = band | oracle | shots | deny ;
band            = "(", "band", number, ")" ;            (* epsilon declarado ANTES de executar *)
oracle          = "(", "oracle", symbol, ")" ;          (* backend: qiskit, qbraid, sim, emulador *)
shots           = "(", "shots", integer, ")" ;          (* tiros declarados, nunca adaptados *)
deny            = "(", "deny", symbol, ")" ;            (* motivos de recusa permitidos neste programa *)

decide-form     = "(", "decide", { clause }, ")" ;
clause          = condition | otherwise ;
condition       = "(", "if", predicate, decision, ")" ;
otherwise       = "(", "otherwise", decision, ")" ;
predicate       = "(", "p0", comparison, number, ")" | "(", "within", number, ")" ;
comparison      = "<=" | ">=" | "<" | ">" | "=" ;

receipt-form    = "(", "emit", "receipt", { field }, ")" ;
field           = fmt | issuer | reason ;
fmt             = "(", "canonical", symbol, ")" ;       (* sempre "rfc8785" *)
issuer          = "(", "issuer", symbol, string, ")" ;  (* nome e fingerprint *)
reason          = "(", "on-refused", symbol, ")" ;      (* motivo declarado para REFUSED *)

decision        = "1" | "0" | "REFUSED" ;
symbol          = letter, { letter | digit | "-" | "_" } ;
integer         = digit, { digit } ;
number          = [ "-" ], digit, { digit }, [ ".", digit, { digit } ] ;
string          = '"', { any-char - '"' }, '"' ;
comment         = ";;", { any-char - newline } ;
```

Removido em relação ao ZYQL v2, por decisão: `define`, formas arbitrárias em `list`, booleanos, portas, laços, aritmética livre e qualquer `atom` que não esteja listado. Em Isthmus não existe `define`; se a travessia precisa de abstração, ela pertence ao nível de cima.

---

## 6. Semântica, em regras executáveis

1. Ordem obrigatória: `band` → `oracle` → `shots` → `deny` → `decide` → `emit receipt`. Fora dessa ordem, recusa de compilação com código `ISTH-ORDER`
2. `band` ausente: recusa `ISTH-NOBAND`, nunca decisão com banda implícita
3. `within ε` avalia a banda de erro da estimativa; se `ε` exceder a banda declarada, o veredito é `REFUSED` com motivo `BAND-EXCEEDED`
4. `p0 <= t` e `p0 >= t` produzem `1` ou `0`; qualquer outra situação cai em `otherwise`, e `otherwise` sem `REFUSED` explícito é erro de compilação `ISTH-FORCED`, porque obrigar veredito binário é a fraude que o projeto combate
5. Cada `deny` autoriza um motivo de recusa. Recusa com motivo não declarado é erro `ISTH-UNDECLARED`
6. Recibo: `canonical rfc8785`, `issuer NOME FINGERPRINT`, `on-refused MOTIVO`. Sem `issuer`, o recibo é inválido mesmo que o selo confira
7. Determinismo: mesmo programa, mesmo backend, mesma semente → mesmos bytes de recibo

---

## 7. Pré-requisitos técnicos, com os defeitos atuais

Estes três precisam ser corrigidos antes de Isthmus ser publicável.

1. *Forma canônica não fixada.* [DADO] `\b` e `\u0008` geram hashes distintos para o mesmo payload. Correção: RFC 8785 mais vetores em `tests/vectors/canonical/`, rodando em Python, Rust e JS no CI
2. *Formatos de recibo incompatíveis.* [DADO] O verificador do repositório exige `payload["recibo"]` com schema `1.0.0`, gramática `1.5.0` e campo `saida_sha3`; o recibo gerado pelo pacote publicado não traz esses campos, então recibo legítimo volta `REPROVA` com a mensagem "recibo ausente". Correção: um único schema, versionado, aceito pelos dois lados
3. *Versão em desacordo.* [DADO] `pyproject` em 2.5.10, PyPI em 2.5.9. Isthmus declara a versão da gramática que fala, e essa versão precisa existir publicada

---

## 8. Doze testes de aceitação

Cada linha é um caso que o compilador ou o verificador precisam passar. `PASS` significa que o comportamento observado é o descrito.

```
#  caso                          entrada                                   esperado
1  decisão limpa                 band 0.01, shots 512, p0<=0.05 -> 1        veredito 1, selo confere
2  reprovação clara              p0>=0.95 -> 0                              veredito 0, selo confere
3  banda excedida                within 0.02 com band 0.01                  REFUSED, BAND-EXCEEDED
4  sem banda                     decide sem band                            erro ISTH-NOBAND
5  otherwise binário             otherwise 1 sem REFUSED declarado           erro ISTH-FORCED
6  motivo não declarado          REFUSED com motivo fora de deny             erro ISTH-UNDECLARED
7  ordem invertida               oracle antes de band                        erro ISTH-ORDER
8  adulteração de recibo         trocar um dígito de p0                      verificação False
9  escape divergente             payload com backspace em \b e \u0008        mesmo hash nos dois, após RFC 8785
10 emissor ausente               emit receipt sem issuer                     recibo inválido
11 emissor desconhecido          fingerprint fora da lista confiável         verificação False
12 determinismo                  mesmo programa e semente, duas execuções    bytes idênticos
```

Os casos 3 a 7 são de compilação e não tocam hardware. Os casos 1, 2, 8, 10, 11 e 12 rodam localmente com simulador. O caso 9 é o que hoje falha.

---

## 9. Prompt mestre, para o outro agente

Copiar e enviar como está. Está em inglês porque é especificação técnica, e a especificação circula em inglês.

```
You are extending ZEPHIRUM with a sublanguage called ISTHMUS. It is not a new
language: it is the strictest subset of ZYQL v2 that still crosses from a
measurement to a sealed verdict, and it compiles 1:1 to the trivalent C core.

SOURCE OF TRUTH, read before writing anything:
- docs/grammar/zyql.ebnf        (ZYQL v2 EBNF, Lisp syntax, .zph files)
- docs/language.md              (Zephyron v1.4.3 front-end)
- src/zephirum.h               (C contract: one oracle call per decision,
                                 declared noise band, rational receipt sealed
                                 with SHA3-256)
- src/zyql_lisp.py             (the real front-end the EBNF was derived from)

DESIGN CONSTRAINTS, non-negotiable:
1. Isthmus removes: define, gates, loops, booleans, free arithmetic, arbitrary
   atoms, and anything not listed in the grammar you will write.
2. Declaration order is band -> oracle -> shots -> deny -> decide -> emit
   receipt. Any other order is a compile refusal, code ISTH-ORDER.
3. No decision without a declared band. Missing band is ISTH-NOBAND.
4. Three verdicts only: 1, 0, REFUSED. 0 and REFUSED must never collapse.
   An `otherwise` clause that does not explicitly yield REFUSED is a compile
   error, ISTH-FORCED: forcing a binary verdict is the exact fraud this project
   exists to prevent.
5. Every refusal must carry a reason authorised by a `deny` declaration.
   Undeclared reason is ISTH-UNDECLARED.
6. Receipts are canonical per RFC 8785, carry issuer name plus key fingerprint,
   and are sealed with SHA3-256 over the canonical bytes. A receipt without an
   issuer is invalid even if the seal verifies. A receipt only its issuer can
   check is not a receipt, it is a chain.
7. Determinism: same program, backend and seed must produce byte-identical
   receipts.

DELIVERABLES:
a. docs/grammar/isthmus.ebnf, derived line by line from zyql.ebnf, with a diff
   section listing exactly what was removed and why.
b. A table mapping every Isthmus form to the C contract in src/zephirum.h.
c. The 12 acceptance tests as executable cases, with expected verdict, expected
   error code, or expected verification result. Cases 3-7 are compile-time.
d. A one-page rationale answering: why does this sublanguage deserve to exist
   as a separate syntax instead of a lint rule on ZYQL v2?

BLOCKING DEFECTS to fix before this is publishable, with evidence:
- Canonical form is not pinned. The same payload serialised as \b and as \u0008
  yields different hashes (d596f6381c2dbaa2 vs 6bc64e1a412adce4, measured
  2026-11-17). Pin RFC 8785 and add shared vectors in tests/vectors/canonical/
  run by Python, Rust and JS in CI.
- Receipt schemas disagree. The repository verifier requires payload["recibo"]
  with schema 1.0.0, grammar 1.5.0 and field saida_sha3; the receipt produced by
  the published package does not, so a legitimate receipt verifies as REPROVA
  with "recibo ausente". One schema, versioned, accepted on both sides.
- Version drift: pyproject says 2.5.10, PyPI serves 2.5.9. Isthmus must declare
  the grammar version it speaks, and that version must be published.

STYLE RULES:
- Evidence labels on every factual claim: [DATA] verified in primary source,
  [SOURCE] named third party, [INFERENCE] deduction, [OPINION] judgement,
  [UNKNOWN] not established.
- Numbers enter only with method: command, environment, sample size, what was
  controlled.
- No vendor names in product framing, no claimed partnerships, no adjective
  where a measurement belongs.
- English for the spec, Portuguese for the reader-facing abstract.

OUTPUT ORDER: grammar first, contract mapping second, tests third, rationale
last. If a rule above cannot be implemented as written, say which rule and why
instead of silently softening it.
```

---

## 10. O que decidir antes da editoria

1. *Isthmus ou Istimos.* O nome canônico precisa ser um só, e o arquivo `.isth` é sugestão, não decisão
2. *Isthmus entra no livro como capítulo ou como anexo de especificação.* Capítulo exige prosa, anexo exige gramática. O material acima serve aos dois, mas o recorte muda
3. *Os três defeitos da seção 7 aparecem no texto.* [OPINIÃO] Devem aparecer. Um livro que descreve uma linguagem de verificação e esconde que a verificação hoje reprova recibo legítimo perde exatamente o argumento que vende

---

*Ravi dos Anjos · Serena Solutions · 17 de novembro de 2026*
