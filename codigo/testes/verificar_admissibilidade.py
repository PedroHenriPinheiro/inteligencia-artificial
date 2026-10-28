"""Verificador empírico da CascadeHeuristic.

Para cada tabuleiro aleatório pequeno (seed fixa):
  1. explora TODO o componente de estados alcançáveis a partir do estado inicial;
  2. calcula o custo ótimo real h*(n) de cada estado por BFS a partir dos estados
     em que X já pode sair (os movimentos de deslize são reversíveis, então o
     grafo é não direcionado);
  3. verifica admissibilidade:  h(n) <= h*(n)
  4. verifica consistência:      h(n) <= 1 + h(n') para toda ação n -> n'
  5. imprime contraexemplos com o tabuleiro desenhado.

Passar nestes testes NÃO prova admissibilidade; só não encontrou contraexemplo
na amostra. Um contraexemplo, porém, refuta a propriedade.

Variantes da heurística (--variante):
    original  -> ciclo na cascata = infinito (versão do commit fbe748c)
    continue  -> correção da equipe: ciclo é ignorado
    colinear  -> continue + regra colinear (padrão atual do código)

Uso:
    python3 codigo/testes/verificar_admissibilidade.py
    python3 codigo/testes/verificar_admissibilidade.py --variante original
    python3 codigo/testes/verificar_admissibilidade.py --tabuleiros 500 --seed 7
    pytest codigo/testes/verificar_admissibilidade.py
"""

import argparse
import math
import os
import random
import sys
from collections import deque

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))

from domain.model import RushHourBoard  # noqa: E402
from service.heuristic import CascadeHeuristic  # noqa: E402
from presentation.view import TerminalCLI  # noqa: E402

INF = math.inf

VARIANTES = {
    "original": dict(ciclo_como_deadlock=True, regra_colinear=False),
    "continue": dict(ciclo_como_deadlock=False, regra_colinear=False),
    "colinear": dict(ciclo_como_deadlock=False, regra_colinear=True),
}


# ---------------------------------------------------------------------------
# Geração de tabuleiros
# ---------------------------------------------------------------------------
def gerar_tabuleiro(rng, tamanho, num_veiculos):
    """Gera um tabuleiro aleatório. X fica na linha (tamanho // 2) - 1."""
    board = RushHourBoard(grid_size=tamanho)
    estado = {}
    ocupadas = set()

    def celulas(orient, fixo, inicio, comp):
        return [(fixo, inicio + i) if orient == 'H' else (inicio + i, fixo) for i in range(comp)]

    linha_x = tamanho // 2 - 1
    col_x = rng.randint(0, tamanho - 3)
    board.add_vehicle('X', 'H', 2, linha_x)
    estado['X'] = col_x
    ocupadas.update(celulas('H', linha_x, col_x, 2))

    proximo_id, tentativas = 0, 0
    while len(estado) < num_veiculos + 1 and tentativas < 2000:
        tentativas += 1
        orient = rng.choice(['H', 'V'])
        comp = rng.choice([2, 2, 3])
        fixo = rng.randint(0, tamanho - 1)
        if orient == 'H' and fixo == linha_x:
            continue  # nenhum outro horizontal na linha de X
        inicio = rng.randint(0, tamanho - comp)
        cs = celulas(orient, fixo, inicio, comp)
        if any(c in ocupadas for c in cs):
            continue
        vid = str(proximo_id)
        board.add_vehicle(vid, orient, comp, fixo)
        estado[vid] = inicio
        ocupadas.update(cs)
        proximo_id += 1
    return board, estado


# ---------------------------------------------------------------------------
# Cálculo de h* exato
# ---------------------------------------------------------------------------
def calcular_h_estrela(board, estado_inicial, max_estados):
    """Retorna (estados, adj, h_estrela) ou None se o componente for grande demais.

    estados: lista de frozensets (sem o estado objetivo)
    adj[i]: lista de (j, descricao) para vizinhos não objetivo
    sai[i]: True se do estado i existe a ação de saída de X
    h_estrela[i]: custo ótimo restante (INF se insolúvel)
    """
    inicio = frozenset(estado_inicial.items())
    indice = {inicio: 0}
    estados = [inicio]
    adj = [[]]
    sai = [False]
    fila = deque([0])
    while fila:
        i = fila.popleft()
        for prox, _, desc in board.get_successors(dict(estados[i])):
            if board.is_goal(dict(prox)):
                sai[i] = True
                continue
            j = indice.get(prox)
            if j is None:
                if len(estados) >= max_estados:
                    return None
                j = len(estados)
                indice[prox] = j
                estados.append(prox)
                adj.append([])
                sai.append(False)
                fila.append(j)
            adj[i].append((j, desc))

    h_estrela = [INF] * len(estados)
    fila = deque()
    for i, pode_sair in enumerate(sai):
        if pode_sair:
            h_estrela[i] = 1
            fila.append(i)
    while fila:
        i = fila.popleft()
        for j, _ in adj[i]:  # grafo não direcionado (deslizes são reversíveis)
            if h_estrela[j] == INF:
                h_estrela[j] = h_estrela[i] + 1
                fila.append(j)
    return estados, adj, sai, h_estrela


