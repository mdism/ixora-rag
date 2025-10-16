import streamlit as st
from components.auth import is_authenticated
from components.rag_chat import render_chat_interface

if not is_authenticated():
    st.switch_page("home.py")

st.title(" RAG Chat")

# Chat interface
render_chat_interface()