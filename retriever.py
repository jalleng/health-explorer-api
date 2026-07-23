import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL

load_dotenv()

client = OpenAI()
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

TOP_K = 15


def retrieve(question: str) -> list[str]:
    response = client.embeddings.create(input=question, model=EMBEDDING_MODEL)
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    documents = results.get("documents")
    return documents[0] if documents else []
