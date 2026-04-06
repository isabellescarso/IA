import os
from minio import Minio
from dotenv import load_dotenv
import mlflow
from ingestion.silver_pipeline import BronzeParquetReader, SilverParquetWriter, SilverIngestionPipeline

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")
PATIENTS = ["CGMacros-012", "CGMacros-039"]

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Silver_Ingestion")

client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False,
)

reader = BronzeParquetReader(client, MINIO_BUCKET)
writer = SilverParquetWriter(client, MINIO_BUCKET)
pipeline = SilverIngestionPipeline(reader, writer)

for patient_id in PATIENTS:
    with mlflow.start_run(run_name=f"silver_{patient_id}"):
        result = pipeline.run(patient_id)
        mlflow.log_params(result)
        print(f"[silver] {result['patient_id']} → {result['key']} ({result['rows']} linhas · {result['columns']} colunas)")