import os
from io import BytesIO

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from minio import Minio
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from mlops.training_tracker import FeatureImportanceLogger, ModelMetrics, TrainingExperimentTracker
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


load_dotenv()

TARGET = "target_glucose"
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
        key = f"gold/CGMacros/{patient_id}/{patient_id}_ML_READY.parquet"
        response = self._client.get_object(self._bucket, key)
        raw_bytes = response.read()
        response.close()
        response.release_conn()
        return pd.read_parquet(BytesIO(raw_bytes)).sort_values("Timestamp")


class PatientDatasetCollection:
    def __init__(self, frames: list[pd.DataFrame]):
        self._frames = frames

    def combined(self) -> pd.DataFrame:
        return pd.concat(self._frames, ignore_index=True)

NON_FEATURE_COLUMNS = [TARGET, "Timestamp", "Meal Type"]

class TemporalSplit:
    def __init__(self, dataframe: pd.DataFrame):
        numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
        self._feature_columns = [col for col in numeric_columns if col != TARGET]
        cleaned = dataframe[[TARGET, "Timestamp"] + self._feature_columns].dropna().reset_index(drop=True)
        cutoff = int(len(cleaned) * 0.8)
        self._train = cleaned.iloc[:cutoff]
        self._test = cleaned.iloc[cutoff:]

    def x_train(self) -> pd.DataFrame:
        return self._train[self._feature_columns]

    def y_train(self) -> pd.Series:
        return self._train[TARGET]

    def x_test(self) -> pd.DataFrame:
        return self._test[self._feature_columns]

    def y_test(self) -> pd.Series:
        return self._test[TARGET]


class CandidateModel:
    def __init__(self, name: str, estimator):
        self._name = name
        self._estimator = estimator

    def fit(self, x_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._estimator.fit(x_train, y_train)

    def predict(self, x_test: pd.DataFrame) -> np.ndarray:
        return self._estimator.predict(x_test)

    def name(self) -> str:
        return self._name

    def estimator(self):
        return self._estimator


class CandidateModelCollection:
    def __init__(self):
        self._models = [
            CandidateModel("random_forest", RandomForestRegressor(
                n_estimators=100, max_depth=15,
                min_samples_split=5, min_samples_leaf=2,
                n_jobs=-1, random_state=42,
            )),
            CandidateModel("xgboost", XGBRegressor(
                n_estimators=100, max_depth=6,
                learning_rate=0.1, n_jobs=-1,
                random_state=42, verbosity=0,
            )),
            CandidateModel("ridge", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("ridge", Ridge(alpha=1.0)),
            ])),
        ]

    def each(self) -> list[CandidateModel]:
        return self._models


class ModelEvaluator:
    def __init__(self, y_true: pd.Series, y_pred: np.ndarray):
        self._y_true = y_true
        self._y_pred = y_pred

    def mae(self) -> float:
        return mean_absolute_error(self._y_true, self._y_pred)

    def rmse(self) -> float:
        return np.sqrt(mean_squared_error(self._y_true, self._y_pred))

    def r2(self) -> float:
        return r2_score(self._y_true, self._y_pred)


class TrainingOrchestrator:
    def __init__(self, split: TemporalSplit, tracker: TrainingExperimentTracker):
        self._split = split
        self._tracker = tracker

    def run_all(self) -> None:
        for candidate in CandidateModelCollection().each():
            self._run_candidate(candidate)

    def _run_candidate(self, candidate: CandidateModel) -> None:
        candidate.fit(self._split.x_train(), self._split.y_train())
        evaluator = ModelEvaluator(self._split.y_test(), candidate.predict(self._split.x_test()))
        self._tracker.log_run(
            params={"model": candidate.name(), "target": TARGET, "patients": PATIENTS, "split": "temporal"},
            metrics=ModelMetrics(mae=evaluator.mae(), r2=evaluator.r2(), rmse=evaluator.rmse()),
            importance=FeatureImportanceLogger.from_estimator(candidate.estimator(), self._split.x_train().columns.tolist()),
            model=candidate.estimator(),
        )
        print(f"[train] {candidate.name()} · RMSE: {evaluator.rmse():.4f} · MAE: {evaluator.mae():.4f} · R²: {evaluator.r2():.4f}")


loader = GoldDatasetLoader(client, MINIO_BUCKET)
dataset = PatientDatasetCollection([loader.load(pid) for pid in PATIENTS]).combined()
split = TemporalSplit(dataset)
tracker = TrainingExperimentTracker("http://0.0.0.0:5000", "Sprint_4_CGMacros")

TrainingOrchestrator(split, tracker).run_all()