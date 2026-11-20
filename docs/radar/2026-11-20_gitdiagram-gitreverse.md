---
title: GitDiagram e GitReverse, leitura de repositório por IA
summary: Duas ferramentas open source que resumem repositório, uma em diagrama e outra em prompt; ambas verificadas no GitHub, e o limite de confiança que o próprio post admite.
---

# GitDiagram e GitReverse

Post do perfil Aprendendo IA lido em 20/11/2026. O post é declaradamente escrito
por IA, segundo o próprio rodapé ("IASMIN, redatora autônoma"). As duas
ferramentas foram conferidas no GitHub.

## O que cada uma faz

[DADO] *GitDiagram*: `ahmedkhaleel2004/gitdiagram`, licença MIT, criado em
15/12/2024, 19.024 estrelas. Gera diagrama navegável de arquitetura a partir de
repositório público, com exportação em PNG.

[DADO] *GitReverse*: `filiksyos/gitreverse`, licença MIT, criado em 31/03/2026,
2.096 estrelas. Descrição oficial: "Reverse engineer any repo into it's original
prompt". Transforma README e lista de arquivos em prompt estruturado.

[OPINIÃO] São complementares, e a diferença é o produto final: um entrega figura
para humano, o outro entrega contexto para modelo. Nenhum dos dois lê o histórico
de commits com profundidade, então nenhum serve como auditoria.

## O limite que o próprio post admite, e está certo

Diagrama e prompt gerados por IA são *síntese*, não fonte. O post diz isso
explicitamente, e é a mesma regra que aplicamos aqui: nada entra como fato sem
conferência no arquivo, no teste ou no histórico.

Risco específico em repositório privado: usar token de acesso exige avaliar
permissões, política da empresa e destino dos dados. O `quanso-os` é privado, e
não deve ser apontado para serviço de terceiro sem essa avaliação.

## O que interessa para nós

[OPINIÃO] O `isthmus` tem 89 arquivos e uma separação clara em camadas; um
diagrama gerado serviria como material de apresentação, com a ressalva de que
diagrama não substitui o README verificado. Vale como imagem de divulgação, não
como documentação.

## O que não foi verificado

1. Não rodei nenhuma das duas ferramentas
2. Não conferi se o GitDiagram aceita repositório privado, nem com que escopo
3. Não medi a qualidade do diagrama gerado para um repositório do nosso tamanho
