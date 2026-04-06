from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility


class MilvusCollectionFactory:
    def __init__(self, collection_name: str, host: str, port: str):
        self._collection_name = collection_name
        self._host = host
        self._port = port

    def connect(self) -> None:
        connections.connect(alias="default", host=self._host, port=self._port)

    def get_or_create(self, dimension: int) -> Collection:
        if utility.has_collection(self._collection_name):
            return Collection(self._collection_name)
        return self._create(dimension)

    def _create(self, dimension: int) -> Collection:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]
        schema = CollectionSchema(fields, description="CGMacros gold embeddings")
        collection = Collection(name=self._collection_name, schema=schema)
        collection.create_index(
            field_name="embedding",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}},
        )
        collection.load()
        return collection


class MilvusRecordBatch:
    def __init__(self):
        self._ids: list[int] = []
        self._texts: list[str] = []
        self._embeddings: list[list[float]] = []

    def add(self, record_id: int, text: str, embedding: list[float]) -> None:
        self._ids.append(record_id)
        self._texts.append(text)
        self._embeddings.append(embedding)

    def flush_into(self, collection: Collection) -> int:
        collection.insert([self._ids, self._texts, self._embeddings])
        collection.flush()
        collection.load()
        return len(self._ids)