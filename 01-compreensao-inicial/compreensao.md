## 1º Compreensão

*• Como representaríamos um estado?*
    - Compreendemos que a representação de estado se daria pelo formato que os carros estariam distribuidos pelo tabuleiro e os demais estados aconteceriam a partir do momento em que a gente modificasse o estado inicial conseguiriamos chegar a um próximo estado e consecutivamente até conseguirmos chegar ao estado final.

*• Como descobriríamos os movimentos possíveis?*
    - Verificamos as retrições e possíbilidades de como o mundo(tabuleiro) no qual estamos observamos ou no caso o agente pode ser alterado. O movimento é determinado pelo tamanho do veiculo que é representado por uma sequencia de letras, verificamos os seus adjacentes para determinarmos para onde esse veiculo está orientado verticalmente ou horizontalmente e a partir disso podemos efetuar o movimento seguindo essa horientação. Um veículo pode se deslocar em uma ou mais casas em uma unica ação desde que o caminho esteja livre. 

*• Como saberíamos que chegamos ao objetivo?*
    - Quando conseguirmos verificar o tabuleiro e não possuir mais nenhum veículo nomeado de X.

*• Que algoritmo de busca utilizaríamos?*
    - A* com uma heurística `admissível`.

*• O que poderia ser utilizado para estimar se um estado está próximo da
solução?*
    - A nossa substimativa que será a distância estimada do veículo até a `saída`
    - G(n) + H(n) = X
    - H(n) é a distancia substimada até a saída, ele precisa chegar a 0.
    - G(n) é a distância que já foi percorrida.