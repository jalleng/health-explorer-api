import hashlib
import json
import time

import chromadb
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from config import CHROMA_PATH, COLLECTION_NAME, DATA_PATH, EMBEDDING_MODEL

load_dotenv()

client = OpenAI()
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

BATCH_SIZE = 100
MAX_RETRIES = 5
RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, APITimeoutError)


def build_chunk(record):
    return (
        f"{record.get('locationname')} County, {record.get('statedesc')}: "
        f"{record.get('short_question_text')} prevalence is "
        f"{record.get('data_value')}% among adults. "
        f"Category: {record.get('category')}. "
        f"Year: {record.get('year')}."
    )


def build_id(chunk: str) -> str:
    return hashlib.sha256(chunk.encode("utf-8")).hexdigest()


def embed_batch(texts: list[str]) -> list[list[float]]:
    last_error: Exception = RuntimeError("embed_batch: no attempts were made")
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
            return [item.embedding for item in response.data]
        except RETRYABLE_ERRORS as e:
            last_error = e
            if attempt == MAX_RETRIES - 1:
                break
            wait_seconds = 2**attempt
            print(f"Embedding request failed ({e}); retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)
    raise last_error


def ingest():
    print(f"Loading data from {DATA_PATH}...")
    with open(DATA_PATH, "r") as f:
        records = json.load(f)
    print(f"Loaded {len(records)} records.")

    # Content-based IDs let reruns upsert in place instead of requiring a
    # destructive delete-and-recreate of the collection first.
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    for batch_start in range(0, len(records), BATCH_SIZE):
        batch = records[batch_start : batch_start + BATCH_SIZE]
        chunks = [build_chunk(record) for record in batch]
        ids = [build_id(chunk) for chunk in chunks]
        embeddings = embed_batch(chunks)

        collection.upsert(ids=ids, embeddings=embeddings, documents=chunks)  # type: ignore[arg-type]

        print(
            f"Ingested {min(batch_start + BATCH_SIZE, len(records))}/{len(records)} records."
        )

    print(f"Done. Ingested {len(records)} chunks into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest()
