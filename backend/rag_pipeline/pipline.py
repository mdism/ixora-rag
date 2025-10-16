from rag_pipeline.loader import load_document_elements
from rag_pipeline.splitter import chunk_text, chunk_elements
from rag_pipeline.embedder import embed_and_store, embed_and_store_bulk
from rag_pipeline.retriever import retriever_similarity
from rag_pipeline.llm import generate_answer
from django.conf import settings
from rag_pipeline.utility import generate_no_context_message


def index_document(document_id, file_path, customer_id: None, tag_id=None):
    # 1. Load: Returns a list of Elements
    elements = load_document_elements(file_path)

    # 2. Chunk: Needs the Elements as input
    chunks = chunk_elements(elements) 
    
    # 3. Embed & Store (Bulk): Needs the chunked Elements as input
    result = embed_and_store_bulk(
        document_id, 
        chunks, 
        customer_id=customer_id, 
        tag_id=tag_id
    )
    return result


def answer_query(
    query: str,
    customer_id: int,
    tag_id: int,
    provider: str,
    temperature: float,
    top_p: float,
    max_token: int
) -> str:
    """
    RAG pipeline: Retrieve context, generate answer, and format output.
    """
    

    selected_chunks = retriever_similarity(
        query=query,
        customer_id=customer_id,
        tag_id=tag_id
    )

    # if not selected_chunks:
    #     return generate_no_context_message(query=query, fallback=False)

    # 2. Context Aggregation and Source Generation
    context_texts = []
    sources_set = set()

    for filename, parent_chunk_text, page_number, section_title in selected_chunks:
        # Use the larger parent_chunk_text for the LLM context
        context_texts.append(parent_chunk_text)
        
        # Create a citation string
        source_citation = f"Source: {filename} (Page {page_number})"
        if section_title:
            source_citation += f" - Section: {section_title}"
        sources_set.add(source_citation)

    context = "\n---\n".join(context_texts)
    sources = list(sources_set)[:3]

    # 3. Answer Generation (Call the LLM)
    answer = generate_answer(
        query=query,
        context=context,
        sources=sources,
        provider=provider,
        temperature=temperature,
        top_p=top_p,
        max_token=max_token
    )

    # 4. Final Formatting: Append sources to the LLM's answer
    sources_text = "\n\n### Sources\n" + "\n".join(sources)
    return answer + sources_text, sources
