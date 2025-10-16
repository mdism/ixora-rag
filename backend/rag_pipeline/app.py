import streamlit as st
import requests
import os
import json
import time
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration & Constants ---

def load_config():
    """Determines BASE_URL based on command line argument and defines API endpoints."""
    # Check for command line argument (e.g., 'streamlit run rag_ui.py 10')
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "10":
        base_url = 'http://localhost:8010/api'
    else:
        # Default to 8000 if no argument or different argument is provided
        base_url = 'http://localhost:8000/api'
    
    return {
        'BASE_URL': base_url,
        'LOGIN_API_URL': base_url + "/login/",
        'RAG_API_URL': base_url + "/rag/query/",
        'CUSTOMER_URL': base_url + "/customers/",
        'SERVICES_URL': base_url + "/tags/"
    }

# Load the configuration once
CONFIG = load_config()

# Set Streamlit page configuration
st.set_page_config(page_title="RAG Query UI", layout="wide")
st.title("📚 RAG Query Interface")
# st.subheader(f"API Base URL: `{CONFIG['BASE_URL']}`")
st.markdown("---")

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None


# --- Utility Functions (Time and Data Extraction) ---

def format_time_str(seconds):
    """Formats seconds into a human-readable string (e.g., '1 min 30.50 sec')."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes} min {seconds:.2f} sec"

# def extract_rag_content(data):
#     """Safely extracts the main content and sources from the nested RAG response structure."""
#     answer_data = data.get("answer", {})
#     answer_list = answer_data.get("content", [])
    
#     content = answer_list

#     # for item in answer_list:
#     #     if isinstance(item, list) and len(item) == 2 and item[0] == "content":
#     #         content = item[1]
#     #         break
            
#     sources = answer_data["source"]
#     return content, sources

def extract_rag_content(data):
    answer_data = data.get("answer", {})
    answer_list = data.get("answer", {})[0].get('messages',{})
    
    # res.answer[0].messages[0]

    content = None
    for item in answer_list[0]:
        if isinstance(item, list) and len(item) >= 2 and item[0] == "content":
            content = item[1]
            break

    sources = answer_data[1]
    return content, sources

def extract_rag_content1(data):
    """
    Safely extracts the main content and sources from the complex, nested LangChain 
    response structure (the 'answer' value).
    
    It now correctly expects data["answer"] to be a list, with the main content dict at index [0].
    """
    # 1. Access the 'answer' key, which is a list [ResultDict, SourceList]
    answer_list = data.get("answer", [])
    
    # Safety check: ensure 'answer' is a list and has at least one element
    if not isinstance(answer_list, list) or len(answer_list) == 0:
        return None, []

    # Get the complex result dictionary from the first element (index [0])
    answer_data = answer_list[0] 
    
    # The list of documents (sources) is typically extracted from the prompt/template metadata
    # or passed separately in the second index (which is [] in the no-source case).
    
    # --- Source List Check (Index 1) ---
    # We prioritize the list at index [1] if it exists and contains actual sources.
    final_sources = []
    if len(answer_list) > 1 and isinstance(answer_list[1], list) and len(answer_list[1]) > 0:
        final_sources = answer_list[1]
    
    messages = answer_data.get('messages', [])
    content = None
    sources_from_template = None

    # --- 1. Extract Content (From the first message's 'content' element) ---
    if len(messages) > 0 and isinstance(messages[0], list):
        # messages[0] is the AI message part, which is a list of [key, value] pairs
        for item in messages[0]:
            if isinstance(item, list) and len(item) >= 2 and item[0] == "content":
                content = item[1]
                break

    # --- 2. Extract Sources (From the second message's 'prompt' -> 'template' element) ---
    # This path is used if sources are embedded in the prompt template metadata
    if len(messages) > 1 and isinstance(messages[1], list):
        # messages[1] is the Human/Prompt message part
        for item in messages[1]:
            if isinstance(item, list) and len(item) >= 2 and item[0] == "prompt":
                prompt_details = item[1] 
                if isinstance(prompt_details, list):
                    for detail in prompt_details:
                        if isinstance(detail, list) and len(detail) >= 2 and detail[0] == "template":
                            sources_from_template = detail[1]
                            break
            if sources_from_template:
                break
    
    # Fallback to sources from template if the index [1] list was empty.
    if not final_sources and sources_from_template:
        # Assuming the template string for "no context" is simple text
        if "I could not find relevant information" in content or "No relevant documents were found" in sources_from_template:
            final_sources = ["No relevant documents were found."]
        elif isinstance(sources_from_template, str):
            # Attempt to parse a markdown list if sources were placed here
            lines = sources_from_template.split('\n')
            final_sources = [line.strip().replace('- ', '') for line in lines if line.strip().startswith('- ')]
    
    return content, final_sources

# --- Data Loading (with Caching) ---

@st.cache_data(ttl=3600)
def load_customers(token: str):
    """Fetches list of customers from the API, uses caching to optimize performance."""
    if not token:
        # This will be caught by the main UI flow, but good to check
        return []
        
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CONFIG['CUSTOMER_URL'], headers=headers, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        result = [{"id": customer.get('id'), 'name': customer.get('name')} 
                  for customer in data if customer.get('id') is not None and customer.get('name') is not None]
        return result
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # Propagate the need to re-authenticate by letting the main flow fail
            return []
        st.error(f"HTTP Error loading customers: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error loading customers: {e}")
    
    return []

@st.cache_data(ttl=3600)
def load_services(token: str):
    """Fetches list of services/tags from the API, uses caching to optimize performance."""
    if not token:
        return []
        
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CONFIG['SERVICES_URL'], headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        result = [{"id": tag.get('id'), 'name': tag.get('name')} 
                  for tag in data if tag.get('id') is not None and tag.get('name') is not None]
        return result
    
    except requests.exceptions.HTTPError:
        return [] # Let the main flow handle the 401
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error loading services: {e}")
    
    return []


# --- Main RAG Application UI Function ---
def main_rag_ui():
    """Displays the RAG Query interface."""

    ACCESS_TOKEN = st.session_state['access_token']
    
    # Load data with caching
    customers = load_customers(token=ACCESS_TOKEN)
    services = load_services(token=ACCESS_TOKEN)
    
    if not customers or not services:
        st.warning("Cannot proceed with query. Customer or Service data failed to load. Check API connectivity or if your token expired.")
        # If loading failed, especially due to 401, force logout and rerun
        if not customers and not services:
             # Check if we were logged in but data failed to load (likely 401)
            try:
                # Try to force a re-fetch to see if the 401 triggers the rerun
                requests.get(CONFIG['CUSTOMER_URL'], headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, timeout=5).raise_for_status()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    st.error("Access Token expired or invalid. Please log in again.")
                    st.session_state['authenticated'] = False
                    st.session_state['access_token'] = None
                    time.sleep(0.5)
                    st.rerun()
            except requests.exceptions.RequestException:
                pass # Ignore network errors here
        return
        
    # Create maps and options for selectboxes
    customer_map = {item["id"]: item['name'] for item in customers}
    customer_options = list(customer_map.keys())
    services_map = {item["id"]: item['name'] for item in services}
    services_options = list(services_map.keys())
    
    # Select box format functions
    def format_customer_name(id):
        return customer_map.get(id, f"ID: {id}")
    
    def format_service_name(id):
        return services_map.get(id, f"ID: {id}")
    
    # --- Input Fields ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        customer_id = st.selectbox(
            "Select **Customer**", 
            options=customer_options, 
            format_func=format_customer_name
        )

    with col2:
        tag_id = st.selectbox(
            "Select **Service**", 
            options=services_options, 
            format_func=format_service_name
        )

    with col3:
        provider = st.selectbox('Select **Provider**', ['phi3','mistral', 'llama', "gemma"])

    max_token_str_opsions = ['Small (512)', "Medium (1024)", 'Large (2048)', 'V.Large (4096)']
    with col4:
        max_token_str = st.select_slider("Response **Length**:", max_token_str_opsions, value=max_token_str_opsions[1])
        # Extract the token count from the label
        try:
            max_token = int(max_token_str.split('(')[1].split(')')[0])
        except (IndexError, ValueError):
            max_token = 1024 # Default safety fallback

    question = st.text_area(
        "Enter your **query**:", 
        "What are the main services offered by this customer, and what are the serving terms?", 
        height=100
    )
    
    # Optional advanced settings
    with st.expander("Advanced LLM Settings"):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        with col_adv1:
            chatid = st.number_input("**Chat ID**:", value=12, min_value=1, help="Unique identifier for the chat session.", step=1)
        with col_adv2:
            temperature = st.slider("**Temperature**:", min_value=0.0, max_value=1.0, value=0.5, step=0.01, help="Controls randomness. Lower is more deterministic.")
        with col_adv3:
            top_p = st.slider("**Top P** (Nucleus Sampling):", min_value=0.0, max_value=1.0, value=0.2, step=0.01, help="Controls diversity. Lower is less diverse.")


    payload = {
        "customer_id": customer_id, 
        "tag_id": tag_id, 
        "question": question, 
        "provider": provider, 
        "chatid": chatid, 
        "temperature": temperature,
        "top_p": top_p,
        "max_token": max_token 
    }

    if st.button("Ask Query", type="primary", use_container_width=True):
        if not ACCESS_TOKEN or not customer_id or not tag_id or not question:
            st.error("Missing required input. Please ensure all fields are selected/filled and you are logged in.")
            return

        # Use st.status for a better, clearer loading indicator
        with st.status("🚀 Processing query...", expanded=True) as status:
            try:
                status.update(label="1. Sending request to RAG API...", state="running")
                
                headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                }
                
                start_time = time.time()
                # Set a robust timeout, e.g., 5 minutes (300 seconds)
                response = requests.post(CONFIG['RAG_API_URL'], headers=headers, json=payload, timeout=300)
                end_time = time.time()
                
                elapsed_time_seconds = end_time - start_time
                time_str = format_time_str(elapsed_time_seconds)
                
                status.update(label=f"2. Received response in **{time_str}**...", state="running")
                
                response.raise_for_status() # Check for 4xx/5xx status codes
                
                data = response.json()
                # try:
                #     if 'message' in data.get('answer', {}).keys():
                #         content = data.get('answer', {}).get('message', 'No Data in the Responce')
                #         sources = data.get('answer', {}).get('source', ['No source in the Responce'])
                #     else:
                #         content, sources = extract_rag_content(data)
                        
                # except Exception as e:
                #     pass

                content, sources = extract_rag_content1(data)
    
                status.update(label="3. Displaying results.", state="complete")
                
                st.markdown("---")
                st.subheader("✅ Answer")
                st.info(f"Response Time: **{time_str}**")

                if content:
                    st.markdown(content, unsafe_allow_html=True)
                else:
                    st.warning("Query successful, but the RAG model returned no textual content.")
                
                # Show sources
                if sources:
                    st.markdown("### Sources")
                    for src in sources:
                        st.write(f"- {src}")
                else:
                    st.markdown("### Sources")
                    st.info("No explicit sources were returned for this query.")
                
            except requests.exceptions.HTTPError as e:
                status.update(label=f"❌ HTTP Error: {e.response.status_code}", state="error")
                if e.response.status_code == 401:
                    st.error("Authentication failed (401). Access Token invalid or expired. Please log in again.")
                    st.session_state['authenticated'] = False
                    st.session_state['access_token'] = None
                    time.sleep(1)
                    st.rerun()
                else:
                    try:
                        error_detail = e.response.json()
                        st.error(f"Error fetching response from server. Status code: {e.response.status_code}")
                        st.json(error_detail)
                    except json.JSONDecodeError:
                        st.error(f"Error fetching response from server. Status code: {e.response.status_code}. Raw response: {e.response.text[:200]}...")
                        
            except requests.exceptions.Timeout:
                status.update(label="❌ Request Timed Out (300s)", state="error")
                st.error("The request timed out. The API took too long to respond (exceeded 5 minutes).")
                
            except requests.exceptions.RequestException as e:
                status.update(label="❌ Network Error", state="error")
                st.error(f"Network Error: Could not connect to API server or unexpected connection issue: {e}")
                
            except Exception as e:
                status.update(label="❌ Unexpected Error", state="error")
                st.exception(f"An unexpected error occurred: {e}")


# --- Authentication/Login Logic ---

def login_form():
    """Displays the login form and handles authentication."""
    st.sidebar.subheader("🔒 Login")
    with st.sidebar.form("login_form"):
        # Removed hardcoded default values for security/production use
        username = st.text_input("Username", value='mdism')
        password = st.text_input("Password", type="password", value="Info@1234")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.sidebar.error("Please enter both username and password.")
                return

            try:
                st.sidebar.info("Authenticating...")
                login_response = requests.post(
                    CONFIG['LOGIN_API_URL'], 
                    data={"username": username, "password": password},
                    timeout=5
                )
                
                if login_response.status_code in (200, 201, 202):
                    token_data = login_response.json()
                    # Check for common token keys
                    access_token = token_data.get("access-token") or token_data.get("token") or token_data.get("access")

                    if access_token:
                        st.session_state['access_token'] = access_token
                        st.session_state['authenticated'] = True
                        st.sidebar.success("Login Successful!")
                        
                        # IMPORTANT: Clear the caches to load data specific to this new user/session
                        load_customers.clear()
                        load_services.clear()
                        
                        time.sleep(0.5) 
                        st.rerun()
                    else:
                        st.sidebar.error("Login successful, but 'access token' not found in response.")

                elif login_response.status_code == 400 or login_response.status_code == 401:
                    st.sidebar.error("Invalid username or password.")
                else:
                    st.sidebar.error(f"Authentication failed with status code: {login_response.status_code}")
                    st.sidebar.json(login_response.json())
                    
            except requests.exceptions.RequestException:
                st.sidebar.error("Could not connect to the authentication server.")

def logout():
    """Handles user logout."""
    load_customers.clear()
    load_services.clear()
    
    st.session_state['authenticated'] = False
    st.session_state['access_token'] = None
    st.info("Logged out successfully.")
    st.rerun()

# --- Application Control Flow ---

if st.session_state['authenticated']:
    # Display user info and logout button
    with st.sidebar:
        st.success("You are logged in.")
        token_display = st.session_state['access_token'][:15] + "..." if st.session_state['access_token'] else "N/A"
        st.markdown(f"**Token:** `{token_display}`")
        st.markdown("---")
        if st.button("Logout", type="secondary", use_container_width=True):
            logout()

    # Run the main protected UI
    main_rag_ui()
else:
    # Show the login form when not authenticated
    login_form()
    st.info("Please log in using the sidebar form to access the RAG Query UI.")
