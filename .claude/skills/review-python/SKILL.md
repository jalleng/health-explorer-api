---
name: review-python
description: Review code for Python best practices, common gotchas, and project conventions
---

## Scope

If "$ARGUMENTS" is "all", read all `.py` source files in the project (excluding `__pycache__/`, `venv/`, `.venv/`, and `data/`) and review the entire codebase against the checklist.

Otherwise, review only the current diff:

!`git diff HEAD`

## Python

- Missing type hints on function parameters or return values
- Type assertions used instead of runtime validation
- Unused imports
- PEP 8 violations (e.g., line length, indentation, spacing)
- Bare `except Exception` (or bare `except:`) that swallows unrelated errors — catch the specific exception type instead
- Mutable/expensive objects (API clients, DB connections) instantiated at module import time instead of behind a factory or dependency — makes testing and reconfiguration hard, and hides initialization failures until unrelated code runs
- Hardcoded config values (file paths, model names, collection/table names) duplicated across multiple files instead of a single shared constant or config module — if copies drift, different parts of the app silently target different resources
- Relative file paths (e.g. `"data/..."`, `"chroma_db"`) that depend on the process's current working directory — prefer paths derived from `__file__` or a configured base dir
- Missing timeouts and retry/backoff on outbound HTTP calls (`urllib`, `requests`, SDK clients) — a hung or transient-failing request can block or crash the process
- Unvalidated API responses — code assumes a specific shape (e.g., a list of records) without checking for error payloads or unexpected types before using the data
- Unpinned or missing versions in `requirements.txt` — breaks reproducibility; SDKs like `openai` and `chromadb` have shipped breaking changes across versions
- No validation that required env vars are actually set before using them — fail fast with a clear error instead of letting `None` propagate into an SDK call
- Loops issuing one external API call per item instead of batching — costly and more likely to hit rate limits, especially with no retry/backoff around it
- Destructive operations (deleting/overwriting persisted state) performed before new data is confirmed successfully written — a mid-run failure can leave the system worse off (empty/partial) than before the run started

## FastAPI

- Endpoints with no error handling around calls that can fail (network, external API, DB) — unhandled exceptions leak raw tracebacks/500s to clients; wrap in try/except and raise `HTTPException` with an appropriate status code
- Route handlers returning raw dicts instead of a declared `response_model` — loses response validation and OpenAPI schema accuracy
- `async def` route handlers calling blocking/synchronous SDK or I/O calls directly — blocks the event loop; either use a sync `def` (FastAPI runs it in a threadpool) or offload with `run_in_threadpool`/an async client
- `CORSMiddleware` configured with `allow_origins=["*"]` combined with `allow_credentials=True` — invalid per spec and a security smell if it slips into a real deployment
- No input validation beyond basic types (e.g., empty-string or excessively long fields) on request fields that drive paid external API calls

## AI / RAG pipeline gotchas (embeddings, vector DBs, LLM calls)

- Text chunk or prompt construction using unvalidated `dict.get()` lookups — a missing/renamed source field silently embeds the literal string "None" into the corpus instead of failing loudly
- Fields referenced when building chunks/prompts that aren't actually present in the upstream data fetch/query (e.g., a `$select` or projection that dropped a column still used downstream) — a common source of silent, hard-to-notice data-quality bugs; when a fetch/ingest step and a consuming step live in different files, check that their field lists actually agree
- Vector DB client (e.g., Chroma `PersistentClient`) path or collection name duplicated across ingest and retrieval code — if they ever diverge, writes and reads silently target different stores
- No handling for the LLM response being empty/`None` (e.g., refusal, content filter) before returning it to callers
- Retrieval count / context size increased without considering prompt-token cost or relevance dilution (more chunks isn't strictly better)
- Deleting/recreating a vector collection on every ingestion run instead of incremental upserts — acceptable for small datasets, but flag it as a scaling/safety limit, especially combined with no batching or retry logic
- Treating API values as native types without casting — Socrata (and many REST JSON APIs) return numeric fields as strings; comparisons or math on them will misbehave unless explicitly cast

## Project hygiene

- `.env.example` (or equivalent) referenced in README/run instructions or code comments but missing from the repo, or missing from git tracking entirely
- Files or setup steps referenced in documentation that don't exist or no longer match the actual code
- Multiple virtual environments (e.g. both `venv/` and `.venv/`) left on disk — easy source of "works in my terminal but not my editor" confusion

## Output format

For each issue: file path, line number, what's wrong, and a suggested fix.
If the code is clean, say so explicitly.
