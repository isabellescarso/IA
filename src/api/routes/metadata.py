from fastapi import APIRouter
from pydantic import BaseModel
from pymilvus import Collection

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
)


class MetadataResponse(BaseModel):
    total_vectors: int
    patients: list[str]
    embed_model: str
    llm_model: str


class MilvusCollectionStats:
    def __init__(self, collection: Collection):
        self._collection = collection

    def total_entities(self) -> int:
        return self._collection.num_entities


class MetadataHandler:
    def __init__(self, collection: Collection, patients: list[str], embed_model: str, llm_model: str):
        self._stats = MilvusCollectionStats(collection)
        self._patients = patients
        self._embed_model = embed_model
        self._llm_model = llm_model

    def handle(self) -> MetadataResponse:
        return MetadataResponse(
            total_vectors=self._stats.total_entities(),
            patients=self._patients,
            embed_model=self._embed_model,
            llm_model=self._llm_model,
        )