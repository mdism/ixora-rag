import streamlit as st
from components.api_client import API_CLIENT # Import the API client class

def render_chat_interface():
    """Render chat interface connected to API, allowing dynamic customer/provider per query."""
    api_client = st.session_state.api_client # Get the initialized API client

    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_customer_id" not in st.session_state:
        st.session_state.current_customer_id = None # Track customer for the *current query*
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = "phi3" # Default provider

    # Fetch customers (for selection per query)
    customers = api_client.get_all_customers() or []

    # --- Session Selection (Optional, for loading history) ---
    sessions = api_client.get_my_chat_sessions() or []
    if sessions:
        session_options = {f"Session {s['id']}: {s.get('customer', 'N/A')}": s['id'] for s in sessions}
        selected_session_id = st.selectbox(
            "Load Previous Session (Optional)",
            options=[None] + list(session_options.values()),
            format_func=lambda x: "Select a session..." if x is None else next(k for k, v in session_options.items() if v == x),
            index=0 # Default to None
        )
        if selected_session_id:
            st.session_state.current_session_id = selected_session_id
            # Note: Loading history is complex with dynamic customer/provider.
            # You might load messages from the API here if needed, but the frontend state
            # might not perfectly reflect the backend's per-message customer/provider context.
            # For now, we'll focus on the dynamic query flow.
            st.info(f"Using session ID: {selected_session_id}. History not loaded dynamically.")

    # --- Customer Selection for Current Query ---
    customer_options = {c['name']: c['id'] for c in customers}
    selected_customer_id = st.selectbox(
        "Select Customer for Query",
        options=list(customer_options.values()),
        format_func=lambda x: next(k for k, v in customer_options.items() if v == x),
        index=None if st.session_state.current_customer_id not in customer_options.values() else list(customer_options.values()).index(st.session_state.current_customer_id)
    )
    if selected_customer_id:
        st.session_state.current_customer_id = selected_customer_id

    # --- Provider Selection for Current Query ---
    available_providers = ['phi3', 'mistral', 'llama', 'gemma'] # Or fetch from API if dynamic
    selected_provider = st.selectbox(
        "Select Provider for Query",
        options=available_providers,
        index=available_providers.index(st.session_state.current_provider) if st.session_state.current_provider in available_providers else 0
    )
    st.session_state.current_provider = selected_provider

    # --- Tags Selection (Optional, for RAG context if needed by backend) ---
    # Fetch tags *after* customer is potentially selected, or make it independent
    # For now, fetching all tags. Backend might filter based on customer/tag access.
    tags = api_client.get_all_tags() or []
    tag_options = {t['name']: t['id'] for t in tags}
    selected_tag_id = st.selectbox(
        "Select Tag for Query (Optional)",
        options=[None] + list(tag_options.values()),
        format_func=lambda x: "None" if x is None else next(k for k, v in tag_options.items() if v == x),
        index=0 # Default to None
    )

    # --- Display Chat History ---
    # Note: The history displayed here is *frontend* state. It might not perfectly reflect
    # the backend's session history if messages were added via different customer/providers
    # outside this specific frontend session state.
    # For a true history view, load messages from the API based on the selected session_id.
    if st.session_state.messages:
        st.subheader("Chat History")
        for message in st.session_state.messages:
            # Include context info (customer, provider) in the message display if desired
            context_info = f" (Customer: {message.get('customer_name', 'Unknown')}, Provider: {message.get('provider', 'Unknown')})"
            with st.chat_message(message["role"]):
                st.markdown(message["content"] + context_info)

    # --- Chat Input & Submission ---
    if prompt := st.chat_input("Ask about your documents..."):
        if not st.session_state.current_customer_id:
            st.error("Please select a customer before sending a message.")
            return

        # Add user message to frontend history with context
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "customer_name": next((c['name'] for c in customers if c['id'] == st.session_state.current_customer_id), "Unknown"),
            "provider": st.session_state.current_provider
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send message to API and get response using the new integrated method
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call the new integrated method in the API client

                    rag_response = api_client.send_query_and_get_response(
                        customer_id=st.session_state.current_customer_id,
                        tag_id=selected_tag_id, # Pass selected tag ID
                        question=prompt,
                        session_id=st.session_state.current_session_id, # Pass existing session ID or None
                        provider=st.session_state.current_provider # Pass selected provider
                        # Add other parameters like temperature, top_p, max_tokens if needed
                    )


                    if rag_response and 'answer' in rag_response: # Check for the new structure
                        response_text = rag_response['answer']
                        sources = rag_response.get('sources', []) # Get sources list
                        metadata = rag_response.get('metadata', {}) # Get metadata dict

                        # Display answer
                        st.markdown(response_text)

                        # Display sources (optional, maybe in an expander)
                        if sources:
                            with st.expander("Sources"):
                                for source in sources:
                                    st.write(f"- {source}")

                        # Display metadata (optional, maybe in an expander or sidebar)
                        if metadata:
                            with st.expander("Query Details"):
                                st.write(f"**Model:** {metadata.get('model', 'Unknown')}")
                                st.write(f"**Duration:** {metadata.get('total_duration_sec', 0)} sec")
                                st.write(f"**Prompt Tokens:** {metadata.get('prompt_tokens', 0)}")
                                st.write(f"**Completion Tokens:** {metadata.get('completion_tokens', 0)}")
                                st.write(f"**Total Tokens:** {metadata.get('total_tokens', 0)}")
                                st.write(f"**Eval Count:** {metadata.get('eval_count', 0)}")
                                st.write(f"**Prompt Eval Count:** {metadata.get('prompt_eval_count', 0)}")

                        # Add AI response to frontend history with context
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "customer_name": next((c['name'] for c in customers if c['id'] == st.session_state.current_customer_id), "Unknown"),
                            "provider": st.session_state.current_provider,
                            # Optionally store sources/metadata here too if needed later in the session
                            "sources": sources,
                            "metadata": metadata
                        })

                        # Update session ID if needed
                        if 'session_id' in rag_response and st.session_state.current_session_id != rag_response['session_id']:
                            st.session_state.current_session_id = rag_response['session_id']
                            st.info(f"New session started: {st.session_state.current_session_id}")

                    else:
                        st.error("Failed to get response from RAG API.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Sorry, I couldn't process your request.",
                            "customer_name": next((c['name'] for c in customers if c['id'] == st.session_state.current_customer_id), "Unknown"),
                            "provider": st.session_state.current_provider
                        })
                except Exception as e:
                    st.error(f"An error occurred while querying the API: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "An error occurred.",
                        "customer_name": next((c['name'] for c in customers if c['id'] == st.session_state.current_customer_id), "Unknown"),
                        "provider": st.session_state.current_provider
                    })
