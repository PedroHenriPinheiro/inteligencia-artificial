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
    """h(n) = 0. Com ela o A* vira busca de custo uniforme (referência)."""

    name = "zero"

    def calculate(self, state_dict):
        return 0


class CascadeHeuristic(Heuristic):
    """Service: Isola a complexidade matemática da heurística (Efeito Cascata).

    h(n) = 1 + |D(n)|, onde D(n) é o conjunto de veículos que, pelo argumento
    da cascata, precisam se mover pelo menos uma vez em toda solução.

    Parâmetro `ciclo_como_deadlock`:
      - False (padrão, versão corrigida): quando a recursão reencontra um
        veículo que já está na cadeia (ciclo), essa restrição é ignorada.
        O veículo ancestral já foi contado em D, então não há nada novo a
        somar; e o ciclo não prova que o estado é insolúvel (h* finito com
        h = infinito foi observado no 6x6 registrado pela equipe).
      - True (versão original): o ciclo invalida o ramo (retorna infinito).
        Mantida apenas para reproduzir o contraexemplo nos experimentos.

    Parâmetro `regra_colinear` (padrão True):
      Dois veículos na mesma linha (ou na mesma coluna) e com a mesma
      orientação nunca passam um pelo outro. Se o veículo M precisa avançar na
      direção d e o veículo u, colinear a M, ocupa as células de que M precisa,
      então u só pode liberá-las indo também na direção d: andar no sentido
      oposto o deixa ainda dentro do trecho que M precisa percorrer.
      Por isso o ramo do sentido oposto é descartado.
      A mesma regra faz u sair do trecho INTEIRO de que M precisa (e não só
      das casas que u ocupa hoje), pois recuar pouco o deixaria no trecho.
      Com regra_colinear=False o comportamento é o do código original.
    """

    def __init__(self, board: RushHourBoard, ciclo_como_deadlock: bool = False,
                 regra_colinear: bool = True):
        super().__init__(board)
        self.ciclo_como_deadlock = ciclo_como_deadlock
        self.regra_colinear = regra_colinear

    @property
    def name(self):
        if self.ciclo_como_deadlock:
            return "cascata-original"
        return "cascata" if self.regra_colinear else "cascata-continue"

    def calculate(self, state_dict):
        if 'X' not in state_dict:
            return 0

        guaranteed_deps = self.dependencies(state_dict)

        if guaranteed_deps is None:
            return float('inf')

        return 1 + len(guaranteed_deps)

    def dependencies(self, state_dict):
        """Retorna o conjunto D(n), ou None se algum bloqueador não tem rota geométrica."""
        X_v = self.board.vehicles['X']
        X_col = state_dict['X']
        X_row = X_v.fixed_axis

        occupied = self.board.get_occupied_cells(state_dict)
        target_cells_for_x = set((X_row, c) for c in range(X_col + X_v.length, self.board.grid_size))

        return self._get_guaranteed_deps(state_dict, occupied, target_cells_for_x,
                                         visited=frozenset(), mover='X', direction=+1)

    def _get_guaranteed_deps(self, state_dict, occupied, target_cells, visited,
                             mover=None, direction=None):
        """Método encapsulado para cálculo recursivo de interseções.

        mover/direction: o veículo que precisa das `target_cells` e o sentido
        (+1 = direita/baixo, -1 = esquerda/cima) em que ele vai se mover.
        """
        deps = set()
        vehicles_in_way = set(occupied[cell] for cell in target_cells if cell in occupied)

        if not vehicles_in_way:
            return deps

        # Ordem determinística: o resultado não pode depender da ordem de um set.
        for u_id in sorted(vehicles_in_way):
            if u_id in visited:
                if self.ciclo_como_deadlock:
                    return None
                # Ciclo: o ancestral já está em D (já foi exigido que ele se
                # mova). Exigir de novo não acrescenta nada ao limite inferior,
                # e o ciclo não prova que o estado é insolúvel: o ancestral
                # pode estar em outra posição quando este ramo acontecer.
                continue

            deps.add(u_id)
            u_v = self.board.vehicles[u_id]
            u_head = state_dict[u_id]
            u_axis = u_v.fixed_axis

            if self.regra_colinear:
                # Células-alvo que estão na linha (H) ou coluna (V) de u.
                # u precisa sair de TODAS elas, não só das que ocupa agora: um
                # veículo colinear que recua só o suficiente para sair das
                # casas que ocupa pode cair em outras casas do mesmo trecho.
                # (Para u perpendicular ao `mover`, é sempre uma única célula.)
                if u_v.orientation == 'H':
                    intersecting = {c for c in target_cells if c[0] == u_axis}
                else:
                    intersecting = {c for c in target_cells if c[1] == u_axis}
            else:
                # Versão original: só as células-alvo que u ocupa agora.
                u_current_cells = set(
                    (u_axis, u_head + i) if u_v.orientation == 'H' else (u_head + i, u_axis)
                    for i in range(u_v.length)
                )
                intersecting = target_cells.intersection(u_current_cells)
            if not intersecting:
                continue

            # Regra colinear: u não pode passar por `mover`, então só pode fugir
            # no mesmo sentido em que `mover` avança.
            allow_neg, allow_pos = True, True
            if self.regra_colinear and mover is not None:
                m_v = self.board.vehicles[mover]
                if m_v.orientation == u_v.orientation and m_v.fixed_axis == u_axis:
                    allow_neg = (direction == -1)
                    allow_pos = (direction == +1)

            # --- ROTA NEGATIVA ---
            min_intersect = min(c[1] if u_v.orientation == 'H' else c[0] for c in intersecting)
            target_head_neg = min_intersect - u_v.length
            possible_neg = allow_neg and (target_head_neg >= 0)
            deps_neg = None
            if possible_neg:
                cells_to_clear_neg = set(
                    (u_axis, r) if u_v.orientation == 'H' else (r, u_axis)
                    for r in range(target_head_neg, u_head)
                )
                deps_neg = self._get_guaranteed_deps(state_dict, occupied, cells_to_clear_neg,
                                                    visited | {u_id}, mover=u_id, direction=-1)

            # --- ROTA POSITIVA ---
            max_intersect = max(c[1] if u_v.orientation == 'H' else c[0] for c in intersecting)
            target_head_pos = max_intersect + 1
            possible_pos = allow_pos and (target_head_pos + u_v.length - 1 < self.board.grid_size)
            deps_pos = None
            if possible_pos:
                cells_to_clear_pos = set(
                    (u_axis, r) if u_v.orientation == 'H' else (r, u_axis)
                    for r in range(u_head + u_v.length, target_head_pos + u_v.length)
                )
                deps_pos = self._get_guaranteed_deps(state_dict, occupied, cells_to_clear_pos,
                                                    visited | {u_id}, mover=u_id, direction=+1)

            # --- INTERSEÇÃO ---
            valid_branches = [d for d in (deps_neg, deps_pos) if d is not None]
            if len(valid_branches) == 0:
                return None
            elif len(valid_branches) == 1:
                deps.update(valid_branches[0])
            else:
                deps.update(valid_branches[0].intersection(valid_branches[1]))

        return deps


# Heurísticas disponíveis por nome (usado pela linha de comando e pela interface).
HEURISTICAS = {
    "cascata": CascadeHeuristic,
    "zero": ZeroHeuristic,
}
