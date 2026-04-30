from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import mlflow

"""
Params: patient_id, row_count, column_count, columns_above_30pct_missing
Metrics: glucose_mean, glucose_std, glucose_min, glucose_max, glucose_missing
Artifacts: gráfico de missing ratio + histograma de distribuição de glicose (.png)

Quantos dados tem? — registra quantas linhas e colunas existem
O que está faltando? — calcula a porcentagem de valores em branco por coluna e gera um gráfico de barras mostrando isso. Também lista quais colunas têm mais de 30% de buracos — essas são problemáticas
Como está a glicose? — pega a coluna Dexcom GL (a medição de glicose) e calcula média, desvio padrão, mínimo, máximo e quantos valores faltam. Gera também um histograma mostrando a distribuição dos valores

"""
class ParquetDataFrame:
    def __init__(self, raw_bytes: bytes):
        self._dataframe = pd.read_parquet(BytesIO(raw_bytes))

    def describe(self) -> pd.DataFrame:
        return self._dataframe.describe()

    def missing_ratio(self) -> pd.Series:
        return self._dataframe.isnull().mean().sort_values(ascending=False)

    def column_names(self) -> list[str]:
        return self._dataframe.columns.tolist()

    def column(self, name: str) -> pd.Series:
        return self._dataframe[name]

    def row_count(self) -> int:
        return len(self._dataframe)


class MissingRatioReport:
    def __init__(self, missing_ratio: pd.Series):
        self._missing_ratio = missing_ratio

    def columns_above_threshold(self, threshold: float) -> list[str]:
        return self._missing_ratio[self._missing_ratio > threshold].index.tolist()

    def as_figure(self) -> plt.Figure:
        figure, axis = plt.subplots(figsize=(10, 4))
        self._missing_ratio.plot(kind="bar", ax=axis)
        axis.set_title("Missing ratio por coluna")
        axis.set_ylabel("Proporção ausente")
        figure.tight_layout()
        return figure


class GlucoseDistributionReport:
    GLUCOSE_COLUMN = "Dexcom GL"

    def __init__(self, glucose_series: pd.Series):
        self._series = glucose_series

    def as_figure(self) -> plt.Figure:
        figure, axis = plt.subplots(figsize=(8, 4))
        self._series.hist(bins=50, ax=axis)
        axis.set_title("Distribuição de glicose (Dexcom GL)")
        axis.set_xlabel("mg/dL")
        axis.set_ylabel("Frequência")
        figure.tight_layout()
        return figure

    def summary(self) -> dict:
        return {
            "mean": self._series.mean(),
            "std": self._series.std(),
            "min": self._series.min(),
            "max": self._series.max(),
            "missing": self._series.isnull().sum(),
        }


class PatientEdaRunner:
    def __init__(self, patient_id: str, dataframe: ParquetDataFrame):
        self._patient_id = patient_id
        self._dataframe = dataframe

    def run(self) -> None:
        with mlflow.start_run(run_name=f"eda_{self._patient_id}"):
            self._log_shape()
            self._log_missing()
            self._log_glucose()

    def _log_shape(self) -> None:
        mlflow.log_param("patient_id", self._patient_id)
        mlflow.log_param("row_count", self._dataframe.row_count())
        mlflow.log_param("column_count", len(self._dataframe.column_names()))

    def _log_missing(self) -> None:
        missing_ratio = self._dataframe.missing_ratio()
        report = MissingRatioReport(missing_ratio)
        critical_columns = report.columns_above_threshold(threshold=0.3)
        mlflow.log_param("columns_above_30pct_missing", critical_columns)
        figure = report.as_figure()
        mlflow.log_figure(figure, f"missing_ratio_{self._patient_id}.png")
        plt.close(figure)

    def _log_glucose(self) -> None:
        glucose_column = self._dataframe.column("Dexcom GL")
        report = GlucoseDistributionReport(glucose_column)
        for metric_name, value in report.summary().items():
            mlflow.log_metric(f"glucose_{metric_name}", value)
        figure = report.as_figure()
        mlflow.log_figure(figure, f"glucose_dist_{self._patient_id}.png")
        plt.close(figure)