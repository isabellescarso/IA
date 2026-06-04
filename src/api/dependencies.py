import os
from functools import lru_cache
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher
from rag.retriever import ContextRetriever
from mlops.ask_tracker import AskExperimentTracker
from api.routes.metadata import MetadataHandler
from rag.model_loader import RidgeGlucosePredictorLoader
from rag.glucose_predictor import RidgeGlucosePredictor
import mlflow
from rag.rag_pipeline import ContextualPredictor, OllamaLlmClient, RagPipeline

from embeddings.milvus_indexer import MilvusCollectionFactory


@lru_cache
def build_milvus_collection() -> Collection:
    connections.connect(
        alias="default",
        host=os.getenv("MILVUS_HOST", "localhost"),
        port=os.getenv("MILVUS_PORT", "19530"),
    )
    collection = Collection(os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings"))
    collection.load()
    return collection


@lru_cache
def build_ridge_predictor() -> RidgeGlucosePredictor:
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    return RidgeGlucosePredictorLoader("modelo_glicose").load()


@lru_cache
def build_rag_pipeline() -> RagPipeline:
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    milvus_port = os.getenv("MILVUS_PORT", "19530")

    connections.connect(alias="default", host=milvus_host, port=milvus_port)

    embedder = OllamaEmbedder(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("EMBED_MODEL", "nomic-embed-text"),
    )
    dimension = embedder.embed("dim").dimension()

    col_clinical = MilvusCollectionFactory("cgmacros_embeddings", milvus_host, milvus_port).get_or_create(dimension)
    col_mlflow   = MilvusCollectionFactory("mlflow_embeddings",   milvus_host, milvus_port).get_or_create(dimension)

    retriever = ContextualPredictor(
        ContextRetriever(collections=[col_clinical, col_mlflow], embedder=embedder),
        build_ridge_predictor(),
    )
    llm = OllamaLlmClient(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("LLM_MODEL", "llama3.2"),
    )
    return RagPipeline(retriever, llm)


@lru_cache
def build_ask_tracker() -> AskExperimentTracker:
    return AskExperimentTracker(
        tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
        experiment_name="RAG_Requests",
    )


@lru_cache
def build_metadata_handler() -> MetadataHandler:
    return MetadataHandler(
        collection=build_milvus_collection(),
        patients=["CGMacros-012", "CGMacros-039"],
        embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        llm_model=os.getenv("LLM_MODEL", "llama3.2"),
    )