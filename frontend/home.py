import streamlit as st
from components.auth import login_page, is_authenticated, logout, register_page
from components.sidebar import render_sidebar
from components.api_client import API_CLIENT


def main():
    st.set_page_config(
        page_title="IXORA Chat App",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize API client
    if "api_client" not in st.session_state:
        st.session_state.api_client = API_CLIENT(base_url=st.secrets.get("API_BASE_URL", "http://localhost:8000"))
        
    # Check authentication
    if not is_authenticated():
        with st.expander('Login', expanded=True):
            login_page()

        with st.expander('Register', expanded=False):
            register_page()
        return
    
    # if is_authenticated():
    #     logout()

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("Welcome to RAG Chat App")
    st.markdown("""
    This application provides:
    - Secure file uploads
    - Customer & Project management
    - RAG-powered chatbot
    """)

    # Optional: Display user info from session state (populated during login)
    if "user_info" in st.session_state:
        st.sidebar.write(f"**User:** {st.session_state['user_info'].get('username', 'Unknown')}")


if __name__ == "__main__":
    main()

