import pandas as pd


class NumericColumnSelector:
    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.select_dtypes(include=["number"])


class ControlledInterpolator:
    TARGET_COLUMN = "Dexcom GL"

    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        interpolated = dataframe.interpolate(method="linear", limit_direction="forward")
        return interpolated.dropna(subset=[self.TARGET_COLUMN])


class TemporalSplitMarker:
    def __init__(self, train_ratio: float = 0.8):
        self._train_ratio = train_ratio

    def apply(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        cutoff = int(len(dataframe) * self._train_ratio)
        marked = dataframe.copy()
        marked["split"] = "test"
        marked.iloc[:cutoff, marked.columns.get_loc("split")] = "train"
        return marked


class GoldTransformationPipeline:
    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        numeric = NumericColumnSelector().apply(dataframe)
        interpolated = ControlledInterpolator().apply(numeric)
        return TemporalSplitMarker().apply(interpolated)