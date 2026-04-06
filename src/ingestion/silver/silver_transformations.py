import numpy as np
import pandas as pd


class TemporalFeatureSet:
    TIMESTAMP_COLUMN = "Timestamp"

    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe

    def apply(self) -> pd.DataFrame:
        parsed = pd.to_datetime(self._dataframe[self.TIMESTAMP_COLUMN], errors="coerce")
        enriched = self._dataframe.copy()
        enriched["hora_sin"] = np.sin(2 * np.pi * parsed.dt.hour / 24)
        enriched["hora_cos"] = np.cos(2 * np.pi * parsed.dt.hour / 24)
        enriched["dia_semana"] = parsed.dt.dayofweek
        enriched["mes"] = parsed.dt.month
        return enriched.drop(columns=[self.TIMESTAMP_COLUMN])


class HighMissingColumnFilter:
    def __init__(self, threshold: float):
        self._threshold = threshold

    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        missing_ratio = dataframe.isnull().mean()
        columns_to_keep = missing_ratio[missing_ratio <= self._threshold].index.tolist()
        return dataframe[columns_to_keep]


class TargetNullDropper:
    TARGET_COLUMN = "Dexcom GL"

    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.dropna(subset=[self.TARGET_COLUMN])


class NonNumericColumnDropper:
    COLUMNS_TO_DROP = ["Image path", "Meal", "Meal_Type", "Diet", "arquivo_origem"]

    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.drop(columns=self.COLUMNS_TO_DROP, errors="ignore")


class SilverTransformationPipeline:
    def __init__(self, missing_threshold: float = 0.3):
        self._missing_filter = HighMissingColumnFilter(missing_threshold)
        self._null_dropper = TargetNullDropper()

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        without_non_numeric = NonNumericColumnDropper().apply(dataframe)
        with_temporal = TemporalFeatureSet(without_non_numeric).apply()
        without_high_missing = self._missing_filter.apply(with_temporal)
        return self._null_dropper.apply(without_high_missing)