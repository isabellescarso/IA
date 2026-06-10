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
    def __init__(self, collections: list, embedder, top_k_per_collection: int = 4):
        self._collections = collections
        self._embedder = embedder
        self._top_k_per_collection = top_k_per_collection

    def retrieve(self, question: str, top_k: int) -> RetrievedContext:
        query_vector = self._embedder.embed(question).as_list()
        all_records = []

        for collection in self._collections:
            print(f"[retriever] buscando em: {collection.name}, entidades: {collection.num_entities}")
            results = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["text"],
            )
            for hits in results:
                for hit in hits:
                    all_records.append(
                        SourceRecord({
                            "chunk_id": hit.id,
                            "distance": hit.score,
                            "text": hit.entity.get("text", ""),
                        })
                    )

        all_records.sort(key=lambda r: r.score, reverse=False)
        return RetrievedContext(SourceRecordCollection(all_records[:top_k]))