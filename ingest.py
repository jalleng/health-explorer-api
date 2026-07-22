import json
import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="chroma_db")

DATA_PATH = os.path.join("data", "wa_health.json")
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "health_data"


def build_chunk(record):
    return (
        f"{record.get('locationname')} County, {record.get('statedesc')}: "
        f"{record.get('short_question_text')} prevalence is "
        f"{record.get('data_value')}% among adults. "
        f"Category: {record.get('category')}. "
        f"Year: {record.get('year')}."
    )


def embed_text(text):
    response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding


def ingest():
    print(f"Loading data from {DATA_PATH}...")
    with open(DATA_PATH, "r") as f:
        records = json.load(f)
    print(f"Loaded {len(records)} records.")

    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    for i, record in enumerate(records):
        chunk = build_chunk(record)
        embedding = embed_text(chunk)

        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[chunk],
        )

        print(f"Ingested {i + 1}/{len(records)}: {chunk[:60]}...")

    print(f"Done. Ingested {len(records)} chunks into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest()
