# Revisão da Heurística 3 (Cascata)- (Enzo Carvalho + Claude): ciclos, admissibilidade e consistência

Análise feita a partir do contraexemplo encontrado pela equipe (6x6, h = ∞, h* = 12)
e do verificador `codigo/testes/verificar_admissibilidade.py`.
Coordenadas: (linha, coluna), a partir de 0.

## 1. Por que a versão original dá h = ∞ no exemplo

```
 .  1  1  .  .  .
 .  2  7  .  .  8
 .  2  7  X  X  8
 4  4  4 11 11  8
 0  5  5  5  3  3
 0  9  9  6  6  6
```
(A view antiga mostrava os veículos "1" e "11" como "1".)

| Passo | Veículo | Precisa liberar | Rota negativa (esq/cima) | Rota positiva (dir/baixo) |
|---|---|---|---|---|
| 1 | X | (2,5) | — | ocupada por **8** |
| 2 | 8 (V, col 5, linhas 1–3) | (2,5) | cabeça na linha −1: impossível (borda) | linhas 3–5: precisa de (4,5)=**3** e (5,5)=**6** |
| 3 | 3 (H, linha 4, col 4–5) | (4,5) | cabeça na col 3: precisa de (4,3)=**5** | impossível (borda) |
| 4 | 5 (H, linha 4, col 1–3) | (4,3) | cabeça na col 0: precisa de (4,0)=**0** | impossível (borda) |
| 5 | 0 (V, col 0, linhas 4–5) | (4,0) | cabeça na linha 2: precisa de (2,0) livre e (3,0)=**4** | impossível (borda) |
| 6 | 4 (H, linha 3, col 0–2) | (3,0) | impossível (borda) | cabeça na col 1: precisa de (3,3)=**11** |
| 7 | 11 (H, linha 3, col 3–4) | (3,3) | precisa de (3,1),(3,2) = **4** → já visitado → `return None` | precisa de (3,5) = **8** → já visitado → `return None` |

Os dois ramos de 11 dão `None`. O `None` sobe pela cadeia 11 → 4 → 0 → 5 → 3. O `return None` dentro do laço sobre {3, 6} invalida a rota positiva de 8. Como a rota negativa de 8 já era impossível, 8 fica sem rotas e h = ∞.

**Por que isso é falso.** A recursão supõe, sem dizer, que cada veículo se move uma única vez, num único sentido, e que todos os outros estão parados nas posições atuais. Ela trata "11 precisa da casa onde 8 está" como impossível. A solução ótima (custo 12, encontrada pelo próprio A*) mostra o contrário:

```
 1. 8 sobe (linhas 0–2)        ← libera (3,5)
 2. 11 vai para a coluna 4     ← usa a casa que 8 acabou de liberar
 3. 4 vai para a coluna 1
 4. 0 sobe (linhas 0–1)
 5. 4 volta para a coluna 0
 6. 11 volta para a coluna 3
 7. 9 → col 0   8. 5 → col 0   9. 3 → col 3   10. 6 → col 2
11. 8 desce (linhas 3–5)       ← 8 se move pela 2ª vez
12. X sai
```
Os veículos 8, 4 e 11, os mesmos que formam os ciclos, se movem duas vezes cada. Um ciclo de dependências indica que alguém vai precisar se mover mais de uma vez. Ele não indica que o estado é insolúvel.

## 2. Crítica da correção `continue`

**Mantém a admissibilidade? Sim, e o argumento é este.** Quando a recursão encontra um ancestral `w`, `w` já está em D, porque `deps.add(w)` acontece antes da recursão. Exigir de novo que `w` se mova não acrescenta nada ao limite inferior. Com `continue`, a restrição é descartada:
- nenhum veículo novo entra em D;
- um ramo que antes era `None` pode virar válido, e aí a interseção dos ramos só diminui.

Ou seja, D_continue ⊆ D_original sempre que a original é finita. Se a original não superestima nos estados finitos, a `continue` também não. No verificador, `continue` teve 0 superestimativas em 3,1 milhões de estados (tabela abaixo).

**Limitação: o `continue` descarta informação verdadeira.** Alguns ciclos são impossibilidades reais: dois veículos na **mesma linha (ou coluna)** nunca passam um pelo outro. É daí que vêm as violações de consistência (seção 3).

**Correção melhor: `continue` + regra colinear** (`regra_colinear=True`, padrão no código):
1. Se `u` é colinear ao veículo `M` que precisa das células, `u` só pode fugir no **mesmo sentido** em que `M` avança. No sentido oposto, ele continuaria no trecho que `M` precisa percorrer, já que não pode atravessar `M`.
2. `u` precisa sair do **trecho inteiro** de que `M` precisa, e não só das casas que ocupa hoje. Esse 2º defeito só apareceu nos testes em 7x7 (episódio M02).

