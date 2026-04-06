import requests
from rag.retriever import ContextRetriever
from rag.prompt_builder import PromptBuilder


class LlmResponse:
    def __init__(self, content: str):
        self._content = content

    def print(self) -> None:
        print(f"\nResposta:\n{self._content}\n")

    def as_text(self) -> str:
        return self._content


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


class RagPipeline:
    def __init__(self, retriever: ContextRetriever, llm: OllamaLlmClient):
        self._retriever = retriever
        self._llm = llm

    def answer(self, question: str) -> LlmResponse:
        context = self._retriever.retrieve(question)
        prompt = PromptBuilder().build(question, context)
        return self._llm.generate(prompt.as_text())
