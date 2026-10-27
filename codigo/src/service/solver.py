import heapq
from domain.model import RushHourBoard
from service.heuristic import CascadeHeuristic

class AStarSolver:
    """Service: Executa o algoritmo A* utilizando um Board e uma Heuristic."""
    def __init__(self, board: RushHourBoard, heuristic: CascadeHeuristic):
        self.board = board
        self.heuristic = heuristic

    def solve(self, initial_state):
        start = frozenset(initial_state.items())
        frontier = []
        heapq.heappush(frontier, (self.heuristic.calculate(initial_state), 0, start))

        came_from = {start: (None, "Estado Inicial")}
        cost_so_far = {start: 0}

        while frontier:
            _, current_cost, current_state = heapq.heappop(frontier)
            current_dict = dict(current_state)

            if self.board.is_goal(current_dict):
                return self._reconstruct_path(came_from, start, current_state), cost_so_far[current_state]

            for next_state, action_cost, action_desc in self.board.get_successors(current_dict):
                new_cost = cost_so_far[current_state] + action_cost
                if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_cost
                    priority = new_cost + self.heuristic.calculate(dict(next_state))
                    heapq.heappush(frontier, (priority, new_cost, next_state))
                    came_from[next_state] = (current_state, action_desc)

        return None, -1

    def _reconstruct_path(self, came_from, start, current_state):
        path = []
        state_trace = current_state
        while state_trace != start:
            parent_state, action_taken = came_from[state_trace]
            path.append(action_taken)
            state_trace = parent_state
        path.reverse()
        return path