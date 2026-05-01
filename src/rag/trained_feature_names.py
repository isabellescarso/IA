# src/rag/trained_feature_names.py
import pandas as pd


class TrainedFeatureNames:
    def __init__(self, names: list[str]):
        self._names = frozenset(names)

    def align(self, raw_frame: pd.DataFrame) -> pd.DataFrame:
        known_columns = [col for col in raw_frame.columns if col in self._names]
        return raw_frame[known_columns]