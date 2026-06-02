import time


class AskExecutionTimer:
    def __init__(self):
        self._start_time = time.monotonic()
        self._retrieval_completed_at: float = 0.0

    def mark_retrieval_complete(self) -> None:
        self._retrieval_completed_at = time.monotonic()

    def retrieval_milliseconds(self) -> int:
        return int((self._retrieval_completed_at - self._start_time) * 1000)

    def generation_milliseconds(self) -> int:
        return int((time.monotonic() - self._retrieval_completed_at) * 1000)

    def total_milliseconds(self) -> int:
        return int((time.monotonic() - self._start_time) * 1000)
        
    def get_total_seconds(self) -> float:
        """Retorna o tempo total em segundos"""
        return time.monotonic() - self._start_time
