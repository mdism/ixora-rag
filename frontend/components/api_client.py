import requests
import streamlit as st

class API_CLIENT:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session() # Use a session to reuse connections

    def _get_auth_headers(self):
        """Helper to get headers with access token"""
        token = st.session_state.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _handle_response(self, response, success_message=None):
        """Helper to handle API response"""
        if response.status_code in [200, 201, 202, 204]:
            if success_message:
                st.success(success_message)
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                # Some endpoints might return empty body on success
                return {}
        else:
            try:
                error_data = response.json()
                st.error(f"API Error: {error_data}")
                return None
            except requests.exceptions.JSONDecodeError:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None

    # --- Authentication Endpoints ---
    def login(self, username, password):
        url = f"{self.base_url}/api/login/"
        payload = {"username": username, "password": password}
        response = self.session.post(url, json=payload)
        return self._handle_response(response)

    def register(self, username, first_name, last_name, email, password):
        url = f"{self.base_url}/api/register/"
        payload = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        }
        response = self.session.post(url, json=payload)
        return self._handle_response(response)

    # --- User Endpoints ---
    def get_user_info(self, user_id):
        url = f"{self.base_url}/api/users/{user_id}/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def get_all_users(self):
        url = f"{self.base_url}/api/users/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    # --- NEW: User Profile Endpoint ---
    def get_user_profile(self):
        url = f"{self.base_url}/api/me/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    # --- Team Endpoints ---
    def get_all_teams(self):
        url = f"{self.base_url}/api/teams/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def get_all_teams(self):
        url = f"{self.base_url}/api/teams/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    # --- Customer Endpoints ---
    def get_all_customers(self):
        url = f"{self.base_url}/api/customers/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def create_customer(self, name, contact, description="", team_ids=None):
        url = f"{self.base_url}/api/customers/"
        headers = self._get_auth_headers()
        payload = {
            "name": name,
            "contact": contact,
            "description": description,
            "teams_ids": team_ids or [] # Default to empty list if no teams
        }
        response = self.session.post(url, headers=headers, json=payload)
        return self._handle_response(response, f"Customer '{name}' created successfully!")

    # --- Document Endpoints ---
    def get_my_documents(self):
        url = f"{self.base_url}/api/documents/my-documents/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def upload_document(self, file, customer_id, tag_id=None, file_name=None):
        url = f"{self.base_url}/api/documents/"
        headers = self._get_auth_headers() # Note: For file upload, might need multipart, check backend
        # For multipart form data
        files = {'file': (file_name or file.name, file.getvalue(), file.type)}
        data = {'customer': customer_id}
        if tag_id:
            data['tag'] = tag_id
        # If backend expects file_name as a field too
        # data['file_name'] = file_name or file.name

        response = self.session.post(url, headers=headers, files=files, data=data)
        return self._handle_response(response, f"Document '{file.name}' uploaded successfully!")


    # --- Tag Endpoints ---
    def get_all_tags(self):
        url = f"{self.base_url}/api/tags/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)


    # --- Chat Session Endpoints ---
    def get_my_chat_sessions(self):
        url = f"{self.base_url}/api/chat-sessions/my-sessions/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def create_chat_session(self, customer_id, tag_id=None):
        url = f"{self.base_url}/api/chat-sessions/"
        headers = self._get_auth_headers()
        payload = {"customer": customer_id}
        if tag_id:
            payload["tag"] = tag_id
        response = self.session.post(url, headers=headers, json=payload)
        return self._handle_response(response, "Chat session created successfully!")

    # --- Chat Message Endpoints ---
    def get_chat_messages(self, session_id):
        url = f"{self.base_url}/api/chat-messages/?session={session_id}"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def send_chat_message(self, session_id, message_text):
        url = f"{self.base_url}/api/chat-messages/"
        headers = self._get_auth_headers()
        payload = {"session": session_id, "sender": "user", "message": message_text}
        response = self.session.post(url, headers=headers, json=payload)
        return self._handle_response(response)

    # --- RAG Query Endpoint ---
    def query_rag(self, customer_id, tag_id, question, session_id, provider="llama", temperature=0.5, top_p=0.5, max_tokens=512):
        url = f"{self.base_url}/api/rag/query/"
        headers = self._get_auth_headers()
        payload = {
            "customer_id": customer_id,
            "tag_id": tag_id,
            "question": question,
            "provider": provider,
            "chatid": session_id, # Assuming chatid refers to session_id
            "temprature": temperature, # Note: typo in API endpoint name
            "top_p": top_p,
            "max_token": max_tokens
        }
        response = self.session.post(url, headers=headers, json=payload)
        return self._handle_response(response)
        # Note: This synchronous call might not be ideal for streaming responses.
        # For streaming, you'd need a different endpoint or handle it differently in Streamlit.

    # --- NEW: Integrated Chat & RAG Logic ---
    def send_query_and_get_response(self, customer_id, tag_id, question, session_id, provider="llama", temperature=0.5, top_p=0.5, max_tokens=512):
        """
        Sends a user query to the RAG API and returns the response.
        Handles the full interaction: sending the query and receiving the AI answer.
        This method centralizes the logic previously in the Streamlit component.
        """
        # Call the existing query_rag method
        response_data = self.query_rag(
            customer_id=customer_id,
            tag_id=tag_id,
            question=question,
            session_id=session_id,
            provider=provider,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        return response_data # Return the full response from the API (e.g., {"session_id": ..., "answer": ...})
