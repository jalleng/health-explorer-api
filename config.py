import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "data", "wa_health.json")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

COLLECTION_NAME = "health_data"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
