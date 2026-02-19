from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.qa_engine import get_answer, get_by_keyword

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


@app.get("/category/{selected_keyword}")
def get_category(selected_keyword: str):
    return get_by_keyword(selected_keyword)


@app.post("/ask")
def ask_question(req: QuestionRequest):
    return get_answer(req.question)
