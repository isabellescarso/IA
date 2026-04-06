import os
from functools import lru_cache
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher
from rag.retriever import ContextRetriever
from rag.rag_pipeline import OllamaLlmClient, RagPipeline

from mlops.ask_tracker import AskExperimentTracker


@lru_cache
def build_rag_pipeline() -> RagPipeline:
    connections.connect(
        alias="default",
        host=os.getenv("MILVUS_HOST", "localhost"),
        port=os.getenv("MILVUS_PORT", "19530"),
    )
    collection = Collection(os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings"))
    collection.load()

    embedder = OllamaEmbedder(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("EMBED_MODEL", "nomic-embed-text"),
    )
    searcher = MilvusSemanticSearcher(collection)
    retriever = ContextRetriever(embedder, searcher)
    llm = OllamaLlmClient(
        os.getenv("OLLAMA_URL", "http://localhost:11434"),
        os.getenv("LLM_MODEL", "llama3.2"),
    )
    return RagPipeline(retriever, llm)


@lru_cache
def build_ask_tracker() -> AskExperimentTracker:
    return AskExperimentTracker(
        tracking_uri="sqlite:///mlflow.db",
        experiment_name="RAG_Requests",
    )