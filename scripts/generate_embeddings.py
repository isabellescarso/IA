import os
from io import BytesIO

import pandas as pd
import requests
from dotenv import load_dotenv
from minio import Minio
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")
GOLD_OBJECT = os.getenv("GOLD_OBJECT", "gold/dataset_ml.csv")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

def read_csv_from_minio(bucket: str, object_name: str) -> pd.DataFrame:
    response = None
    try:
        response = client.get_object(bucket, object_name)
        data = response.read()
        return pd.read_csv(BytesIO(data))
    finally:
        if response is not None:
            response.close()
            response.release_conn()

def build_text(row: pd.Series) -> str:
    partes = []
    for col in row.index:
        partes.append(f"{col}: {row[col]}")
    return " | ".join(partes)

def get_embedding(text: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": EMBED_MODEL,
            "prompt": text
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["embedding"]

def create_collection_if_not_exists(dim: int):
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(MILVUS_COLLECTION):
        return Collection(MILVUS_COLLECTION)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
    ]
    schema = CollectionSchema(fields, description="Embeddings do dataset CGMacros")
    collection = Collection(name=MILVUS_COLLECTION, schema=schema)

    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()
    return collection

def main():
    df = read_csv_from_minio(MINIO_BUCKET, GOLD_OBJECT)

    if df.empty:
        raise ValueError("O dataset Gold está vazio.")

    textos = []
    ids = []
    embeddings = []

    for idx, (_, row) in enumerate(df.head(200).iterrows()):
        texto = build_text(row)
        emb = get_embedding(texto)

        ids.append(idx + 1)
        textos.append(texto)
        embeddings.append(emb)

        if idx == 0:
            dim = len(emb)

    collection = create_collection_if_not_exists(dim)

    existing = collection.num_entities
    if existing > 0:
        print(f"Coleção já possui {existing} entidades. Inserindo novos dados...")

    collection.insert([ids, textos, embeddings])
    collection.flush()
    collection.load()

    print(f"Embeddings gerados e indexados com sucesso na coleção '{MILVUS_COLLECTION}'.")
    print(f"Total inserido: {len(ids)}")

if __name__ == "__main__":
    main()