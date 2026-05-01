import mlflow
import mlflow.sklearn
import numpy as np
"""
    Experiment: definido em train_model.py (não enviado, mas o tracker mostra)
    Run name: random_forest_temporal_split
    Params: dict livre (passado pelo script de treino)
    Metrics: MAE, R2
    Artifact: feature_importance.json + modelo sklearn em modelo_glicose
"""

class ModelMetrics:
    def __init__(self, mae: float, r2: float, rmse: float):
        self._mae = mae
        self._r2 = r2
        self._rmse = rmse

    def log(self) -> None:
        mlflow.log_metric("MAE", self._mae)
        mlflow.log_metric("R2", self._r2)
        mlflow.log_metric("RMSE", self._rmse)


class FeatureImportanceLogger:
    def __init__(self, column_names: list[str], importances: list[float]):
        self._column_names = column_names
        self._importances = importances

    @classmethod
    def from_estimator(cls, estimator, column_names: list[str]) -> "FeatureImportanceLogger":
        if hasattr(estimator, "feature_importances_"):
            return cls(column_names, estimator.feature_importances_.tolist())
        if hasattr(estimator, "coef_"):
            return cls(column_names, np.abs(estimator.coef_).tolist())
        return cls(column_names, [0.0] * len(column_names))

    def log(self) -> None:
        mlflow.log_dict(
            dict(zip(self._column_names, self._importances)),
            "feature_importance.json",
        )


class TrainingExperimentTracker:
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def log_run(self, params: dict, metrics: ModelMetrics, importance: FeatureImportanceLogger, model) -> None:
        with mlflow.start_run(run_name=params.get("model", "unnamed")):
            mlflow.log_params(params)
            metrics.log()
            importance.log()
            mlflow.sklearn.log_model(
                model,
                artifact_path="modelo_glicose",
                registered_model_name="modelo_glicose",
            )