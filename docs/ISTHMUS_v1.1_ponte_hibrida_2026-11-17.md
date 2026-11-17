---
title: ISTHMUS 1.1 — ponte híbrida e veredito verificável
summary: Revisão da especificação de Isthmus com o pilar de interoperabilidade híbrida quântico-clássica, as cinco responsabilidades da ponte, o limite de uma chamada de oráculo por decisão, a separação entre implementado e planejado, e a medição de 12 erros plantados.
---

# ISTHMUS 1.1

**SublinGuagem híbrida de interoperabilidade, controle e verificação do ecossistema Zephirum.**
Define a passagem formal entre operações clássicas, execuções quânticas e resultados computacionais verificáveis.
Versão 1.1 · 17/11/2026 · Ravi dos Anjos · Serena Solutions

---

## 1. Duas funções, uma passagem

Na versão 1.0, Isthmus era só controle de veredito. A revisão corrige o escopo, e a correção é do dono do projeto, não minha:

1. *Função de controle*: decidir com três estados e selar a decisão
2. *Função de ponte*: coordenar a travessia entre o ambiente clássico e o ambiente quântico, levando parâmetros para dentro, contagens para fora, e nada além disso

As duas funções compartilham a mesma propriedade: são passagem estreita. Isthmus não executa computação. Isthmus controla o que atravessa.

---

## 2. Arquitetura

```
APLICAÇÕES CLÁSSICAS
          |
          v
    ZYQL / ZEPHIRUM
          |
          v
        ISTHMUS
     (PONTE HÍBRIDA)
          |
    +-----+-----+
    |           |
    v           v
CLÁSSICO     QUÂNTICO
    |           |
    |      +----+----+
    |      |         |
    |      v         v
    |    QPU     SIMULADOR
    |      |         |
    +------+---------+
           |
           v
   RESULTADOS E MEDIÇÕES
           |
           v
   VALIDAÇÃO ISTHMUS
           |
           v
   VEREDITO ZEPHIRUM
           |
           v
   RECIBO VERIFICÁVEL
```

---

## 3. As cinco responsabilidades da ponte

| # | Responsabilidade | O que atravessa | O que não atravessa |
|---|---|---|---|
| 1 | Receber parâmetros do ambiente clássico | band, shots, oracle, deny | código arbitrário |
| 2 | Encaminhar a operação ao backend compatível | nome do backend, circuito já compilado | estado quântico cru |
| 3 | Receber medições e resultados | contagens, id de job, backend real | contagem não declarada |
| 4 | Controlar a validação estatística | intervalo, banda, comparação com o limiar | ajuste depois de olhar |
| 5 | Entregar resultado classificado ao decisor | `1`, `0`, `REFUSED` com motivo | veredito sem banda |

### 3.1 O limite que não pode ser cruzado

O contrato da API C declara *uma chamada de oráculo por decisão*. A ponte híbrida respeita esse contrato, e portanto:

1. Não existe ciclo adaptativo: nada de medir, decidir e medir de novo dentro da mesma travessia
2. Não existe múltipla chamada silenciosa: se o programa precisa de duas amostragens, são duas decisões e dois recibos
3. Não existe orçamento variável: `shots` é declarado antes, e observação não reescreve declaração

[OPINIÃO] Se algum dia houver execução adaptativa, ela nasce como outra linguagem, com outro nome, e com o custo declarado. Chamar de Isthmus o que faz laço adaptativo destrói o argumento inteiro, porque o valor da passagem estreita é justamente não poder voltar atrás depois de ver o resultado.

---

## 4. Implementado e planejado, sem confundir os dois

Exigência do dono do projeto, e é a mais importante deste documento: interoperabilidade híbrida não é capacidade comprovada até haver teste de integração.

| Capacidade | Estado | Evidência |
|---|---|---|
| Decisão trivalente local, simulador | **implementado** | `zyql-decide` em ambiente limpo, 1,1 ms por decisão, [DADO] 16/11 |
| Recibo selado e verificação pelo pacote publicado | **implementado** | `verify_receipt` no PyPI 2.5.9, True no intacto e False no adulterado, [DADO] |
| Verificador do repositório aceitar recibo do pacote | **quebrado** | exige `payload["recibo"]` com `saida_sha3`, que o pacote não emite: REPROVA legítimo, [DADO] |
| Forma canônica estável entre implementações | **parcial** | reordenar chaves e mudar indentação não afeta o selo, 12 testes, [DADO] 17/11; escape de control char diverge entre portas escritas à mão |
| Execução em QPU | **implementado, sem recibo de ponte** | rodada em `ibm_marrakesh` registrada em PR #120, [DADO] |
| Ponte clássico-quântica com as cinco responsabilidades | **planejado** | esta seção; nenhum teste de integração escrito |
| Validação estatística como etapa formal da ponte | **planejado** | banda já existe no recibo, falta a etapa declarada na ponte |
| Interoperabilidade entre backends (qiskit, qbraid, sim) | **parcial** | adaptador qBraid entregue na 2.5.10, ainda não publicada |

[DADO] A 2.5.10 está commitada em 15/11 às 16h33 e o PyPI serve 2.5.9. Isthmus declara a versão da gramática que fala, e essa versão precisa existir publicada.

---

## 5. Medição: 12 erros plantados

Teste executado em 17/11/2026, ambiente limpo, `zephirum 2.5.9` do PyPI, Python 3.11, um recibo base gerado por `zyql-decide --oracle one --n 4 --shots 512 --seed 1 --seal`. Doze erros plantados, um por recibo, e um controle intacto.

