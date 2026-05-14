import pandas as pd
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher, SemanticQuery
from embeddings.text_builder import TextCollectionParser
from api.schemas.ask_schemas import RetrievalSource


class SourceRecord:
    def __init__(self, raw_hit: dict):
        self.chunk_id = str(raw_hit["chunk_id"])
        self.score = float(raw_hit["distance"])
        self.text = str(raw_hit.get("text", ""))

    def to_schema(self) -> RetrievalSource:
        return RetrievalSource(
            chunk_identifier=self.chunk_id,
            similarity_score=self.score,
        )


class SourceRecordCollection:
    def __init__(self, records: list[SourceRecord]):
        self._records = records

    def __iter__(self):
        return iter(self._records)

    def as_texts(self) -> list[str]:
        return [r.text for r in self._records]


class RetrievedContext:
    def __init__(self, source_collection: SourceRecordCollection):
        self._source_collection = source_collection

    def as_joined_text(self) -> str:
        return "\n".join(self._source_collection.as_texts())

    def as_feature_row(self) -> pd.DataFrame:
        return TextCollectionParser(self._source_collection.as_texts()).as_feature_dataframe()

    def source_records(self) -> SourceRecordCollection:
        return self._source_collection


class ContextRetriever:
    def __init__(self, embedder: OllamaEmbedder, searcher: MilvusSemanticSearcher):
        self._embedder = embedder
        self._searcher = searcher

    def retrieve(self, query_text: str, top_k: int = 3) -> RetrievedContext:
        embedding = self._embedder.embed(SemanticQuery(query_text).as_text())
        raw_hits = self._searcher.search_with_metadata(embedding.as_list(), top_k)
        records = [SourceRecord(hit) for hit in raw_hits]
        return RetrievedContext(SourceRecordCollection(records))