# ---------------------------------------------------------------------------
# Verificação
# ---------------------------------------------------------------------------
def verificar(seed=42, tabuleiros=200, tamanho=6, veiculos=12, max_estados=150_000,
              variante="colinear", max_exemplos=3, verbose=True):
    rng = random.Random(seed)
    r = {
        "tabuleiros_analisados": 0, "tabuleiros_insoluveis": 0, "tabuleiros_pulados": 0,
        "estados": 0, "transicoes": 0,
        "superestimativas": 0, "infinitos_com_solucao": 0, "violacoes_consistencia": 0,
        "estados_com_X_em_D": 0, "soma_h": 0, "soma_h_estrela": 0,
        "exemplos_adm": [], "exemplos_cons": [],
    }

    for _ in range(tabuleiros):
        board, estado = gerar_tabuleiro(rng, tamanho, veiculos)
        res = calcular_h_estrela(board, estado, max_estados)
        if res is None:
            r["tabuleiros_pulados"] += 1
            continue
        estados, adj, sai, h_estrela = res
        if h_estrela[0] == INF:
            r["tabuleiros_insoluveis"] += 1
            continue
        r["tabuleiros_analisados"] += 1

        heur = CascadeHeuristic(board, **VARIANTES[variante])
        h = [heur.calculate(dict(s)) for s in estados]

        for i, s in enumerate(estados):
            r["estados"] += 1
            if h_estrela[i] == INF:
                continue
            if h[i] != INF:
                r["soma_h"] += h[i]
                r["soma_h_estrela"] += h_estrela[i]
            deps = heur.dependencies(dict(s))
            if deps is not None and 'X' in deps:
                r["estados_com_X_em_D"] += 1
            if h[i] > h_estrela[i]:
                r["superestimativas"] += 1
                if h[i] == INF:
                    r["infinitos_com_solucao"] += 1
                if len(r["exemplos_adm"]) < max_exemplos:
                    r["exemplos_adm"].append((board, dict(s), h[i], h_estrela[i], deps))

            # Consistência: h(n) <= 1 + h(n') (inclui a ação de saída: h(objetivo)=0)
            vizinhos = [(h[j], j, desc) for j, desc in adj[i]]
            if sai[i]:
                vizinhos.append((0, None, "X sai do tabuleiro"))
            for h_viz, j, desc in vizinhos:
                r["transicoes"] += 1
                if h[i] > 1 + h_viz:
                    r["violacoes_consistencia"] += 1
                    if len(r["exemplos_cons"]) < max_exemplos:
                        viz = dict(estados[j]) if j is not None else {}
                        r["exemplos_cons"].append(
                            (board, dict(s), viz, desc, h[i], h_viz, deps,
                             heur.dependencies(viz) if viz else set(),
                             h_estrela[i], h_estrela[j] if j is not None else 0))

    if verbose:
        imprimir_relatorio(r, seed, tamanho, veiculos, variante)
    return r


