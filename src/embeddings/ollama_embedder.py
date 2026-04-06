import requests


class EmbeddingVector:
    def __init__(self, values: list[float]):
        self._values = values

    def as_list(self) -> list[float]:
        return self._values

    def dimension(self) -> int:
        return len(self._values)


class OllamaEmbedder:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model

    def embed(self, text: str) -> EmbeddingVector:
        response = requests.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._model, "prompt": text},
            timeout=120,
        )
        response.raise_for_status()
        return EmbeddingVector(response.json()["embedding"])