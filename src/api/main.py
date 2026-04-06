from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from api.routes.ask import router as ask_router, AskRequest, AskResponse, AskHandler
from api.dependencies import build_rag_pipeline
from rag.rag_pipeline import RagPipeline

from mlops.ask_tracker import AskExperimentTracker

from api.dependencies import build_ask_tracker

load_dotenv()

app = FastAPI(title="RAG CGMacros")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    pipeline: RagPipeline = Depends(build_rag_pipeline),
    tracker: AskExperimentTracker = Depends(build_ask_tracker),
) -> AskResponse:
    return AskHandler(pipeline, tracker).handle(request)