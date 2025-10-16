
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rag_pipeline.rag_chain import ask_question
from rag_pipeline.pipline import index_document,answer_query
from project_management.models import ChatSession, ChatMessage, Customer
from project_management.models import ChatSession, ChatMessage, Customer, UserCustomerAssignment
from api.models import Team
from project_management.permissions import IsCustomerMember

from project_management.models import ChatSession, ChatMessage
from django.conf import settings


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rag_query(request):
    """
    POST body: {
        "question": "...",
        "session_id": 10, // Optional: if provided, use existing session (check user ownership & customer access)
        "customer_id": 1, // Required: customer context for this query
        "tag_id": 2,      // Optional: tag context for this query (for RAG logic, not access control)
        "provider": "llama", // Optional: provider for this query (default from settings)
        "temperature": 0.5, // Optional
        "top_p": 0.8,       // Optional
        "max_token": 512    // Optional
    }
    """
    user = request.user
    question = request.data.get("question")
    session_id = request.data.get("session_id") # Optional
    customer_id = request.data.get("customer_id") # Required for context
    tag_id = request.data.get("tag_id") # Optional for RAG logic
    provider = request.data.get("provider", settings.DEFAULT_LLM_PROVIDER)
    temperature = request.data.get("temperature", settings.DEFAULT_TEMPERATURE)
    top_p = request.data.get("top_p", settings.DEFAULT_TOP_P)
    max_token = request.data.get("max_token", settings.DEFAULT_MAX_TOKENS)

    # Validate required fields
    if not question or not customer_id:
        return Response({"error": "Question and customer_id are required."}, status=400)

    # Fetch customer object
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Invalid customer_id."}, status=404)

    # --- Permission Check for Customer Access (Updated) ---
    user_has_access = (
        UserCustomerAssignment.objects.filter(user=user, customer=customer).exists() or
        Team.objects.filter(members=user, customers=customer).exists()
    )

    if not user_has_access:
        return Response({"error": "Access denied for this customer."}, status=403)

    # Retrieve or Create Session associated with the *initial customer*
    try:
        if session_id:
            # Check if the session belongs to the current user AND was initially created for the requested customer
            session = ChatSession.objects.get(id=session_id, user=user, initial_customer=customer)
        else:
            # Create a new session for the user and the requested customer
            session = ChatSession.objects.create(user=user, initial_customer=customer)
    except ChatSession.DoesNotExist:
        return Response({"error": "Invalid session ID, access denied, or session initial customer mismatch."}, status=403)

    # Create User Message associated with the session AND the specific customer context of this query
    user_message = ChatMessage.objects.create(
        session=session,
        sender="user",
        message=question,
        provider=provider,
        customer=customer
    )

    # --- Call the RAG logic and Handle Potential Errors ---
    raw_response = None # Initialize to None
    try:
        # Assume answer_query returns the tuple structure: (complex_dict_like_message, list_of_sources)
        raw_response = answer_query(
            query=question,
            customer_id=customer_id,
            tag_id=tag_id,
            provider=provider,
            temperature=temperature,
            top_p=top_p,
            max_token=max_token
        )

        # --- Extract Information from the Raw Response (Tuple) ---
        # raw_response is expected to be a tuple: (message_structure_dict, sources_list)
        if not isinstance(raw_response, tuple) or len(raw_response) < 2:
             # Handle if it's just the message structure dict (unlikely based on your output)
             if isinstance(raw_response, dict) and 'messages' in raw_response:
                 message_structure_dict = raw_response
                 sources_list = [] # Initialize empty list
                 print("Warning: answer_query returned a single dict, not a tuple. Sources might be missing.")
             else:
                 # It's an unexpected structure
                 return Response({"error": "Unexpected response format from RAG backend (not a tuple with at least 2 elements or a single dict with messages)."}, status=500)
        else:
            # It's the expected tuple (message_structure_dict, sources_list)
            message_structure_dict = raw_response[0]
            sources_list = raw_response[1] # This should be the ["Source: ...", ...] list

        # --- Navigate the message_structure_dict to find content and metadata ---
        # Based on your example: message_structure_dict['messages'][0][0][1] is the content string
        # message_structure_dict['messages'][0][2][1] is the metadata dict
        answer_text = "Could not extract answer text." # Default fallback
        metadata = {} # Default fallback

        answer_text = message_structure_dict.messages[0].content
        metadata = message_structure_dict.messages[0].response_metadata
        usage_metadata = message_structure_dict.messages[0].usage_metadata

        # Extract specific metadata fields from the extracted metadata dictionary
        model_used = metadata.get('model_name', metadata.get('model', 'Unknown'))
        total_duration_ns = metadata.get('total_duration', 0) # Duration in nanoseconds
        # Usage metadata is nested inside the main metadata dict in your example
        prompt_tokens = usage_metadata.get('input_tokens', 0)
        completion_tokens = usage_metadata.get('output_tokens', 0)
        total_tokens = usage_metadata.get('total_tokens', 0)
        eval_count = metadata.get('eval_count', 0) # Number of tokens generated
        prompt_eval_count = metadata.get('prompt_eval_count', 0) # Number of prompt tokens processed

        # Convert duration from nanoseconds to milliseconds for easier reading
        total_duration_sec = float((total_duration_ns / 1_000_000 if total_duration_ns else 0) * 100)

        # sources_list is already the list you provided: ["Source: ...", ...]

        # --- Create AI Message associated with the session ---
        ai_message = ChatMessage.objects.create(
            session=session,
            sender="ai",
            message=answer_text, # Save the extracted text
            provider=provider,
            customer=customer
        )

        # --- Prepare the Response for the Frontend ---
        formatted_response = {
            "session_id": session.id,
            "answer": answer_text, # The clean answer text
            "sources": sources_list, # The list of sources
            "metadata": {
                "model": model_used,
                "total_duration_sec": round(total_duration_sec, 2), # Rounded to 2 decimal places
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "eval_count": eval_count, # Often same as completion_tokens
                "prompt_eval_count": prompt_eval_count # Often same as prompt_tokens
            }
        }

        return Response(formatted_response)

    except Exception as e:
        import logging
        logging.error(f"Error in answer_query or response parsing: {e}", exc_info=True)
        logging.error(f"Raw response at time of error: {raw_response}")
        return Response({"error": "An error occurred while processing your request."}, status=500)
