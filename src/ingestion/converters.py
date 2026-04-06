import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from io import BytesIO


class ParquetBuffer:
    def __init__(self, dataframe: pd.DataFrame):
        self._buffer = self._convert(dataframe)

    def _convert(self, dataframe: pd.DataFrame) -> BytesIO:
        buffer = BytesIO()
        table = pa.Table.from_pandas(dataframe, preserve_index=False)
        pq.write_table(table, buffer)
        buffer.seek(0)
        return buffer

    def as_bytes(self) -> bytes:
        self._buffer.seek(0)
        return self._buffer.read()

    def size_in_bytes(self) -> int:
        return self._buffer.getbuffer().nbytes