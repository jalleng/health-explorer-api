# Run instructions:
# 1. pip install -r requirements.txt
# 2. copy .env.example to .env and fill in keys
# 3. python fetch_data.py
# 4. python ingest.py
# 5. uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    question: str


@app.post("/query")
def query(request: QueryRequest):
    chunks = retrieve(request.question)
    answer = generate(request.question, chunks)
    return {"answer": answer, "sources": chunks}


@app.get("/health")
def health():
    return {"status": "ok"}
