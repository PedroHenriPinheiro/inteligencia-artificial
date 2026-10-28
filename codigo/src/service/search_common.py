"""Funções compartilhadas pelos algoritmos de busca."""


def reconstruct(parents, goal):
    """Reconstrói (ações, estados) do estado inicial até `goal`.

    parents: {estado: (estado_pai, descrição_da_ação)}; o inicial tem pai None.
    Devolve a lista de descrições das ações e a lista de estados (dicts),
    começando no estado inicial e terminando no objetivo.
    """
    actions, states = [], []
    node = goal
    while node is not None:
        parent, action = parents[node]
        states.append(dict(node))
        if parent is not None:
            actions.append(action)
        node = parent
    actions.reverse()
    states.reverse()
    return actions, states
