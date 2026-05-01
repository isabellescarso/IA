from rag.retriever import RetrievedContext

from rag.glucose_predictor import GlucosePrediction
class RagPrompt:
    def __init__(self, content: str):
        self._content = content

    def as_text(self) -> str:
        return self._content


class PromptBuilder:
    TEMPLATE = (
        "Você é um assistente especializado em saúde e nutrição.\n"
        "Use apenas os dados abaixo para responder.\n\n"
        "Dados relevantes:\n{context}\n\n"
        "{prediction}\n\n"
        "Pergunta: {question}\n"
        "Resposta:"
    )

    def build(self, question: str, context: RetrievedContext, prediction: GlucosePrediction) -> RagPrompt:
        content = self.TEMPLATE.format(
            context=context.as_joined_text(),
            prediction=prediction.as_text(),
            question=question,
        )
        return RagPrompt(content)