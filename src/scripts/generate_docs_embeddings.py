# src/scripts/generate_docs_embeddings.py
import os
from dotenv import load_dotenv
from pymilvus import connections, Collection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.milvus_indexer import MilvusCollectionFactory, MilvusRecordBatch

load_dotenv()

OLLAMA_URL  = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION  = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")
BASE_ID     = 8_000_000

DOCS = [
    "docs/eda_readme.md",
]

def chunk_text(text: str, size: int = 500) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def main() -> None:
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    embedder  = OllamaEmbedder(OLLAMA_URL, EMBED_MODEL)
    dimension = embedder.embed("dim").dimension()
    collection = MilvusCollectionFactory(COLLECTION, MILVUS_HOST, MILVUS_PORT).get_or_create(dimension)

    batch     = MilvusRecordBatch()
    record_id = BASE_ID

    for path in DOCS:
        with open(path, "r") as f:
            text = f.read()
        chunks = chunk_text(text)
        for chunk in chunks:
            embedding = embedder.embed(chunk)
            batch.add(record_id, chunk, embedding.as_list())
            record_id += 1
            print(f"[docs] chunk {record_id} indexado")

    inserted = batch.flush_into(collection)
    print(f"[docs] {inserted} chunks indexados em '{COLLECTION}'")


if __name__ == "__main__":
    main()