from pathlib import Path
import pandas as pd


class PatientIdentifier:
    def __init__(self, value: str):
        self._value = value

    def as_bronze_object_key(self) -> str:
        return f"bronze/{self._value}/data.parquet"

    def __str__(self) -> str:
        return self._value


class PatientCsvFile:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def patient_identifier(self) -> PatientIdentifier:
        return PatientIdentifier(self._file_path.parent.name)

    def read_as_dataframe(self) -> pd.DataFrame:
        return pd.read_csv(self._file_path)

    def is_valid(self) -> bool:
        return self._file_path.exists() and self._file_path.suffix == ".csv"


class PatientCsvFileCollection:
    def __init__(self, files: list[PatientCsvFile]):
        self._files = files

    def only_valid(self) -> "PatientCsvFileCollection":
        valid = [file for file in self._files if file.is_valid()]
        return PatientCsvFileCollection(valid)

    def each(self, action) -> None:
        for file in self._files:
            action(file)

    def __len__(self) -> int:
        return len(self._files)


class CsvDirectoryScanner:
    def __init__(self, root_directory: Path):
        self._root_directory = root_directory

    def scan(self) -> PatientCsvFileCollection:
        discovered = [
            PatientCsvFile(path)
            for path in self._root_directory.rglob("*.csv")
        ]
        return PatientCsvFileCollection(discovered).only_valid()