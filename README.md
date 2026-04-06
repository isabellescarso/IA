# Plataforma RAG com Governança de Dados

Projeto desenvolvido para a disciplina de **Inteligência Artificial**.

Plataforma de **Retrieval-Augmented Generation (RAG)** para consultas inteligentes sobre dados de saúde e nutrição.

---

## Domínio

Saúde — Laboratório de análises clínicas.

---

## Problema de Negócio

Informações de saúde e nutrição distribuídas em múltiplas bases dificultam análise rápida. A plataforma centraliza esses dados e permite consultas em linguagem natural com interpretação via IA.

---

## Dataset

https://www.physionet.org/content/cgmacros/1.0.0/

---

## Arquitetura

```
CSV (Bronze) → Parquet (Silver) → Gold → Embeddings → Milvus → RAG → FastAPI → Gradio
```

### Camadas de dados (Medallion Architecture — MinIO)

| Camada | Formato | Responsabilidade |
|--------|---------|-----------------|
| Bronze | Parquet | Dados brutos por paciente |
| Silver | Parquet | Filtro missing · features temporais · tipos corretos |
| Gold   | Parquet | Numérico · interpolação · split temporal 80/20 |

### Componentes

| Componente | Tecnologia |
|-----------|-----------|
| Data Lake | MinIO |
| Banco vetorial | Milvus |
| Banco relacional | PostgreSQL |
| LLM local | Ollama (llama3.2) |
| Embeddings | Ollama (nomic-embed-text) |
| Experiment tracking | MLflow |
| API | FastAPI |
| Interface | Gradio |
| Infraestrutura | Docker Compose |

---

## Estrutura do Projeto

```
src/
├── api/
│   ├── dependencies.py
│   ├── main.py
│   └── routes/
│       └── ask.py
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── embeddings/
│   ├── gold_reader.py
│   ├── milvus_indexer.py
│   ├── ollama_embedder.py
│   └── text_builder.py
├── ingestion/
│   ├── bronze_pipeline.py
│   ├── converters.py
│   ├── eda_report.py
│   ├── gold_pipeline.py
│   ├── gold_transformations.py
│   ├── loaders.py
│   ├── silver_pipeline.py
│   └── silver_transformations.py
├── mlops/
│   └── ask_tracker.py
├── rag/
│   ├── prompt_builder.py
│   ├── rag_pipeline.py
│   └── retriever.py
├── scripts/
│   ├── ask.py
│   ├── eda_bronze.py
│   ├── generate_embeddings.py
│   ├── ingest_bronze.py
│   ├── ingest_gold.py
│   ├── ingest_silver.py
│   └── search_embeddings.py
└── ui/
    └── gradio_app.py
```

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