"""Testes da BFS, do A* com heurística plugável e das métricas (SearchResult).

    pytest codigo/testes/test_solvers.py
"""

import os
import random
import sys

import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "..", "src")))
sys.path.insert(0, AQUI)

from infra.board_loader import parse_board  # noqa: E402
from service.bfs_solver import BFSSolver  # noqa: E402
from service.heuristic import CascadeHeuristic, Heuristic, ZeroHeuristic  # noqa: E402
from service.solver import AStarSolver  # noqa: E402
from verificar_admissibilidade import (  # noqa: E402
    INF, calcular_h_estrela, gerar_tabuleiro, tabuleiro_exemplo)


def todos_os_solvers(board):
    return [BFSSolver(board),
            AStarSolver(board, ZeroHeuristic(board)),
            AStarSolver(board, CascadeHeuristic(board))]


def caminho_valido(board, result):
    """Cada estado da solução é sucessor do anterior pela ação registrada."""
    assert len(result.states) == result.cost + 1 == len(result.path) + 1
    for antes, depois, acao in zip(result.states, result.states[1:], result.path):
        sucessores = {s: a for s, _, a in board.get_successors(antes)}
        assert sucessores.get(frozenset(depois.items())) == acao
    assert board.is_goal(result.states[-1])
    return True


# --------------------------------------------------------------------------
# Correção: todos encontram o custo ótimo
# --------------------------------------------------------------------------
def test_exemplo_6x6_custo_12_em_todos():
    board, estado = tabuleiro_exemplo()
    for solver in todos_os_solvers(board):
        r = solver.solve(estado)
        assert r.found and r.cost == 12, r.algorithm
        assert caminho_valido(board, r)


def test_custo_igual_ao_h_estrela_em_tabuleiros_aleatorios():
    rng = random.Random(2026)
    testados = 0
    while testados < 15:
        board, estado = gerar_tabuleiro(rng, 6, 11)
        ref = calcular_h_estrela(board, estado, 60_000)
        if ref is None or ref[3][0] == INF:
            continue
        h_estrela = ref[3][0]
        for solver in todos_os_solvers(board):
            r = solver.solve(estado)
            assert r.found and r.cost == h_estrela, (r.algorithm, r.heuristic)
            assert caminho_valido(board, r)
        testados += 1


def test_x_com_caminho_livre_custo_1():
    board, estado = parse_board("""
        . . . .
        X X . .
        . . . .
        . . . .
    """)
    for solver in todos_os_solvers(board):
        r = solver.solve(estado)
        assert r.found and r.cost == 1 and r.path[-1].startswith("Veículo [X]")


def test_estado_inicial_ja_objetivo():
    board, estado = parse_board("""
        . . .
        X X .
        . . .
    """)
    del estado['X']  # X já saiu
    for solver in todos_os_solvers(board):
        r = solver.solve(estado)
        assert r.found and r.cost == 0 and r.path == [] and r.expanded == 0


# --------------------------------------------------------------------------
# Instância sem solução
# --------------------------------------------------------------------------
SEM_SOLUCAO = """
    . . . . .
    X X . A A
    . B . . .
    . B . . .
    . . . . .
"""


def test_sem_solucao_bfs_esgota_o_espaco():
    board, estado = parse_board(SEM_SOLUCAO)
    r = BFSSolver(board).solve(estado)
    assert not r.found and r.cost is None and r.path == [] and r.states == []
    assert r.expanded > 1  # visitou todos os estados alcançáveis


def test_sem_solucao_cascata_detecta_sem_expandir():
    board, estado = parse_board(SEM_SOLUCAO)
    r = AStarSolver(board, CascadeHeuristic(board)).solve(estado)
    assert not r.found and r.expanded == 0  # h = inf no estado inicial


# --------------------------------------------------------------------------
# Métricas
# --------------------------------------------------------------------------
def test_metricas_coerentes():
    board, estado = tabuleiro_exemplo()
    for solver in todos_os_solvers(board):
        r = solver.solve(estado)
        assert r.generated >= r.expanded >= 1
        assert r.max_frontier >= 1
        assert r.time_ms > 0
        assert set(r.to_row("ex")) == {"instancia", "algoritmo", "heuristica", "encontrou",
                                       "custo", "gerados", "expandidos", "reexpandidos",
                                       "fronteira_max", "tempo_ms"}


def test_gerados_contam_todos_os_sucessores():
    """gerados = 1 (inicial) + soma do nº de sucessores de cada expandido."""
    board, estado = parse_board("""
        . . . .
        A X X .
        A . . .
        . . . .
    """)
    r = BFSSolver(board).solve(estado)
    # Expande só o inicial; X pode ir 1 casa à direita ou sair: 2 sucessores.
    # A (vertical, col 0, linhas 1-2) pode subir 1 ou descer 1: 2 sucessores.
    assert (r.expanded, r.generated, r.cost) == (1, 5, 1)


def test_astar_nao_expande_o_mesmo_estado_duas_vezes_com_h_zero():
    """Com h = 0 (consistente), nenhuma reexpansão; entradas antigas da heap
    são descartadas e não contam como expandidas."""
    rng = random.Random(7)
    for _ in range(10):
        board, estado = gerar_tabuleiro(rng, 6, 11)
        ref = calcular_h_estrela(board, estado, 60_000)
        if ref is None:
            continue
        r = AStarSolver(board, ZeroHeuristic(board)).solve(estado)
        assert r.reexpanded == 0
        assert r.expanded <= len(ref[0])  # nunca mais que o nº de estados distintos


def test_cascata_expande_menos_que_bfs_no_exemplo():
    board, estado = tabuleiro_exemplo()
    bfs = BFSSolver(board).solve(estado)
    astar = AStarSolver(board, CascadeHeuristic(board)).solve(estado)
    assert astar.expanded < bfs.expanded


# --------------------------------------------------------------------------
# Interface Heuristic
# --------------------------------------------------------------------------
def test_heuristica_qualquer_que_herde_da_interface():
    class BloqueadoresDiretos(Heuristic):
        name = "bloqueadores-diretos"

        def calculate(self, state_dict):
            if 'X' not in state_dict:
                return 0
            ocupadas = self.board.get_occupied_cells(state_dict)
            x = self.board.vehicles['X']
            frente = range(state_dict['X'] + x.length, self.board.grid_size)
            return 1 + len({ocupadas[(x.fixed_axis, c)] for c in frente
                            if (x.fixed_axis, c) in ocupadas})

    board, estado = tabuleiro_exemplo()
    r = AStarSolver(board, BloqueadoresDiretos(board)).solve(estado)
    assert r.found and r.cost == 12 and r.heuristic == "bloqueadores-diretos"


def test_rejeita_objeto_que_nao_e_heuristic():
    board, _ = tabuleiro_exemplo()

    class SoTemCalculate:
        def calculate(self, state_dict):
            return 0

    with pytest.raises(TypeError):
        AStarSolver(board, SoTemCalculate())


def test_interface_abstrata_nao_instancia():
    board, _ = tabuleiro_exemplo()
    with pytest.raises(TypeError):
        Heuristic(board)
