import os
from fastapi import FastAPI
from pydantic import BaseModel
from src.qa_engine import get_answer
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

app = FastAPI(title="QnA Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local 
    # allow_origins=[os.getenv("URL_SITE")],  # with host
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


# HEALTHCHECK
@app.get("/")
def root():
    return {
        "message": "QnA Chatbot API is running",
        "docs": "/docs",
        "endpoint": "/ask",
    }


@app.post("/ask")
def ask_question(req: QuestionRequest):
    return get_answer(req.question)