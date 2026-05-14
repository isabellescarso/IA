# import time
# import os
# import psycopg
# from fastapi import APIRouter, Depends
# from pydantic import BaseModel
# from rag.rag_pipeline import RagPipeline
# from mlops.ask_tracker import AskExperimentTracker
#
# router = APIRouter()
#
# # ── Schemas ───────────────────────────────────────────────────────────────────
#
# class AskRequest(BaseModel):
#     question: str
#     model: str | None = None  # opcional: "llama3.2" ou "mistral"
#
#
# class AskResponse(BaseModel):
#     answer: str
#     model_used: str
#
#
# # ── Persistência no PostgreSQL ────────────────────────────────────────────────
#
# def save_log_to_postgres(question: str, answer: str, model_used: str, latency_ms: int) -> None:
#     try:
#         conn = psycopg.connect(
#             host=os.getenv("POSTGRES_HOST", "localhost"),
#             port=os.getenv("POSTGRES_PORT", "5432"),
#             user=os.getenv("POSTGRES_USER", "rag_user"),
#             password=os.getenv("POSTGRES_PASSWORD", "rag_pass"),
#             dbname=os.getenv("POSTGRES_DB", "rag_db"),
#         )
#         with conn:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     "SELECT id FROM llm_models WHERE name = %s",
#                     (model_used,),
#                 )
#                 row = cur.fetchone()
#                 model_id = row[0] if row else None
#                 cur.execute(
#                     """
#                     INSERT INTO ask_logs (question, answer, model_id, latency_ms)
#                     VALUES (%s, %s, %s, %s)
#                     """,
#                     (question, answer, model_id, latency_ms),
#                 )
#         conn.close()
#     except Exception as e:
#         print(f"[postgres] Erro ao salvar log: {e}")
#
# # ── Handler ───────────────────────────────────────────────────────────────────
#
# class AskHandler:
#     def __init__(self, pipeline: RagPipeline, tracker: AskExperimentTracker):
#         self._pipeline = pipeline
#         self._tracker = tracker
#
#     def handle(self, request: AskRequest) -> AskResponse:
#         # Decide qual modelo usar: o pedido pelo usuário ou o padrão do .env
#         model_used = request.model or os.getenv("LLM_MODEL", "llama3.2")
#         print(f"[AskHandler] model={model_used}")
#         # Troca temporária de modelo no pipeline se necessário
#         original_model = self._pipeline._llm._model
#         self._pipeline._llm._model = model_used
#
#         start = time.monotonic()
#         response = self._pipeline.answer(request.question)
#         elapsed = time.monotonic() - start
#         latency_ms = int(elapsed * 1000)
#
#         # Restaura o modelo original
#         self._pipeline._llm._model = original_model
#
#         answer_text = response.as_text()
#
#         # Rastreia no MLflow
#         self._tracker.track(request.question, answer_text, elapsed)
#
#         # Persiste no PostgreSQL
#         save_log_to_postgres(request.question, answer_text, model_used, latency_ms)
#
#         return AskResponse(answer=answer_text, model_used=model_used)

import os
import uuid
import psycopg
from fastapi import APIRouter
from api.schemas.ask_schemas import (
    AskRequest, AskResponse, LatencyBreakdown,
    RetrievalDetail, RetrievalSourceCollection, TokenUsage,
)
from api.routes.ask_timer import AskExecutionTimer
from rag.rag_pipeline import RagPipeline
from mlops.ask_tracker import AskExperimentTracker

router = APIRouter()


class ModelSelector:
    def __init__(self, requested_model: str | None):
        self._requested_model = requested_model

    def resolve(self) -> str:
        return self._requested_model or os.getenv("LLM_MODEL", "llama3.2")


class AskLogPersistence:
    def __init__(self, question: str, response: AskResponse):
        self._question = question
        self._response = response

    def persist(self) -> None:
        try:
            self._write_to_postgres()
        except Exception as error:
            print(f"[postgres] Erro ao salvar log: {error}")

    def _write_to_postgres(self) -> None:
        connection = psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "rag_user"),
            password=os.getenv("POSTGRES_PASSWORD", "rag_pass"),
            dbname=os.getenv("POSTGRES_DB", "rag_db"),
        )
        with connection:
            with connection.cursor() as cursor:
                model_id = self._fetch_model_id(cursor, self._response.model_used)
                cursor.execute(
                    "INSERT INTO ask_logs (question, answer, model_id, latency_ms, response_json) VALUES (%s, %s, %s, %s, %s)",
                    (
                        self._question,
                        self._response.answer,
                        model_id,
                        self._response.latency_breakdown.total_milliseconds,
                        self._response.model_dump_json(),
                    ),
                )
        connection.close()

    def _fetch_model_id(self, cursor, model_name: str) -> int | None:
        cursor.execute("SELECT id FROM llm_models WHERE name = %s", (model_name,))
        row = cursor.fetchone()
        return row[0] if row else None



class AskHandler:
    def __init__(self, pipeline: RagPipeline, tracker: AskExperimentTracker):
        self._pipeline = pipeline
        self._tracker = tracker

    def handle(self, request: AskRequest) -> AskResponse:
        model_used = ModelSelector(request.model).resolve()
        timer = AskExecutionTimer()

        pipeline_result = self._pipeline.answer_with_retrieval(
            query=request.query,
            model=model_used,
            rag_configuration=request.rag_configuration,
            generation_configuration=request.generation_configuration,
            on_retrieval_complete=timer.mark_retrieval_complete,
        )

        ask_response = AskResponse(
            conversation_identifier=request.conversation_identifier or str(uuid.uuid4()),
            model_used=model_used,
            answer=pipeline_result.answer_text(),
            token_usage=pipeline_result.token_usage(),
            latency_breakdown=LatencyBreakdown(
                total_milliseconds=timer.total_milliseconds(),
                retrieval_milliseconds=timer.retrieval_milliseconds(),
                generation_milliseconds=timer.generation_milliseconds(),
            ),
            retrieval_detail=pipeline_result.retrieval_detail(),
        )

        self._tracker.track(request.query, ask_response.answer, timer.total_milliseconds() / 1000)
        AskLogPersistence(request.query, ask_response).persist()

        return ask_response