---
title: Gestão da equipe de engenharia do ecossistema Zephirum
summary: Papéis, portões obrigatórios e decisões de ferramenta que valem para todo repositório do ecossistema, com a evidência que sustenta cada portão.
---

# Gestão da equipe de engenharia

Vale para `isthmus`, `zephirum-lang` e `quanso-os`. Regra geral: nenhum item entra
por opinião. Entra com medida, com fonte ou não entra.

## Papéis, com o que cada um pode assinar

1. *Mantenedora* (Clara): decide escopo, aprova merge, assina release. Nenhum agente
   decide em nome dela
2. *Agentes de engenharia* (Solene, Agente Serena, ZYQL Agent): commitam com o
   próprio nome. Nunca assinam com nome de pessoa real; Luciano Bello entra apenas
   como revisor
3. *Auditoria independente*: quem não escreveu o código. Auditor que pertence ao
   mesmo dono do gerador não vale como evidência

## Oito portões, e a evidência de cada um

| # | portão | evidência que o justifica |
|---|---|---|
| 1 | suíte verde antes do merge | 114 testes no isthmus; 3 pulados declarados |
| 2 | campanha hostil com casos contados | 136 exceções cruas achadas e zeradas; 24.000 casos |
| 3 | catálogo fechado de recusas | `ISTH-*` no isthmus; `ZYQL-*` propostos para o runtime |
| 4 | nenhuma exceção crua na fronteira | `tools/roda_bugs.py` roda em 3 s e reprova |
| 5 | documento cita só o verificado | radar marca o não verificado item por item |
| 6 | credencial nunca em chat nem em log | token entra por build-arg ou variável de ambiente |
| 7 | vocabulário não pode divergir do código | `nomenclature.validate()` importa cada alvo |
| 8 | nome e contagem conferidos na fonte | README, About e CHANGELOG alinhados ao PyPI |

## Decisões de ferramenta, com veredito

1. *Docker*: adotado. `Dockerfile.quanso` fecha a dependência do provedor MCP. Ainda
   não construído por falta de docker no ambiente, e assim está declarado
2. *Postman*: adiado até existir endpoint HTTP (metade A2A)
3. *n8n*: recusado. Criaria terceiro lugar de automação com credencial nova
4. *DBeaver*: recusado. Não há banco SQL; recibo é JSON selado
5. *Excalidraw*: recusado. Redundante com diagrama gerado a partir do código
6. *MCP*: adotado. `isthmus-mcp` com seis ferramentas, stdio, sem token
7. *A2A*: estudado, não adotado. Falta endpoint e cartão de agente

## Rotina de revisão

1. Toda segunda: conferir membresia no Qiskit Ecosystem e alinhamento de versão
   entre `pyproject`, `VERSION` e PyPI
2. Toda entrega de código: rodar suíte, rodar campanha hostil, e só então commitar
3. Toda leitura externa: entra em `docs/radar/` com fonte, veredito e o que não foi
   verificado. Radar não é backlog
4. Toda correção de nome ou número: corrigir também o registro histórico, não só o
   README

## O que este documento não faz

Não cria autoridade nova. Ele registra o que já é praticado e medido, para que a
próxima pessoa ou agente não precise redescobrir os mesmos erros.
