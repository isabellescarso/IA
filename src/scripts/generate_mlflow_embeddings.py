# src/scripts/generate_mlflow_embeddings.py

import os
import mlflow
from dotenv import load_dotenv
from src.embeddings.ollama_embedder import OllamaEmbedder
from src.embeddings.milvus_indexer import MilvusCollectionFactory, MilvusRecordBatch
from pymilvus import connections, utility

load_dotenv()

OLLAMA_URL        = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL       = os.getenv("EMBED_MODEL", "nomic-embed-text")
MILVUS_HOST       = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT       = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MLFLOW_MILVUS_COLLECTION", "mlflow_embeddings")
MLFLOW_URI        = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT = os.getenv("MLFLOW_TRAIN_EXPERIMENT", "Sprint_4_CGMacros")
BASE_RECORD_ID    = 9_000_000


def build_run_text(run: mlflow.entities.Run) -> str:
    parts = [
        f"Experimento de Machine Learning: {run.info.experiment_id}",
        f"Run: {run.info.run_name or run.info.run_id}",
    ]

    model_name = (
        run.data.tags.get("model_name")
        or run.data.params.get("model_name")
        or run.data.params.get("model", "")
    )
    if model_name:
        parts.append(f"Algoritmo utilizado: {model_name}")

    if run.data.params:
        params_str = " | ".join(f"{k}: {v}" for k, v in run.data.params.items())
        parts.append(f"Parâmetros: {params_str}")

    if run.data.metrics:
        metrics_str = " | ".join(f"{k}: {v:.4f}" for k, v in run.data.metrics.items())
        parts.append(f"Métricas: {metrics_str}")

    return "\n".join(parts)


def drop_existing_collection() -> None:
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    if utility.has_collection(MILVUS_COLLECTION):
        utility.drop_collection(MILVUS_COLLECTION)
        print(f"[mlflow-embeddings] coleção '{MILVUS_COLLECTION}' removida")


def main() -> None:
    drop_existing_collection()

    mlflow.set_tracking_uri(MLFLOW_URI)
    embedder  = OllamaEmbedder(OLLAMA_URL, EMBED_MODEL)
    factory   = MilvusCollectionFactory(MILVUS_COLLECTION, MILVUS_HOST, MILVUS_PORT)

    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT)
    if experiment is None:
        print(f"[mlflow-embeddings] Experimento '{MLFLOW_EXPERIMENT}' não encontrado.")
        return

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        output_format="list",
    )

    batch      = MilvusRecordBatch()
    collection = None
    record_id  = BASE_RECORD_ID

    for run in runs:
        text      = build_run_text(run)
        embedding = embedder.embed(text)

        if collection is None:
            collection = factory.get_or_create(embedding.dimension())

        batch.add(record_id, text, embedding.as_list())
        record_id += 1
        print(f"[mlflow-embeddings] run {run.info.run_id[:8]}… adicionado")

    if collection is not None:
        inserted = batch.flush_into(collection)
        print(f"[mlflow-embeddings] {inserted} vetores indexados em '{MILVUS_COLLECTION}'")
    else:
        print("[mlflow-embeddings] Nenhum run encontrado.")


if __name__ == "__main__":
    main()