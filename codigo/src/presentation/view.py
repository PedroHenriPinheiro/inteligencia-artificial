from domain.model import RushHourBoard
from service.heuristic import CascadeHeuristic


class TerminalCLI:
    @staticmethod
    def render_board(board: RushHourBoard, state: dict) -> str:
        """Retorna o tabuleiro como texto, mostrando o id completo de cada veículo.

        Antes era usado só o primeiro caractere do id (str(v_id)[0]), então os
        veículos "1", "10" e "11" apareciam todos como "1". Agora cada célula tem
        a largura do maior id, e ids de vários caracteres aparecem inteiros.
        """
        width = max([1] + [len(str(v_id)) for v_id in state])
        grid = [['.' for _ in range(board.grid_size)] for _ in range(board.grid_size)]
        for v_id, var_coord in state.items():
            v = board.vehicles[v_id]
            for i in range(v.length):
                if v.orientation == 'H':
                    grid[v.fixed_axis][var_coord + i] = str(v_id)
                else:
                    grid[var_coord + i][v.fixed_axis] = str(v_id)

        lines = [" ".join(cell.rjust(width) for cell in row) for row in grid]
        separator = "-" * len(lines[0])
        return "\n".join([separator] + lines + [separator])

    @staticmethod
    def print_board(board: RushHourBoard, state: dict):
        print("\n" + TerminalCLI.render_board(board, state) + "\n")

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
        target_cells = set((X_row, c) for c in range(X_col + X_v.length, board.grid_size))

        print(f"Custo de Saída de X (C): 1")
        print(f"Células da linha {X_row} que X precisa desocupar: {target_cells}\n")

        deps = heuristic.dependencies(state_dict)

        if deps is None:
            print("-> NENHUMA ROTA GEOMÉTRICA PARA ALGUM BLOQUEADOR.")
            print("h(n) Calculado: Infinito")
        else:
            print(f"Conjunto de Dependências Garantidas mapeado pela Cascata:\n-> {deps}\n")
            print(f"Quantidade de veículos estruturalmente inevitáveis: {len(deps)}")
            print(f"h(n) Calculado: 1 (X) + {len(deps)} (Cascata) = {1 + len(deps)}")
        print("="*50 + "\n")

    @staticmethod
    def print_result(result):
        """Mostra o resultado de qualquer busca (SearchResult)."""
        nome = result.algorithm + (f" ({result.heuristic})" if result.heuristic else "")
        print("\n" + "-" * 50)
        if result.found:
            print(f"✅ {nome}: solução encontrada. Custo (nº de ações): {result.cost}")
        else:
            print(f"❌ {nome}: nenhuma solução encontrada.")
        print(f"   Gerados: {result.generated} | Expandidos: {result.expanded} | "
              f"Reexpandidos: {result.reexpanded}")
        print(f"   Fronteira máxima: {result.max_frontier} | Tempo: {result.time_ms:.1f} ms")
        print("-" * 50)
        if result.found:
            print("TRACE DA SOLUÇÃO (Passo a Passo):")
            for i, step in enumerate(result.path, 1):
                print(f"Passo {i}: {step}")
            print("-" * 50)

    @staticmethod
    def print_solution_steps(board: RushHourBoard, result):
        """Desenha o tabuleiro depois de cada ação da solução."""
        if not result.found:
            return
        for i, (acao, estado) in enumerate(zip(result.path, result.states[1:]), 1):
            print(f"\nPasso {i}: {acao}")
            if estado:
                print(TerminalCLI.render_board(board, estado))
            else:
                print("(X saiu do tabuleiro)")
