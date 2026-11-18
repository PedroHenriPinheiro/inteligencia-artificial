# Nova heurística — hipótese refinada em investigação

## Status

**Hipótese não finalizada. Ainda não há fórmula definida nem prova de admissibilidade.**

## Motivação

A heurística inicial baseada diretamente na distância de X até a saída pode confundir distância geométrica com custo em ações. Além disso, o número de veículos envolvidos nos bloqueios não é necessariamente igual ao número de ações restantes: algumas movimentações podem não ser obrigatórias, e uma ação pode resolver várias dependências.

## Direção de investigação

Investigar estimativas construídas a partir de movimentações comprovadamente inevitáveis, usando argumentos que estabeleçam um limite inferior para o número de ações restantes.

Antes de incluir uma contribuição, avaliar:
- se a movimentação é inevitável em toda solução;
- se a ação já foi contabilizada;
- se uma mesma ação pode resolver várias dependências;
- se a soma proposta nunca ultrapassa o custo ótimo restante;
- se a condição de consistência também é satisfeita, caso seja necessária.

## Critérios para aceitar um candidato

Um candidato não deve ser tratado como heurística admissível até que haja:
1. definição precisa da função e de seus dados de entrada;
2. argumento geral de que não superestima o custo ótimo;
3. verificação da condição no estado objetivo;
4. análise de consistência, se pretendida;
5. testes em estados pequenos com custo ótimo calculado por busca exata;
6. registro de contraexemplos encontrados e de como a hipótese foi ajustada.

## Limitação atual

A conversa estabeleceu critérios de raciocínio, não uma regra numérica completa. Portanto, não se deve implementar uma soma específica de bloqueadores ou dependências como se já estivesse validada.
