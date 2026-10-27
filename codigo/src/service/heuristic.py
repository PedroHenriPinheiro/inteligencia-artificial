from domain.model import RushHourBoard

class CascadeHeuristic:
    """Service: Isola a complexidade matemática da heurística (Efeito Cascata)."""
    def __init__(self, board: RushHourBoard):
        self.board = board

    def calculate(self, state_dict):
        if 'X' not in state_dict:
            return 0

        X_v = self.board.vehicles['X']
        X_col = state_dict['X']
        X_row = X_v.fixed_axis

        occupied = self.board.get_occupied_cells(state_dict)
        target_cells_for_x = set((X_row, c) for c in range(X_col + X_v.length, self.board.grid_size))

        guaranteed_deps = self._get_guaranteed_deps(state_dict, occupied, target_cells_for_x, visited=frozenset())

        if guaranteed_deps is None:
            return float('inf')

        return 1 + len(guaranteed_deps)

    def _get_guaranteed_deps(self, state_dict, occupied, target_cells, visited):
        """Método encapsulado para cálculo recursivo de interseções."""
        deps = set()
        vehicles_in_way = set(occupied[cell] for cell in target_cells if cell in occupied)

        if not vehicles_in_way:
            return deps

        for u_id in vehicles_in_way:
            if u_id in visited:
                return None

            deps.add(u_id)
            u_v = self.board.vehicles[u_id]
            u_head = state_dict[u_id]
            u_axis = u_v.fixed_axis

            u_current_cells = set(
                (u_axis, u_head + i) if u_v.orientation == 'H' else (u_head + i, u_axis)
                for i in range(u_v.length)
            )
            intersecting = target_cells.intersection(u_current_cells)
            if not intersecting: continue

            # --- ROTA NEGATIVA ---
            min_intersect = min(c[1] if u_v.orientation == 'H' else c[0] for c in intersecting)
            target_head_neg = min_intersect - u_v.length
            possible_neg = (target_head_neg >= 0)
            deps_neg = None
            if possible_neg:
                cells_to_clear_neg = set(
                    (u_axis, r) if u_v.orientation == 'H' else (r, u_axis)
                    for r in range(target_head_neg, u_head)
                )
                deps_neg = self._get_guaranteed_deps(state_dict, occupied, cells_to_clear_neg, visited | {u_id})

            # --- ROTA POSITIVA ---
            max_intersect = max(c[1] if u_v.orientation == 'H' else c[0] for c in intersecting)
            target_head_pos = max_intersect + 1
            possible_pos = (target_head_pos + u_v.length - 1 < self.board.grid_size)
            deps_pos = None
            if possible_pos:
                cells_to_clear_pos = set(
                    (u_axis, r) if u_v.orientation == 'H' else (r, u_axis)
                    for r in range(u_head + u_v.length, target_head_pos + u_v.length)
                )
                deps_pos = self._get_guaranteed_deps(state_dict, occupied, cells_to_clear_pos, visited | {u_id})

            # --- INTERSEÇÃO ---
            valid_branches = [d for d in (deps_neg, deps_pos) if d is not None]
            if len(valid_branches) == 0:
                return None
            elif len(valid_branches) == 1:
                deps.update(valid_branches[0])
            else:
                deps.update(valid_branches[0].intersection(valid_branches[1]))

        return deps