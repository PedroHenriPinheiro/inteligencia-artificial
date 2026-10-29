import heapq, time, csv, os
from teste_e01_h01 import RushHourBoard, solve

def h_sem_limites(state, board):
    if 'X' not in state: return 0
    occ = board.get_occupied(state)
    target_up = -1
    # Loop em índices negativos não acha nada no dict 'occ', logo acha que está livre!
    blocked = any((r, 3) in occ for r in range(-1, 0)) 
    return 1 + 1 + (1 if blocked else 0)

def h_com_limites(state, board):
    if 'X' not in state: return 0
    target_up = -1
    if target_up < 0: return 1 + 1 + 1 # Parede = bloqueio garantido (Gargalo 2)
    return 1 + 1

if __name__ == "__main__":
    board = RushHourBoard(10)
    board.add_vehicle('X', 'H', 2, 2)
    board.add_vehicle('V1', 'V', 3, 3) 
    board.add_vehicle('H1', 'H', 2, 6) # Parede embaixo também
    state = {'X': 0, 'V1': 0, 'H1': 3} # V1 já está colado na linha 0
    
    print("Testando E03: Limites Absolutos (Gargalo 2)...")
    c1, g1, e1, f1, t1 = solve(board, state, lambda s: h_sem_limites(s, board))
    c2, g2, e2, f2, t2 = solve(board, state, lambda s: h_com_limites(s, board))
    
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
        w.writerow(["Teste 10x10 (Limites Absolutos)", "A*", "H2 (Sem limites rígidos)", c1, g1, e1, f"{t1:.4f}"])
        w.writerow(["Teste 10x10 (Limites Absolutos)", "A*", "H3 (Com Limites Absolutos)", c2, g2, e2, f"{t2:.4f}"])
    print(f"Resultados salvos em {csv_path}")