| Erro plantado | Verificação |
|---|---|
| `p0` alterado em 0,001 | False |
| `shots` 512 → 513 | False |
| `n` 4 → 5 | False |
| `verdict` 1 → 0 | False |
| `mode` trocado | False |
| `error_bound` inflado | False |
| `seed` 1 → 2 | False |
| campo `p0` removido | False |
| campo extra injetado | False |
| selo adulterado | False |
| chaves reordenadas | True |
| indentação trocada | True |

*Resultado*: 10 de 10 adulterações semânticas detectadas. Os dois "aceitos" não são falha: reordenar chave e mudar indentação produzem o mesmo payload canônico, e aceitar é o comportamento correto.

*Custo*: 3 ms para as 12 verificações, 0,2 ms por verificação. Controle intacto: True.

*Correção que eu devo a mim mesma*: na versão 1.0 deste documento eu tratei a divergência `\b` contra `\u0008` como se já quebrasse o verificador. A medição mostra que este verificador normaliza ordem e espaçamento. O defeito real está em porta escrita à mão que serialize diferente, e o remédio continua o mesmo: vetores compartilhados, não confiança na implementação.

---

## 6. Definição estratégica

Isthmus é a sublinguagem híbrida de interoperabilidade, controle e verificação do ecossistema Zephirum, responsável por estabelecer uma passagem formal entre operações clássicas, execuções quânticas e resultados computacionais verificáveis.

Essa definição amplia a finalidade sem abandonar a característica que dá valor: a passagem controlada até um veredito.

---

## 7. Prompt mestre 1.1, para o outro agente

```
You are extending ZEPHIRUM with a sublanguage called ISTHMUS, version 1.1.
Isthmus has two functions on one narrow path: it decides with three states and
seals the decision, and it is the hybrid bridge that carries parameters into the
quantum environment and counts out of it. Isthmus never computes. It controls
what crosses.

READ FIRST, these are the source of truth:
- docs/grammar/zyql.ebnf     ZYQL v2 EBNF, Lisp syntax, .zph files
- docs/language.md           Zephyron v1.4.3 front-end
- src/zephirum.h             C contract: ONE oracle call per decision, declared
                             noise band, rational receipt sealed with SHA3-256
- src/zyql_lisp.py           the front-end the EBNF was derived from

ARCHITECTURE to specify, not to invent:
classical applications -> ZYQL/ZEPHIRUM -> ISTHMUS (hybrid bridge) -> classical
computation and quantum computation (QPU or simulator) -> results and
measurements -> Isthmus validation -> Zephirum verdict -> verifiable receipt.

FIVE BRIDGE RESPONSIBILITIES, each with an explicit "what must not cross":
1. receive parameters from the classical side (band, shots, oracle, deny; never
   arbitrary code)
2. dispatch the operation to a compatible backend (compiled circuit and backend
   name; never a raw quantum state)
3. receive measurements and results (counts, job id, real backend; never
   undeclared counts)
4. control statistical validation (interval, band, threshold comparison; never
   adjustment after looking at the data)
5. hand the classified result to the decider (1, 0, REFUSED with reason; never a
   verdict without a band)

HARD CONSTRAINT, do not soften it: the C contract allows exactly one oracle call
per decision. Therefore no adaptive loop, no silent second call, no variable shot
budget inside one crossing. A program that needs two samples is two decisions and
two receipts. If adaptive execution ever exists, it is a different language with a
different name and its cost declared up front.

KEEP FROM 1.0, unchanged:
- declaration order band -> oracle -> shots -> deny -> decide -> emit receipt, and
  any other order is compile refusal ISTH-ORDER
- no decision without a declared band (ISTH-NOBAND)
- three verdicts only; an `otherwise` that does not explicitly yield REFUSED is
  compile error ISTH-FORCED, because forcing a binary verdict is the fraud this
  project exists to prevent
- every refusal carries a reason authorised by a `deny` declaration, else
  ISTH-UNDECLARED
- receipts canonical per RFC 8785, carrying issuer name plus key fingerprint; a
  receipt only its issuer can check is not a receipt, it is a chain
- determinism: same program, backend and seed produce byte-identical receipts

DELIVER A MATURITY TABLE, mandatory. Every capability is labelled implemented,
partial, broken or planned, with the evidence for the label. Hybrid
interoperability is NOT a proven capability until an integration test exists.
Known state to encode, do not contradict it:
- implemented: local trivalent decision on simulator (1.1 ms per decision);
  sealed receipt verified by the published package (True intact, False tampered)
- broken: the repository verifier expects payload["recibo"] with saida_sha3 and
  the published package does not emit it, so a legitimate receipt verifies as
  REPROVA
- partial: canonical form holds against key reordering and indentation, measured
  on 12 planted errors; hand-written ports that escape control characters differ
- planned: the five bridge responsibilities, the statistical validation stage,
  and backend-agnostic dispatch as a specified step rather than an adapter

EVIDENCE RULES: label every factual claim as [DATA], [SOURCE], [INFERENCE],
[OPINION] or [UNKNOWN]. Numbers enter only with command, environment, sample size
and what was controlled. No vendor names in product framing, no claimed
partnerships, no adjective where a measurement belongs.

OUTPUT ORDER: definition, architecture, five responsibilities with their
prohibitions, hard constraint, maturity table, grammar delta from ZYQL v2, twelve
acceptance tests, rationale. If a rule above cannot be implemented as written, say
which rule and why instead of silently softening it.
```