def imprimir_relatorio(r, seed, tamanho, veiculos, variante):
    modo = {"original": "ORIGINAL (ciclo = infinito)",
            "continue": "CONTINUE (ciclo ignorado)",
            "colinear": "COLINEAR (ciclo ignorado + regra colinear)"}[variante]
    print("=" * 64)
    print(f"Verificação da CascadeHeuristic — modo {modo}")
    print(f"seed={seed}  tabuleiro={tamanho}x{tamanho}  veículos≈{veiculos}")
    print("=" * 64)
    print(f"Tabuleiros analisados: {r['tabuleiros_analisados']}  "
          f"(insolúveis: {r['tabuleiros_insoluveis']}, pulados por tamanho: {r['tabuleiros_pulados']})")
    print(f"Estados verificados:   {r['estados']}")
    print(f"Transições verificadas: {r['transicoes']}")
    print(f"Superestimativas h > h*:           {r['superestimativas']}")
    print(f"  dos quais h = inf com solução:   {r['infinitos_com_solucao']}")
    print(f"Violações h(n) > 1 + h(n'):        {r['violacoes_consistencia']}")
    print(f"Estados em que X aparece em D(n):  {r['estados_com_X_em_D']}")
    if r["soma_h_estrela"]:
        print(f"Informatividade média  Σh/Σh*:     {r['soma_h'] / r['soma_h_estrela']:.3f}")

    for k, (board, s, h, he, deps) in enumerate(r["exemplos_adm"], 1):
        print(f"\n--- Contraexemplo de ADMISSIBILIDADE #{k}: h={h}, h*={he}, D={deps}")
        print(TerminalCLI.render_board(board, s))

    for k, (board, s, viz, desc, h1, h2, d1, d2, he1, he2) in enumerate(r["exemplos_cons"], 1):
        print(f"\n--- Contraexemplo de CONSISTÊNCIA #{k}: h(n)={h1} > 1 + h(n')={1 + h2}"
              f"   [h*(n)={he1}, h*(n')={he2}]")
        print(f"n  (D={sorted(d1) if d1 is not None else None}):")
        print(TerminalCLI.render_board(board, s))
        print(f"ação: {desc}")
        print(f"n' (D={sorted(d2) if d2 is not None else None}):")
        if viz:
            print(TerminalCLI.render_board(board, viz))
        else:
            print("(objetivo)")


# ---------------------------------------------------------------------------
# Exemplo registrado pela equipe (h* = 12)
# ---------------------------------------------------------------------------
def tabuleiro_exemplo():
    """O 6x6 do relatório. Os dois carros que a view antiga mostrava como "1"
    são aqui "1" (linha 0) e "11" (linha 3)."""
    board = RushHourBoard(grid_size=6)
    veiculos = [  # id, orientação, comprimento, eixo fixo, coordenada variável
        ('X', 'H', 2, 2, 3), ('1', 'H', 2, 0, 1), ('11', 'H', 2, 3, 3),
        ('2', 'V', 2, 1, 1), ('7', 'V', 2, 2, 1), ('8', 'V', 3, 5, 1),
        ('4', 'H', 3, 3, 0), ('0', 'V', 2, 0, 4), ('5', 'H', 3, 4, 1),
        ('3', 'H', 2, 4, 4), ('9', 'H', 2, 5, 1), ('6', 'H', 3, 5, 3),
    ]
    estado = {}
    for vid, o, comp, fixo, var in veiculos:
        board.add_vehicle(vid, o, comp, fixo)
        estado[vid] = var
    return board, estado


# ---------------------------------------------------------------------------
# Testes pytest
# ---------------------------------------------------------------------------
def test_exemplo_do_relatorio():
    board, estado = tabuleiro_exemplo()
    _, _, _, h_estrela = calcular_h_estrela(board, estado, 500_000)
    assert h_estrela[0] == 12
    assert CascadeHeuristic(board, **VARIANTES["original"]).calculate(estado) == INF
    for v in ("continue", "colinear"):
        assert CascadeHeuristic(board, **VARIANTES[v]).calculate(estado) <= 12


def test_view_mostra_ids_completos():
    board, estado = tabuleiro_exemplo()
    texto = TerminalCLI.render_board(board, estado)
    assert "11" in texto.split("\n")[4]  # linha 3 do tabuleiro


def test_corrigidas_sem_superestimativa_na_amostra():
    for v in ("continue", "colinear"):
        r = verificar(seed=1, tabuleiros=40, variante=v, verbose=False)
        assert r["tabuleiros_analisados"] > 0
        assert r["superestimativas"] == 0


def test_original_tem_infinito_falso_na_amostra():
    r = verificar(seed=1, tabuleiros=40, variante="original", verbose=False)
    assert r["infinitos_com_solucao"] > 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tabuleiros", type=int, default=200)
    p.add_argument("--tamanho", type=int, default=6)
    p.add_argument("--veiculos", type=int, default=12)
    p.add_argument("--max-estados", type=int, default=150_000)
    p.add_argument("--max-exemplos", type=int, default=3)
    p.add_argument("--variante", choices=sorted(VARIANTES), default="colinear")
    a = p.parse_args()
    res = verificar(a.seed, a.tabuleiros, a.tamanho, a.veiculos, a.max_estados,
                    a.variante, a.max_exemplos)
    sys.exit(1 if res["superestimativas"] else 0)
