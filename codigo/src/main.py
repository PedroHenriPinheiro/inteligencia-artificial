import random
from domain.model import RushHourBoard
from service.heuristic import CascadeHeuristic
from service.solver import AStarSolver
from presentation.view import TerminalCLI

def generate_random_board(grid_size=12, num_vehicles=10):
    board = RushHourBoard(grid_size=grid_size)
    initial_state = {}
    occupied = set()

    def is_free(orientation, fixed_axis, start, length):
        for i in range(length):
            cell = (fixed_axis, start + i) if orientation == 'H' else (start + i, fixed_axis)
            if cell in occupied: return False
        return True

    x_row = 2
    x_col = random.randint(0, (grid_size // 2) - 1)
    board.add_vehicle('X', 'H', 2, x_row)
    initial_state['X'] = x_col
    for i in range(2): occupied.add((x_row, x_col + i))

    attempts, v_id = 0, 0
    while len(initial_state) < num_vehicles and attempts < 1000:
        attempts += 1
        orientation = random.choice(['H', 'V'])
        length = random.choice([2, 3])
        fixed_axis = random.randint(0, grid_size - 1)
        if orientation == 'H' and fixed_axis == x_row: continue
        start = random.randint(0, grid_size - length)

        if is_free(orientation, fixed_axis, start, length):
            str_id = str(v_id)
            board.add_vehicle(str_id, orientation, length, fixed_axis)
            initial_state[str_id] = start
            for i in range(length):
                cell = (fixed_axis, start + i) if orientation == 'H' else (start + i, fixed_axis)
                occupied.add(cell)
            v_id += 1

    return board, initial_state

if __name__ == "__main__":
    TAMANHO_TABULEIRO = 12
    QUANTIDADE_VEICULOS = 15

    print(f"Gerando tabuleiro aleatório {TAMANHO_TABULEIRO}x{TAMANHO_TABULEIRO} com {QUANTIDADE_VEICULOS} veículos...")

    # 1. Inicializa o Model
    board, initial_state = generate_random_board(TAMANHO_TABULEIRO, QUANTIDADE_VEICULOS)

    # 2. Inicializa os Services
    heuristic_service = CascadeHeuristic(board)
    solver_service = AStarSolver(board, heuristic_service)

    # 3. Interage com a View
    TerminalCLI.print_board(board, initial_state)
    print(f"Posições Iniciais (Dicionário): {initial_state}\n")
    print("Iniciando busca A* (Pode levar tempo em deadlocks complexos)...")

    # 4. Executa Lógica e Exibe Resultados
    path, cost = solver_service.solve(initial_state)
    TerminalCLI.print_results(cost, path)
    TerminalCLI.print_diagnostic(board, initial_state, heuristic_service)