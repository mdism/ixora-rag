import os
from typing import List
from unstructured.partition.auto import partition
from unstructured.documents.elements import Element
from unstructured.cleaners.core import clean_extra_whitespace


KEEP_ELEMENTS = [
    'NarrativeText', 
    'ListItem', 
    'Title', 
    'Table', 
    'text',
    'UncategorizedText',
]


UNWANTED_TEXT_PATTERNS = [
    '.............',
    " . . . . . . . . . . . . "
    'footer:',
    r'page\s+\d+\s+of\s+\d+',
]

def load_document_and_clean(path: str) -> str:
    """
    Loads text content from a document using Unstructured, applies filtering, 
    and cleaning.

    Args:
        path: The file path to the document.

    Returns:
        The extracted and cleaned text content as a single string.
    """
    if not os.path.exists(path):
        return f"Error: File not found at path: {path}"

    try:
        # Use the auto-partition function from unstructured, which detects file type
        # For PDF, DOCX, TXT, this will handle the extraction.
        elements: List[Element] = partition(
            filename=path, 
            # Optionally set the strategy for better results on complex PDFs
            # strategy="hi_res" 
        )
        
        # 3. Filter the elements based on category and unwanted text
        filtered_elements: List[Element] = []
        for element in elements:
            # Check for element category
            is_kept_category = element.category in KEEP_ELEMENTS
            
            # Check for unwanted text (case-insensitive)
            is_unwanted_text = any(
                pattern.lower() in element.text.lower()
                for pattern in UNWANTED_TEXT_PATTERNS
            )

            # Keep the element only if it meets both conditions
            if is_kept_category and not is_unwanted_text:
                filtered_elements.append(element)
        
        # 4. Join the cleaned text 
        # Apply the clean_extra_whitespace cleaner from Unstructured
        cleaned_text_list = [
            clean_extra_whitespace(el.text) 
            for el in filtered_elements
        ]
        
        # Join all the cleaned elements into a single string, separated by newlines
        return '\n\n'.join(cleaned_text_list)

    except Exception as e:
        return f"Error loading document with Unstructured: {e}"


def load_document_elements(path: str, start_page:int = 1) -> List[Element]:
    """
    Loads document elements using Unstructured, applies element filtering 
    and text cleaning, and returns the filtered list of Element objects.

    Args:
        path: The file path to the document.

    Returns:
        A list of filtered and cleaned Unstructured Element objects.
    """
    if not os.path.exists(path):
        print(f"Error: File not found at path: {path}")
        return []

    try:
        # 1. Partition the document into raw elements
        elements: List[Element] = partition(
            filename=path, 
            # strategy="hi_res",

        )
        
        # 2. Filter and Clean the elements
        filtered_elements: List[Element] = []
        for element in elements:
            # Check for element category
            is_kept_category = element.category in KEEP_ELEMENTS
            
            # Check for unwanted text (case-insensitive for strings, or use compiled regex)
            is_unwanted_text = False
            for pattern in UNWANTED_TEXT_PATTERNS:
                text_to_check = element.text.lower()
                if isinstance(pattern, str):
                    if pattern.lower() in text_to_check:
                        is_unwanted_text = True
                        break
                elif pattern.search(text_to_check): # For compiled regex
                    is_unwanted_text = True
                    break
            
            # 3. Keep the element only if it meets both conditions
            if is_kept_category and not is_unwanted_text:
                
                # Apply the cleaning *before* passing to the chunker/storer
                # Modify the element's text in place
                element.text = clean_extra_whitespace(element.text)
                
                filtered_elements.append(element)
        
        return filtered_elements

    except Exception as e:
        print(f"Error loading document with Unstructured: {e}")
        return []
