## 1º Solução

# Perguntas de modelagem para a solução

Antes de comparar heurísticas, registrar as regras exatas do problema:

1. Qual movimento é considerado uma ação?
2. O veículo pode deslocar-se por várias células em uma ação?
3. O movimento de saída de X é uma ação própria?
4. Como os estados são codificados e como estados repetidos são reconhecidos?
5. A busca A* usa custo uniforme de 1 para cada ação legal?
6. Como será obtido o custo ótimo de referência em instâncias pequenas?

Essas definições são pré-requisitos para comparar o valor de uma heurística com o custo ótimo restante.