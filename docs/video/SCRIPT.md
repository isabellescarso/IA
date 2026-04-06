**Roteiro — Pitch 10 minutos**

---

**0:00–1:00 — Problema**
Dados de glicose e nutrição distribuídos em múltiplos arquivos CSV por paciente. Análise manual é lenta e não escala. Pergunta direta: *"Como permitir que qualquer pessoa consulte esses dados em linguagem natural?"*

---

**1:00–2:30 — Arquitetura**
Mostrar o diagrama:
```
CSV → Bronze → Silver → Gold → Embeddings → Milvus → RAG → FastAPI → Gradio
```
Destacar três decisões técnicas com justificativa:
- CSV → Parquet: redução de 70% no tamanho
- Split temporal no treino: elimina data leakage em séries temporais
- Medallion Architecture: rastreabilidade completa de cada transformação

---

**2:30–4:00 — Demonstração dos dados**
Abrir MLflow em `localhost:5000`. Mostrar:
- Experimento `EDA_Bronze` — missing ratio e distribuição de glicose por paciente
- Experimento `Sprint_4_CGMacros` — MAE 11.62 · R2 0.94 · feature importance

---

**4:00–5:30 — Demonstração do RAG**
Abrir Gradio em `localhost:7860`. Fazer duas perguntas ao vivo:
1. *"Quais registros apresentam glicose elevada com baixa atividade física?"*
2. *"Qual o valor médio de glicose nos registros?"*

Mostrar resposta gerada e comentar que o modelo usa apenas os dados indexados.

---

**5:30–7:00 — MLflow · Avaliação de prompts**
Mostrar experimento `Prompt_Evaluation`:

| Variante | Latência | Chars |
|----------|----------|-------|
| direto | 22.7s | 876 |
| especialista | 36.2s | 1773 |
| estruturado | 37.1s | 2046 |

Conclusão: `direto` 40% mais rápido, suficiente para consultas objetivas.

---

**7:00–8:00 — Validação do sistema**
Rodar ao vivo:
```bash
make validate
```
Mostrar 4/4 verificações passando.

---

**8:00–9:00 — Decisões técnicas**
Três pontos que diferenciam o projeto:
- Data leakage identificado e corrigido — split temporal sobre coluna `split` gerada no Gold
- `fillna(0)` removido — imputação zero em glicose introduz viés clínico
- MLflow em SQLite — elimina deprecation do filesystem e persiste experimentos

---

**9:00–10:00 — Encerramento**
Mostrar estrutura final do projeto no terminal:
```bash
make up && make validate
```
Pipeline completo em um comando. Sistema reproduzível por qualquer membro da equipe.