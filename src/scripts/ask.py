import os
from dotenv import load_dotenv
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher
from rag.retriever import ContextRetriever
from rag.rag_pipeline import OllamaLlmClient, RagPipeline

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")

connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
collection = Collection(MILVUS_COLLECTION)
collection.load()

embedder = OllamaEmbedder(OLLAMA_URL, EMBED_MODEL)
searcher = MilvusSemanticSearcher(collection)
retriever = ContextRetriever(embedder, searcher)
llm = OllamaLlmClient(OLLAMA_URL, LLM_MODEL)
pipeline = RagPipeline(retriever, llm)

question = "Quais registros apresentam glicose elevada com baixa atividade física?"
pipeline.answer(question).print()