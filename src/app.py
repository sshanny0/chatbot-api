from typing import List

from fastapi import APIRouter, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.qa_crud import (
    delete_qna_bulk,
    delete_qna_data,
    get_categories,
    get_qna_data,
    insert_qna_data,
    update_qna_data,
)
from src.qa_engine import get_answer, get_by_keyword

app = FastAPI(title="QnA Chatbot API")

# PREFIX UNTUK API ROUTER
crud = APIRouter(prefix="/crud")
chatbot = APIRouter(prefix="/chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=[os.getenv("URL_SITE")],  # with host
    allow_methods=["*"],
    allow_headers=["*"],
)


class BulkDeleteRequest(BaseModel):
    delete_ids: List[int]


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


@chatbot.get("/categories")
def read_categories():
    return get_categories()


@chatbot.get("/category/{selected_keyword}")
def get_category(selected_keyword: str):
    return get_by_keyword(selected_keyword)


@chatbot.post("/ask")
def ask_question(req: QuestionRequest):
    return get_answer(req.question)


# CRUD ROUTES
# GET ALL DATA WITH PAGINATION
@crud.get("/list")
def read_qna(page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    result = get_qna_data(page, limit)

    return {
        "page": page,
        "limit": limit,
        "total": result["total"],
        "data": result["data"],
    }


# INSERT NEW DATA
@crud.post("/add")
def add_qna(data: dict):
    qna_id = insert_qna_data(
        question=data["question"],
        category=data["category"],
        answer=data["answer"],
        hyperlink=data["hyperlink"],
        tag=data["tag"],
        status=data["status"],
    )
    return {"message": "QnA added successfully", "id": qna_id}


# UPDATE QNA DATA {ID}
@crud.put("/update/{qna_id}")
def update_qna(qna_id: int, data: dict):
    update_qna_data(
        qna_id=qna_id,
        question=data["question"],
        category=data["category"],
        answer=data["answer"],
        hyperlink=data["hyperlink"],
        tag=data["tag"],
        status=data["status"],
    )
    return {"message": "QnA updated successfully"}


# DELET QNA DATA {ID}
@crud.delete("/delete/{qna_id}")
def delete_qna(qna_id: int):
    delete_qna_data(qna_id)
    return {"message": "QnA deleted successfully"}


# DELETE BULK SELECTED DATA
@crud.post("/delete-bulk")
def delete_bulk(data: BulkDeleteRequest):
    delete_qna_bulk(data.delete_ids)
    return {"message": "Selected QnA deleted successfully"}


# INCLUDE ROUTE INTO APP FASTAPI
app.include_router(chatbot)
app.include_router(crud)
