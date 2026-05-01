# src/rag/glucose_predictor.py
import pandas as pd
from rag.trained_feature_names import TrainedFeatureNames


class GlucosePrediction:
    def __init__(self, value: float):
        self._value = value

    def as_text(self) -> str:
        return f"Predição do modelo (Ridge): glicose estimada em {self._value:.1f} mg/dL nos próximos 30 minutos."

    def as_float(self) -> float:
        return self._value


class RidgeGlucosePredictor:
    def __init__(self, model, feature_names: TrainedFeatureNames):
        self._model = model
        self._feature_names = feature_names



    def predict(self, raw_frame: pd.DataFrame) -> GlucosePrediction:
        aligned = self._feature_names.align(raw_frame)
        return GlucosePrediction(self._model.predict(aligned)[0])