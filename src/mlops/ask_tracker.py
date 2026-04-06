import time
import mlflow


class AskExperimentTracker:
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def track(self, question: str, answer: str, elapsed_seconds: float) -> None:
        with mlflow.start_run():
            mlflow.log_param("question", question)
            mlflow.log_param("answer", answer)
            mlflow.log_metric("latency_seconds", elapsed_seconds)