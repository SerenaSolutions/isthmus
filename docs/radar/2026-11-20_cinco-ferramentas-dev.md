---
title: Cinco ferramentas de rotina de desenvolvimento
summary: Post de Khristian Tomaz com n8n, Postman, Docker, DBeaver e Excalidraw; quais servem ao nosso fluxo hoje e quais não têm lugar.
---

# Cinco ferramentas de rotina

Post de Khristian Tomaz lido em 20/11/2026 (publicado há 2 dias, 98 reações).
Lista n8n, Postman, Docker, DBeaver e Excalidraw.

## Avaliação item por item, contra o nosso fluxo real

[DADO] *Docker*: temos necessidade concreta e medida. O QuanSo exige `pip install
quanso` mais repositório clonado, e o provedor MCP depende disso. Sem imagem
reproduzível, o `quanso_status` funciona nesta máquina e falha na de outra pessoa.
É o único dos cinco com dívida real apontada.

[OPINIÃO] *Postman*: vale no dia em que a metade A2A existir. Hoje não temos
endpoint HTTP; nosso servidor fala stdio. Antes do endpoint, não há o que testar.

[OPINIÃO] *n8n*: sobrepõe ao que já fazemos com workflows da plataforma e GitHub
Actions. Adotar criaria terceiro lugar de automação, com credencial nova. Não
recomendo agora.

[OPINIÃO] *DBeaver*: não temos banco SQL. O armazém do QuanSo e os recibos são
arquivo JSON selado. Sem uso.

[OPINIÃO] *Excalidraw*: útil para diagrama manual, mas o GitDiagram gera o mesmo
a partir do código, sem desenho à mão. Redundante.

## O que isso vira

[DADO] Uma tarefa candidata: Dockerfile para o `quanso_status`, com o pacote e o
repositório dentro, para o provedor MCP não depender da máquina. É a única das
cinco que fecha uma lacuna já documentada.

As outras quatro ficam registradas como avaliadas e recusadas, com motivo, para não
voltarem como sugestão nova na próxima vez.

## O que não foi verificado

1. Não testei n8n, Postman, DBeaver nem Excalidraw nesta máquina
2. Não medi quanto a imagem Docker do QuanSo pesaria
3. Não conferi se o QuanSo sobe com as dependências opcionais dentro de container
