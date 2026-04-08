from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from api.routes.ask import router as ask_router, AskRequest, AskResponse, AskHandler
from api.dependencies import build_rag_pipeline
from rag.rag_pipeline import RagPipeline

from mlops.ask_tracker import AskExperimentTracker

from api.dependencies import build_ask_tracker
from api.routes.metadata import router as metadata_router, MetadataResponse, MetadataHandler
from api.dependencies import build_metadata_handler

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

@app.get("/metadata", response_model=MetadataResponse)
def metadata(handler: MetadataHandler = Depends(build_metadata_handler)) -> MetadataResponse:
    return handler.handle()