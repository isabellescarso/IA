import requests
from rag.retriever import ContextRetriever
from rag.prompt_builder import PromptBuilder

from rag.glucose_predictor import GlucosePrediction, RidgeGlucosePredictor
from rag.retriever import RetrievedContext

class LlmResponse:
    def __init__(self, content: str):
        self._content = content

    def print(self) -> None:
        print(f"\nResposta:\n{self._content}\n")

    def as_text(self) -> str:
        return self._content


class OllamaEndpoint:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def generate_url(self) -> str:
        return f"{self._base_url}/api/generate"


class OllamaLlmClient:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model

    def generate(self, prompt: str) -> LlmResponse:
        response = requests.post(
            f"{self._base_url}/api/generate",
            json={"model": self._model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return LlmResponse(response.json()["response"])


class ContextualPredictor:
    def __init__(self, retriever: ContextRetriever, predictor: RidgeGlucosePredictor):
        self._retriever = retriever
        self._predictor = predictor

    def resolve(self, question: str) -> tuple[RetrievedContext, GlucosePrediction]:
        context = self._retriever.retrieve(question)
        prediction = self._predictor.predict(context.as_feature_row())
        return context, prediction


class RagPipeline:
    def __init__(self, contextual_predictor: ContextualPredictor, llm: OllamaLlmClient):
        self._contextual_predictor = contextual_predictor
        self._llm = llm

    def answer(self, question: str) -> LlmResponse:
        context, prediction = self._contextual_predictor.resolve(question)
        prompt = PromptBuilder().build(question, context, prediction)
        return self._llm.generate(prompt.as_text())