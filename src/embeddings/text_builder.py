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