import pandas as pd


class RowTextRepresentation:
    def __init__(self, row: pd.Series):
        self._row = row

    def build(self) -> str:
        return " | ".join(f"{col}: {self._row[col]}" for col in self._row.index)


class DataFrameTextCollection:
    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe

    def as_texts(self) -> list[str]:
        return [RowTextRepresentation(row).build() for _, row in self._dataframe.iterrows()]

class ParsedFeatureRow:
    def __init__(self, text: str):
        self._pairs = dict(pair.split(": ", 1) for pair in text.split(" | "))

    def as_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self._pairs]).apply(pd.to_numeric, errors="coerce")


class TextCollectionParser:
    def __init__(self, texts: list[str]):
        self._texts = texts

    def as_feature_dataframe(self) -> pd.DataFrame:
        frames = [ParsedFeatureRow(text).as_dataframe() for text in self._texts]
        return pd.concat(frames, ignore_index=True).mean().to_frame().T