from pymilvus import Collection


class SemanticQuery:
    def __init__(self, text: str):
        self._text = text

    def as_text(self) -> str:
        return self._text


class SearchResultCollection:
    def __init__(self, raw_results):
        self._hits = raw_results[0]

    def print_each(self) -> None:
        for hit in self._hits:
            print(f"ID: {hit.id}")
            print(f"Distância: {hit.distance:.4f}")
            print(f"Texto: {hit.entity.get('text')}")
            print("-" * 80)

    def as_texts(self) -> list[str]:
        return [hit.entity.get("text") for hit in self._hits]


class MilvusSemanticSearcher:
    def __init__(self, collection: Collection):
        self._collection = collection

    def search(self, embedding: list[float], top_k: int = 3) -> SearchResultCollection:
        results = self._collection.search(
            data=[embedding],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["text"],
        )
        return SearchResultCollection(results)