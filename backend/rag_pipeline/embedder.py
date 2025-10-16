import psycopg2
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from django.utils import timezone
from project_management.models import DocumentEmbedding, Document
from unstructured.documents.elements import Element
from typing import List, Dict
from project_management.models import DocumentEmbedding
from django.conf import settings

embedding_model = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
print(f"{embedding_model=}")


def embed_and_store(document_id, chunks, customer_id=None, tag_id=None):
    embeddings = embedding_model.embed_documents(chunks)
    conn = psycopg2.connect("dbname=mydb user=myuser password=mypassword host=localhost port=5432")
    # check_embedding_dim(embedding_model=embedding_model, conn=conn)
    cur = conn.cursor()
    for idx, emb in enumerate(embeddings):
        cur.execute(
            """
            INSERT INTO project_management_documentembedding
            (document_id, embedding, customer_id, tag_id, created_at, chunk_text)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (document_id, emb, customer_id, tag_id, timezone.now(), chunks[idx])
        )
    conn.commit()
    cur.close()
    conn.close()

def embed_and_store_bulk(
    document_id: int, 
    chunks: List['Element'], 
    customer_id: int = None, 
    tag_id: int = None
):
    """
    Generates embeddings and bulk-inserts them into the database using the ORM.
    
    CRITICAL UPDATE: Now calculates and stores the larger 'parent_chunk_text'
    by looking at the neighboring chunks.
    """
    
    # 1. Extract text from Elements for embedding
    chunk_texts = [c.text for c in chunks]
    
    # 2. Generate all embeddings in a single call (fastest way)
    # NOTE: embedding_model must be defined/imported
    embeddings = embedding_model.embed_documents(chunk_texts)
    
    embedding_objects = []
    total_chunks = len(chunks)
    
    # 3. Prepare ORM objects with all metadata and the Parent Chunk
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        
        # --- PARENT CHUNK LOGIC (THE FIX) ---
        # Define the parent window (current chunk + 1 before + 1 after)
        start_idx = max(0, idx - 1)
        end_idx = min(total_chunks, idx + 2) # +2 because slicing is exclusive
        
        # Get the texts of the chunks in the window
        parent_chunks_window = chunks[start_idx:end_idx]
        
        # Join the texts to form the large context chunk
        parent_chunk_text = "\n\n".join([c.text for c in parent_chunks_window])
        # -----------------------------------
        
        # Extract metadata
        # NOTE: Using getattr(chunk, 'metadata') to safely handle the ElementMetadata object
        metadata = getattr(chunk, 'metadata', None)
        page_number = getattr(metadata, 'page_number', None) if metadata else None 
        section_title = getattr(metadata, 'section', None) if metadata else None 
        if section_title is None:
             section_title = getattr(metadata, 'title', None) if metadata else None 
             
        embedding_objects.append(
            DocumentEmbedding(
                document_id=document_id,
                chunk_text=chunk.text, # Small chunk for searching
                parent_chunk_text=parent_chunk_text, # Large chunk for LLM context
                embedding=emb,
                customer_id=customer_id,
                tag_id=tag_id,
                page_number=page_number,
                section_title=section_title, 
                created_at=timezone.now()
            )
        )
    
    DocumentEmbedding.objects.bulk_create(embedding_objects)
    message = f"Successfully inserted {len(embedding_objects)} embeddings in bulk."
    print(message)
    return message



# def embed_and_store(document_id, chunks, customer_id=None, tag_id=None):
#     embeddings = embedding_model.embed_documents(chunks)
#     conn = psycopg2.connect("dbname=mydb user=myuser password=mypassword host=localhost port=5432")
#     cur = conn.cursor()
#     for idx, emb in enumerate(embeddings):
#         cur.execute(
#             """
#             INSERT INTO project_management_documentembedding
#             (document_id, embedding, customer_id, tag_id, created_at, chunk_text)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             """,
#             (document_id, emb, customer_id, tag_id, timezone.now(), chunks[idx])
#         )
#     conn.commit()
#     cur.close()
#     conn.close()