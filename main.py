# Run instructions:
# 1. pip install -r requirements.txt
# 2. copy .env.example to .env and fill in keys
# 3. python fetch_data.py
# 4. python ingest.py
# 5. uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from generator import generate
from retriever import retrieve

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        chunks = retrieve(request.question)
        answer = generate(request.question, chunks)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to answer question: {e}")

    return QueryResponse(answer=answer, sources=chunks)


@app.get("/health")
def health():
    return {"status": "ok"}
