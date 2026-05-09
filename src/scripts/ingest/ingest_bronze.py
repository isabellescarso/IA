from minio import Minio
from ._store import MinioStore, PatientList


class BronzeValidator:
    def __init__(self, store: MinioStore, patients: PatientList):
        self._store = store
        self._patients = patients

    def run(self) -> None:
        client = self._store.client()
        for pid in self._patients:
            self._validate(client, pid)

    def _validate(self, client: Minio, pid: str) -> None:
        path = f"bronze/CGMacros/{pid}/{pid}.csv"
        try:
            client.stat_object(self._store.bucket, path)
            print(f"bronze ok: {path}")
        except Exception as e:
            raise RuntimeError(f"bronze missing: {path}") from e


if __name__ == "__main__":
    BronzeValidator(MinioStore.from_env(), PatientList.from_env()).run()