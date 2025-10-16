"""
rag_local_demo.py
Simple demonstration of:
- chunking
- embedding
- storing embeddings to Postgres (pgvector)
- retrieving nearest chunks (using SQL)
- calling an LLM adapter (pluggable)
"""

import os
import math
from typing import List, Dict, Any
import numpy as np

# Install these in your env
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text

############### CONFIG ###############
PG_DSN = os.getenv("PG_DSN", "postgresql://user:pass@localhost:5432/ragdb")
EMBED_MODEL = "all-MiniLM-L6-v2"   # small for demo; swap for production
EMBED_DIM = 384                    # depends on model (MiniLM => 384)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
######################################

# Embedding model (SentenceTransformers)
embedder = SentenceTransformer(EMBED_MODEL)

# SQLAlchemy Engine for convenience
engine = create_engine(PG_DSN)

# Ensure pgvector extension and table exist (run once)
def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS document_chunk (
            id SERIAL PRIMARY KEY,
            project_id INT NOT NULL,
            file_id INT NOT NULL,
            chunk_index INT NOT NULL,
            content TEXT NOT NULL,
            embedding vector({EMBED_DIM}),
            created_at TIMESTAMP DEFAULT now()
        );
        """))
    print("DB ready")

# Simple chunker (character based)
def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunks.append(text[start:end])
        if end == L:
            break
        start = end - overlap
    return chunks

# Create embeddings and save to pgvector
def ingest_file(project_id: int, file_id: int, text: str):
    chunks = chunk_text(text)
    embeddings = embedder.encode(chunks, show_progress_bar=False)
    # Convert numpy arrays to Python lists
    vecs = [emb.tolist() for emb in embeddings]

    # Insert into DB
    with engine.begin() as conn:
        sql = "INSERT INTO document_chunk (project_id, file_id, chunk_index, content, embedding) VALUES %s"
        values = [
            (project_id, file_id, idx, chunks[idx], vecs[idx])
            for idx in range(len(chunks))
        ]
        # psycopg2 execute_values works with raw connection, use engine.raw_connection
        raw = conn.connection
        cur = raw.cursor()
        execute_values(cur, sql, values, template="(%s,%s,%s,%s,%s)")
        raw.commit()
    print(f"Ingested {len(chunks)} chunks for file {file_id}")

# Retrieve nearest chunks using pgvector distance
def retrieve_by_pgvector(project_id: int, query: str, top_k: int = 5):
    q_emb = embedder.encode([query])[0].tolist()
    sql = text(f"""
    SELECT id, file_id, chunk_index, content, embedding <-> :q_emb AS distance
    FROM document_chunk
    WHERE project_id = :project_id
    ORDER BY embedding <-> :q_emb
    LIMIT :top_k;
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"q_emb": q_emb, "project_id": project_id, "top_k": top_k}).fetchall()
    results = [{"id": r[0], "file_id": r[1], "chunk_index": r[2], "content": r[3], "distance": r[4]} for r in rows]
    return results

# Example LLM adapter placeholder (replace with real calls)
def call_llm(prompt: str, model="local", temperature=0.0, max_tokens=256):
    # For learning: just echo prompt + pretend answer
    return f"[LLM {model} | temp={temperature}] Answer based on prompt: {prompt[:200]}..."

# Compose full RAG call
def rag_query(project_id: int, user_prompt: str, top_k=4, temperature=0.0):
    # Step 1: retrieve
    chunks = retrieve_by_pgvector(project_id, user_prompt, top_k=top_k)
    context = "\n\n---\n\n".join([c["content"] for c in chunks])
    # Build augmented prompt
    system_prompt = "You are an assistant that answers only from the provided context. If unsupported, say you don't know."
    full_prompt = system_prompt + "\n\nContext:\n" + context + "\n\nUser question:\n" + user_prompt
    # Step 2: call LLM
    ans = call_llm(full_prompt, model="local-mock", temperature=temperature)
    # Return with sources
    return {"answer": ans, "sources": [{"file_id": c["file_id"], "chunk_index": c["chunk_index"], "distance": c["distance"]} for c in chunks]}

# Quick demo main
if __name__ == "__main__":
    init_db()
    # Demo: ingest a file
    demo_text = "This is a demo document. " * 400  # long text
    ingest_file(project_id=1, file_id=1, text=demo_text)
    # Query
    out = rag_query(project_id=1, user_prompt="What is this doc about?", top_k=3)
    print(out)
