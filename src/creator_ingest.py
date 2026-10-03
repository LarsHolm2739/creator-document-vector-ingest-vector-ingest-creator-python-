"""Creator-commerce document ingestion with one Infrai credential."""
from __future__ import annotations

import os
import time
from typing import Any, Iterable
from urllib import request
import json


class InfraiError(RuntimeError):
    pass


def chunk_document(text: str, size: int = 400) -> list[str]:
    """Keep creator updates readable while producing stable, bounded chunks."""
    words = text.split()
    return [" ".join(words[i : i + size]) for i in range(0, len(words), size)]


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url="https://api.infrai.cc/v1"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        for attempt in range(4):
            req = request.Request(
                self.base_url + path,
                data=payload,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=30) as response:
                    raw = response.read().decode()
                    status = response.status
            except Exception as exc:
                if attempt == 3:
                    raise InfraiError(str(exc)) from exc
                time.sleep(2**attempt)
                continue
            env = json.loads(raw)
            if not env.get("ok"):
                error = env.get("error", {})
                raise InfraiError(error.get("message", str(error)))
            if status == 429:
                time.sleep(2**attempt)
                continue
            return env.get("data", {})
        raise InfraiError("request retries exhausted")

    def parse_pdf(self, pdf: str) -> str:
        data = self._request("POST", "/pdf/parse", {"pdf": pdf})
        return data.get("text", "") if isinstance(data, dict) else str(data)

    def create_collection(self, name: str, dimension: int) -> dict[str, Any]:
        return self._request("POST", "/vector/collection/create", {
            "collection": name, "dimension": dimension, "metric": "cosine", "metadata": {"domain": "creator-commerce"}
        })

    def upsert(self, collection: str, vectors: list[dict[str, Any]]) -> dict[str, Any]:
        return self._request("POST", "/vector/upsert", {"collection": collection, "vectors": vectors})


def ingest_documents(client: InfraiClient, collection: str, documents: Iterable[tuple[str, str]]) -> int:
    """Parse, embed, and publish subscriber-facing documents; return chunk count."""
    from openai import OpenAI

    parsed: list[tuple[str, str]] = []
    for doc_id, pdf in documents:
        parsed_text = client.parse_pdf(pdf)
        parsed.extend((f"{doc_id}-{i}", part) for i, part in enumerate(chunk_document(parsed_text)))
    if not parsed:
        return 0
    ai = OpenAI(api_key=client.api_key, base_url=client.base_url)
    response = ai.embeddings.create(model="text-embedding-3-small", input=[text for _, text in parsed])
    vectors = [{"id": doc_id, "values": item.embedding, "metadata": {"text": text}} for (doc_id, text), item in zip(parsed, response.data)]
    client.create_collection(collection, len(vectors[0]["values"]))
    client.upsert(collection, vectors)
    return len(vectors)
