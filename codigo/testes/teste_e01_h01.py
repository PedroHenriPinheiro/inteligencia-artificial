import heapq
import time
import csv
import os

class Vehicle:
    def __init__(self, v_id, o, l, f_axis): self.id, self.orientation, self.length, self.fixed_axis = v_id, o, l, f_axis

class RushHourBoard:
    def __init__(self, grid_size=6):
        self.grid_size = grid_size
        self.vehicles = {}
    def add_vehicle(self, v_id, o, l, f_axis): self.vehicles[v_id] = Vehicle(v_id, o, l, f_axis)
    def is_goal(self, state): return 'X' not in state
    def get_occupied(self, state):
        occ = {}
        for v_id, c in state.items():
            v = self.vehicles[v_id]
            for i in range(v.length): occ[(v.fixed_axis, c + i) if v.orientation == 'H' else (c + i, v.fixed_axis)] = v_id
        return occ
    def get_successors(self, state):
        succ, occ = [], self.get_occupied(state)
        for v_id, c in state.items():
            v = self.vehicles[v_id]
            nc = c - 1
            while nc >= 0 and ((v.fixed_axis, nc) if v.orientation == 'H' else (nc, v.fixed_axis)) not in occ:
                ns = dict(state); ns[v_id] = nc; succ.append((frozenset(ns.items()), 1))
                nc -= 1
            nc = c + 1
            while nc + v.length - 1 < self.grid_size and ((v.fixed_axis, nc + v.length - 1) if v.orientation == 'H' else (nc + v.length - 1, v.fixed_axis)) not in occ:
                ns = dict(state); ns[v_id] = nc; succ.append((frozenset(ns.items()), 1))
                nc += 1
            if v_id == 'X' and nc + v.length - 1 == self.grid_size:
                ns = dict(state); del ns['X']; succ.append((frozenset(ns.items()), 1))
        return succ

def solve(board, init_state, h_func):
    start_time = time.perf_counter()
    start = frozenset(init_state.items())
    frontier = [(h_func(init_state), 0, start)]
    cost_so_far = {start: 0}
    ger, exp = 1, 0
    max_front = 1
    while frontier:
        max_front = max(max_front, len(frontier))
        _, cost, curr = heapq.heappop(frontier)
        curr_d = dict(curr)
        if board.is_goal(curr_d): return cost, ger, exp, max_front, time.perf_counter() - start_time
        exp += 1
        for nxt, ac, in board.get_successors(curr_d):
            ger += 1
            nc = cost_so_far[curr] + ac
            if nxt not in cost_so_far or nc < cost_so_far[nxt]:
                cost_so_far[nxt] = nc
                heapq.heappush(frontier, (nc + h_func(dict(nxt)), nc, nxt))
    return -1, ger, exp, max_front, time.perf_counter() - start_time

def h1_distancia(state):
    if 'X' not in state: return 0
    return 6 - (state['X'] + 2) # Casas restantes até a saída

def h3_bloqueios(state):
    return 1 if 'X' in state else 0 # Nenhum bloqueador, custo é apenas 1 ação

if __name__ == "__main__":
    board = RushHourBoard(6)
    board.add_vehicle('X', 'H', 2, 2)
    state = {'X': 0} # X tem 4 casas livres pela frente
    
    print("Testando E01: Ações vs Distância...")
    c1, g1, e1, f1, t1 = solve(board, state, h1_distancia)
    c2, g2, e2, f2, t2 = solve(board, state, h3_bloqueios)
    
    # === CÓDIGO DE SALVAMENTO CORRIGIDO ===
    # 1. Pega o caminho absoluto da pasta onde o script está rodando (.../codigo/testes)
    pasta_testes = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe duas pastas estruturalmente (.../codigo -> .../inteligencia-artificial)
    pasta_codigo = os.path.dirname(pasta_testes)
    pasta_raiz = os.path.dirname(pasta_codigo)
    
    # 3. Monta o caminho exato para a pasta 06-dados
    csv_path = os.path.join(pasta_raiz, '06-dados', 'resultados.csv')
    
    print(f"\n[DEBUG] Tentando salvar os resultados no caminho exato:\n{csv_path}")
    
    # Grava no CSV
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        
        # Substitua as linhas de w.writerow(...) abaixo de acordo com cada teste específico!
        # Exemplo para o E01:
        w.writerow(["Teste 6x6 (Corredor Livre)", "A*", "H1 (Distância Espacial)", c1, g1, e1, f"{t1:.4f}"])
        w.writerow(["Teste 6x6 (Corredor Livre)", "A*", "H3 (Bloqueios)", c2, g2, e2, f"{t2:.4f}"])
        
    print("Resultados salvos com sucesso!")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Teste 6x6 (Corredor Livre)", "A*", "H1 (Distância Espacial)", c1, g1, e1, f"{t1:.4f}"])
        w.writerow(["Teste 6x6 (Corredor Livre)", "A*", "H3 (Bloqueios)", c2, g2, e2, f"{t2:.4f}"])
    print(f"Resultados salvos em {csv_path}")