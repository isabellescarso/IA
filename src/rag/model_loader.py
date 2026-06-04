# src/rag/model_loader.py
import mlflow.sklearn
from rag.trained_feature_names import TrainedFeatureNames
from rag.glucose_predictor import RidgeGlucosePredictor


class RidgeGlucosePredictorLoader:
    def __init__(self, model_name: str):
        self._model_name = model_name

    def load(self) -> RidgeGlucosePredictor:
        model = mlflow.sklearn.load_model(f"models:/{self._model_name}/latest")
        print("[loader] type:", type(model))
        print("[loader] feature_names_in_:", getattr(model, "feature_names_in_", "NOT FOUND"))
        print("[loader] steps:", getattr(model, "steps", "NOT A PIPELINE"))
        names = model.feature_names_in_.tolist()
        print("[loader] names[:5]:", names[:5])
        feature_names = TrainedFeatureNames(names)
        return RidgeGlucosePredictor(model, feature_names)