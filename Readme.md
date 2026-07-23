# Health Explorer API

A FastAPI backend that answers natural-language questions about public health
data using retrieval-augmented generation (RAG). Chronic disease prevalence
data for Washington state is pulled from the CDC PLACES dataset, embedded,
and stored in a local Chroma vector database. Questions are answered by
retrieving the most relevant records and passing them to an LLM as context.

## How it works

1. **`fetch_data.py`** — Calls the CDC PLACES Socrata API
   (`chronicdata.cdc.gov/resource/swc5-untb.json`), filtered to
   `stateabbr=WA`, and saves the results to `data/wa_health.json`.
2. **`ingest.py`** — Loads `data/wa_health.json`, converts each record into a
   natural-language text chunk, embeds it with OpenAI's
   `text-embedding-3-small`, and stores it in a local Chroma collection
   (`health_data`).
3. **`retriever.py`** — Embeds an incoming question and queries Chroma for
   the top 5 most similar chunks.
4. **`generator.py`** — Builds a prompt from the retrieved chunks and the
   question, then calls `gpt-4o-mini` to produce an answer.
5. **`main.py`** — Exposes the API (see below) and wires the retriever and
   generator together.

## API

### `POST /query`

Answers a question using the ingested health data.

**Request body:**

```json
{ "question": "What is the diabetes prevalence in King County?" }
```

**Response:**

```json
{
  "answer": "...",
  "sources": ["chunk 1 text", "chunk 2 text", "..."]
}
```

- `answer` — the LLM-generated answer, grounded in retrieved context.
- `sources` — the raw text chunks used as context for the answer.

### `GET /health`

Health check.

**Response:**

```json
{ "status": "ok" }
```

CORS is enabled for `http://localhost:3000`.

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment variables
cp .env.example .env
# then edit .env and fill in OPENAI_API_KEY and SOCRATA_APP_TOKEN

# 3. Fetch the source data
python fetch_data.py

# 4. Embed and ingest it into Chroma
python ingest.py

# 5. Start the API
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are
at `http://localhost:8000/docs`.
