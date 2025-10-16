
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.documents.elements import Element
from unstructured.chunking.title import chunk_by_title 


def chunk_text(text:str, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def chunk_elements(elements: List[Element], max_chunk_size=500, overlap=50) -> List[Element]:
    """
    Chunks a list of Unstructured Elements using the 'by_title' strategy.

    This preserves section boundaries (titles/headings) to maintain context.
    The resulting objects are still Unstructured Element objects.
    """
    
    # max_characters is the equivalent of chunk_size for Unstructured.
    # new_after_n_chars creates a soft maximum to combine smaller elements.
    # The default for combine_text_under_n_chars (which respects title hierarchy) 
    # is usually max_characters, which is a good default.
    chunks = chunk_by_title(
        elements=elements,
        max_characters=max_chunk_size,
        overlap=overlap,
        # Setting this to 0 prevents breaking a section/page boundary 
        # unless necessary, even if a small element could fit in the previous chunk.
        new_after_n_chars=max_chunk_size - overlap 
    )
    
    return chunks