"""Leitura e escrita de instâncias de Rush Hour em arquivo texto.

Formato (uma linha do arquivo = uma linha do tabuleiro):

    # comentário (linhas e trechos após '#' são ignorados)
    A A . B . .
    . . . B . C
    . X X B . C        <- a saída fica na borda direita da linha do X
    . . . . . C
    D D . . . .
    . . . E E .

- Células separadas por espaços; '.' ou '·' = célula vazia.
- Cada "palavra" diferente é um veículo diferente. Maiúsculas e minúsculas
  são ids diferentes ('a' != 'A') e ids podem ter mais de um caractere
  ('10', '11'), o que permite salvar tabuleiros gerados com ids numéricos.
- O tamanho N é deduzido pelo número de linhas; toda linha precisa ter N
  células (tabuleiro NxN).
- Coordenadas nas mensagens de erro são 1-indexadas (linha, coluna), como no
  enunciado. Internamente o RushHourBoard usa índices a partir de 0.
"""

from collections import defaultdict

from domain.model import RushHourBoard

VAZIO = {'.', '·'}
COMENTARIO = '#'
ALVO = 'X'
TAMANHOS_VALIDOS = (2, 3)


class BoardFormatError(ValueError):
    """Instância inválida. `erros` traz TODOS os problemas encontrados."""

    def __init__(self, erros, origem="<texto>"):
        self.erros = list(erros)
        self.origem = origem
        lista = "\n".join(f"  - {e}" for e in self.erros)
        super().__init__(f"Instância inválida ({origem}): {len(self.erros)} erro(s)\n{lista}")


def load_board(caminho):
    """Lê um arquivo de instância e devolve (RushHourBoard, estado_inicial)."""
    with open(caminho, encoding="utf-8") as f:
        return parse_board(f.read(), origem=str(caminho))


def parse_board(texto, origem="<texto>"):
    """Converte o texto de uma instância em (RushHourBoard, estado_inicial).

    estado_inicial: dict {id: coordenada variável} (coluna da ponta esquerda
    para horizontais, linha da ponta de cima para verticais), igual ao usado
    pelo resto do programa.

    Lança BoardFormatError com a lista completa de erros se a instância for
    inválida.
    """
    linhas = []  # (número da linha no arquivo, lista de células)
    for num, bruta in enumerate(texto.splitlines(), start=1):
        conteudo = bruta.split(COMENTARIO, 1)[0].strip()
        if conteudo:
            linhas.append((num, conteudo.split()))

    if not linhas:
        raise BoardFormatError(["o arquivo não contém nenhuma linha de tabuleiro"], origem)

    # --- 1. Forma NxN -------------------------------------------------------
    n = len(linhas)
    erros = [
        f"linha {num} do arquivo tem {len(celulas)} célula(s); esperado {n} "
        f"(o arquivo tem {n} linhas de tabuleiro e o tabuleiro deve ser {n}x{n})"
        for num, celulas in linhas if len(celulas) != n
    ]
    if erros:
        # Sem a forma NxN as coordenadas não fazem sentido; para aqui.
        raise BoardFormatError(erros, origem)

    # --- 2. Agrupa as células de cada id (ordem de primeira aparição) -------
    celulas_por_id = defaultdict(list)
    for r, (_, celulas) in enumerate(linhas):
        for c, token in enumerate(celulas):
            if token not in VAZIO:
                celulas_por_id[token].append((r, c))

    # --- 3. Deduz e valida cada veículo -------------------------------------
    veiculos = []  # (id, orientação, comprimento, eixo fixo, coordenada variável)
    for vid, celulas in celulas_por_id.items():
        desc = _descrever(celulas)
        linhas_ocupadas = {r for r, _ in celulas}
        colunas_ocupadas = {c for _, c in celulas}

        if len(celulas) == 1:
            erros.append(f"veículo '{vid}' ocupa só 1 célula {desc}; "
                         f"veículos devem ter tamanho 2 ou 3")
            continue
        if len(linhas_ocupadas) == 1:
            orient, fixo, variaveis = 'H', celulas[0][0], sorted(colunas_ocupadas)
        elif len(colunas_ocupadas) == 1:
            orient, fixo, variaveis = 'V', celulas[0][1], sorted(linhas_ocupadas)
        else:
            erros.append(f"veículo '{vid}' não está em linha reta: ocupa {desc}")
            continue
        if variaveis != list(range(variaveis[0], variaveis[-1] + 1)):
            erros.append(f"veículo '{vid}' tem células não contíguas {desc} "
                         f"(o mesmo id foi usado em dois lugares?)")
            continue
        if len(celulas) not in TAMANHOS_VALIDOS:
            erros.append(f"veículo '{vid}' tem tamanho {len(celulas)} {desc}; "
                         f"veículos devem ter tamanho 2 ou 3")
            continue
        veiculos.append((vid, orient, len(celulas), fixo, variaveis[0]))

    # --- 4. Veículo alvo ----------------------------------------------------
    if ALVO not in celulas_por_id:
        erros.append(f"veículo alvo '{ALVO}' ausente")
    else:
        alvo = next((v for v in veiculos if v[0] == ALVO), None)
        if alvo is not None and alvo[1] != 'H':
            erros.append(f"veículo alvo '{ALVO}' deve ser horizontal, mas é vertical "
                         f"{_descrever(celulas_por_id[ALVO])}")

    if erros:
        raise BoardFormatError(erros, origem)

    # --- 5. Monta o modelo ---------------------------------------------------
    board = RushHourBoard(grid_size=n, exit_col=n - 1)
    estado = {}
    for vid, orient, comp, fixo, var in veiculos:
        board.add_vehicle(vid, orient, comp, fixo)
        estado[vid] = var
    return board, estado


def avisos(board, estado):
    """Problemas que NÃO tornam a instância inválida, mas valem ser mostrados.

    Hoje: veículo horizontal na linha de X, à direita dele. Pelas regras ele
    nunca sai da frente de X, então a instância não tem solução.
    """
    resultado = []
    x = board.vehicles[ALVO]
    fim_x = estado[ALVO] + x.length - 1
    for vid, v in board.vehicles.items():
        if vid != ALVO and v.orientation == 'H' and v.fixed_axis == x.fixed_axis \
                and estado[vid] > fim_x:
            resultado.append(
                f"veículo '{vid}' é horizontal e está à direita de X na linha "
                f"{x.fixed_axis + 1}: X nunca alcançará a saída (instância sem solução)")
    return resultado


def board_to_text(board, estado):
    """Inverso de parse_board: gera o texto da instância (colunas alinhadas)."""
    largura = max([1] + [len(str(v)) for v in estado])
    grade = [['.'] * board.grid_size for _ in range(board.grid_size)]
    for vid, var in estado.items():
        v = board.vehicles[vid]
        for i in range(v.length):
            r, c = (v.fixed_axis, var + i) if v.orientation == 'H' else (var + i, v.fixed_axis)
            grade[r][c] = str(vid)
    return "\n".join(" ".join(cel.ljust(largura) for cel in linha).rstrip()
                     for linha in grade) + "\n"


def save_board(board, estado, caminho, comentario=None):
    """Grava a instância em arquivo, no mesmo formato lido por load_board."""
    with open(caminho, "w", encoding="utf-8") as f:
        if comentario:
            for linha in comentario.splitlines():
                f.write(f"{COMENTARIO} {linha}\n")
        f.write(board_to_text(board, estado))


def _descrever(celulas):
    return "[" + ", ".join(f"({r + 1},{c + 1})" for r, c in sorted(celulas)) + "]"
