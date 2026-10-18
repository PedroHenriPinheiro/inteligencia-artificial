# Reflexão: de dependências a estimativas justificáveis

O principal aprendizado até aqui é que a estrutura de bloqueios do tabuleiro não pode ser convertida diretamente em uma soma de custos sem justificativa.

Um veículo pode ser uma dependência sem precisar mover-se em toda solução. Mesmo quando uma movimentação é obrigatória, a estimativa pode já incluir essa ação. Além disso, uma movimentação pode resolver mais de uma dependência, de modo que somar uma unidade por relação pode gerar dupla contagem.

O raciocínio deve avançar em etapas:

1. Identificar uma possível dependência.
2. Investigar se a movimentação é inevitável em toda solução válida.
3. Estabelecer o que já está contabilizado na estimativa.
4. Verificar se a contagem proposta é um limite inferior.
5. Avaliar a admissibilidade da heurística para todos os estados relevantes.
6. Testar a consistência separadamente, se ela for uma propriedade desejada.

Uma heurística não precisa estimar perfeitamente o custo para ser admissível. Ela precisa não ultrapassar o custo ótimo restante. Uma estimativa mais informativa só é útil se continuar respeitando as propriedades necessárias à busca.

A próxima etapa é formular candidatos explícitos, testar estados pequenos com busca exata e procurar contraexemplos antes de adotar qualquer candidato como heurística do projeto.