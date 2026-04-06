from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher, SemanticQuery


class RetrievedContext:
    def __init__(self, texts: list[str]):
        self._texts = texts

    def as_joined_text(self) -> str:
        return "\n".join(self._texts)


class ContextRetriever:
    def __init__(self, embedder: OllamaEmbedder, searcher: MilvusSemanticSearcher):
        self._embedder = embedder
        self._searcher = searcher

    def retrieve(self, query_text: str, top_k: int = 3) -> RetrievedContext:
        query = SemanticQuery(query_text)
        embedding = self._embedder.embed(query.as_text())
        results = self._searcher.search(embedding.as_list(), top_k)
        return RetrievedContext(results.as_texts())