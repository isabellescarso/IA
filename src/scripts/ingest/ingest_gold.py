import os
from io import BytesIO, StringIO
import numpy as np
import pandas as pd
from minio import Minio
from ._store import MinioStore, PatientList

HORIZON = int(os.environ.get("HORIZON_MINUTES", "30"))


class FeatureBuilder:
    def __init__(self, df: pd.DataFrame, horizon: int):
        self._df = df.sort_values("Timestamp").copy()
        self._horizon = horizon

    def build(self) -> pd.DataFrame:
        df = self._df
        df["Meal_Event"] = df["Meal Type"].notnull().astype(int)
        df["In_Meal_Window"] = df["Meal_Event"].rolling(window=120, min_periods=1).max().fillna(0)
        df["target_glucose"] = df["Libre GL"].shift(-self._horizon)

        for lag in [5, 15, 30, 60]:
            df[f"lag_GL_{lag}min"] = df["Libre GL"].shift(lag)
            df[f"lag_HR_{lag}min"] = df["HR"].shift(lag)

        df["diff_5min"] = df["Libre GL"].diff(5)
        df["diff_10min"] = df["Libre GL"].diff(10)
        df["hour_sin"] = np.sin(2 * np.pi * df["Timestamp"].dt.hour / 23.0)
        df["hour_cos"] = np.cos(2 * np.pi * df["Timestamp"].dt.hour / 23.0)

        return df.dropna(subset=["target_glucose", "lag_GL_5min", "lag_GL_60min"])


class GoldIngestion:
    def __init__(self, store: MinioStore, patients: PatientList):
        self._store = store
        self._patients = patients

    def run(self) -> None:
        client = self._store.client()
        for pid in self._patients:
            self._process(client, pid)

    def _process(self, client: Minio, pid: str) -> None:
        df = self._load_silver(client, pid)
        df_gold = FeatureBuilder(df, HORIZON).build()
        self._save_parquet(client, pid, df_gold)
        self._save_stats(client, pid, df_gold)
        print(f"gold: {pid} → {len(df_gold)} rows")

    def _load_silver(self, client: Minio, pid: str) -> pd.DataFrame:
        path = f"silver/CGMacros/{pid}/{pid}.parquet"
        resp = client.get_object(self._store.bucket, path)
        df = pd.read_parquet(BytesIO(resp.read()))
        resp.close()
        resp.release_conn()
        return df

    def _save_parquet(self, client: Minio, pid: str, df: pd.DataFrame) -> None:
        path = f"gold/CGMacros/{pid}/{pid}_ML_READY.parquet"
        buf = BytesIO()
        df.to_parquet(buf, index=False)
        buf.seek(0)
        client.put_object(self._store.bucket, path,
                          data=buf, length=buf.getbuffer().nbytes,
                          content_type="application/x-parquet")

    def _save_stats(self, client: Minio, pid: str, df: pd.DataFrame) -> None:
        path = f"gold/metadata/{pid}/{pid}_stats_summary.csv"
        csv_buf = StringIO()
        df.describe().rename_axis("statistic").to_csv(csv_buf)
        raw = BytesIO(csv_buf.getvalue().encode())
        client.put_object(self._store.bucket, path,
                          data=raw, length=raw.getbuffer().nbytes,
                          content_type="text/csv")


if __name__ == "__main__":
    GoldIngestion(MinioStore.from_env(), PatientList.from_env()).run()