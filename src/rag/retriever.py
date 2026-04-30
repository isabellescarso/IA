import pandas as pd
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher, SemanticQuery


from embeddings.text_builder import TextCollectionParser


class RetrievedContext:
    def __init__(self, texts: list[str]):
        self._texts = texts

    def as_joined_text(self) -> str:
        return "\n".join(self._texts)

    def as_feature_row(self) -> pd.DataFrame:
        return TextCollectionParser(self._texts).as_feature_dataframe()


class ContextRetriever:
    def __init__(self, embedder: OllamaEmbedder, searcher: MilvusSemanticSearcher):
        self._embedder = embedder
        self._searcher = searcher

    def retrieve(self, query_text: str, top_k: int = 3) -> RetrievedContext:
        embedding = self._embedder.embed(SemanticQuery(query_text).as_text())
        results = self._searcher.search(embedding.as_list(), top_k)
        return RetrievedContext(results.as_texts())