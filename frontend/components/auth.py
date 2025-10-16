import streamlit as st
from components.api_client import API_CLIENT

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)


def login_page():
    """Render login page"""
    st.title("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username", value='mdism')
        password = st.text_input("Password", type="password", value='Info@1234')
        submitted = st.form_submit_button("Login")

        if submitted:
            api_client = st.session_state.api_client # Get the initialized client
            result = api_client.login(username, password)
            if result and "access-token" in result: # Check for successful login response format from your API
                st.session_state["authenticated"] = True
                st.session_state["access_token"] = result["access-token"] # Store token
                st.session_state["refresh_token"] = result.get("refresh-token") # Store refresh token if needed

                # Fetch user profile details after login
                profile_data = api_client.get_user_profile()
                if profile_data:
                    st.session_state["user_info"] = profile_data.get("user", {})
                    st.session_state["user_teams"] = profile_data.get("teams", [])
                    st.session_state["user_roles"] = profile_data.get("roles", [])
                    st.session_state["user_customers"] = profile_data.get("customers", [])
                    st.session_state["user_documents"] = profile_data.get("documents", [])
                    # Add other profile sections as needed

                st.rerun()
            else:
                st.error("Invalid credentials or login failed")


def register_page():
    """Render registration page (optional, can be a separate page or modal)"""
    st.title("📝 Register")
    with st.form("register_form"):
        username = st.text_input("Username")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                api_client = st.session_state.api_client
                result = api_client.register(username, first_name, last_name, email, password)
                if result: # Check if registration was successful based on your API
                    st.success("Registration successful! Please log in.")
                    # Optionally switch to login page
                    # st.switch_page("home.py") # This might not work as expected in this context
                    # Instead, just show success and let user click login again or auto-redirect after delay
                    # time.sleep(2)
                    # st.rerun()
                else:
                    st.error("Registration failed")

def logout():
    """Logout user"""
    st.session_state["authenticated"] = False
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("user_info", None)
    st.rerun()

# Optional: Add a registration link on the login page
# st.page_link("pages/0_Register.py", label="Don't have an account? Register here") # If you make a separate register page