class Vehicle:
    def __init__(self, v_id, orientation, length, fixed_axis):
        self.id = v_id
        self.orientation = orientation
        self.length = length
        self.fixed_axis = fixed_axis

class RushHourBoard:
    def __init__(self, grid_size=12, exit_col=11):
        self.grid_size = grid_size
        self.exit_col = exit_col
        self.vehicles = {}

    def add_vehicle(self, v_id, orientation, length, fixed_axis):
        self.vehicles[v_id] = Vehicle(v_id, orientation, length, fixed_axis)

    def is_goal(self, state):
        return 'X' not in state

    def get_occupied_cells(self, state):
        occupied = {}
        for v_id, var_coord in state.items():
            v = self.vehicles[v_id]
            for i in range(v.length):
                if v.orientation == 'H':
                    occupied[(v.fixed_axis, var_coord + i)] = v_id
                else:
                    occupied[(var_coord + i, v.fixed_axis)] = v_id
        return occupied

    def get_successors(self, state):
        """Lista (novo_estado, custo, descrição) de todas as ações legais.

        Os veículos são percorridos na ordem de `self.vehicles` (ordem em que
        foram adicionados, ou seja, a ordem de leitura do arquivo), e NÃO na
        ordem de `state.items()`. O estado vem de um frozenset, e a ordem de
        iteração de um frozenset depende do hash das strings, que o Python
        sorteia a cada execução (PYTHONHASHSEED). Com a ordem de state.items(),
        a ordem dos sucessores, e por isso os desempates da BFS e do A*,
        mudavam entre execuções.
        """
        successors = []
        occupied = self.get_occupied_cells(state)

        for v_id in self.vehicles:
            if v_id not in state:
                continue  # X depois de sair do tabuleiro
            var_coord = state[v_id]
            v = self.vehicles[v_id]
            eixo_nome = "coluna" if v.orientation == 'H' else "linha"

            # 1. Movimento Recuando (Esquerda / Cima)
            new_coord = var_coord - 1
            while new_coord >= 0:
                cell = (v.fixed_axis, new_coord) if v.orientation == 'H' else (new_coord, v.fixed_axis)

                # Se bater em algum obstáculo, quebra o laço (não pode deslizar mais)
                if cell in occupied:
                    break

                # Gera um estado possível deslizando até aqui (Custo = 1 ação)
                new_state = dict(state)
                new_state[v_id] = new_coord
                acao = f"Deslizou [{v_id}] recuando para a {eixo_nome} {new_coord}"
                successors.append((frozenset(new_state.items()), 1, acao))

                new_coord -= 1 # Continua testando a próxima casa

            # 2. Movimento Avançando (Direita / Baixo)
            new_coord = var_coord + 1
            while new_coord + v.length - 1 < self.grid_size:
                cell = (v.fixed_axis, new_coord + v.length - 1) if v.orientation == 'H' else (new_coord + v.length - 1, v.fixed_axis)

                # Se bater em algum obstáculo, quebra o laço
                if cell in occupied:
                    break

                new_state = dict(state)
                new_state[v_id] = new_coord
                acao = f"Deslizou [{v_id}] avançando para a {eixo_nome} {new_coord}"
                successors.append((frozenset(new_state.items()), 1, acao))

                new_coord += 1 # Continua testando a próxima casa

            # 3. Movimento de Saída Especial para o X
            # Se o laço de avançar chegou até a borda (grid_size) sem dar 'break'
            if v_id == 'X' and new_coord + v.length - 1 == self.grid_size:
                new_state = dict(state)
                del new_state['X']
                acao = "Veículo [X] deslizou livremente e saiu do tabuleiro. (OBJETIVO ALCANÇADO)"
                successors.append((frozenset(new_state.items()), 1, acao))

        return successors
