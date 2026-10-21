"""Dense retrieval over six runbooks; SQLite stores vectors and source metadata.

Exact cosine scan is intentional for this small corpus. No LLM keyword classifier
or incident-type fallback is used to select documents.
"""

import hashlib
import json
import math
import os
import sqlite3
import threading
from pathlib import Path

import httpx


def normalize(vector):
    norm = math.sqrt(sum(x * x for x in vector))
    if not norm or not all(math.isfinite(x) for x in vector):
        raise ValueError("Invalid embedding")
    return [x / norm for x in vector]


class OllamaEmbedder:
    model = os.environ.get("EMBEDDING_MODEL", "bge-m3")

    def embed(self, texts):
        response = httpx.post(
            "http://127.0.0.1:11434/api/embed",
            json={
                "model": self.model,
                "input": texts,
                "truncate": False,
                "keep_alive": "10m",
            },
            timeout=float(os.environ.get("EMBEDDING_TIMEOUT_SECONDS", "20")),
            trust_env=False,
        )
        response.raise_for_status()
        vectors = response.json()["embeddings"]
        if len(vectors) != len(texts):
            raise ValueError("Embedding count mismatch")
        return [normalize(v) for v in vectors]


class RunbookRetriever:
    def __init__(
        self, directory: Path, database: Path, embedder=None, minimum_score=0.35
    ):
        self.directory, self.database = directory, database
        self.embedder = embedder or OllamaEmbedder()
        self.minimum_score = minimum_score
        self._lock = threading.Lock()

    def build(self):
        with self._lock:
            docs = [
                (p.stem, p.read_text()) for p in sorted(self.directory.glob("*.md"))
            ]
            metadata_path = self.directory.parent / "runbook_metadata.json"
            metadata = (
                json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
            )
            if not docs:
                raise ValueError("No runbooks")
            digest = hashlib.sha256(
                json.dumps(
                    [self.embedder.model, docs, metadata], ensure_ascii=False
                ).encode()
            ).hexdigest()
            self.database.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.database) as db:
                db.execute("CREATE TABLE IF NOT EXISTS meta (digest TEXT)")
                db.execute(
                    "CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, body TEXT, vector TEXT)"
                )
                row = db.execute("SELECT digest FROM meta").fetchone()
                if (
                    row
                    and row[0] == digest
                    and db.execute("SELECT count(*) FROM documents").fetchone()[0]
                    == len(docs)
                ):
                    return {"cached": True, "documents": len(docs), "digest": digest}
                vectors = self.embedder.embed(
                    [metadata.get(id, "") + "\n" + body for id, body in docs]
                )
                db.execute("DELETE FROM documents")
                db.execute("DELETE FROM meta")
                db.executemany(
                    "INSERT INTO documents VALUES (?,?,?)",
                    [(id, body, json.dumps(v)) for (id, body), v in zip(docs, vectors)],
                )
                db.execute("INSERT INTO meta VALUES (?)", (digest,))
            return {"cached": False, "documents": len(docs), "digest": digest}

    def search(self, query, k=2):
        self.build()
        query_vector = self.embedder.embed([query])[0]
        with sqlite3.connect(self.database) as db:
            rows = db.execute("SELECT id,body,vector FROM documents").fetchall()
        ranked = []
        for id, body, serialized in rows:
            vector = json.loads(serialized)
            if len(vector) != len(query_vector):
                raise ValueError("Embedding dimension mismatch")
            score = sum(a * b for a, b in zip(query_vector, vector))
            ranked.append(
                {
                    "id": id,
                    "title": body.splitlines()[0].lstrip("# "),
                    "uri": f"runbook://incident-response/{id}",
                    "score": round(score, 6),
                    "body": body,
                }
            )
        ranked.sort(key=lambda d: (-d["score"], d["id"]))
        return {
            "model": self.embedder.model,
            "minimum_score": self.minimum_score,
            "matches": [
                d
                for d in ranked[: max(1, min(int(k), 3))]
                if d["score"] >= self.minimum_score
            ],
        }


class MCPRunbookSearch:
    def __init__(self, mcp):
        self.mcp = mcp

    async def search(self, query):
        # The existing ops server advertises the new search capability.
        return await self.mcp.call_tool(
            "search_runbooks", {"query": query, "k": 2}, server="ops"
        )
