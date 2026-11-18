from service.heuristics.base import Heuristic


class H0Distancia(Heuristic):
    """H0 — ideia original da equipe.

    h(n) = número de células entre a frente de X e a saída
           (0 se X já saiu do tabuleiro).

    Crítica (04-heuristicas/criticas-h0-h1-hfinal.md): mede células, mas o
    custo é medido em ações (uma ação pode andar várias células). Por isso
    PODE SUPERESTIMAR: X na coluna 1 de um 6x6 com o caminho livre dá h = 4,
    mas h* = 1. NÃO é admissível nem consistente. Fica no projeto como
    referência para os experimentos.
    """

    name = "h0-distancia"

    def calculate(self, state_dict):
        if 'X' not in state_dict:
            return 0
        x = self.board.vehicles['X']
        return self.board.grid_size - (state_dict['X'] + x.length)
