"""Compatibilidade: as heurísticas agora ficam no pacote service/heuristics/.

Este módulo só reexporta os nomes antigos para que `solver.py`, `view.py` e os
testes existentes continuem funcionando. Código novo deve importar de
`service.heuristics`. Pode ser removido quando ninguém mais o importar.
"""

from service.heuristics import (  # noqa: F401
    HEURISTICAS, CascadeHeuristic, H0Distancia, H1Bloqueadores, Heuristic, ZeroHeuristic)
