from pymilvus import Collection


class SemanticQuery:
    def __init__(self, text: str):
        self._text = text

    def as_text(self) -> str:
        return self._text


class MilvusSearchParameters:
    def __init__(self, metric_type: str = "L2", nprobe: int = 10):
        self._metric_type = metric_type
        self._nprobe = nprobe

    def as_dict(self) -> dict:
        return {"metric_type": self._metric_type, "params": {"nprobe": self._nprobe}}


class HitRecord:
    def __init__(self, raw_hit):
        self._raw_hit = raw_hit

    def as_metadata_dict(self) -> dict:
        return {
            "chunk_id": str(self._raw_hit.id),
            "distance": float(self._raw_hit.distance),
            "text": str(self._raw_hit.entity.get("text", "")),
        }


class HitRecordCollection:
    def __init__(self, raw_results):
        self._records = [HitRecord(hit) for hit in raw_results[0]]

    def as_texts(self) -> list[str]:
        return [record.as_metadata_dict()["text"] for record in self._records]

    def as_metadata_dicts(self) -> list[dict]:
        return [record.as_metadata_dict() for record in self._records]


class MilvusSemanticSearcher:
    def __init__(self, collection: Collection, parameters: MilvusSearchParameters = MilvusSearchParameters()):
        self._collection = collection
        self._parameters = parameters

    def search_with_metadata(self, embedding: list[float], top_k: int = 3) -> list[dict]:
        results = self._collection.search(
            data=[embedding],
            anns_field="embedding",
            param=self._parameters.as_dict(),
            limit=top_k,
            output_fields=["text"],
        )
        return HitRecordCollection(results).as_metadata_dicts()