import os
from io import BytesIO

import pandas as pd
import mlflow
from dotenv import load_dotenv
from minio import Minio
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from mlops.training_tracker import ModelMetrics, FeatureImportanceLogger, TrainingExperimentTracker

load_dotenv()

TARGET = "Dexcom GL"
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")
PATIENTS = ["CGMacros-012", "CGMacros-039"]

client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False,
)


class GoldDatasetLoader:
    def __init__(self, minio_client: Minio, bucket: str):
        self._client = minio_client
        self._bucket = bucket

    def load(self, patient_id: str) -> pd.DataFrame:
        key = f"gold/{patient_id}/data.parquet"
        response = self._client.get_object(self._bucket, key)
        raw_bytes = response.read()
        response.close()
        response.release_conn()
        return pd.read_parquet(BytesIO(raw_bytes))


class TemporalSplit:
    def __init__(self, dataframe: pd.DataFrame):
        self._train = dataframe[dataframe["split"] == "train"].drop(columns=["split"])
        self._test = dataframe[dataframe["split"] == "test"].drop(columns=["split"])

    def x_train(self) -> pd.DataFrame:
        return self._train.drop(columns=[TARGET])

    def y_train(self) -> pd.Series:
        return self._train[TARGET]

    def x_test(self) -> pd.DataFrame:
        return self._test.drop(columns=[TARGET])

    def y_test(self) -> pd.Series:
        return self._test[TARGET]


class PatientDatasetCollection:
    def __init__(self, frames: list[pd.DataFrame]):
        self._frames = frames

    def combined(self) -> pd.DataFrame:
        return pd.concat(self._frames, ignore_index=True)


loader = GoldDatasetLoader(client, MINIO_BUCKET)
frames = PatientDatasetCollection([loader.load(pid) for pid in PATIENTS])
dataset = frames.combined()

split = TemporalSplit(dataset)

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    n_jobs=-1,
    random_state=42,
)
model.fit(split.x_train(), split.y_train())
predictions = model.predict(split.x_test())

metrics = ModelMetrics(
    mae=mean_absolute_error(split.y_test(), predictions),
    r2=r2_score(split.y_test(), predictions),
)
importance = FeatureImportanceLogger(
    column_names=split.x_train().columns.tolist(),
    importances=model.feature_importances_.tolist(),
)
tracker = TrainingExperimentTracker("sqlite:///mlflow.db", "Sprint_4_CGMacros")
tracker.log_run(
    params={
        "target": TARGET,
        "patients": PATIENTS,
        "n_estimators": 100,
        "max_depth": 15,
        "split": "temporal",
    },
    metrics=metrics,
    importance=importance,
    model=model,
)

print(f"[train] MAE: {metrics._mae:.4f} · R2: {metrics._r2:.4f}")