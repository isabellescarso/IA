from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio
from .silver_transformations import SilverTransformationPipeline


class BronzeParquetReader:
    def __init__(self, client: Minio, bucket: str):
        self._client = client
        self._bucket = bucket

    def read(self, patient_id: str) -> pd.DataFrame:
        key = f"bronze/{patient_id}/data.parquet"
        response = self._client.get_object(self._bucket, key)
        raw_bytes = response.read()
        response.close()
        response.release_conn()
        return pd.read_parquet(BytesIO(raw_bytes))


class SilverParquetWriter:
    def __init__(self, client: Minio, bucket: str):
        self._client = client
        self._bucket = bucket

    def write(self, patient_id: str, dataframe: pd.DataFrame) -> str:
        key = f"silver/{patient_id}/data.parquet"
        buffer = BytesIO()
        pq.write_table(pa.Table.from_pandas(df=dataframe, preserve_index=False), buffer)
        buffer.seek(0)
        self._client.put_object(
            bucket_name=self._bucket,
            object_name=key,
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type="application/octet-stream",
        )
        return key


class SilverIngestionPipeline:
    def __init__(self, reader: BronzeParquetReader, writer: SilverParquetWriter):
        self._reader = reader
        self._writer = writer

    def run(self, patient_id: str) -> dict:
        raw = self._reader.read(patient_id)
        transformed = SilverTransformationPipeline().transform(raw)
        key = self._writer.write(patient_id, transformed)
        return {"patient_id": patient_id, "key": key, "rows": len(transformed), "columns": len(transformed.columns)}