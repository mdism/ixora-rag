import streamlit as st

def set_session_state(key, value):
    """Set session state value"""
    st.session_state[key] = value

def get_session_state(key, default=None):
    """Get session state value with default"""
    return st.session_state.get(key, default)

def clear_session_state(keys):
    """Clear specific session state keys"""
    for key in keys:
        st.session_state.pop(key, None)

def display_error(message):
    """Display error message"""
    st.error(message)

def display_success(message):
    """Display success message"""
    st.success(message)

# Add any other utility functions needed for API interaction or UI logic