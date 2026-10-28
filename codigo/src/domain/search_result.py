from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchResult:
    """Resultado de uma busca, com as métricas usadas nos experimentos.

    Definições (ver 05-experimentos/definicao-metricas.md):
      generated     estado inicial + todos os sucessores devolvidos por
                    get_successors em cada expansão (inclui repetidos e o
                    objetivo). É o mesmo critério para BFS e A*.
      expanded      estados para os quais get_successors foi chamado.
      reexpanded    (A*) expansões de um estado que já tinha sido expandido
                    antes, porque foi reencontrado com g menor. Fica 0 com
                    heurística consistente.
      max_frontier  maior número de estados DISTINTOS esperando na fronteira
                    (entradas desatualizadas da heap do A* não contam).
      time_ms       tempo de parede da busca, incluindo o cálculo de h.
    """
    algorithm: str
    heuristic: Optional[str]
    found: bool
    cost: Optional[int]
    path: List[str] = field(default_factory=list)      # descrição de cada ação
    states: List[dict] = field(default_factory=list)   # estado inicial ... objetivo
    generated: int = 0
    expanded: int = 0
    reexpanded: int = 0
    max_frontier: int = 0
    time_ms: float = 0.0

    def to_row(self, instance=""):
        """Linha para o CSV de resultados (sem caminho e estados)."""
        return {
            "instancia": instance,
            "algoritmo": self.algorithm,
            "heuristica": self.heuristic or "",
            "encontrou": self.found,
            "custo": "" if self.cost is None else self.cost,
            "gerados": self.generated,
            "expandidos": self.expanded,
            "reexpandidos": self.reexpanded,
            "fronteira_max": self.max_frontier,
            "tempo_ms": round(self.time_ms, 3),
        }
