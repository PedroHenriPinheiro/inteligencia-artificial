# Definição das métricas de busca

Valem para todos os experimentos e para `06-dados/resultados.csv`.
Implementação: `codigo/src/domain/search_result.py`, `service/bfs_solver.py`, `service/solver.py`.

## Unidade de trabalho comum

BFS e A* usam a **mesma** função `get_successors`, a mesma representação de estado (frozenset de posições) e o mesmo critério para reconhecer estados repetidos (igualdade do estado). As métricas são contadas nos mesmos pontos do código nos dois algoritmos:

| Métrica | Definição | Quando é contada |
|---|---|---|
| **Gerados** | 1 (estado inicial) + **todos** os sucessores devolvidos por `get_successors`, inclusive repetidos, já visitados e o objetivo | a cada expansão, soma-se o tamanho da lista de sucessores |
| **Expandidos** | estados para os quais `get_successors` foi chamado | ao chamar `get_successors` |
| **Reexpandidos** (A*) | expansões de um estado que já tinha sido expandido antes, por ter sido reencontrado com g menor | junto com "expandidos"; é um subconjunto dele |
| **Fronteira máxima** | maior número de estados **distintos** esperando para ser expandidos | após inserir os sucessores de cada expansão |
| **Tempo (ms)** | tempo de parede de `solve()`, **incluindo** o cálculo de h | `time.perf_counter` |
| **Custo** | número de ações da solução (vazio se não encontrou) | — |

### Gerado × expandido
- **Gerar** é criar um estado como sucessor de outro. É barato, e o mesmo estado pode ser gerado muitas vezes, por caminhos diferentes.
- **Expandir** é escolher um estado da fronteira e gerar todos os seus sucessores. É o passo de decisão do algoritmo, e cada expansão produz em média *b* gerados (fator de ramificação).
- Pela definição, gerados = 1 + Σ (nº de sucessores de cada expandido). Por isso "gerados" mede o custo de chamar `get_successors` e, no A*, também o de calcular h. Um estado gerado que já tinha sido visto **continua contando**, porque o trabalho de gerá-lo foi feito.
- O estado objetivo é gerado, mas **não** é expandido.

## Por que a comparação BFS × A* é justa

1. **Mesmo trabalho, mesma régua.** As duas buscas pagam o mesmo preço por expansão (a mesma `get_successors`) e são contadas nos mesmos pontos. Uma diferença em "expandidos" é uma diferença real de trabalho, e não um efeito de contabilidade.
2. **Cada algoritmo na sua forma correta.** A BFS testa o objetivo **ao gerar**. Com custo 1 por ação, a primeira vez que o objetivo é gerado já é pela menor profundidade, então isso continua ótimo. O A* **precisa** testar ao retirar da fila, senão perde a otimalidade.
3. **A diferença de teste de objetivo foi medida, não presumida.** Em 20 tabuleiros 6x6 (o exemplo + 19 aleatórios, seed 5), medidos de novo depois da correção de determinismo (IH05):

   | Variante | Expandidos (soma) |
   |---|---|
   | BFS, teste na geração (implementada) | 46.905 |
   | BFS, teste na retirada | 66.851 |
   | A* com h = 0 | 66.851 |

   A BFS com teste na retirada e o A* com h = 0 expandem **exatamente** o mesmo, e a BFS normal expande 30% menos. Ou seja, comparar BFS com A*(h) mistura dois efeitos: a hora do teste de objetivo e a informação de h.
4. **Por isso os experimentos devem reportar três linhas por instância:** BFS, A*(zero) e A*(heurística).
   - BFS × A*(h) responde "o que ganhamos em relação à busca não informada pedida no enunciado".
   - A*(zero) × A*(h) isola o efeito **da heurística**, porque os dois têm o mesmo algoritmo, o mesmo teste de objetivo e a mesma regra de desempate. Atenção: a regra desempata por h, então com h = 0 ela vira "ordem de inserção". Parte do ganho de A*(h) vem do desempate guiado por h (ver D5).
5. **Entradas desatualizadas da heap não contam.** Antes, o A* expandia de novo uma entrada antiga quando a retirava da heap, e isso inflava "expandidos". Agora ela é descartada (ver D3).
6. **A fronteira conta estados, não entradas.** A heap do A* pode ter entradas antigas. Contá-las faria o A* parecer usar mais memória do que usa de fato.

## Determinismo das contagens (corrigido no IH05)

