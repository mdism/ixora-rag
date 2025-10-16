import streamlit as st
from components.auth import is_authenticated
from components.api_client import API_CLIENT

if not is_authenticated():
    st.switch_page("home.py")

st.title(" Upload Documents")

api_client = st.session_state.api_client

# Fetch customers and tags to associate with the document
customers = api_client.get_all_customers() or []
tags = api_client.get_all_tags() or []

customer_options = {c['name']: c['id'] for c in customers}
tag_options = {t['name']: t['id'] for t in tags}

selected_customer_id = st.selectbox("Select Customer", options=list(customer_options.values()), format_func=lambda x: next(k for k, v in customer_options.items() if v == x))
selected_tag_id = st.selectbox("Select Tag (optional)", options=[None] + list(tag_options.values()), format_func=lambda x: "None" if x is None else next(k for k, v in tag_options.items() if v == x))
# selected_tag_id = st.selectbox("Select Tag (optional)", list(tag_options.values()), format_func=lambda x: "Infra" if x is None else next(k for k, v in tag_options.items() if v == x))

uploaded_file = st.file_uploader("Choose a file", 
                                 type=['pdf',
                                       'docx',
                                       'xlsx/xls', 
                                       'csv', 
                                       'txt/.log', 
                                       '.md',
                                       'E-mails (.eml)',
                                       'EPubs (.epub)'])

if uploaded_file and selected_customer_id:
    if st.button("Upload Document"):
        with st.spinner("Uploading..."):
            result = api_client.upload_document(
                file=uploaded_file,
                customer_id=selected_customer_id,
                tag_id= '1' if selected_tag_id == None else selected_tag_id,
                file_name=uploaded_file.name
            )
            if result:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")