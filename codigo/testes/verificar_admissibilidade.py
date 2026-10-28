"""Verificador empírico das heurísticas (admissibilidade e consistência).

Modo exato (padrão), para tabuleiros pequenos com seed fixa:
  1. explora TODO o componente de estados alcançáveis a partir do estado inicial;
  2. calcula o custo ótimo real h*(n) de cada estado por BFS a partir dos estados
     em que X já pode sair (os deslizes são reversíveis, então o grafo é não
     direcionado);
  3. para cada heurística pedida, verifica
       admissibilidade:  h(n) <= h*(n)
       consistência:     h(n) <= 1 + h(n') para toda ação n -> n'
  4. imprime contraexemplos com o tabuleiro desenhado.

Modo local (--local), para tabuleiros grandes (8x8 a 12x12):
  h* é caro demais, mas a consistência é uma propriedade LOCAL. O verificador
  faz passeios aleatórios a partir do estado inicial e testa
  h(n) <= 1 + h(n') em todas as ações de cada estado visitado.

Passar nestes testes NÃO prova nada; só não achou contraexemplo na amostra.
Um contraexemplo, porém, refuta a propriedade.

Heurísticas (--variante, pode repetir; padrão: h0, h1 e hfinal):
    h0        distância de X até a saída em células   (H0 da equipe)
    h1        1 + bloqueadores diretos distintos        (H1)
    hfinal    cascata corrigida                          (Hfinal)
    original  cascata do commit fbe748c (ciclo = infinito)
    continue  cascata só com a correção "continue"
    colinear  o mesmo que hfinal (nome usado em H3-revisao.md)

Uso:
    python3 codigo/testes/verificar_admissibilidade.py
    python3 codigo/testes/verificar_admissibilidade.py --variante original --variante continue
    python3 codigo/testes/verificar_admissibilidade.py --local --tamanho 12 --veiculos 30
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
from service.heuristics import CascadeHeuristic, H0Distancia, H1Bloqueadores  # noqa: E402
from presentation.view import TerminalCLI  # noqa: E402

INF = math.inf

VARIANTES = {
    "h0": H0Distancia,
    "h1": H1Bloqueadores,
    "hfinal": CascadeHeuristic,
    "original": lambda b: CascadeHeuristic(b, ciclo_como_deadlock=True, regra_colinear=False),
    "continue": lambda b: CascadeHeuristic(b, ciclo_como_deadlock=False, regra_colinear=False),
    "colinear": CascadeHeuristic,
}
PADRAO = ("h0", "h1", "hfinal")
ESPERADAS_ADMISSIVEIS = {"h1", "hfinal", "colinear", "continue"}


# ---------------------------------------------------------------------------
# Geração de tabuleiros
# ---------------------------------------------------------------------------
def gerar_tabuleiro(rng, tamanho, num_veiculos):
    """Gera um tabuleiro aleatório. X fica na linha (tamanho // 2) - 1."""
    board = RushHourBoard(grid_size=tamanho, exit_col=tamanho - 1)
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
    """Retorna (estados, adj, sai, h_estrela) ou None se o componente for grande demais.

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
# Modo exato
# ---------------------------------------------------------------------------
def _novo_relatorio():
    return {
        "tabuleiros_analisados": 0, "tabuleiros_insoluveis": 0, "tabuleiros_pulados": 0,
        "estados": 0, "transicoes": 0,
        "superestimativas": 0, "infinitos_com_solucao": 0, "violacoes_consistencia": 0,
        "exatos": 0, "estados_com_X_em_D": 0, "soma_h": 0, "soma_h_estrela": 0,
        "exemplos_adm": [], "exemplos_cons": [],
    }


def verificar(seed=42, tabuleiros=200, tamanho=6, veiculos=12, max_estados=150_000,
              variantes=PADRAO, max_exemplos=3, verbose=True):
    """Devolve {variante: relatório}. h* é calculado uma vez por tabuleiro e
    usado por todas as variantes. Se 'h1' e 'hfinal' estiverem na lista,
    também conta os estados em que hfinal < h1 (chave especial '_dominancia')."""
    rng = random.Random(seed)
    rel = {v: _novo_relatorio() for v in variantes}
    dominancia = {"estados": 0, "hfinal_menor_que_h1": 0}

    for _ in range(tabuleiros):
        board, estado = gerar_tabuleiro(rng, tamanho, veiculos)
        res = calcular_h_estrela(board, estado, max_estados)
        if res is None:
            for r in rel.values():
                r["tabuleiros_pulados"] += 1
            continue
        estados, adj, sai, h_estrela = res
        if h_estrela[0] == INF:
            for r in rel.values():
                r["tabuleiros_insoluveis"] += 1
            continue

        hs = {}
        for v in variantes:
            heur = VARIANTES[v](board)
            hs[v] = [heur.calculate(dict(s)) for s in estados]
            _avaliar(rel[v], board, heur, estados, adj, sai, h_estrela, hs[v], max_exemplos)

        if "h1" in hs and "hfinal" in hs:
            for i in range(len(estados)):
                if h_estrela[i] != INF:
                    dominancia["estados"] += 1
                    if hs["hfinal"][i] < hs["h1"][i]:
                        dominancia["hfinal_menor_que_h1"] += 1

    if "h1" in variantes and "hfinal" in variantes:
        rel["_dominancia"] = dominancia
    if verbose:
        for v in variantes:
            imprimir_relatorio(rel[v], seed, tamanho, veiculos, v)
        if "_dominancia" in rel:
            print(f"\nDominância: estados com hfinal < h1: {dominancia['hfinal_menor_que_h1']}"
                  f" de {dominancia['estados']}")
    return rel


def _avaliar(r, board, heur, estados, adj, sai, h_estrela, h, max_exemplos):
    r["tabuleiros_analisados"] += 1
    tem_deps = hasattr(heur, "dependencies")
    for i, s in enumerate(estados):
        r["estados"] += 1
        if h_estrela[i] == INF:
            continue
        if h[i] != INF:
            r["soma_h"] += h[i]
            r["soma_h_estrela"] += h_estrela[i]
        if h[i] == h_estrela[i]:
            r["exatos"] += 1
        deps = heur.dependencies(dict(s)) if tem_deps else None
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
                         heur.dependencies(viz) if (tem_deps and viz) else None,
                         h_estrela[i], h_estrela[j] if j is not None else 0))


def imprimir_relatorio(r, seed, tamanho, veiculos, variante):
    print("=" * 64)
    print(f"Verificação exata — heurística {variante}")
    print(f"seed={seed}  tabuleiro={tamanho}x{tamanho}  veículos≈{veiculos}")
    print("=" * 64)
    print(f"Tabuleiros analisados: {r['tabuleiros_analisados']}  "
          f"(insolúveis: {r['tabuleiros_insoluveis']}, pulados por tamanho: {r['tabuleiros_pulados']})")
    print(f"Estados verificados:   {r['estados']}")
    print(f"Transições verificadas: {r['transicoes']}")
    print(f"Superestimativas h > h*:           {r['superestimativas']}")
    print(f"  dos quais h = inf com solução:   {r['infinitos_com_solucao']}")
    print(f"Violações h(n) > 1 + h(n'):        {r['violacoes_consistencia']}")
    print(f"Estados com h = h* (exata):        {r['exatos']}")
    if r["estados_com_X_em_D"]:
        print(f"Estados em que X aparece em D(n):  {r['estados_com_X_em_D']}")
    if r["soma_h_estrela"]:
        print(f"Informatividade média  Σh/Σh*:     {r['soma_h'] / r['soma_h_estrela']:.3f}")

    for k, (board, s, h, he, deps) in enumerate(r["exemplos_adm"], 1):
        extra = f", D={sorted(deps)}" if deps is not None else ""
        print(f"\n--- Contraexemplo de ADMISSIBILIDADE #{k}: h={h}, h*={he}{extra}")
        print(TerminalCLI.render_board(board, s))

    for k, (board, s, viz, desc, h1, h2, d1, d2, he1, he2) in enumerate(r["exemplos_cons"], 1):
        print(f"\n--- Contraexemplo de CONSISTÊNCIA #{k}: h(n)={h1} > 1 + h(n')={1 + h2}"
              f"   [h*(n)={he1}, h*(n')={he2}]")
        print("n" + (f"  (D={sorted(d1)})" if d1 is not None else "") + ":")
        print(TerminalCLI.render_board(board, s))
        print(f"ação: {desc}")
        print("n'" + (f" (D={sorted(d2)})" if d2 is not None else "") + ":")
        print(TerminalCLI.render_board(board, viz) if viz else "(objetivo)")


# ---------------------------------------------------------------------------
# Modo local (só consistência, sem h*) — serve para tabuleiros grandes
# ---------------------------------------------------------------------------
def verificar_consistencia_local(seed=42, tabuleiros=30, tamanho=12, veiculos=30,
                                 passos=300, variantes=PADRAO, max_exemplos=2, verbose=True):
    rng = random.Random(seed)
    rel = {v: {"estados": 0, "transicoes": 0, "violacoes_consistencia": 0, "exemplos": []}
           for v in variantes}
    for _ in range(tabuleiros):
        board, estado = gerar_tabuleiro(rng, tamanho, veiculos)
        heurs = {v: VARIANTES[v](board) for v in variantes}
        cache = {v: {} for v in variantes}

        def h(v, s):
            if s not in cache[v]:
                cache[v][s] = heurs[v].calculate(dict(s))
            return cache[v][s]

        atual = frozenset(estado.items())
        for _ in range(passos):
            sucessores = board.get_successors(dict(atual))
            for v in variantes:
                hn = h(v, atual)
                rel[v]["estados"] += 1
                for prox, _, desc in sucessores:
                    rel[v]["transicoes"] += 1
                    hp = h(v, prox)
                    if hn > 1 + hp:
                        rel[v]["violacoes_consistencia"] += 1
                        if len(rel[v]["exemplos"]) < max_exemplos:
                            rel[v]["exemplos"].append((board, dict(atual), dict(prox), desc, hn, hp))
            nao_objetivo = [p for p, _, _ in sucessores if not board.is_goal(dict(p))]
            if not nao_objetivo:
                break
            atual = rng.choice(nao_objetivo)

    if verbose:
        print("=" * 64)
        print(f"Consistência local — seed={seed} tabuleiro={tamanho}x{tamanho} "
              f"veículos≈{veiculos} passeios de {passos} passos em {tabuleiros} tabuleiros")
        print("=" * 64)
        for v in variantes:
            r = rel[v]
            print(f"{v:>10}: estados {r['estados']}, transições {r['transicoes']}, "
                  f"violações h(n) > 1 + h(n'): {r['violacoes_consistencia']}")
            for board, s, p, desc, hn, hp in r["exemplos"]:
                print(f"\n--- {v}: h(n)={hn} > 1 + h(n')={1 + hp}")
                print(TerminalCLI.render_board(board, s))
                print(f"ação: {desc}")
                print(TerminalCLI.render_board(board, p) if p else "(objetivo)")
    return rel


# ---------------------------------------------------------------------------
# Exemplo registrado pela equipe (h* = 12)
# ---------------------------------------------------------------------------
def tabuleiro_exemplo():
    """O 6x6 do relatório. Os dois carros que a view antiga mostrava como "1"
    são aqui "1" (linha 0) e "11" (linha 3)."""
    board = RushHourBoard(grid_size=6, exit_col=5)
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
    assert VARIANTES["original"](board).calculate(estado) == INF
    assert VARIANTES["continue"](board).calculate(estado) <= 12
    assert VARIANTES["h0"](board).calculate(estado) == 1
    assert VARIANTES["h1"](board).calculate(estado) == 2
    assert VARIANTES["hfinal"](board).calculate(estado) == 9


def test_view_mostra_ids_completos():
    board, estado = tabuleiro_exemplo()
    texto = TerminalCLI.render_board(board, estado)
    assert "11" in texto.split("\n")[4]  # linha 3 do tabuleiro


def test_h0_superestima_com_caminho_livre():
    """Contraexemplo de H0: X na coluna 1 de um 6x6, caminho livre."""
    board = RushHourBoard(grid_size=6, exit_col=5)
    board.add_vehicle('X', 'H', 2, 2)
    estado = {'X': 0}
    assert H0Distancia(board).calculate(estado) == 4
    _, _, _, h_estrela = calcular_h_estrela(board, estado, 100)
    assert h_estrela[0] == 1


def test_amostra_h0_h1_hfinal():
    rel = verificar(seed=1, tabuleiros=40, variantes=("h0", "h1", "hfinal"), verbose=False)
    assert rel["h1"]["tabuleiros_analisados"] > 0
    assert rel["h0"]["superestimativas"] > 0          # H0 não é admissível
    assert rel["h0"]["violacoes_consistencia"] > 0    # nem consistente
    for v in ("h1", "hfinal"):
        assert rel[v]["superestimativas"] == 0
        assert rel[v]["violacoes_consistencia"] == 0
    assert rel["_dominancia"]["hfinal_menor_que_h1"] == 0


def test_original_tem_infinito_falso_e_continue_nao():
    rel = verificar(seed=1, tabuleiros=40, variantes=("original", "continue"), verbose=False)
    assert rel["original"]["infinitos_com_solucao"] > 0
    assert rel["continue"]["superestimativas"] == 0


def test_consistencia_local_12x12():
    rel = verificar_consistencia_local(seed=3, tabuleiros=3, tamanho=12, veiculos=30,
                                       passos=40, variantes=("h0", "h1", "hfinal"),
                                       verbose=False)
    assert rel["h1"]["transicoes"] > 0
    assert rel["h1"]["violacoes_consistencia"] == 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tabuleiros", type=int, default=None,
                   help="padrão: 200 no modo exato, 30 no modo local")
    p.add_argument("--tamanho", type=int, default=None, help="padrão: 6 (exato) ou 12 (local)")
    p.add_argument("--veiculos", type=int, default=None, help="padrão: 12 (exato) ou 30 (local)")
    p.add_argument("--max-estados", type=int, default=150_000)
    p.add_argument("--max-exemplos", type=int, default=3)
    p.add_argument("--variante", choices=list(VARIANTES), action="append",
                   help="pode repetir; padrão: h0, h1 e hfinal")
    p.add_argument("--local", action="store_true",
                   help="só consistência, por passeios aleatórios (tabuleiros grandes)")
    p.add_argument("--passos", type=int, default=300, help="passos de cada passeio (--local)")
    a = p.parse_args()
    variantes = tuple(a.variante) if a.variante else PADRAO

    if a.local:
        verificar_consistencia_local(a.seed, a.tabuleiros or 30, a.tamanho or 12,
                                     a.veiculos or 30, a.passos, variantes, a.max_exemplos)
        sys.exit(0)

    rel = verificar(a.seed, a.tabuleiros or 200, a.tamanho or 6, a.veiculos or 12,
                    a.max_estados, variantes, a.max_exemplos)
    falhou = any(rel[v]["superestimativas"] for v in variantes if v in ESPERADAS_ADMISSIVEIS)
    sys.exit(1 if falhou else 0)
