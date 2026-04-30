import mlflow

"""
Run name: prompt_{variant_name}
Params: variant, answer (truncado em 500 chars)
Metrics: latency_seconds, answer_length
"""
class PromptVariant:
    def __init__(self, name: str, template: str):
        self._name = name
        self._template = template

    def build(self, context: str, question: str) -> str:
        return self._template.format(context=context, question=question)

    def name(self) -> str:
        return self._name


class PromptEvaluationResult:
    def __init__(self, variant_name: str, answer: str, latency: float):
        self._variant_name = variant_name
        self._answer = answer
        self._latency = latency

    def log(self) -> None:
        with mlflow.start_run(run_name=f"prompt_{self._variant_name}"):
            mlflow.log_param("variant", self._variant_name)
            mlflow.log_param("answer", self._answer[:500])
            mlflow.log_metric("latency_seconds", self._latency)
            mlflow.log_metric("answer_length", len(self._answer))


class PromptVariantCollection:
    def __init__(self, variants: list[PromptVariant]):
        self._variants = variants

    def each(self, action) -> None:
        for variant in self._variants:
            action(variant)