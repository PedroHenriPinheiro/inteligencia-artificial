import heapq, time, csv, os
from teste_e01_h01 import RushHourBoard, solve

def h_dupla_contagem(state, board):
    if 'X' not in state: return 0
    occ = board.get_occupied(state)
    E_sum = 0
    # H1 bloqueia ambos V1 e V2. Somamos +1 para cada um independentemente (Erro H05)
    if any((r, 3) in occ for r in range(3, 5)): E_sum += 1 # Bloqueio de V1
    if any((r, 4) in occ for r in range(3, 5)): E_sum += 1 # Bloqueio de V2
    return 1 + 2 + E_sum

def h_conjunto_unico(state, board):
    if 'X' not in state: return 0
    occ = board.get_occupied(state)
    E_set = set()
    # Adicionamos os IDs dos bloqueadores ao set (Solução H3.1)
    for r in range(3, 5):
        if (r, 3) in occ: E_set.add(occ[(r, 3)])
        if (r, 4) in occ: E_set.add(occ[(r, 4)])
    return 1 + 2 + len(E_set)

if __name__ == "__main__":
    board = RushHourBoard(8)
    board.add_vehicle('X', 'H', 2, 2)
    board.add_vehicle('V1', 'V', 2, 3) # Bloqueador 1
    board.add_vehicle('V2', 'V', 2, 4) # Bloqueador 2
    board.add_vehicle('H1', 'H', 3, 4) # O GRANDE VILÃO: Tranca V1 e V2 ao mesmo tempo
    state = {'X': 0, 'V1': 1, 'V2': 1, 'H1': 3}
    
    print("Testando E04: Superestimativa por Dupla Contagem...")
    c1, g1, e1, f1, t1 = solve(board, state, lambda s: h_dupla_contagem(s, board))
    c2, g2, e2, f2, t2 = solve(board, state, lambda s: h_conjunto_unico(s, board))
    
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
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Teste 8x8 (Dupla Contagem)", "A*", "H05 (+1 por V1 preso)", c1, g1, e1, f"{t1:.4f}"])
        w.writerow(["Teste 8x8 (Dupla Contagem)", "A*", "H3.1 (Apenas IDs únicos)", c2, g2, e2, f"{t2:.4f}"])
    print(f"Resultados salvos em {csv_path}")