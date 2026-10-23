import os
import sys
from pathlib import Path

# Add root project dir to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.brain.assistant import process_message
from app.actions.windows import run_allowed_action, allowed_actions

app = FastAPI(title="SUVI Assistant API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    reply: str

class ActionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=64)

@app.get("/health")
def health():
    return {"status": "online", "assistant": "SUVI"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return ChatResponse(reply=process_message(request.message))
    except Exception:
        raise HTTPException(status_code=500, detail="SUVI could not process that request.")

@app.get("/actions")
def get_actions():
    return {"actions": allowed_actions()}

@app.post("/actions/run")
def run_action(request: ActionRequest):
    result = run_allowed_action(request.action)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
