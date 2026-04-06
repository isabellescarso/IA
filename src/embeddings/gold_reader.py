from io import BytesIO
import pandas as pd
from minio import Minio


class GoldPatientDataFrame:
    def __init__(self, raw_bytes: bytes):
        self._dataframe = pd.read_parquet(BytesIO(raw_bytes))

    def training_rows(self) -> pd.DataFrame:
        return self._dataframe[self._dataframe["split"] == "train"]

    def row_count(self) -> int:
        return len(self._dataframe)


class GoldParquetReader:
    def __init__(self, client: Minio, bucket: str):
        self._client = client
        self._bucket = bucket

    def read(self, patient_id: str) -> GoldPatientDataFrame:
        key = f"gold/{patient_id}/data.parquet"
        response = self._client.get_object(self._bucket, key)
        raw_bytes = response.read()
        response.close()
        response.release_conn()
        return GoldPatientDataFrame(raw_bytes)