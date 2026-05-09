import time
import os
import psycopg
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from rag.rag_pipeline import RagPipeline
from mlops.ask_tracker import AskExperimentTracker

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    model: str | None = None  # opcional: "llama3.2" ou "mistral"


class AskResponse(BaseModel):
    answer: str
    model_used: str


# ── Persistência no PostgreSQL ────────────────────────────────────────────────

def save_log_to_postgres(question: str, answer: str, model_used: str, latency_ms: int) -> None:
    """Persiste o log da consulta no banco relacional PostgreSQL."""
    try:
        conn = psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "rag_user"),
            password=os.getenv("POSTGRES_PASSWORD", "rag_pass"),
            dbname=os.getenv("POSTGRES_DB", "rag_db"),
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ask_logs (question, answer, model_used, latency_ms)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (question, answer, model_used, latency_ms),
                )
        conn.close()
    except Exception as e:
        # Não quebra a API se o banco estiver indisponível
        print(f"[postgres] Erro ao salvar log: {e}")


# ── Handler ───────────────────────────────────────────────────────────────────

class AskHandler:
    def __init__(self, pipeline: RagPipeline, tracker: AskExperimentTracker):
        self._pipeline = pipeline
        self._tracker = tracker

    def handle(self, request: AskRequest) -> AskResponse:
        # Decide qual modelo usar: o pedido pelo usuário ou o padrão do .env
        model_used = request.model or os.getenv("LLM_MODEL", "llama3.2")

        # Troca temporária de modelo no pipeline se necessário
        original_model = self._pipeline._llm._model
        self._pipeline._llm._model = model_used

        start = time.monotonic()
        response = self._pipeline.answer(request.question)
        elapsed = time.monotonic() - start
        latency_ms = int(elapsed * 1000)

        # Restaura o modelo original
        self._pipeline._llm._model = original_model

        answer_text = response.as_text()

        # Rastreia no MLflow
        self._tracker.track(request.question, answer_text, elapsed)

        # Persiste no PostgreSQL
        save_log_to_postgres(request.question, answer_text, model_used, latency_ms)

        return AskResponse(answer=answer_text, model_used=model_used)