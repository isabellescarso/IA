import os
from minio import Minio
from dotenv import load_dotenv
import mlflow
from src.ingestion.eda_report import ParquetDataFrame, PatientEdaRunner

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")
PATIENTS = ["CGMacros-012", "CGMacros-039"]

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("EDA_Bronze")

client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False,
)

for patient_id in PATIENTS:
    object_key = f"bronze/{patient_id}/data.parquet"
    response = client.get_object(MINIO_BUCKET, object_key)
    raw_bytes = response.read()
    response.close()
    response.release_conn()

    dataframe = ParquetDataFrame(raw_bytes)
    PatientEdaRunner(patient_id, dataframe).run()
    print(f"[eda] {patient_id} → {dataframe.row_count()} linhas · {len(dataframe.column_names())} colunas")