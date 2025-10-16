import uuid 


def generate_no_context_message(query: str, fallback = False):
    """
    Manually constructs the complex, nested JSON dictionary that mimics a 
    LangChain/LLM framework response when no context is available.
    
    This is necessary to satisfy the strict indexing logic in the frontend's 
    'extract_rag_content' function.
    
    Args:
        query (str): The original user query, used for context in the response message.
        
    Returns:
        dict: A dictionary mimicking the complex 'answer' field of a LangChain serialization.
    """
    
    # 1. The clean answer text
    clean_answer = (
        f"Based on the provided context, the answer to the user query ***\"{query}\"***  is:\n\n"
        "The provided document does not contain the relevant answer.\n\n"
        "Please provide more information or context for me to assist you better."
    )
    sources_string = []
    sources_string.append("No relevant documents were found.")

    if fallback == True:
        return {"message" : clean_answer, 
         "source":sources_string }
        

    # --- Part 1: The AI Message (Message 0) ---
    ai_message_part = [
        ["content", clean_answer],
        ["additional_kwargs", {}],
        ["response_metadata", {"finish_reason": "stop"}],
        ["type", "ai"],
        ["name", None],
        ["id", f"run-manual-{uuid.uuid4()}-0"], # Mock ID
        ["example", False],
        ["tool_calls", []],
        ["invalid_tool_calls", []],
        ["usage_metadata", None]
    ]



    prompt_message_part = [
        [
            "prompt",
            [
                ["name", None],
                ["input_variables", []],
                ["optional_variables", []],
                ["input_types", {}],
                ["output_parser", None],
                ["partial_variables", {}],
                ["metadata", None],
                ["tags", None],
                # This 'template' field is the one the extraction logic relies on for sources.
                ["template", sources_string], 
                ["template_format", "f-string"],
                ["validate_template", False]
            ]
        ],
        ["additional_kwargs", {}]
    ]

    # --- The full 'answer' object structure ---
    full_answer_object = {
        "name": None,
        "input_variables": [],
        "optional_variables": [],
        "input_types": {},
        "output_parser": None,
        "partial_variables": {},
        "metadata": None,
        "tags": None,
        "messages": [
            ai_message_part,  # Message 0 (contains the answer)
            prompt_message_part  # Message 1 (contains the source string in 'template')
        ],
        "validate_template": False
    }
    return full_answer_object
