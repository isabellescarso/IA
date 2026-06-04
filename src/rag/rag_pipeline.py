import time
import requests
from rag.retriever import ContextRetriever, RetrievedContext
from rag.prompt_builder import PromptBuilder
from rag.glucose_predictor import GlucosePrediction, RidgeGlucosePredictor
from api.schemas.ask_schemas import (
    TokenUsage, LatencyBreakdown, RetrievalDetail,
    RetrievalSourceCollection, GenerationConfiguration, RagConfiguration,
)
from typing import Callable
import mlflow


class TokenUsageExtractor:
    def __init__(self, raw_response: dict):
        self._raw_response = raw_response

    def extract(self) -> TokenUsage:
        prompt_tokens = self._raw_response.get("prompt_eval_count", 0)
        completion_tokens = self._raw_response.get("eval_count", 0)
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )


class LlmResponse:
    def __init__(self, content: str, token_usage: TokenUsage):
        self._content = content
        self._token_usage = token_usage

    def as_text(self) -> str:
        return self._content

    def token_usage(self) -> TokenUsage:
        return self._token_usage


class OllamaLlmClient:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model

    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str, generation_configuration: GenerationConfiguration, model: str = "") -> LlmResponse:
        resolved_model = model or self._model
        raw = self._post(prompt, generation_configuration, resolved_model)

        # Log LLM response to MLflow
        with mlflow.start_run():
            mlflow.log_param("llm_model", resolved_model)
            mlflow.log_param("prompt", prompt)
            mlflow.log_param("temperature", generation_configuration.temperature)
            mlflow.log_param("max_tokens", generation_configuration.maximum_tokens)
            mlflow.log_param("top_p", generation_configuration.top_p)
            mlflow.log_metric("prompt_tokens", raw.get("prompt_eval_count", 0))
            mlflow.log_metric("completion_tokens", raw.get("eval_count", 0))
            mlflow.log_metric("total_tokens", raw.get("prompt_eval_count", 0) + raw.get("eval_count", 0))
            mlflow.log_text(raw["response"], "llm_response.txt")

        return LlmResponse(
            content=raw["response"],
            token_usage=TokenUsageExtractor(raw).extract(),
        )

    def _post(self, prompt: str, generation_configuration: GenerationConfiguration, model: str) -> dict:
        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": generation_configuration.temperature,
                    "num_predict": generation_configuration.maximum_tokens,
                    "top_p": generation_configuration.top_p,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()


class PipelineResult:
    def __init__(self, llm_response: LlmResponse, retrieval_detail: RetrievalDetail, model_used: str):
        self._llm_response = llm_response
        self._retrieval_detail = retrieval_detail
        self._model_used = model_used

    def answer_text(self) -> str:
        return self._llm_response.as_text()

    def token_usage(self) -> TokenUsage:
        return self._llm_response.token_usage()

    def retrieval_detail(self) -> RetrievalDetail:
        return self._retrieval_detail

    def model_used(
            self) -> str:
        return self._model_used


class RetrievalTimer:
    def __init__(self):
        self._start = time.monotonic()
        self._retrieval_end: float = 0.0

    def mark_retrieval_complete(self) -> None:
        self._retrieval_end = time.monotonic()

    def retrieval_milliseconds(self) -> int:
        return int((self._retrieval_end - self._start) * 1000)

    def generation_milliseconds(self) -> int:
        return int((time.monotonic() - self._retrieval_end) * 1000)

    def total_milliseconds(self) -> int:
        return int((time.monotonic() - self._start) * 1000)


class ContextualPredictor:
    def __init__(self, retriever: ContextRetriever, predictor: RidgeGlucosePredictor):
        self._retriever = retriever
        self._predictor = predictor

    def resolve(self, question: str, top_k: int) -> tuple[RetrievedContext, GlucosePrediction]:
        context = self._retriever.retrieve(question, top_k)

        clinical_texts = [
            r.text for r in context.source_records()
            if not r.text.startswith("Experimento:")
        ]

        if not clinical_texts:
            return context, GlucosePrediction(None)

        from embeddings.text_builder import TextCollectionParser
        feature_row = TextCollectionParser(clinical_texts).as_feature_dataframe()
        return context, self._predictor.predict(feature_row)


class RagPipeline:
    def __init__(self, contextual_predictor: ContextualPredictor, llm: OllamaLlmClient):
        self._contextual_predictor = contextual_predictor
        self._llm = llm

    def answer_with_retrieval(
            self,
            query: str,
            model: str,
            rag_configuration: RagConfiguration,
            generation_configuration: GenerationConfiguration,
            on_retrieval_complete: Callable[[], None] = lambda: None,
    ) -> PipelineResult:
        context, prediction = self._contextual_predictor.resolve(query, rag_configuration.top_k)
        on_retrieval_complete()

        prompt = PromptBuilder().build(query, context, prediction)
        llm_response = self._llm.generate(prompt.as_text(), generation_configuration, model)

        retrieval_detail = RetrievalDetail(
            collection_name=rag_configuration.collection_name,
            embedding_model_name=self._llm.model_name(),
            sources=[r.to_schema() for r in context.source_records()],
        )
        return PipelineResult(llm_response, retrieval_detail, model)