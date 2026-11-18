# Decisões de implementação sugeridas pela IA (seção 5 do enunciado)

Cada decisão registra: o que a IA sugeriu, a nossa interpretação, a decisão (aceitar / rejeitar / modificar) e o argumento.

---

## Contexto: crítica ao formato de instância proposto pela equipe

**Nossa proposta:** .txt, uma linha do arquivo por linha do tabuleiro, células separadas por espaço, "." = vazio, maiúsculas ≠ minúsculas, saída na borda direita da linha do X.

**Crítica da IA:**

| Ponto | Avaliação |
|---|---|
| Células separadas por espaço | ✅ Bom: permite ids de mais de um caractere sem ambiguidade. |
| Maiúsculas ≠ minúsculas | ✅ Necessário: o enunciado usa "a"–"h" e "A"–"H" como veículos diferentes. |
| N deduzido pelo número de linhas | ✅ Funciona. Exige validar que toda linha tem N células (linhas de tamanhos diferentes = erro). |
| Saída implícita (borda direita da linha do X) | ✅ É o que o enunciado define. O formato não representa outras saídas, mas o problema também não as tem. |
| Um caractere por id | ⚠️ Limita a 52 veículos (62 com dígitos). Um 12x12 comporta até 72. O gerador aleatório usa ids "10", "11"…, que não poderiam ser salvos e relidos. → **D1** |
| "." como vazio | ⚠️ O PDF do enunciado usa "·": copiar e colar falharia. → **D1** |
| Rótulos de linha/coluna e "−→ SAÍDA" do PDF | ❌ Não devem ser aceitos: um rótulo "10" é indistinguível de um veículo "10". É preciso removê-los ao transcrever. |
| Metadados (nome, custo ótimo esperado) | ⚠️ O formato não tem onde anotá-los. Foram adicionados comentários com `#`, ignorados pelo loader. |
| Tabuleiro do enunciado | ❌ Confirmado inválido: 'b' ocupa [(10,5), (11,5), (12,4)] e 'd' ocupa só (11,3). Todo o resto é válido. |

---

## D1 — Ids de vários caracteres e "·" como célula vazia

**O que a IA sugeriu:** tratar cada "palavra" separada por espaços como id de veículo, de qualquer tamanho (`A`, `a`, `10`, `11`). Aceitar tanto "." quanto "·" como vazio.

**Argumentos da IA:**
- O mesmo formato serve para instâncias escritas à mão e para tabuleiros gerados, que podem ser salvos com `save_board` e relidos (`test_ida_e_volta_texto`).
- Não há limite de 52 veículos.
- O tabuleiro do PDF pode ser colado sem trocar "·" por ".".

**Custo / risco:**
- Quem digitar `AA` sem espaço cria **um** veículo chamado "AA" de 1 célula, em vez de duas células de "A". O loader rejeita com "veículo 'AA' ocupa só 1 célula", mas a mensagem não diz que faltou um espaço.
- Arquivos com ids longos ficam desalinhados se não forem salvos com `save_board`.

**Nossa interpretação:** (Enzo) a IA quer que o arquivo seja lido "por palavras" e não "por letras". Assim um carro pode se chamar "10", e o "·" copiado do PDF conta como casa vazia.
**Decisão:** aceitamos.
**Por quê:** o nosso gerador já cria carros "10" e "11" (foi o mesmo problema que vimos na tela no IH02). Sem isso não daria para salvar e reler esses tabuleiros nos experimentos. O risco de alguém digitar `AA` sem espaço fica como limitação conhecida, porque o loader rejeita esse caso, só que com uma mensagem pouco clara.

---

## D2 — Instância válida, mas sem solução: carregar com aviso, não rejeitar

**O que a IA sugeriu:** o loader **rejeita** só o que viola as regras do jogo (forma NxN, linha reta, tamanho 2–3, X presente e horizontal). Quando há um veículo horizontal na linha do X, à direita dele, a instância é válida pelas regras mas nunca terá solução, porque esse veículo não pode sair da frente. Nesse caso o loader **carrega normalmente** e `avisos()` devolve uma mensagem, que o `main.py` exibe.

**Argumentos da IA:**
- "Inválida" (viola as regras) e "insolúvel" (respeita as regras, mas não tem solução) são coisas diferentes. Instâncias insolúveis são úteis em experimentos: a BFS precisa esgotar o espaço, e dá para medir quanto custa provar que não há solução.
- O aviso detecta só um caso trivial. Outros casos insolúveis só a busca descobre, e rejeitar só esse caso daria uma falsa sensação de garantia.

**Alternativa:** rejeitar no carregamento. É mais simples para quem usa a interface, mas mistura validação de formato com análise de solubilidade.

**Nossa interpretação:** (João) o leitor de arquivo só confere se o tabuleiro respeita as regras; descobrir se tem solução é papel da busca. O aviso é só uma ajuda para o caso mais óbvio. *(⚠️ confirmar com João)*
**Decisão:** aceitamos.
**Por quê:** instâncias sem solução são úteis nos experimentos, para medir quanto a BFS gasta até provar que não há saída. E rejeitar só o caso óbvio daria a falsa impressão de que toda instância carregada tem solução. *(⚠️ confirmar com João)*

---

## Pendência: o tabuleiro do enunciado

O arquivo `codigo/instancias/invalidas/enunciado_12x12_como_publicado.txt` guarda a transcrição fiel e é rejeitado pelo loader.

Hipóteses de correção mínima (as casas envolvidas estão vazias no original):
- 'b' em (10,5), (11,5), (12,5): vertical de tamanho 3, mudando só a última casa uma coluna para a direita;
- 'd' em (11,3), (12,3): vertical de tamanho 2.

**Decisão da equipe:** perguntar ao professor (Enzo leva a pergunta). Até a resposta, a transcrição fiel fica em `invalidas/` e nenhum resultado oficial usa uma versão corrigida por nós. Se não houver resposta a tempo, usamos a correção mínima acima e deixamos isso explícito no relatório.
