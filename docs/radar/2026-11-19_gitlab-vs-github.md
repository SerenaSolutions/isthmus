---
title: GitLab vs GitHub, leitura crítica da comparação oficial
summary: A página comparativa da GitLab é material de marketing da própria GitLab; o que dá para usar como critério de decisão, e o que é afirmação não verificada.
---

# GitLab vs GitHub, leitura crítica

Página lida em 19/11/2026: about.gitlab.com/compare/gitlab-vs-github.

## Primeiro, o aviso que vale para o documento inteiro

[OPINIÃO] A fonte é a GitLab comparando a si mesma com o concorrente. Toda linha
tem a GitLab como vencedora por construção. Isso não invalida os fatos, mas obriga
a separar três coisas: o que é verificável na documentação de cada produto, o que é
política publicada, e o que é enquadramento.

## Afirmações que dá para checar por conta própria

1. *Treino de modelo com dados do cliente*: a página afirma que, desde 24/04/2026,
   o GitHub usa dados de interação do Copilot para treinar modelos por padrão nos
   planos Free, Pro e Pro+, com opt-out manual, e que Business e Enterprise ficam
   de fora por contrato. Do lado da GitLab, afirma que não treina com código de
   cliente em nenhum plano. Ambas são verificáveis nos termos de serviço de cada
   um, e é o item de maior consequência para quem tem código proprietário
2. *Créditos de IA*: a página dá números concretos do GitHub (crédito a US$ 0,01,
   Business US$ 19 com 1.900 créditos, Enterprise US$ 39 com 3.900), e diz que o
   Copilot incluído no Enterprise e o Standalone de US$ 10 não trazem crédito.
   Números assim se conferem na página de preços do GitHub
3. *Segurança embutida*: a GitLab afirma SAST, detecção de segredo e varredura de
   contêiner em todos os planos, inclusive Free. Verificável na matriz de planos
4. *Autohospedagem de modelo*: a GitLab afirma rodar modelo e agente na própria
   infraestrutura, inclusive air-gapped. Verificável na documentação do AI Gateway

## O que é enquadramento, não fato

1. "Plataforma unificada" e "um único modelo de dados": é descrição de arquitetura
   com juízo de valor embutido
2. "O GitHub exige add-ons": verdadeiro para alguns itens, mas o GitHub inclui
   Actions, Packages e CodeQL em planos que a página não detalha
3. Qualquer adjetivo do tipo "poderoso", "superior", "sem fricção"

## O que isso significa para a nossa equipe

[DADO] Hoje o ecossistema está no GitHub: `SerenaSolutions/isthmus`,
`SerenaSolutions/zephirum-lang`, mais os repositórios de marca. Migrar não é
decisão de gosto, é reescrita de CI, permissões, badges e histórico de PR.

[OPINIÃO] Nada nesta página justifica migração hoje. Os dois critérios que
justificariam são objetivos e nenhum está atendido: (a) necessidade real de rodar
CI em infraestrutura própria ou air-gapped, que hoje não temos; (b) política de
treino de dados incompatível com cliente pagante, e o nosso uso atual é repositório
público de código aberto, onde o problema não existe.

O que vale extrair da leitura não é a decisão de migrar, é a lista de perguntas a
fazer a qualquer fornecedor: treina com o meu código, por padrão ou por opt-in?
Quanto custa a unidade de IA depois do crédito incluído? Onde o runner executa?
Qual o custo real de sair depois de três anos?

## O que não foi verificado

1. Não conferi os termos de serviço do GitHub nem da GitLab na fonte oficial
2. Não conferi a página de preços de nenhum dos dois
3. Não medi custo de CI em nenhuma das duas plataformas

Enquanto isso não for feito, este documento é leitura de uma fonte interessada, não
auditoria.
