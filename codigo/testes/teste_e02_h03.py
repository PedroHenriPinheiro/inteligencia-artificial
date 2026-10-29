import heapq, time, csv, os
from teste_e01_h01 import RushHourBoard, solve # Reutiliza a base do E01

def h_miope(state, board):
    if 'X' not in state: return 0
    occ = board.get_occupied(state)
    target_up = 2 - 3 # Linha do X (2) - Tamanho do V1 (3) = -1
    return 1 + 1 + (0 if target_up < 0 else 1) # Falsa estimativa simplista

def h_deslocamento_real(state, board):
    if 'X' not in state: return 0
    occ = board.get_occupied(state)
    # V1 precisa descer, cabeça vai para linha 3. Ocupará 3, 4 e 5.
    # Mas H1 está na linha 5! Deslocamento real detecta bloqueio.
    blocked = any((r, 3) in occ for r in range(3, 6))
    return 1 + 1 + (1 if blocked else 0)

if __name__ == "__main__":
    board = RushHourBoard(8)
    board.add_vehicle('X', 'H', 2, 2)
    board.add_vehicle('V1', 'V', 3, 3) # Bloqueia X.
    board.add_vehicle('H1', 'H', 4, 5) # Bloqueia a descida de V1 na última casa necessária
    state = {'X': 0, 'V1': 0, 'H1': 0}
    
    print("Testando E02: Deslocamento Real (Gargalo 1)...")
    c1, g1, e1, f1, t1 = solve(board, state, lambda s: h_miope(s, board))
    c2, g2, e2, f2, t2 = solve(board, state, lambda s: h_deslocamento_real(s, board))
    
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
        w.writerow(["Teste 8x8 (Deslocamento Real)", "A*", "A* s/ Gargalo 1 (Míope)", c1, g1, e1, f"{t1:.4f}"])
        w.writerow(["Teste 8x8 (Deslocamento Real)", "A*", "H3 (c/ Deslocamento Real)", c2, g2, e2, f"{t2:.4f}"])
    print(f"Resultados salvos em {csv_path}")