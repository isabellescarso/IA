import os
from dataclasses import dataclass
from minio import Minio


@dataclass
class MinioStore:
    endpoint: str
    bucket: str

    def client(self) -> Minio:
        return Minio(
            self.endpoint,
            access_key=os.environ["MINIO_USER"],
            secret_key=os.environ["MINIO_PASSWORD"],
            secure=False,
        )

    @classmethod
    def from_env(cls) -> "MinioStore":
        return cls(
            endpoint=os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
            bucket=os.environ.get("MINIO_BUCKET", "cgmacros"),
        )


class PatientList:
    def __init__(self, ids: list[str]):
        self._ids = ids

    def __iter__(self):
        return iter(self._ids)

    @classmethod
    def from_env(cls) -> "PatientList":
        raw = os.environ.get("PATIENTS", "CGMacros-012,CGMacros-039")
        return cls(raw.split(","))