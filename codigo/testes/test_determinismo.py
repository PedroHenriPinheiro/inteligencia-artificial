"""As contagens das buscas não podem depender da execução do Python.

O estado é um frozenset, e a ordem de iteração de um frozenset depende do hash
das strings, que o Python sorteia a cada processo (PYTHONHASHSEED). Este teste
roda as buscas em PROCESSOS SEPARADOS, cada um com uma PYTHONHASHSEED
diferente, e exige que todas as métricas (menos o tempo) sejam idênticas.

    pytest codigo/testes/test_determinismo.py
"""

import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(AQUI, "..", "src"))
INSTANCIA = os.path.abspath(os.path.join(AQUI, "..", "instancias", "exemplo_6x6_h12.txt"))

# Programa executado em cada processo filho: imprime as métricas em JSON.
PROGRAMA = r"""
import json, random, sys
sys.path[:0] = [sys.argv[1], sys.argv[2]]
from infra.board_loader import load_board
from service.bfs_solver import BFSSolver
from service.solver import AStarSolver
from service.heuristics import HEURISTICAS
from verificar_admissibilidade import gerar_tabuleiro

casos = [load_board(sys.argv[3])]
rng = random.Random(4)
casos += [gerar_tabuleiro(rng, 6, 11) for _ in range(3)]

saida = []
for board, estado in casos:
    solvers = [BFSSolver(board)] + [AStarSolver(board, h(board)) for h in HEURISTICAS.values()]
    for solver in solvers:
        r = solver.solve(estado)
        saida.append([r.algorithm, r.heuristic, r.found, r.cost, r.generated,
                      r.expanded, r.reexpanded, r.max_frontier, r.path])
print(json.dumps(saida))
"""

SEMENTES_DE_HASH = ["0", "1", "2", "3", "12345"]


def rodar_em_processo(semente):
    env = dict(os.environ, PYTHONHASHSEED=semente)
    proc = subprocess.run(
        [sys.executable, "-c", PROGRAMA, SRC, AQUI, INSTANCIA],
        env=env, capture_output=True, text=True, timeout=300, check=True)
    return json.loads(proc.stdout)


def test_metricas_iguais_em_processos_com_hash_diferente():
    resultados = {s: rodar_em_processo(s) for s in SEMENTES_DE_HASH}
    referencia = resultados[SEMENTES_DE_HASH[0]]
    assert len(referencia) > 0
    for semente, resultado in resultados.items():
        assert resultado == referencia, f"PYTHONHASHSEED={semente} deu métricas diferentes"
