import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="chroma_db")

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "health_data"
TOP_K = 5


def retrieve(question: str) -> list[str]:
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    response = client.embeddings.create(input=question, model=EMBEDDING_MODEL)
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    return results["documents"][0]
