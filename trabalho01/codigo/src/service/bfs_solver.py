import time
from collections import deque

from domain.model import RushHourBoard
from domain.search_result import SearchResult
from service.search_common import reconstruct


class BFSSolver:
    """Service: busca em largura (não informada) com conjunto de visitados.

    - Busca em grafo: um estado entra em `visited` quando é gerado pela
      primeira vez e nunca mais é inserido na fila.
    - Teste de objetivo na GERAÇÃO. Com custo 1 por ação, a primeira vez que
      a BFS gera o objetivo é pela menor profundidade, então a solução é ótima.
      Testar só ao retirar da fila daria o mesmo custo, mas expandiria o resto
      do penúltimo nível à toa.
    - Pressupõe custo 1 por ação (é o caso deste problema).
    """

    name = "BFS"

    def __init__(self, board: RushHourBoard):
        self.board = board

    def solve(self, initial_state) -> SearchResult:
        t0 = time.perf_counter()
        start = frozenset(initial_state.items())
        parents = {start: (None, None)}
        generated, expanded = 1, 0

        if self.board.is_goal(initial_state):
            return self._result(True, parents, start, generated, expanded, 0, t0)

        frontier = deque([start])
        visited = {start}
        max_frontier = 1

        while frontier:
            state = frontier.popleft()
            successors = self.board.get_successors(dict(state))
            expanded += 1
            generated += len(successors)

            for next_state, _cost, action in successors:
                if next_state in visited:
                    continue
                visited.add(next_state)
                parents[next_state] = (state, action)
                if self.board.is_goal(dict(next_state)):
                    max_frontier = max(max_frontier, len(frontier))
                    return self._result(True, parents, next_state, generated, expanded,
                                        max_frontier, t0)
                frontier.append(next_state)

            max_frontier = max(max_frontier, len(frontier))

        return self._result(False, parents, None, generated, expanded, max_frontier, t0)

    def _result(self, found, parents, goal, generated, expanded, max_frontier, t0):
        path, states = reconstruct(parents, goal) if found else ([], [])
        return SearchResult(
            algorithm=self.name, heuristic=None, found=found,
            cost=len(path) if found else None, path=path, states=states,
            generated=generated, expanded=expanded, reexpanded=0,
            max_frontier=max_frontier, time_ms=(time.perf_counter() - t0) * 1000,
        )
