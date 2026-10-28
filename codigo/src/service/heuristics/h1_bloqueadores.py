from service.heuristics.base import Heuristic


class H1Bloqueadores(Heuristic):
    """H1 — bloqueadores diretos.

    h(n) = 1 + número de veículos DISTINTOS que ocupam alguma célula entre a
           frente de X e a saída (0 se X já saiu do tabuleiro).

    Crítica (04-heuristicas/criticas-h0-h1-hfinal.md):
    - Admissível: cada bloqueador direto precisa se mover pelo menos uma vez,
      cada ação move um único veículo, e a saída de X é mais uma ação.
    - Consistente: uma ação muda a posição de um único veículo, então o
      conjunto de bloqueadores ganha ou perde no máximo um veículo, e
      h(n) <= 1 + h(n').
    - Fraca: ignora quem bloqueia os bloqueadores (no 6x6 do IH02, h = 2 e
      h* = 12).
    """

    name = "h1-bloqueadores"

    def calculate(self, state_dict):
        if 'X' not in state_dict:
            return 0
        x = self.board.vehicles['X']
        linha = x.fixed_axis
        ocupadas = self.board.get_occupied_cells(state_dict)
        bloqueadores = {
            ocupadas[(linha, c)]
            for c in range(state_dict['X'] + x.length, self.board.grid_size)
            if (linha, c) in ocupadas
        }
        return 1 + len(bloqueadores)
