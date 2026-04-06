import os
import time
import requests
from dotenv import load_dotenv
from pymilvus import connections, Collection

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings")


class HealthCheckValidator:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def validate(self) -> bool:
        response = requests.get(f"{self._base_url}/health", timeout=5)
        return response.status_code == 200


class MetadataValidator:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def validate(self) -> dict:
        response = requests.get(f"{self._base_url}/metadata", timeout=5)
        response.raise_for_status()
        return response.json()


class RagResponseValidator:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def validate(self, question: str) -> tuple[str, float]:
        start = time.monotonic()
        response = requests.post(
            f"{self._base_url}/ask",
            json={"question": question},
            timeout=120,
        )
        response.raise_for_status()
        elapsed = time.monotonic() - start
        return response.json()["answer"], elapsed


class MilvusValidator:
    def __init__(self, host: str, port: str, collection_name: str):
        self._host = host
        self._port = port
        self._collection_name = collection_name

    def validate(self) -> int:
        connections.connect(alias="default", host=self._host, port=self._port)
        collection = Collection(self._collection_name)
        collection.load()
        return collection.num_entities


class ValidationReport:
    def __init__(self):
        self._results: list[tuple[str, bool, str]] = []

    def add(self, check: str, passed: bool, detail: str) -> None:
        self._results.append((check, passed, detail))

    def print(self) -> None:
        print("\n── Validação Final ──────────────────────────────")
        for check, passed, detail in self._results:
            status = "✅" if passed else "❌"
            print(f"{status} {check}: {detail}")
        total = len(self._results)
        passed = sum(1 for _, p, _ in self._results if p)
        print(f"────────────────────────────────────────────────")
        print(f"   {passed}/{total} verificações passaram\n")


report = ValidationReport()

try:
    ok = HealthCheckValidator(API_URL).validate()
    report.add("API health", ok, "status ok")
except Exception as error:
    report.add("API health", False, str(error))

try:
    metadata = MetadataValidator(API_URL).validate()
    detail = f"{metadata['total_vectors']} vetores · {metadata['patients']}"
    report.add("Metadata", True, detail)
except Exception as error:
    report.add("Metadata", False, str(error))

try:
    total = MilvusValidator(MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION).validate()
    report.add("Milvus", True, f"{total} entidades indexadas")
except Exception as error:
    report.add("Milvus", False, str(error))

try:
    answer, elapsed = RagResponseValidator(API_URL).validate(
        "Qual o valor médio de glicose nos registros?"
    )
    report.add("RAG pipeline", True, f"{elapsed:.1f}s · {len(answer)} chars")
except Exception as error:
    report.add("RAG pipeline", False, str(error))

report.print()