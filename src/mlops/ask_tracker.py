import time
import mlflow

"""
Params: question, answer
Metric: latency_seconds
Registra cada consulta feita pelo usuário via API
"""
class AskExperimentTracker:
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def track(self, question: str, answer: str, elapsed_seconds: float, relevance_score: float = None, prompt_variant: str = None) -> None:
        with mlflow.start_run():
            mlflow.log_param("question", question)
            mlflow.log_param("answer", answer)
            mlflow.log_metric("latency_seconds", elapsed_seconds)
            
            # Adiciona métrica de relevância se fornecida
            if relevance_score is not None:
                mlflow.log_metric("relevance_score", relevance_score)
            
            # Adiciona variante do prompt se fornecida
            if prompt_variant is not None:
                mlflow.log_param("prompt_variant", prompt_variant)
