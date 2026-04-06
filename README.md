# Plataforma RAG com Governança de Dados

Projeto desenvolvido para a disciplina de **Inteligência Artificial**.

Plataforma de **Retrieval-Augmented Generation (RAG)** para consultas inteligentes sobre dados de saúde e nutrição.

---

## Domínio

Saúde — Laboratório de análises clínicas.

---

## Problema de Negócio

Dados de glicose e nutrição distribuídos em múltiplos arquivos dificultam análise rápida. A plataforma centraliza esses dados e permite consultas em linguagem natural com interpretação via IA.

---

## Dataset

https://www.physionet.org/content/cgmacros/1.0.0/

---

## Arquitetura

```
CSV → Bronze (Parquet) → Silver → Gold → Embeddings → Milvus → RAG → FastAPI → Gradio
```

### Medallion Architecture — MinIO

| Camada | Responsabilidade |
|--------|-----------------|
| Bronze | CSV → Parquet · dados brutos por paciente |
| Silver | Filtro missing >30% · features temporais · drop non-numeric |
| Gold | Interpolação · split temporal 80/20 · coluna `split` |

### Stack

| Componente | Tecnologia |
|-----------|-----------|
| Data Lake | MinIO |
| Banco vetorial | Milvus |
| LLM local | Ollama (llama3.2) |
| Embeddings | Ollama (nomic-embed-text) |
| Experiment tracking | MLflow (SQLite) |
| API | FastAPI |
| Interface | Gradio |
| Infraestrutura | Docker Compose |

### Resultados

| Métrica | Valor |
|---------|-------|
| Vetores indexados | 22.836 |
| MAE glicose | 11.62 mg/dL |
| R2 | 0.94 |
| Latência RAG (CPU) | ~14–46s |
| Validação sistema | 4/4 ✅ |

---

## Estrutura do Projeto

```
src/
├── api/
│   ├── dependencies.py
│   ├── main.py
│   └── routes/
│       ├── ask.py
│       └── metadata.py
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── embeddings/
│   ├── gold_reader.py
│   ├── milvus_indexer.py
│   ├── ollama_embedder.py
│   ├── semantic_searcher.py
│   └── text_builder.py
├── ingestion/
│   ├── bronze/
│   │   └── bronze_pipeline.py
│   ├── silver/
│   │   ├── silver_pipeline.py
│   │   └── silver_transformations.py
│   ├── gold/
│   │   ├── gold_pipeline.py
│   │   └── gold_transformations.py
│   ├── converters.py
│   ├── eda_report.py
│   └── loaders.py
├── mlops/
│   ├── ask_tracker.py
│   ├── prompt_evaluator.py
│   └── training_tracker.py
├── rag/
│   ├── prompt_builder.py
│   ├── rag_pipeline.py
│   └── retriever.py
├── scripts/
│   ├── eda/
│   │   └── eda_bronze.py
│   ├── ingest/
│   │   ├── ingest_bronze.py
│   │   ├── ingest_silver.py
│   │   └── ingest_gold.py
│   ├── evaluate_prompts.py
│   ├── generate_embeddings.py
│   ├── search_embeddings.py
│   ├── train_model.py
│   └── validate_system.py
└── ui/
    └── gradio_app.py
```

---

## Comandos

```bash
# Infraestrutura
make up
make down

# Pipeline completo
make pipeline

# Serviços individuais
make api
make ui
make mlflow

# Validação
make validate
```

---

## Decisões Técnicas

**CSV → Parquet** — redução ~70% no tamanho · schema explícito · leitura colunar eficiente.

**Split temporal** — dados CGM são série temporal. Split aleatório causa data leakage. Corte em 80% cronológico garante que o modelo nunca vê o futuro durante treino.

**fillna(0) removido** — imputação zero em glicose introduz viés clínico severo. Substituído por interpolação forward-only com `dropna` no target.

**PostgreSQL removido** — não utilizado na implementação. Dependência eliminada do compose.

**MLflow em SQLite** — filesystem tracking deprecated desde fev/2026. SQLite persiste experimentos e é compatível com UI local.

---

## Papéis Scrum

**Product Owner** — Isabelle Munhoz Scarso (RA: 223285)

**Scrum Master** — Rafael Ferro Machado (RA: 223347)

**Time de Desenvolvimento**

| Nome | RA |
|------|----|
| Gabriel Habila Pinheiro | 211981 |
| Gabriela Zala Coutinho Arruda | 212191 |
| Cainã Jose Arruda Pinto | 210626 |
| Leonardo Braz de Almeida Fonseca | 212092 |
| André Lucas Costa Pereira | 200431 |
| Lara Beatriz Costa Sabino | 223228 |
| Bruno de Oliveira Malena | 222449 |
| Henry Santuriao Almeida | 211726 |
