from rag.retriever import RetrievedContext
from rag.glucose_predictor import GlucosePrediction
import mlflow

class RagPrompt:
    def __init__(self, content: str):
        self._content = content

    def as_text(self) -> str:
        return self._content


class PromptBuilder:
    TEMPLATE = (
        "Você é um assistente especializado em saúde, nutrição e experimentos de machine learning.\n"
        "Use os dados abaixo para responder de forma clara e organizada.\n"
        "Se não houver dados suficientes, diga que não encontrou informações.\n"
        "Não repita os mesmos modelos ou métricas mais de uma vez.\n\n"
        "Dados relevantes:\n{context}\n\n"
        "{prediction}\n\n"
        "Pergunta: {question}\n"
        "Resposta:"
    )

    def build(self, question: str, context: RetrievedContext, prediction: GlucosePrediction) -> RagPrompt:
        content = self.TEMPLATE.format(
            mlflow_context=self._load_mlflow_runs(),
            context=context.as_joined_text(),
            prediction=prediction.as_text(),
            question=question,
        )
        return RagPrompt(content)

    def _load_mlflow_runs(self) -> str:
        try:
            runs = mlflow.search_runs(
                experiment_names=["Sprint_4_CGMacros"],
                output_format="list",
            )
            lines = []
            for run in runs:
                model = run.data.params.get("model", "desconhecido")
                metrics = run.data.metrics
                lines.append(
                    f"- Modelo: {model} | "
                    f"MAE: {metrics.get('mae', 0):.4f} | "
                    f"RMSE: {metrics.get('rmse', 0):.4f} | "
                    f"R2: {metrics.get('r2', 0):.4f}"
                )
            return "\n".join(lines)
        except Exception:
            return "Não foi possível carregar os experimentos do MLflow."