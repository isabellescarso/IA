from io import BytesIO
import pandas as pd
from minio import Minio
from ._store import MinioStore, PatientList

DTYPES = {
    "Libre GL": "float64", "Dexcom GL": "float64", "HR": "float64",
    "Calories (Activity)": "float64", "METs": "float64",
    "Meal Type": "string", "Calories": "float64",
    "Carbs": "float64", "Protein": "float64", "Fat": "float64",
    "Fiber": "float64", "Amount Consumed": "float64", "Image path": "string",
}


class SilverIngestion:
    def __init__(self, store: MinioStore, patients: PatientList):
        self._store = store
        self._patients = patients

    def run(self) -> None:
        client = self._store.client()
        for pid in self._patients:
            self._convert(client, pid)

    def _convert(self, client: Minio, pid: str) -> None:
        source = f"bronze/CGMacros/{pid}/{pid}.csv"
        target = f"silver/CGMacros/{pid}/{pid}.parquet"

        resp = client.get_object(self._store.bucket, source)
        df = pd.read_csv(BytesIO(resp.read()), dtype=DTYPES, parse_dates=["Timestamp"])
        resp.close()
        resp.release_conn()

        buf = BytesIO()
        df.to_parquet(buf, engine="pyarrow", index=False)
        buf.seek(0)

        client.put_object(
            self._store.bucket, target,
            data=buf, length=buf.getbuffer().nbytes,
            content_type="application/x-parquet",
        )
        print(f"silver: {pid} → {target}")


if __name__ == "__main__":
    SilverIngestion(MinioStore.from_env(), PatientList.from_env()).run()