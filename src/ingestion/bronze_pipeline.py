from io import BytesIO
from minio import Minio

from .loaders import CsvDirectoryScanner, PatientCsvFile
from .converters import ParquetBuffer

class MinioParquetUploader:
    def __init__(self, minio_client: Minio, bucket_name: str):
        self._client = minio_client
        self._bucket_name = bucket_name

    def upload(self, object_key: str, parquet_buffer: ParquetBuffer) -> None:
        raw_bytes = parquet_buffer.as_bytes()
        self._client.put_object(
            bucket_name=self._bucket_name,
            object_name=object_key,
            data=BytesIO(raw_bytes),
            length=parquet_buffer.size_in_bytes(),
            content_type="application/octet-stream",
        )


class BronzeIngestionPipeline:
    def __init__(self, scanner: CsvDirectoryScanner, uploader: MinioParquetUploader):
        self._scanner = scanner
        self._uploader = uploader

    def run(self) -> None:
        self._scanner.scan().each(self._ingest_file)

    def _ingest_file(self, patient_file: PatientCsvFile) -> None:
        identifier = patient_file.patient_identifier()
        object_key = identifier.as_bronze_object_key()
        dataframe = patient_file.read_as_dataframe()
        buffer = ParquetBuffer(dataframe)
        self._uploader.upload(object_key, buffer)
        print(f"[bronze] {identifier} → {object_key} ({buffer.size_in_bytes()} bytes)")
