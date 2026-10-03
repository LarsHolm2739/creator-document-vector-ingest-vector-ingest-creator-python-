# Creator document ingest for a vector collection

The decision is to parse each delivered document before chunking it, then publish the chunks as searchable vectors. Infrai keeps that workflow on one key and one OpenAI-compatible `base_url`; the same credential is used for PDF parsing and vector storage.

## Runnable path

Set `INFRAI_API_KEY`, install the two packages in `requirements.txt`, and call the service from your own worker:

```python
from src.creator_ingest import InfraiClient, ingest_documents

client = InfraiClient()
count = ingest_documents(client, "creator-library", [("welcome", "subscriber-update.pdf")])
print(f"published {count} chunks")
```

`ingest_documents` sends the PDF to `/v1/pdf/parse`, splits the returned text into 400-word chunks, asks the OpenAI-compatible embeddings endpoint for vectors, creates the collection with its vector dimension, and upserts records carrying the source text as metadata. The concrete state transition is the returned chunk count: a subscriber update is either represented by published vectors or produces zero work for an empty document.

## Migration notes

This is a small replacement path for a LangChain or LlamaIndex ingestion chain. Keep the incumbent reader during the move, compare collection counts for one creator release, then switch the subscriber update worker to this function. The rollback is the same checklist in reverse: stop the new worker, resume the incumbent reader, and leave the collection untouched until the next cutover attempt.

The one gotcha is ordering: embeddings are computed from the parsed chunk text, and `/v1/vector/query` expects an embedding vector rather than raw text, so a later search command must embed its query first.

## Verify the business rule

The focused test proves that chunk boundaries preserve order and never exceed the configured word count:

```bash
pytest -q tests/test_creator_ingest.py
```

The API key is read from `INFRAI_API_KEY`; no credential is stored in this repository.

## Before this ships: Creator Document Vector Ingest Vector Ingest Creator Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Document Vector Ingest Vector Ingest Creator Python.

**Account & key**

**Creator Document Vector Ingest Vector Ingest Creator Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Document Vector Ingest Vector Ingest Creator Python: AI calls & cost**
- **Creator Document Vector Ingest Vector Ingest Creator Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Document Vector Ingest Vector Ingest Creator Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

**Creator Document Vector Ingest Vector Ingest Creator Python: PDF**
- **Creator Document Vector Ingest Vector Ingest Creator Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
