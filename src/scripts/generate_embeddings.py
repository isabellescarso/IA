import os
from minio import Minio
from dotenv import load_dotenv
from embeddings.gold_reader import GoldParquetReader
from embeddings.text_builder import DataFrameTextCollection
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.milvus_indexer import MilvusCollectionFactory, MilvusRecordBatch

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")
PATIENTS = ["CGMacros-012", "CGMacros-039"]
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False,
)

reader = GoldParquetReader(minio_client, MINIO_BUCKET)
embedder = OllamaEmbedder(OLLAMA_URL, EMBED_MODEL)
factory = MilvusCollectionFactory(MILVUS_COLLECTION, MILVUS_HOST, MILVUS_PORT)
factory.connect()

record_id = 1

for patient_id in PATIENTS:
    gold = reader.read(patient_id)
    texts = DataFrameTextCollection(gold.training_rows()).as_texts()
    batch = MilvusRecordBatch()

    first_embedding = embedder.embed(texts[0])
    collection = factory.get_or_create(first_embedding.dimension())
    batch.add(record_id, texts[0], first_embedding.as_list())
    record_id += 1

    for text in texts[1:]:
        batch.add(record_id, text, embedder.embed(text).as_list())
        record_id += 1

    inserted = batch.flush_into(collection)
    print(f"[embeddings] {patient_id} → {inserted} vetores indexados")