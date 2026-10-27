from domain.model import RushHourBoard
from service.heuristic import CascadeHeuristic

class TerminalCLI:
    @staticmethod
    def print_board(board: RushHourBoard, state: dict):
        grid = [['.' for _ in range(board.grid_size)] for _ in range(board.grid_size)]
        for v_id, var_coord in state.items():
            v = board.vehicles[v_id]
            char = str(v_id)[0] if v_id != 'X' else 'X'
            for i in range(v.length):
                if v.orientation == 'H':
                    grid[v.fixed_axis][var_coord + i] = char
                else:
                    grid[var_coord + i][v.fixed_axis] = char

        print("\n" + "---" * board.grid_size)
        for r in range(board.grid_size):
            print(" ".join(grid[r]))
        print("---" * board.grid_size + "\n")

    @staticmethod
    def print_diagnostic(board: RushHourBoard, state_dict: dict, heuristic: CascadeHeuristic):
        print("\n" + "="*50)
        print("🧠 RAIO-X DA NOVA HEURÍSTICA (Efeito Cascata Profundo)")
        print("="*50)
        if 'X' not in state_dict:
            print("X já saiu do tabuleiro. h(n) = 0\n" + "="*50)
            return

        X_v = board.vehicles['X']
        X_col = state_dict['X']
        X_row = X_v.fixed_axis

        occupied = board.get_occupied_cells(state_dict)
        target_cells = set((X_row, c) for c in range(X_col + X_v.length, board.grid_size))

        print(f"Custo de Saída de X (C): 1")
        print(f"Células da linha {X_row} que X precisa desocupar: {target_cells}\n")

        deps = heuristic._get_guaranteed_deps(state_dict, occupied, target_cells, visited=frozenset())

        if deps is None:
            print("-> DEADLOCK ABSOLUTO DETECTADO NA CADEIA.")
            print("h(n) Calculado: Infinito")
        else:
            print(f"Conjunto de Dependências Garantidas mapeado pela Cascata:\n-> {deps}\n")
            print(f"Quantidade de veículos estruturalmente inevitáveis: {len(deps)}")
            print(f"h(n) Calculado: 1 (X) + {len(deps)} (Cascata) = {1 + len(deps)}")
        print("="*50 + "\n")

    @staticmethod
    def print_results(cost, path):
        if cost != -1:
            print(f"\n✅ RESULTADO: Busca finalizada com SUCESSO! Custo mínimo de ações: {cost}")
            print("-" * 50)
            print("TRACE DA SOLUÇÃO (Passo a Passo):")
            for i, step in enumerate(path, 1):
                print(f"Passo {i}: {step}")
            print("-" * 50)
        else:
            print("\n❌ RESULTADO: Nenhuma solução encontrada. (Deadlock matemático no tabuleiro)")
            print("-" * 50)