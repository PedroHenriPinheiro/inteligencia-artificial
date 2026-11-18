# Plano de validação das hipóteses

## Objetivo

Comparar estimativas heurísticas com o custo ótimo restante em instâncias pequenas e procurar contraexemplos para as hipóteses.

## Método de comparação

Para cada estado de teste:
    1. Calcular o custo ótimo restante `h*(n)` usando uma busca de referência exata, em instâncias pequenas.
    2. Calcular a estimativa candidata `h(n)`.
    3. Verificar se `h(n) ≤ h*(n)`.
    4. Registrar diferenças, contraexemplos e condições do estado.
    5. Avaliar a consistência verificando cada transição legal `n → n'` e a condição `h(n) ≤ c(n,n') + h(n')`.

Passar nos testes finitos aumenta a confiança, mas não constitui prova geral de admissibilidade ou consistência.