**Esboço de prova de admissibilidade (a equipe precisa revisar):**
- *Lema:* se as células S precisam estar vazias em algum momento antes da saída de X, todo veículo que ocupa S agora se move pelo menos uma vez.
- Para sair de S ∩ linha(u), `u` termina inteiramente de um lado desse trecho. Para isso ele atravessa as `cells_to_clear` daquele lado, e cada uma delas precisa estar vazia em algum momento. Então o lema se aplica de novo a elas.
- Toda solução usa pelo menos um dos dois lados. Por isso os veículos da **interseção** dos ramos se movem em toda solução.
- Um lado impossível pela borda, ou pela regra colinear, não é usado por nenhuma solução.
- Cada ação move um único veículo, logo |D| ações distintas.
- Se X ∈ D, então X precisa sair do lugar antes da saída, e a saída é outra ação. Por isso h = 1 + |D| ≤ h*.

**Resultados do verificador** (seed fixa, todos os estados alcançáveis de cada tabuleiro; Σh/Σh* mede o quanto h se aproxima do custo real):

| Amostra | Variante | Estados | h > h* | h(n) > 1 + h(n') | Σh/Σh* |
|---|---|---|---|---|---|
| 6x6, seed 42, 12 veíc. (104 tab.) | original | 793.856 | **2.859** (todos ∞) | 1.996 | — (∞ excluídos) |
| | continue | 793.856 | 0 | **1.775** | 0,760 |
| | colinear | 793.856 | 0 | **0** | **0,881** |
| 6x6, seed 7, 10 veíc. (143 tab.) | continue | 2.238.314 | 0 | 2.363 | 0,788 |
| | colinear | 2.238.314 | 0 | 0 | 0,841 |
| 6x6, seed 99, 14 veíc. (58 tab.) | continue | 71.559 | 0 | 816 | 0,680 |
| | colinear | 71.559 | 0 | 0 | 0,923 |
| 7x7, seed 3, 15 veíc. (10 tab.) | colinear sem "trecho inteiro" | 413.245 | 0 | 2.964 | 0,702 |
| | colinear (final) | 413.245 | 0 | 0 | 0,707 |

Limite do teste: em 8x8 ou maior, os componentes de estados passam de 60 mil e o cálculo exato de h* fica caro demais. Nada foi verificado nesses tamanhos.

## 3. A afirmação "a heurística é consistente" do H3.md

**Por que é falsa.** A seção "Garantia de Admissibilidade e Consistência" só argumenta que h não superestima, o que é admissibilidade. Consistência é outra propriedade: h(n) ≤ 1 + h(n') para **toda** ação n → n'. Ou seja, uma única ação não pode baixar h em mais de 1. Admissibilidade não implica consistência, e o texto não dá nenhum argumento para a segunda. O verificador encontrou 1.775 violações na versão `continue`. Exemplo:

```
n  (h = 4, h* = 4, D = {3,5,6})        n' (h = 2, h* = 4, D = {3})
 .  4  4  4 10 10                       4  4  4  . 10 10
 2  2  1  1  3  .                       2  2  1  1  3  .
 8  7  X  X  3  .        4 → col 0      8  7  X  X  3  .
 8  7  .  5  5  0      ───────────▶     8  7  .  5  5  0
 8  .  .  6  6  0                       8  .  .  6  6  0
11 11  9  9  .  .                      11 11  9  9  .  .
```
- Em n, a rota "3 sobe" exige que 10 vá para a esquerda. Isso exige que 4 saia, e 4 está preso entre a borda e 10. A rota é descartada, sobra "3 desce" e D = {3, 5, 6}.
- Em n', 4 tem espaço para ir à direita. Só que ir à direita significa ir **contra** 10, que está na mesma linha. A recursão chega a 10, vê o ciclo, aplica `continue` e aceita a rota "3 sobe". A interseção com "3 desce" fica vazia e h cai de 4 para 2 por causa de um veículo (4) que nem estava em D. O custo real continua 4, porque 10 nunca consegue sair da coluna 4.

A regra colinear descarta "4 vai contra 10". Com ela, essas violações sumiram em todas as amostras. **Mesmo assim, não sabemos se a versão colinear é consistente:** não temos prova, só a ausência de contraexemplo em ~3,5 milhões de estados (6x6 e 7x7).

**O nosso A\* continua ótimo?** Sim, desde que três condições valham:
1. **h admissível em todo estado com solução**, inclusive sem ∞ falso. A versão original viola isso, e aí a otimalidade não é garantida.
2. **O A\* reabre estados.** O `solver.py` atual não tem conjunto de fechados. Sempre que um estado é alcançado com g menor, ele volta para a fila (`cost_so_far`). Esse é o A\* com reabertura, que é ótimo com h só admissível. Se alguém adicionar um conjunto "visitados/fechados" que nunca reabre, a otimalidade **pode ser perdida** com h inconsistente.
3. **O teste de objetivo é feito ao retirar o estado da fila, e não ao gerá-lo.** O código atual faz isso.

O preço da inconsistência é desempenho: estados podem ser expandidos mais de uma vez. Por isso vale registrar as **re-expansões** como métrica nos experimentos.
