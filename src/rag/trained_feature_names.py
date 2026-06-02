# src/rag/trained_feature_names.py
import pandas as pd


class TrainedFeatureNames:
    def __init__(self, names: list[str]):
        self._names = frozenset(names)

    def align(self, raw_frame: pd.DataFrame) -> pd.DataFrame:
        known_columns = [col for col in raw_frame.columns if col in self._names]
        return raw_frame[known_columns]
        
    def get_relevant_features(self, raw_frame: pd.DataFrame) -> list[str]:
        """Retorna apenas os nomes das features relevantes presentes no DataFrame"""
        return [col for col in raw_frame.columns if col in self._names]
        
    def get_feature_importance_scores(self, feature_importances: list[float]) -> dict[str, float]:
        """Retorna um dicionário com nomes das features e suas respectivas importâncias"""
        relevant_features = self.get_relevant_features(pd.DataFrame(columns=list(self._names)))
        return dict(zip(relevant_features, feature_importances))
