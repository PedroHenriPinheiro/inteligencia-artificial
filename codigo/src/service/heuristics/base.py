from abc import ABC, abstractmethod

from domain.model import RushHourBoard


class Heuristic(ABC):
    """Interface de toda heurística usada pelo AStarSolver.

    Para criar uma heurística nova: herdar desta classe, definir `name` e
    implementar `calculate(state_dict)`, que devolve uma estimativa do número
    de ações restantes (0 no objetivo; math.inf só se o estado não tiver
    solução).
    """

    name = "abstrata"

    def __init__(self, board: RushHourBoard):
        self.board = board

    @abstractmethod
    def calculate(self, state_dict) -> float:
        """Estimativa h(n) para o estado {id: coordenada}."""


class ZeroHeuristic(Heuristic):
    """h(n) = 0. Com ela o A* vira busca de custo uniforme (controle)."""

    name = "zero"

    def calculate(self, state_dict):
        return 0
