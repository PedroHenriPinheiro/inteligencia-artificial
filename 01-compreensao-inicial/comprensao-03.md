## Terceira compreensao do problema - João Victor + Gemini

# Questões respondidas da Segunda Compreensão

- A movimentação de X para fora do tabuleiro deve contar como uma ação de custo 1 de forma a garantir a que a função de transição seja uniforme. Para isto é possível implementar uma ação especial `(ex: SAIR_DIREITA)` que é válida apenas para o veículos X quando não há obstáculos entre ele e a borda.

- Uma ação pode deslocar o veículo por qualquer número de células consecutivas, desde que o caminho esteja totalmente livre. As unicas restrições são:
-- O veículo deve se manter estritamente na sua linha ou coluna
-- Não pode haver pulo sobre outros veículos
-- Nenhum veículo pode ultrapassar os limites do grid 12x12, com a única exceção sendo o veículo X no seu movimento final

- O estado deve registrar apenas posições dinâmicas. Propriedades como tamanho do veículo, orientação e identificador são classificadas como propridades estáticas.

# Descoberta de Movimentação e Representação

- A visão inicial da equipe: Varrer o tabuleiro, encontrar sequências `(ex: AAA)`, deduzir o tamanho e a orientação olhando os adjacentes, e calcular as casas livres.

- O Problema: Fazer a leitura da matriz a cada novo estado gerado é custoso computacionalmente.

- Solução: Realizar a leitura do tabuleiro apenas uma vez no estado inicial. Guardaremos isso em uma estrutura estática. Para a busca, o estado dinâmico precisa saber apenas que um veículo (ex: A) está na linha Y e sua ponta começa na coluna X. Para descobrir os movimentos, é necessário apenas checar a coordenada atual do veículo contra as coordenadas dos outros veículos para ver quantas casas livres existem no eixo dele.

# Teste de Objetivo

- A visão inicial da equipe: O objetivo é atingido quando o veículo X não existe mais no tabuleiro.

- O Refinamento: A lógica em si está alinhada com a definição de que a saída do tabuleiro conta como uma ação de custo 1. Na prática, quando o gerador de sucessores avaliar que o veículo principal consta com caminho à direita totalmente livre, ele gera um estado sucessor aplicando a ação especial `(ex: SAIR_DIREITA)`. O estado resultando não conterá coordenadas do veículo principal. O teste de objetivo simplesmente verifica.

# Algoritmo de Busca A* e a Função Heurística

- A visão inicial da equipe: `f(n) = g(n) + h(n), onde g(n)` é a distância percorrida e h(n) é a distância estimada até a saída.

- O Problema: É necessário ter cuidado com o que é definido como a distância. Como estabelecido que o custo de cada ação é 1 independente do número de células, g(n) então deverá ser estritamente a quantidade de movimentos (ações) realizados desde o ínicio, e não casas percorridas. Se h(n) calcula a distância em células de X até a saída, a heurística deixa de ser admíssivel.

# Heurísticas Recomendadas

Para garantir um h(n) admíssivel é possível utilizar abordagens baseadas em bloqueios ao invés da distância espacial no tabuleiro.

H1:
- `h(n) = 0`, se X já saiu
- `h(n) = 1`, se o caminho à direita de X está totalmente livre
- `h(n) = 2`, se há qualquer veículo bloqueando o caminho de X

H2 `(Recomendada pelo Gemini)`: Abordada na `Heurística 3`
- `h(n) = 1 + b`, onde b é a quantidade de veículos diferentes que estão bloqueando o caminho de X até a saída
- Como cada veículo bloqueador precisa ser movido pelo menos uma vez, e X precisa de pelo menos um movimento para sair, o custo real nunca será menor que 1 + b.