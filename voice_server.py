
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend import AudicLabsError, check_health, create_ticket
from scripts.rag import answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-helpdesk")

app = FastAPI(title="AudicLabs Voice Help Desk")

WEB_DIR = Path(__file__).resolve().parent / "web"
WEB_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: str = Field(default="", max_length=8000)


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    try:
        return check_health()
    except AudicLabsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/ticket/{service}")
def ticket(service: str):
    if service not in {"stt", "tts"}:
        raise HTTPException(status_code=400, detail="Unsupported service")

    try:
        return create_ticket(service)
    except AudicLabsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/ask")
def ask(body: QuestionRequest):
    try:
        return answer_question(body.question, history=body.history)
    except Exception as exc:
        logger.exception("Question processing failed")
        raise HTTPException(
            status_code=500,
            detail="The question could not be processed.",
        ) from exc
