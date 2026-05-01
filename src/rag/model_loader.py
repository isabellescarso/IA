# src/rag/model_loader.py
import mlflow.sklearn
from rag.trained_feature_names import TrainedFeatureNames
from rag.glucose_predictor import RidgeGlucosePredictor


class RidgeGlucosePredictorLoader:
    def __init__(self, model_name: str):
        self._model_name = model_name

    def load(self) -> RidgeGlucosePredictor:
        model = mlflow.sklearn.load_model(f"models:/{self._model_name}/latest")
        feature_names = TrainedFeatureNames(model.feature_names_in_.tolist())
        return RidgeGlucosePredictor(model, feature_names)