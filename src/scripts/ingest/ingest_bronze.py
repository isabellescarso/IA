import os
from pathlib import Path
from minio import Minio
from dotenv import load_dotenv

from src.ingestion import (CsvDirectoryScanner, BronzeIngestionPipeline, MinioParquetUploader)

load_dotenv()

BRONZE_ROOT = Path("src/data/bronze/CGMacros")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")

client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False,
)

scanner = CsvDirectoryScanner(BRONZE_ROOT)
uploader = MinioParquetUploader(client, MINIO_BUCKET)
pipeline = BronzeIngestionPipeline(scanner, uploader)
pipeline.run()