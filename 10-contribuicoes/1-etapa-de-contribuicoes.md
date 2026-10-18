### Pedro Henrique Pinheiro de Oliveira

# Resumo da contribuição — investigação de heurísticas

## Contribuição até o momento

- Formalização da diferença entre distância geométrica e custo em ações.
- Identificação do risco de inadmissibilidade ao usar diretamente a distância em células quando um veículo pode percorrer várias células por ação.
- Distinção entre bloqueios diretos, dependências indiretas e movimentações inevitáveis.
- Identificação do risco de dupla contagem quando uma ação resolve várias dependências ou já está incluída na estimativa.
- Definição de um plano de experimentos para comparar estimativas com custos ótimos em estados pequenos.

## Resultado

O trabalho refinou os critérios para construir uma heurística, mas ainda não estabeleceu uma nova heurística final admissível.

## Próximo passo

Construir instâncias pequenas, calcular seus custos ótimos por busca exata, registrar `h(n)` e `h*(n)` e procurar contraexemplos. Somente depois dessa etapa será possível avaliar quais candidatos merecem uma prova geral.
