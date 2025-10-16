import ast
import psycopg2
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from rag_pipeline.embedder import embedding_model
from project_management.models import DocumentEmbedding
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from pgvector.django import CosineDistance


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)



def mmr(
    query_vector: np.ndarray,
    doc_vectors: List[np.ndarray],
    doc_data: List[Tuple[str, str, int, str]], # (filename, parent_chunk_text, page_number, section_title)
    top_k: int,
    lambda_param: float,
) -> List[Tuple[str, str, int, str]]:
    """
    Maximal Marginal Relevance (MMR) selection for diversity.
    
    Args:
        query_vector: The embedding of the user's query.
        doc_vectors: List of candidate embedding vectors.
        doc_data: List of corresponding chunk data to be returned.
        top_k: The number of items to select.
        lambda_param: The balance between relevance (1.0) and diversity (0.0).
        
    Returns:
        A list of the top_k selected documents with data.
    """
    if not doc_vectors:
        return []
    
    # Calculate similarity between query and all documents (relevance scores)
    relevance_scores = [cosine_similarity(query_vector, d_v) for d_v in doc_vectors]
    
    selected_indices = []
    unselected_indices = list(range(len(doc_vectors)))
    
    for _ in range(top_k):
        if not unselected_indices:
            break
            
        best_score = -np.inf
        best_idx = -1
        
        for candidate_idx in unselected_indices:
            
            # 1. Calculate Relevance Term (Similarity to Query)
            relevance_term = relevance_scores[candidate_idx]
            
            # 2. Calculate Diversity Term (Max Similarity to already Selected documents)
            diversity_term = 0
            if selected_indices:
                max_sim_to_selected = max(
                    cosine_similarity(doc_vectors[candidate_idx], doc_vectors[s_idx])
                    for s_idx in selected_indices
                )
                diversity_term = max_sim_to_selected
            
            # 3. Calculate MMR Score
            mmr_score = (lambda_param * relevance_term) - ((1 - lambda_param) * diversity_term)
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = candidate_idx
        
        if best_idx != -1:
            selected_indices.append(best_idx)
            unselected_indices.remove(best_idx)
        else:
            # Should not happen if doc_vectors is not empty, but ensures loop termination
            break
            
    # Return the data corresponding to the selected indices
    return [doc_data[i] for i in selected_indices]




def retriever_similarity(
    query: str, 
    customer_id: int = None, 
    tag_id: int = None, 
    top_k: int = settings.DEFAULT_RETRIEVAL_K, 
    min_sim: float = settings.DEFAULT_MIN_SIM, 
    lambda_param: float = settings.DEFAULT_MMR_LAMBDA_PARAM
) -> List[Tuple[str, str, int, str]]:
    """
    Finds relevant document chunks using Vector Search (pgvector) and MMR.
    
    This version uses the Django ORM and native pgvector operators for efficiency.
    We are retrieving the larger 'parent_chunk_text' for better LLM context.
    
    Returns: 
        List of tuples: (filename, parent_chunk_text, page_number, section_title)
    """
    
    # 1. Embed the query
    q_emb = np.array(embedding_model.embed_query(query), dtype=np.float32)

    # 2. Build the base query with filters
    queryset = DocumentEmbedding.objects.select_related('document').filter(
        # Filter on customer and tag for multi-tenancy
        customer_id=customer_id,
        tag_id=tag_id
    )
    
    # 3. Annotate the queryset with the distance (similarity)
    # We use the '<=>' operator for cosine distance (pgvector)
    # Distance = 1 - Similarity. So lower distance is higher similarity.
    # We explicitly select only the necessary fields to optimize the query.
    
    # NOTE: The VectorField (embedding) must be the first argument to the distance operator.
    # The 'distance' field now holds the cosine distance (0=perfect match, 1=orthogonal).
    # queryset = queryset.annotate( distance=(F('embedding') <==> q_emb) ) .order_by('distance')
    # min_sim = 0.05
    queryset = queryset.annotate(distance=CosineDistance('embedding', q_emb)).order_by('distance')
    
    # 4. Determine the number of candidates to fetch before MMR
    # Fetch a multiplier of the final k to ensure good diversity/quality for MMR
    candidates_to_fetch = top_k * settings.DEFAULT_RETRIVER_K_MULTIPLIER
    
    # 5. Fetch all candidates efficiently
    rows = queryset.values(
        'document__file_name', 
        'parent_chunk_text', 
        'embedding', 
        'page_number', 
        'section_title',
        'distance'
    )[:candidates_to_fetch]
    
    doc_data, doc_embs = [], []
    counter = 0
    for row in rows:
        # Calculate similarity from distance (Sim = 1 - Dist)
        distance = row['distance']
        similarity = 1 - distance
        # with open("./out.txt", mode='a', ) as file:
        #     if counter > 0:
        #         file.writelines(row['parent_chunk_text'])
        #     else:
        #         file.writelines('---------')
        #         file.writelines(f"question : {query}")
        #         file.writelines('---------')
        #         file.writelines(row['parent_chunk_text'])

        #     counter+=1


        # Apply minimum similarity threshold if required
        if similarity >= min_sim:
            # Append the data needed for the final output
            doc_data.append((
                row['document__file_name'],
                row['parent_chunk_text'],
                row['page_number'],
                row['section_title']
            ))
            
            # Append the embedding for the MMR calculation
            # NOTE: pgvector typically returns the embedding as a standard Python list/array here.
            doc_embs.append(np.array(row['embedding'], dtype=np.float32))

    if not doc_data:
        return []
        
    # 6. Apply MMR for diversity and select the final k chunks
    # selected_chunks = mmr(
    #     q_emb, 
    #     doc_embs, 
    #     doc_data, 
    #     top_k=top_k, 
    #     lambda_param=lambda_param
    # )
    
    return doc_data