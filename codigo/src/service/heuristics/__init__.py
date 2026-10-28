"""Heurísticas do projeto. Todas herdam de `Heuristic` (base.py).

    zero    h = 0 (controle: A* vira busca de custo uniforme)
    h0      distância de X até a saída em células   (ideia original)
    h1      1 + bloqueadores diretos distintos
    hfinal  cascata corrigida (IH02)
"""

from service.heuristics.base import Heuristic, ZeroHeuristic
from service.heuristics.h0_distancia import H0Distancia
from service.heuristics.h1_bloqueadores import H1Bloqueadores
from service.heuristics.hfinal_cascata import CascadeHeuristic

# Heurísticas disponíveis por nome (linha de comando, interface, experimentos).
HEURISTICAS = {
    "zero": ZeroHeuristic,
    "h0": H0Distancia,
    "h1": H1Bloqueadores,
    "hfinal": CascadeHeuristic,
}

__all__ = ["Heuristic", "ZeroHeuristic", "H0Distancia", "H1Bloqueadores",
           "CascadeHeuristic", "HEURISTICAS"]
