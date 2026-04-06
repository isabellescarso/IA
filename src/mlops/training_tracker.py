import mlflow
import mlflow.sklearn


class ModelMetrics:
    def __init__(self, mae: float, r2: float):
        self._mae = mae
        self._r2 = r2

    def log(self) -> None:
        mlflow.log_metric("MAE", self._mae)
        mlflow.log_metric("R2", self._r2)


class FeatureImportanceLogger:
    def __init__(self, column_names: list[str], importances: list[float]):
        self._column_names = column_names
        self._importances = importances

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
        with mlflow.start_run(run_name="random_forest_temporal_split"):
            mlflow.log_params(params)
            metrics.log()
            importance.log()
            mlflow.sklearn.log_model(model, "modelo_glicose")