import os
import requests
from dotenv import load_dotenv
from pymilvus import connections, Collection

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")

def get_embedding(text: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["embedding"]

def main():
    query = "registro com glicose elevada e dados nutricionais"
    query_embedding = get_embedding(query)

    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    collection = Collection(MILVUS_COLLECTION)
    collection.load()

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=3,
        output_fields=["text"]
    )

    print(f"\nConsulta: {query}\n")
    for hits in results:
        for hit in hits:
            print(f"ID: {hit.id}")
            print(f"Distância: {hit.distance}")
            print(f"Texto: {hit.entity.get('text')}")
            print("-" * 80)

if __name__ == "__main__":
    main()