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
    """
    Constrói o pipeline de RAG, incluindo o embedder, retriever, predictor e cliente LLM.
    Utiliza caching para evitar reconstrução desnecessária dos componentes.
    """
    # Configura o embedder para gerar vetores de embedding usando o modelo especificado
    embedder = OllamaEmbedder(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("EMBED_MODEL", "nomic-embed-text"),
    )
    # Faz o get das colecoes,
    retriever = ContextRetriever(embedder, MilvusSemanticSearcher(build_milvus_collection()))
    # Load do modelo registrado no MLFlow
    contextual_predictor = ContextualPredictor(retriever, build_ridge_predictor())
    llm = OllamaLlmClient(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("LLM_MODEL", "llama3.2"),
    )
    return RagPipeline(contextual_predictor, llm)


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