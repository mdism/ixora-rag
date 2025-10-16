import streamlit as st
from components.auth import logout

def render_sidebar():
    """Render sidebar with navigation"""
    with st.sidebar:
        st.title("🤖 RAG Chat")

        # Navigation
        st.page_link("home.py", label=" Dashboard", icon="🏠")
        st.page_link("./pages/1_Customers_Create.py", label=" Manage Customers", icon="📝")
        st.page_link("./pages/2_File_Upload.py", label=" Upload Files", icon="📁")
        st.page_link("./pages/3_Chat_Page.py", label=" Chat", icon="💬")

        # Logout button
        st.sidebar
        if st.button("🚪 Logout", type="secondary"):
            logout()