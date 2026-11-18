## Segunda compreensao do problema

# Modelagem do problema e custo das ações

## Problema

O tabuleiro tem dimensões 12×12 e contém veículos que ocupam células consecutivas, na horizontal ou na vertical. O veículo-alvo X precisa alcançar a saída localizada à direita do tabuleiro.

Para movimentar um veículo, as células necessárias ao deslocamento devem estar livres. Outros veículos podem bloquear o caminho de X ou impedir que veículos bloqueadores se movimentem para posições úteis.

## Estado

Um estado representa as posições atuais dos veículos no tabuleiro. Para que a busca reconheça estados equivalentes, a representação deve identificar de forma inequívoca a posição de cada veículo relevante.

## Ações e custo

Neste problema, uma ação corresponde a movimentar um veículo. Um veículo pode percorrer uma ou mais células em uma única ação, desde que o movimento seja legal.

Assim, o custo de uma ação é 1, independentemente da quantidade de células percorridas nessa movimentação.

Essa definição é central para projetar a heurística: distância geométrica em células e quantidade de ações restantes são grandezas diferentes.

## Estado objetivo

O objetivo é atingido quando X consegue sair do tabuleiro pela saída à direita. A implementação precisa definir de forma consistente se o movimento que retira X do tabuleiro é contado como uma ação; essa convenção deve ser usada tanto no algoritmo de busca quanto na avaliação da heurística.

## Questões ainda abertas

- A movimentação de X para fora do tabuleiro conta como uma ação? A implementação deve fixar essa convenção.
- Uma ação pode deslocar um veículo por qualquer número de células livres, ou existem restrições adicionais?
- A representação de estado diferencia apenas posições ou também registra outras propriedades relevantes?
""",