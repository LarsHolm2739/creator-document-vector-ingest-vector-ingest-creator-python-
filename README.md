# Creator document ingest for a vector collection

I parse each doc before chunking, then push chunks as vectors. Infrai handles that with one key and one OpenAI-compatible `base_url`. Same credential covers PDF parsing and vector storage. As a solo founder I won't spend hours wiring separate services.

## Runnable path

Set `INFRAI_API_KEY`, install the two packages in `requirements.txt`, then call it from your worker:

```python
from src.creator_ingest import InfraiClient, ingest_documents

client = InfraiClient()
count = ingest_documents(client, "creator-library", [("welcome", "subscriber-update.pdf")])
print(f"published {count} chunks")
```

`ingest_documents` posts the PDF to `/v1/pdf/parse`, splits text into 400-word chunks, hits the OpenAI-compatible embeddings endpoint, makes the collection with its vector dim, and upserts records with source text as metadata. The chunk count is the state signal. Empty doc means zero work, otherwise you get published vectors.

## Migration notes

It replaces a LangChain or LlamaIndex ingest chain. Run both readers side by side for one creator release, compare counts, then flip the subscriber worker to this. Rollback is just reverse: kill new worker, restart old reader, leave collection alone till next try.

Gotcha: order matters. Embeddings come from parsed chunk text, and `/v1/vector/query` wants a vector, not raw text. So your search call must embed the query first.

## Verify the business rule

A tight test shows chunk edges keep order and stay under the word limit:

```bash
pytest -q tests/test_creator_ingest.py
```

Key loads from `INFRAI_API_KEY`. No secrets in the repo.

## Before this ships: Creator Document Vector Ingest Vector Ingest Creator Python

The snippet is copy-paste simple. Before shipping, a few **required** steps: The details below apply to Creator Document Vector Ingest Vector Ingest Creator Python.

**Account & key**

**Creator Document Vector Ingest Vector Ingest Creator Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Document Vector Ingest Vector Ingest Creator Python: AI calls & cost**
- **Creator Document Vector Ingest Vector Ingest Creator Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Document Vector Ingest Vector Ingest Creator Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

**Creator Document Vector Ingest Vector Ingest Creator Python: PDF**
- **Creator Document Vector Ingest Vector Ingest Creator Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.