import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from rag.rag_pipeline import RagPipeline
from mlops.ask_tracker import AskExperimentTracker

router = APIRouter()


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class AskHandler:
    def __init__(self, pipeline: RagPipeline, tracker: AskExperimentTracker):
        self._pipeline = pipeline
        self._tracker = tracker

    def handle(self, request: AskRequest) -> AskResponse:
        start = time.monotonic()
        response = self._pipeline.answer(request.question)
        elapsed = time.monotonic() - start
        self._tracker.track(request.question, response.as_text(), elapsed)
        return AskResponse(answer=response.as_text())