**Problema (achado pela equipe):** o mesmo comando dava contagens diferentes a cada execução (BFS: 992, 992, 992 e 1.009), sempre com custo 12.

**Causa (a explicação da equipe estava certa):**
1. O estado é um `frozenset` de pares (id, coordenada).
2. A ordem de iteração de um frozenset depende do hash dos elementos, e o hash de strings é sorteado a cada processo do Python (`PYTHONHASHSEED`).
3. `get_successors` percorria `state.items()`, então a ordem dos sucessores mudava de execução para execução.
4. Com ela mudavam a ordem da fila da BFS e os desempates do A*.

O custo não muda porque os dois algoritmos são ótimos. As contagens mudam.

**A explicação anterior da IA estava errada.** Ela atribuía a diferença 1.006 × 995 à "ordem dos veículos no arquivo". Com `PYTHONHASHSEED` fixo, o arquivo e outra ordem de montagem davam números **idênticos**: a ordem do arquivo nem era usada, e a diferença vinha de as medições terem sido feitas em processos diferentes.

**Correção:** `get_successors` percorre os veículos na ordem de `board.vehicles`, que é a ordem de leitura do arquivo, e não mais a ordem do frozenset. O teste `codigo/testes/test_determinismo.py` roda as buscas em 5 processos com `PYTHONHASHSEED` diferentes e exige métricas idênticas. Ele falha sem a correção e passa com ela.

**Consequência:** agora sim a ordem dos veículos no arquivo influencia as contagens, de forma determinística e pequena (A*(zero) no exemplo: 1.187 carregado do arquivo × 1.186 montado em outra ordem).
**Regra:** todos os experimentos carregam as instâncias de arquivo, e o arquivo nunca é reordenado entre execuções.

## Exemplo (instância `exemplo_6x6_h12.txt`)

| Algoritmo | Custo | Gerados | Expandidos | Reexp. | Fronteira máx. |
|---|---|---|---|---|---|
| BFS | 12 | 8.349 | 1.009 | 0 | 216 |
| A* (zero) | 12 | 9.850 | 1.187 | 0 | 216 |
| A* (hfinal) | 12 | 226 | 37 | 0 | 71 |

(O tempo varia entre execuções e máquinas. Os outros valores são determinísticos e verificados por `test_determinismo.py`.)

> **Nota da equipe (Enzo, 28/10):** na prática, os valores **não** se repetiam entre execuções. A mesma BFS deu 992 expandidos em três execuções e 1.009 em uma, sempre com custo 12. Ver IH04, "Evidência posterior". **Resolvido no IH05** (seção "Determinismo das contagens"). A tabela acima já foi medida depois da correção.

---

## Decisões de implementação para a equipe avaliar (seção 5 do enunciado)

### D3 — A*: verificação de entrada desatualizada + reabertura (em vez de conjunto de fechados)

**O que a IA sugeriu:** ao retirar `(g, estado)` da heap, descartar a entrada se `g > melhor_g[estado]`. Se um estado já expandido for reencontrado com g menor, ele **volta** para a fila (reabertura), e isso é contado em "reexpandidos".

**Alternativa:** um conjunto de fechados sem reabertura (um estado expandido nunca mais é expandido).

**Argumentos da IA:**
- Com conjunto de fechados sem reabertura, o A* só é garantidamente ótimo se a heurística for **consistente**. A cascata atual não tem prova de consistência (H3-revisao.md), e as próximas heurísticas podem não ser consistentes.
- A reabertura mantém a otimalidade com h só admissível. Com h consistente ela nunca acontece, então não custa nada.
- "Reexpandidos" vira um **indicador de inconsistência**: se aparecer > 0, a heurística não é consistente naquela instância.

**Evidência (30 tabuleiros 6x6: o exemplo + 29 aleatórios, seed 11; A* antigo × antigo com a verificação, mesmo desempate):**

| Heurística | Expandidos (antigo) | Re-expansões (antigo) | Expandidos (com verificação) | Reexpandidos (com verificação) |
|---|---|---|---|---|
| hfinal (cascata) | 5.607 | 8 | 5.599 | 0 |
| zero | 95.900 | 0 | 95.900 | 0 |
| H0 (distância em células, inadmissível) | 52.509 | 141 | 52.377 | 9 |

A hipótese da equipe se confirmou: as entradas antigas inflavam "expandidos". O efeito, porém, foi pequeno nesta amostra (≤ 0,3%). Com a H0, as 9 reexpansões que sobraram são reaberturas legítimas, causadas pela inconsistência.
*Correção (IH05):* a versão anterior desta tabela foi medida antes da correção de determinismo e usava "distância + 1" no lugar da H0 exata. Os números acima substituem os anteriores, e as conclusões não mudam.

