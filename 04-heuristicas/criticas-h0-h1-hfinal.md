# Crítica das heurísticas H0, H1 e Hfinal

Pedido da equipe: criticar, **não substituir**. Para cada heurística: ela representa bem o custo restante? Em que situações estima mal? Pode superestimar? É admissível? É consistente? Contraexemplo concreto quando a resposta é "não".

Notação: h*(n) = custo ótimo real (nº de ações); consistência = h(n) ≤ 1 + h(n') para toda ação n → n', com h(objetivo) = 0. Coordenadas 1-indexadas.
Implementação: `codigo/src/service/heuristics/`. Verificação: `codigo/testes/verificar_admissibilidade.py`.

> **Opinião prévia da equipe:** **Registrado em 28/10/2026, depois de ler esta crítica.** O campo de opinião foi enviado vazio por falha nossa. Para não inventar uma opinião "prévia", usamos o que a equipe **já tinha escrito antes** no repositório:
> - **H0 (distância):** em `04-heuristicas/H1.md` (primeira heurística da equipe) afirmamos que ela era **admissível e consistente**, "porque ela subestima a distância real". Estava errado: a crítica mostra que ela superestima com o caminho livre. Isso entra no relatório como "uma ideia nossa que estava errada".
> - **H1 (1 + bloqueadores):** em `01-compreensao-inicial/comprensao-03.md` (João + Gemini), ela já aparecia como admissível, com o argumento "cada bloqueador precisa se mover pelo menos uma vez". A crítica confirma e acrescenta a prova de consistência. *(⚠️ confirmar com João)*
> - **Hfinal (cascata):** o `H3.md` afirmava que ela era admissível **e consistente**. A admissibilidade se sustenta nos testes, mas a consistência continua sem prova (ver IH02).

---

## Resumo

| | H0 (distância em células) | H1 (1 + bloqueadores diretos) | Hfinal (cascata corrigida) |
|---|---|---|---|
| Pode superestimar? | **Sim** | Não | Não (nenhum caso encontrado) |
| Admissível? | **Não** (contraexemplo abaixo) | **Sim** (prova curta) | **Sim** (esboço de prova + testes) |
| Consistente? | **Não** (contraexemplo abaixo) | **Sim** (prova curta) | **Não sabemos** (sem prova; 0 violações nos testes) |
| Σh/Σh* (6x6, seed 42) | 0,596 (com 12% de superestimativas) | 0,672 | 0,881 |
| Estados com h = h* | 21,9% | 60,8% | 81,6% |

Verificação exata: 6x6, seed 42, 104 tabuleiros, 793.856 estados, 9.641.711 transições.

| Heurística | h > h* | h(n) > 1 + h(n') |
|---|---|---|
| H0 | **95.874** | **172.736** |
| H1 | 0 | 0 |
| Hfinal | 0 | 0 |

Consistência local, com passeios aleatórios de 300 passos em 30 tabuleiros por tamanho (8x8, 10x10 e 12x12, inclusive 10x10 com 30 veículos e 12x12 com 40): H1 e Hfinal tiveram 0 violações. H0 teve milhares em todos os tamanhos.

---

## H0 — h = número de células entre a frente de X e a saída

**Representa bem o custo restante?** Não. Ela mede **células**, e o custo é medido em **ações**: uma ação pode deslizar X por várias células. Além disso, ela não enxerga nenhum bloqueador.

**Onde estima mal:**
- *Superestima* quando o caminho está livre e longe. X pode atravessar tudo em uma ação.
- *Subestima muito* quando o caminho é curto mas está bloqueado. No 6x6 do IH02, h0 = 1 e h* = 12.
- Vale 0 em estados que **não** são objetivo: com a frente de X na borda, X ainda precisa da ação de saída (h* = 1).

**Pode superestimar? Sim. Admissível? Não.** Contraexemplo (6x6, X na linha 3, colunas 1–2, caminho livre):
```
. . . . . .
. . . . . .
X X . . . .     h0 = 4 (colunas 3, 4, 5, 6 livres)   h* = 1 (X sai em uma ação)
. . . . . .
. . . . . .
. . . . . .
```
(teste `test_h0_superestima_com_caminho_livre`)

**Consistente? Não.** No mesmo tabuleiro, a ação "X sai" leva ao objetivo: h(n) = 4 > 1 + h(objetivo) = 1. Há também violação entre estados que **não** são objetivo, encontrada pelo verificador: X nas colunas 3–4 de um 6x6 (h0 = 2) desliza para as colunas 5–6 (h0 = 0), e 2 > 1 + 0. Com h(objetivo) = 0, consistência implica admissibilidade, então uma heurística inadmissível nunca pode ser consistente.

**O que se aproveita:** a intuição "X precisa andar até a saída" está certa, mas vale **no máximo 1 ação**, não uma por célula. É exatamente o "1 +" da H1.

---

## H1 — h = 1 + número de veículos distintos que bloqueiam diretamente a linha de X

**Representa bem o custo restante?** Em parte. Ela conta ações obrigatórias de verdade, mas só o primeiro nível delas.

**Onde estima mal:**
- Quando os bloqueadores estão presos. No 6x6 do IH02, h1 = 2 (X + o veículo 8) e h* = 12. A cadeia 8 → 3, 6 → 5, 9 → 0 → 4 → 11 é invisível para ela.
- Quando há um veículo horizontal na linha de X, à frente dele: o estado não tem solução (h* = ∞), mas H1 dá um valor finito. Isso não quebra a admissibilidade, só desperdiça busca.

**Pode superestimar? Não. Admissível? Sim.** Prova:
1. Toda célula entre a frente de X e a saída precisa estar vazia no momento em que X sai.
2. Logo, todo veículo que ocupa uma dessas células agora precisa se mover pelo menos uma vez antes disso.
3. Cada ação move um único veículo, então b bloqueadores distintos exigem pelo menos b ações distintas.
4. Nenhuma delas é a saída de X, que é mais uma ação.
5. Portanto h1 = 1 + b ≤ h*. No objetivo, h1 = 0.

**Consistente? Sim.** Prova: uma ação muda a posição de **um** veículo v.
- Se v ≠ X, o conjunto de bloqueadores só pode ganhar v ou perder v, então h muda no máximo 1.
- Se X anda para a direita, ele só passa por células livres, e os bloqueadores continuam à frente. Se anda para a esquerda, as células que entram no trecho da frente são as que X acabou de liberar (vazias). Nos dois casos, h não muda.
- Na saída, o caminho estava livre (h = 1) e o objetivo tem h = 0: 1 ≤ 1 + 0.

Logo h(n) ≤ 1 + h(n') sempre. O verificador confirma: 0 violações.

---

## Hfinal — cascata corrigida (h = 1 + |D(n)|, regra colinear, ciclos ignorados)

**Representa bem o custo restante?** É a melhor das três: Σh/Σh* = 0,881, e h = h* em 81,6% dos estados da amostra. Ela **domina** a H1: D(n) sempre contém todos os bloqueadores diretos, então hfinal ≥ h1 em todo estado. O verificador encontrou 0 estados com hfinal < h1 em 793.856.

**Onde estima mal:**
1. **Veículos que precisam se mover mais de uma vez.** D é um conjunto, e cada veículo conta 1. No 6x6 do IH02, hfinal = 9 e h* = 12: os veículos 8, 4 e 11 se movem duas vezes na solução ótima, e cada um conta só uma vez.
2. **Rotas alternativas com dependências diferentes.** Suponha que um bloqueador vertical possa subir (exigindo que A saia) ou descer (exigindo que B saia). Toda solução move A **ou** B, então ao menos 1 ação extra é certa. Mas a interseção {A} ∩ {B} = ∅ não conta nada. A interseção é segura (não superestima), mas joga fora o "pelo menos um dos dois".
3. **Estados sem solução por bloqueio mútuo complexo** recebem h finito. Só os casos geométricos (sem rota pela borda ou pela regra colinear) viram ∞.

**Pode superestimar? Admissível?** Nenhuma superestimativa em 793.856 estados (6x6, seed 42) nem nas amostras do H3-revisao.md (6x6 e 7x7, cerca de 3,5 milhões de estados). Há um **esboço** de prova em H3-revisao.md: todo veículo de D precisa se mover em toda solução, um veículo por ação, e a saída de X é uma ação extra. Classificação: **admissível, com argumento e testes. A prova formal ainda precisa ser revisada pela equipe.**

**Consistente? Não sabemos.**
- Não há prova.
- Não há contraexemplo: 0 violações em 9,6 milhões de transições exatas (6x6), nas amostras 6x6 e 7x7 do H3-revisao.md e nos passeios em 8x8, 10x10 e 12x12.
- Por que a prova não é simples: uma única ação pode mudar a **viabilidade geométrica** de rotas em vários níveis da recursão ao mesmo tempo. Foi exatamente assim que a variante `continue` violava a consistência (H3-revisao.md, seção 3).
- Na prática, o A* atual continua ótimo de qualquer forma: ele reabre estados (D3). E "reexpandidos" = 0 nos experimentos será um indício a favor da consistência.

---

## O que isso implica para a previsão da seção 7

A teoria diz que, se h₂ ≥ h₁ em todo estado e as duas são consistentes, o A* com h₂ não expande nenhum estado que o A* com h₁ deixaria de expandir, a menos de empates em f = C*.
- Hfinal ≥ H1 foi verificado.
- H1 é consistente (prova).
- A consistência da Hfinal não está provada.
- A regra de desempate (D5, definicao-metricas.md) pesa muito nas contagens.

**A previsão é da equipe e deve ser registrada antes de rodar a comparação de expandidos.** Esta crítica não roda essa comparação.
