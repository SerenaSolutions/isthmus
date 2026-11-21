---
title: Escopo do ecossistema ZEPHIRUM
summary: Define o que está dentro e o que está fora do ecossistema, com a regra única que atravessa todos os repositórios e a razão de cada exclusão.
---

# Escopo

Documento de referência única. Todo outro documento aponta para cá em vez de
redefinir escopo. Se algo não aparece aqui, está fora até decisão da mantenedora.

## Regra única

Um repositório pertence ao ecossistema ZEPHIRUM quando *publica ou executa a
linguagem, a sub-linguagem, o sistema quântico ou uma aplicação derivada delas*.
Marca, site e orquestração entram como apoio. Empresa, cooperativa de terceiro e
projeto de outra natureza ficam fora, mesmo que a conta seja a mesma.

## Dentro

| frente | repositórios | papel |
|---|---|---|
| linguagem | `zephirum-lang`, `zephirum` (ponteiro), `the-zyql-zephirum-code`, `zeph-bridges`, `pennylane-zephirum` | núcleo, ponteiro, livro, pontes, adaptador |
| sub-linguagem | `isthmus`, `decision-receipt` | verificação e recibo |
| sistema quântico | `quanso-os` (privado) | SO em camadas |
| aplicações derivadas | `imutq`, `qsr-crypto-gate`, `zyql-quantum-vulnerability`, `ravi-quantuno`, `quantum-poc`, `zq-gate`, `zq-ir`, `zqea-guardian`, `zqea-seal`, `zqea-verify`, `zy-ai-rag`, `z-anyon-lab`, `ediptec-tasks` | produtos sobre a linguagem |
| equipe | `equipe-orquestracao`, `serena-quantum-safe-readiness` | orquestração e prontidão |
| marca | `serenasolutions`, `serenasolutions.github.io` | presença |

## Fora

1. *`AgroSolutions`*: cooperativa agrícola de terceiro, três repositórios de API.
   Não é da mantenedora e não recebe workflow, PR, issue ou leitura nossa
2. *`Aigro-Solutions`*: organização de desenvolvimento própria, a ser renomeada
   *Ravi Solutions*. Os nove CIs criados em 21/11/2026 permanecem, porque servem à
   empresa, mas *não* contam como cobertura do ecossistema e não entram na conta de
   portões do ecossistema
3. *`AigroQuantumFintech`*: produto de marca anterior. Tem `package.json` de app
   React e *não tem pasta `src/`*, medido em 21/11/2026. Fica fora até a mantenedora
   decidir se é produto vivo ou arquivo

## O que a regra obriga em todo repositório dentro do escopo

1. Nomenclatura: Isthmus, ISTH e STH. Nunca IST
2. Commit assina como agente, nunca com nome de pessoa real
3. Nada vira número ou afirmação sem medição; o não verificado fica marcado
4. CI de sanidade e Pages quando fizer sentido publicar
5. Publicação em PyPI, registro MCP, Qiskit Ecosystem ou CNCF só com aval da
   mantenedora

## O que este documento não decide

Não decide se `Aigro-Solutions` deve ser absorvida, arquivada ou renomeada. Isso é
decisão de marca da mantenedora, e o registro atual é: renomear para Ravi Solutions
mantendo a URL.
