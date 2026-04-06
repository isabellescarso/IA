import os
from minio import Minio
from dotenv import load_dotenv
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import SemanticQuery, MilvusSemanticSearcher

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")

connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
collection = Collection(MILVUS_COLLECTION)
collection.load()

embedder = OllamaEmbedder(OLLAMA_URL, EMBED_MODEL)
searcher = MilvusSemanticSearcher(collection)

query = SemanticQuery("registro com glicose elevada e dados nutricionais")
embedding = embedder.embed(query.as_text())
results = searcher.search(embedding.as_list())

print(f"\nConsulta: {query.as_text()}\n")
results.print_each()