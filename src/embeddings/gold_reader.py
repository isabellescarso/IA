from io import BytesIO
import pandas as pd
from minio import Minio


class PatientIdentifier:
    def __init__(self, patient_id: str):
        self._patient_id = patient_id

    def to_gold_parquet_key(self) -> str:
        return f"gold/CGMacros/{self._patient_id}/{self._patient_id}_ML_READY.parquet"


class GoldPatientDataFrame:
    def __init__(self, raw_bytes: bytes):
        self._dataframe = pd.read_parquet(BytesIO(raw_bytes)).sort_values("Timestamp")

    def training_rows(self) -> pd.DataFrame:
        cutoff = int(len(self._dataframe) * 0.8)
        return self._dataframe.iloc[:cutoff]

    def row_count(self) -> int:
        return len(self._dataframe)


class GoldParquetReader:
    def __init__(self, client: Minio, bucket: str):
        self._client = client
        self._bucket = bucket

    def read(self, patient_identifier: PatientIdentifier) -> GoldPatientDataFrame:
        response = self._client.get_object(self._bucket, patient_identifier.to_gold_parquet_key())
        raw_bytes = response.read()
        response.close()
        response.release_conn()
        return GoldPatientDataFrame(raw_bytes)