**Nossa interpretação:** (João) quando o A* acha um caminho mais curto para um estado, ele coloca o estado de novo na fila e simplesmente ignora a entrada velha. Fechar o estado para sempre só é seguro se a heurística for consistente, e a nossa não tem prova disso. *(⚠️ confirmar com João)*
**Decisão:** aceitamos.
**Por quê:** a otimalidade é o mais importante, e a cascata só é garantida como admissível (com testes), não como consistente. Além disso, "reexpandidos" passa a mostrar se a heurística foi inconsistente, o que é útil no relatório. O custo é quase zero: 0 reexpansões com a cascata nos 30 tabuleiros. *(⚠️ confirmar com João)*

### D4 — BFS testa o objetivo na geração, e A*(zero) entra como controle

**O que a IA sugeriu:** a BFS testa o objetivo ao gerar (forma padrão, ótima com custo unitário). Nos experimentos, reportar sempre BFS, A*(zero) e A*(h), para separar o efeito do teste de objetivo do efeito da heurística (tabela do item 3).

**Alternativa:** testar o objetivo na retirada nos dois algoritmos ("mesma regra para todos"). Isso piora a BFS em ~30% sem mudar o custo encontrado.

**Nossa interpretação:** (Enzo) a BFS pode parar assim que **cria** o estado objetivo, porque todos os passos custam 1 e ela anda por camadas. O A* precisa esperar o objetivo **sair da fila**. Por isso a BFS normal expande menos que o A* com h = 0, e a diferença não tem nada a ver com heurística.
**Decisão:** aceitamos.
**Por quê:** cada algoritmo fica na sua forma correta, e o A*(zero) serve de controle: comparando A*(zero) com A*(h), vemos só o efeito da heurística. Ressalva: as contagens estão variando entre execuções (ver IH04, "Evidência posterior"). Isso precisa ser corrigido antes dos experimentos. *(Resolvido no IH05.)*

### D5 — Desempate no A*: menor f, depois **menor h**, depois ordem de inserção

**O que a IA implementou (no IH04, classificado como "escolha menor"):** quando dois estados têm o mesmo f, expandir primeiro o de menor h, ou seja, o mais perto do objetivo pela estimativa. Em caso de novo empate, vale a ordem de inserção. O A* antigo desempatava por menor g e depois comparando os próprios frozensets, o que na prática é uma ordem arbitrária.

**Por que deixou de ser "menor" (medido no IH05, mesmos 30 tabuleiros da D3, ambos com a verificação de entrada antiga):**

| Heurística | Desempate antigo (f, g, frozenset) | Desempate novo (f, h, inserção) |
|---|---|---|
| hfinal | 5.599 | **2.804** (−50%) |
| zero | 95.900 | 94.164 (−2%) |
| H0 | 52.377 | 38.381 (−27%) |

O custo encontrado é o mesmo, mas os expandidos da hfinal caem pela metade **só por causa do desempate**. Isso acontece porque com custo 1 por ação muitos estados empatam em f. Na comparação entre heurísticas, parte do ganho de A*(h) sobre A*(zero) vem desse desempate guiado por h.

**Alternativas:** (a) manter (f, h, inserção); (b) desempatar só por ordem de inserção, para que a heurística aja apenas via f; (c) reportar as duas versões nos experimentos.

**Nossa interpretação:** (Pedro) quando muitos estados empatam em f (o que é comum com custo 1 por ação), escolher o de menor h é como "confiar mais" na heurística na hora do empate. Isso ajuda, mas mistura dois efeitos: o da heurística dentro de f e o do desempate. *(⚠️ confirmar com Pedro)*
**Decisão:** modificamos: alternativa (c).
**Por quê:** mantemos (f, h, inserção) como padrão, porque é o que dá menos expansões sem mudar o custo. Mas os experimentos também vão rodar com desempate só por ordem de inserção. Assim a comparação A*(zero) × A*(h) mostra quanto vem da heurística em f e quanto vem do desempate. Pedimos essa opção junto com o script de experimentos (prompt 6). *(⚠️ confirmar com Pedro)*

### Outras escolhas (menores) já implementadas
- **Poda de h = ∞:** um estado com h = ∞ não entra na fila do A*, mas conta como gerado. Isso só é seguro com h admissível: a versão original da cascata podaria estados com solução.
