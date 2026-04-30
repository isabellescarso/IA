import mlflow.sklearn
import mlflow
import pandas as pd


class RidgePrediction:
    def __init__(self, value: float):
        self._value = value

    def as_text(self) -> str:
        return f"Predição do modelo (Ridge): glicose estimada em {self._value:.1f} mg/dL nos próximos 30 minutos."


class RidgeGlucosePredictor:
    def __init__(self, model_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(model_uri)
        self._model = self._load_best_ridge(experiment_name)

    def _load_best_ridge(self, experiment_name: str):
        runs = mlflow.search_runs(
            experiment_names=[experiment_name],
            filter_string="params.model = 'ridge'",
            order_by=["metrics.RMSE ASC"],
            max_results=1,
        )
        run_id = runs.iloc[0]["run_id"]
        return mlflow.sklearn.load_model(f"runs:/{run_id}/modelo_glicose")

    def predict(self, features: pd.DataFrame) -> RidgePrediction:
        value = self._model.predict(features)[0]
        return RidgePrediction(float(value))