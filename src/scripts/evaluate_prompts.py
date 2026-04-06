import os
import time
from dotenv import load_dotenv
from pymilvus import connections, Collection
import mlflow

from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.semantic_searcher import MilvusSemanticSearcher
from rag.retriever import ContextRetriever
from rag.rag_pipeline import OllamaLlmClient
from mlops.prompt_evaluator import PromptVariant, PromptVariantCollection, PromptEvaluationResult

load_dotenv()

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Prompt_Evaluation")

connections.connect(
    alias="default",
    host=os.getenv("MILVUS_HOST", "localhost"),
    port=os.getenv("MILVUS_PORT", "19530"),
)
collection = Collection(os.getenv("MILVUS_COLLECTION", "cgmacros_embeddings"))
collection.load()

embedder = OllamaEmbedder(os.getenv("OLLAMA_URL", "http://localhost:11434"), os.getenv("EMBED_MODEL", "nomic-embed-text"))
searcher = MilvusSemanticSearcher(collection)
retriever = ContextRetriever(embedder, searcher)
llm = OllamaLlmClient(os.getenv("OLLAMA_URL", "http://localhost:11434"), os.getenv("LLM_MODEL", "llama3.2"))

QUESTION = "Quais registros apresentam glicose elevada com baixa atividade física?"

variants = PromptVariantCollection([
    PromptVariant(
        name="direto",
        template="Dados:\n{context}\n\nPergunta: {question}\nResposta:",
    ),
    PromptVariant(
        name="especialista",
        template=(
            "Você é um especialista em saúde e nutrição.\n"
            "Use apenas os dados abaixo para responder com precisão.\n\n"
            "Dados:\n{context}\n\nPergunta: {question}\nResposta:"
        ),
    ),
    PromptVariant(
        name="estruturado",
        template=(
            "Contexto clínico:\n{context}\n\n"
            "Responda de forma estruturada e objetiva.\n"
            "Pergunta: {question}\nResposta:"
        ),
    ),
])


def evaluate(variant: PromptVariant) -> None:
    context = retriever.retrieve(QUESTION).as_joined_text()
    prompt = variant.build(context, QUESTION)
    start = time.monotonic()
    answer = llm.generate(prompt).as_text()
    elapsed = time.monotonic() - start
    PromptEvaluationResult(variant.name(), answer, elapsed).log()
    print(f"[eval] {variant.name()} · {elapsed:.1f}s · {len(answer)} chars")


variants.each(evaluate)