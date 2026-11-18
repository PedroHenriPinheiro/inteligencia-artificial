"""Testes do leitor de instâncias (codigo/src/infra/board_loader.py).

    pytest codigo/testes/test_board_loader.py
"""

import os
import sys

import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "..", "src")))
INSTANCIAS = os.path.abspath(os.path.join(AQUI, "..", "instancias"))

from infra.board_loader import (  # noqa: E402
    BoardFormatError, avisos, board_to_text, load_board, parse_board, save_board)


def erros_de(texto):
    with pytest.raises(BoardFormatError) as info:
        parse_board(texto)
    return info.value.erros


# --------------------------------------------------------------------------
# Casos válidos
# --------------------------------------------------------------------------
def test_deduz_tamanho_orientacao_e_posicao():
    board, estado = parse_board("""
        A A . . . .
        . . . B . .
        . X X B . .
        . . . B . .
        . . . . . .
        . . . . C C
    """)
    assert board.grid_size == 6 and board.exit_col == 5
    assert estado == {'A': 0, 'B': 1, 'X': 1, 'C': 4}
    a, b, x = board.vehicles['A'], board.vehicles['B'], board.vehicles['X']
    assert (a.orientation, a.length, a.fixed_axis) == ('H', 2, 0)
    assert (b.orientation, b.length, b.fixed_axis) == ('V', 3, 3)
    assert (x.orientation, x.length, x.fixed_axis) == ('H', 2, 2)


def test_maiusculas_e_minusculas_sao_veiculos_diferentes():
    board, estado = parse_board("""
        a a . A A .
        . . . . . .
        X X . . . .
        . . . . . .
        . . . . . .
        . . . . . .
    """)
    assert {'a', 'A', 'X'} == set(board.vehicles)
    assert estado['a'] == 0 and estado['A'] == 3


def test_ids_com_varios_caracteres_ponto_medio_e_comentarios():
    board, estado = parse_board("""
        # comentário
        10 10 ·  ·  ·  ·
        ·  ·  ·  11 ·  ·   # comentário no fim da linha
        X  X  ·  11 ·  ·

        ·  ·  ·  ·  ·  ·
        ·  ·  ·  ·  ·  ·
        ·  ·  ·  ·  ·  ·
    """)
    assert board.grid_size == 6
    assert estado == {'10': 0, '11': 1, 'X': 0}


def test_tamanhos_6_a_12():
    for n in range(6, 13):
        linhas = [["."] * n for _ in range(n)]
        linhas[n // 2 - 1][0] = linhas[n // 2 - 1][1] = "X"
        board, estado = parse_board("\n".join(" ".join(l) for l in linhas))
        assert board.grid_size == n and estado == {'X': 0}


def test_ida_e_volta_texto(tmp_path):
    board, estado = load_board(os.path.join(INSTANCIAS, "exemplo_6x6_h12.txt"))
    caminho = tmp_path / "copia.txt"
    save_board(board, estado, caminho, comentario="cópia")
    board2, estado2 = load_board(caminho)
    assert estado2 == estado
    assert board_to_text(board2, estado2) == board_to_text(board, estado)


def test_instancia_exemplo_6x6():
    board, estado = load_board(os.path.join(INSTANCIAS, "exemplo_6x6_h12.txt"))
    assert board.grid_size == 6 and len(estado) == 12
    assert board.vehicles['11'].orientation == 'H' and estado['11'] == 3
    assert board.vehicles['8'].orientation == 'V' and board.vehicles['8'].length == 3


# --------------------------------------------------------------------------
# Casos inválidos
# --------------------------------------------------------------------------
def test_enunciado_como_publicado_e_rejeitado_com_os_dois_erros():
    with pytest.raises(BoardFormatError) as info:
        load_board(os.path.join(INSTANCIAS, "invalidas", "enunciado_12x12_como_publicado.txt"))
    erros = info.value.erros
    assert len(erros) == 2
    assert "'b' não está em linha reta" in erros[0] and "(12,4)" in erros[0]
    assert "'d' ocupa só 1 célula" in erros[1] and "(11,3)" in erros[1]


def test_linhas_de_tamanhos_diferentes():
    erros = erros_de("""
        . . .
        X X
        . . .
    """)
    assert len(erros) == 1 and "tem 2 célula(s); esperado 3" in erros[0]


def test_tabuleiro_nao_quadrado():
    erros = erros_de("""
        . . . .
        X X . .
        . . . .
    """)
    assert len(erros) == 3  # 3 linhas, mas cada uma com 4 células


def test_veiculo_fora_de_linha_reta():
    erros = erros_de("""
        A A . .
        A . . .
        X X . .
        . . . .
    """)
    assert erros == ["veículo 'A' não está em linha reta: ocupa [(1,1), (1,2), (2,1)]"]


def test_veiculo_com_buraco_ou_id_repetido():
    erros = erros_de("""
        A . A .
        . . . .
        X X . .
        . . . .
    """)
    assert len(erros) == 1 and "não contíguas" in erros[0]


@pytest.mark.parametrize("linha0, tamanho", [("A . . . .", 1), ("A A A A .", 4)])
def test_tamanho_diferente_de_2_ou_3(linha0, tamanho):
    erros = erros_de(f"""
        {linha0}
        . . . . .
        X X . . .
        . . . . .
        . . . . .
    """)
    assert len(erros) == 1 and "'A'" in erros[0] and "tamanho 2 ou 3" in erros[0]
    assert ("1 célula" in erros[0]) == (tamanho == 1)


def test_x_ausente():
    assert erros_de("""
        A A .
        . . .
        . . .
    """) == ["veículo alvo 'X' ausente"]


def test_x_vertical():
    erros = erros_de("""
        . X .
        . X .
        . . .
    """)
    assert len(erros) == 1 and "deve ser horizontal" in erros[0]


def test_varios_erros_sao_reportados_juntos():
    erros = erros_de("""
        A . B .
        A B . .
        . . . C
        . . . .
    """)
    textos = " | ".join(erros)
    assert "'B' não está em linha reta" in textos
    assert "'C' ocupa só 1 célula" in textos
    assert "'X' ausente" in textos


def test_arquivo_vazio():
    assert erros_de("# só comentário\n\n") == ["o arquivo não contém nenhuma linha de tabuleiro"]


# --------------------------------------------------------------------------
# Avisos (instância válida, mas sem solução)
# --------------------------------------------------------------------------
def test_aviso_horizontal_na_frente_de_x():
    board, estado = parse_board("""
        . . . .
        X X A A
        . . . .
        . . . .
    """)
    lista = avisos(board, estado)
    assert len(lista) == 1 and "'A'" in lista[0] and "sem solução" in lista[0]


def test_sem_aviso_para_horizontal_atras_de_x():
    board, estado = parse_board("""
        . . . . .
        A A X X .
        . . . . .
        . . . . .
        . . . . .
    """)
    assert avisos(board, estado) == []
