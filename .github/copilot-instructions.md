# Instruções para agentes e Copilot neste repositório

Este repositório faz parte do ecossistema ZEPHIRUM / ZYQL da Serena Solutions.
Leia esta página antes de propor código.

## Regra científica (vale para código, texto e número)

1. Nenhuma afirmação sem comando que a reproduza. Número digitado à mão é defeito.
2. Medir antes de afirmar: medir, escrever, revisar. Se a medição desmentir o texto, o texto muda.
3. Quatro estados, sem quinto: IMPLEMENTADO, EXPERIMENTAL, ESPECIFICAÇÃO, BLOQUEADO.
4. REFUSED é resultado, não falha: sem evidência, recuse com motivo nomeado.
5. Resultado negativo é publicado. Esconder falha para o número ficar bonito é o único erro sem reparação.
6. Portão entre fases: a fase seguinte só começa com a anterior verificável.
7. Uma fonte de verdade por dado. Se dois lugares discordam, o defeito se corrige na origem.
8. Gate que reprova a mudança: ajuste a mudança ou justifique o gate por escrito. Nunca desligar teste.

## Invariantes da linguagem

1. Proof antes de Compute: o ZCA elimina execução quando existe prova.
2. Lógica trivalente estrita 1 / 0 / REFUSED. Nunca converter REFUSED em booleano.
3. Aritmética exata no núcleo analítico: sem float no caminho de decisão.
4. Todo resultado emite recibo: SHA3-256 mais assinatura pós-quântica ML-DSA-44.
5. Backend não verificado recusa explicitamente, fail-closed, sem fallback silencioso.

## Ao propor mudança

1. Diga o que foi medido, com o comando.
2. Diga o que continua não demonstrado.
3. Se tocar em selo, assinatura ou veredito, traga teste que reproduz o defeito antes da correção.

## Governança

A diretriz de governança do agente arquiteto é privativa da Serena Solutions e não é publicada
neste repositório. Ela vive no repositório privado `quanso-os`, em `docs/GOVERNANCA-AGENTE-ARQUITETO.md`.

Resumo operacional público, sem detalhe estratégico: evidência antes de afirmação; nada é
concluído sem teste executado; toda falha termina em correção, evidência ou limitação declarada;
não inventar arquivo, commit, teste, resultado ou funcionalidade.
