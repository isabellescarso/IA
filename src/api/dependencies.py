import os
from functools import lru_cache
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher
from rag.retriever import ContextRetriever
from rag.rag_pipeline import OllamaLlmClient, RagPipeline
from rag.ridge_predictor import RidgeGlucosePredictor
from mlops.ask_tracker import AskExperimentTracker
from api.routes.metadata import MetadataHandler


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
    return RidgeGlucosePredictor(
        model_uri=os.getenv("RIDGE_MODEL_URI", "http://localhost:5000"),
        experiment_name=os.getenv("MLFLOW_EXPERIMENT", "Sprint_4_CGMacros"),
    )


@lru_cache
def build_rag_pipeline() -> RagPipeline:
    embedder = OllamaEmbedder(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("EMBED_MODEL", "nomic-embed-text"),
    )
    retriever = ContextRetriever(embedder, MilvusSemanticSearcher(build_milvus_collection()))
    llm = OllamaLlmClient(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("LLM_MODEL", "llama3.2"),
    )
    return RagPipeline(retriever, llm, build_ridge_predictor())


@lru_cache
def build_ask_tracker() -> AskExperimentTracker:
    return AskExperimentTracker(
        tracking_uri="http://localhost:5000",
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