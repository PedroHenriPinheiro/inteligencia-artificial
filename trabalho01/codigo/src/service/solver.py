import heapq
import itertools
import math
import time

from domain.model import RushHourBoard
from domain.search_result import SearchResult
from service.heuristic import Heuristic
from service.search_common import reconstruct


class AStarSolver:
    """Service: A* em grafo, com qualquer heurística que herde de `Heuristic`.

    Decisões (ver 05-experimentos/definicao-metricas.md):
    - Verificação de entrada desatualizada ("lazy deletion"): quando um estado
      é reencontrado com g menor, uma nova entrada vai para a heap e a antiga
      fica lá. Ao ser retirada, a antiga é descartada (g > melhor g conhecido)
      e NÃO conta como expansão. Antes ela era expandida de novo.
    - Reabertura permitida: se um estado já expandido for reencontrado com g
      menor, ele volta para a fila e pode ser expandido outra vez
      (`reexpanded`). Isso mantém o A* ótimo com heurística só admissível;
      um conjunto de fechados sem reabertura perderia essa garantia.
    - Teste de objetivo ao RETIRAR da fila (necessário para a otimalidade).
    - Desempate na heap: menor f, depois menor h, depois ordem de inserção
      (determinístico).
    - Estado com h = infinito não entra na fila (com h admissível, h = ∞
      significa sem solução). Ele conta como gerado.
    """

    name = "A*"

    def __init__(self, board: RushHourBoard, heuristic: Heuristic):
        if not isinstance(heuristic, Heuristic):
            raise TypeError("a heurística deve herdar de service.heuristic.Heuristic")
        self.board = board
        self.heuristic = heuristic

    def solve(self, initial_state) -> SearchResult:
        t0 = time.perf_counter()
        start = frozenset(initial_state.items())
        h_cache = {}

        def h(state):
            if state not in h_cache:
                h_cache[state] = self.heuristic.calculate(dict(state))
            return h_cache[state]

        tie = itertools.count()
        best_g = {start: 0}
        parents = {start: (None, None)}
        heap = []
        in_frontier = set()
        ever_expanded = set()
        generated, expanded, reexpanded = 1, 0, 0

        h_start = h(start)
        if h_start != math.inf:
            heapq.heappush(heap, (h_start, h_start, next(tie), 0, start))
            in_frontier.add(start)
        max_frontier = len(in_frontier)

        while heap:
            _f, _h, _, g, state = heapq.heappop(heap)
            if g > best_g[state]:
                continue  # entrada desatualizada: existe outra com g menor
            in_frontier.discard(state)

            state_dict = dict(state)
            if self.board.is_goal(state_dict):
                return self._result(True, parents, state, g, generated, expanded,
                                    reexpanded, max_frontier, t0)

            expanded += 1
            if state in ever_expanded:
                reexpanded += 1
            ever_expanded.add(state)

            successors = self.board.get_successors(state_dict)
            generated += len(successors)
            for next_state, action_cost, action in successors:
                new_g = g + action_cost
                if new_g >= best_g.get(next_state, math.inf):
                    continue
                h_next = h(next_state)
                if h_next == math.inf:
                    continue
                best_g[next_state] = new_g
                parents[next_state] = (state, action)
                heapq.heappush(heap, (new_g + h_next, h_next, next(tie), new_g, next_state))
                in_frontier.add(next_state)

            max_frontier = max(max_frontier, len(in_frontier))

        return self._result(False, parents, None, None, generated, expanded,
                            reexpanded, max_frontier, t0)

    def _result(self, found, parents, goal, cost, generated, expanded, reexpanded,
                max_frontier, t0):
        path, states = reconstruct(parents, goal) if found else ([], [])
        return SearchResult(
            algorithm=self.name, heuristic=self.heuristic.name, found=found,
            cost=cost, path=path, states=states,
            generated=generated, expanded=expanded, reexpanded=reexpanded,
            max_frontier=max_frontier, time_ms=(time.perf_counter() - t0) * 1000,
        )
