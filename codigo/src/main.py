import argparse
import random
import sys

from domain.model import RushHourBoard
from infra.board_loader import BoardFormatError, avisos, load_board
from service.bfs_solver import BFSSolver
from service.heuristic import HEURISTICAS, CascadeHeuristic
from service.solver import AStarSolver
from presentation.view import TerminalCLI


def generate_random_board(grid_size=12, num_vehicles=10):
    board = RushHourBoard(grid_size=grid_size, exit_col=grid_size - 1)
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


def parse_args():
    p = argparse.ArgumentParser(description="Resolvedor de Rush Hour NxN (BFS e A*).")
    p.add_argument("instancia", nargs="?",
                   help="arquivo .txt da instância (sem ele, gera um tabuleiro aleatório)")
    p.add_argument("--algoritmo", choices=["astar", "bfs"], default="astar")
    p.add_argument("--heuristica", choices=sorted(HEURISTICAS), default="cascata",
                   help="heurística do A* (ignorada na BFS)")
    p.add_argument("--passos", action="store_true",
                   help="desenha o tabuleiro depois de cada ação da solução")
    p.add_argument("--tamanho", type=int, default=12, help="tamanho do tabuleiro aleatório")
    p.add_argument("--veiculos", type=int, default=15, help="veículos do tabuleiro aleatório")
    p.add_argument("--seed", type=int, default=None, help="seed do tabuleiro aleatório")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 1. Inicializa o Model (arquivo ou aleatório)
    if args.instancia:
        try:
            board, initial_state = load_board(args.instancia)
        except (BoardFormatError, OSError) as erro:
            print(erro, file=sys.stderr)
            sys.exit(2)
        print(f"Instância carregada: {args.instancia} ({board.grid_size}x{board.grid_size}, "
              f"{len(initial_state)} veículos)")
        for aviso in avisos(board, initial_state):
            print(f"⚠️  AVISO: {aviso}")
    else:
        if args.seed is not None:
            random.seed(args.seed)
        print(f"Gerando tabuleiro aleatório {args.tamanho}x{args.tamanho} "
              f"com {args.veiculos} veículos...")
        board, initial_state = generate_random_board(args.tamanho, args.veiculos)

    # 2. Inicializa os Services
    if args.algoritmo == "bfs":
        solver_service = BFSSolver(board)
    else:
        solver_service = AStarSolver(board, HEURISTICAS[args.heuristica](board))

    # 3. Interage com a View
    TerminalCLI.print_board(board, initial_state)
    print(f"Posições Iniciais (Dicionário): {initial_state}\n")
    print(f"Iniciando busca {solver_service.name}...")

    # 4. Executa Lógica e Exibe Resultados
    result = solver_service.solve(initial_state)
    TerminalCLI.print_result(result)
    if args.passos:
        TerminalCLI.print_solution_steps(board, result)
    TerminalCLI.print_diagnostic(board, initial_state, CascadeHeuristic(board))
