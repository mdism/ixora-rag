import streamlit as st
import pandas as pd
from components.auth import is_authenticated
from components.api_client import API_CLIENT

if not is_authenticated():
    st.switch_page("home.py")

st.title(" Manage Customers")

api_client = st.session_state.api_client

# Fetch existing customers
customers = api_client.get_all_customers()

if customers:
    st.subheader("Existing Customers")

    # Prepare data for the DataFrame
    # Flatten the 'teams' list into a string for display in the table
    df_data = []
    for customer in customers:
        # Join team names with a separator (e.g., ', ')
        teams_str = ', '.join(customer.get('teams', [])) if customer.get('teams') else 'None'
        df_data.append({
            'ID': customer['id'],
            'Name': customer['name'],
            'Contact': customer['contact'],
            'Description': customer['description'],
            'Created At': customer['created_at'],
            'Updated At': customer['updated_at'],
            'Teams': teams_str # Flattened teams list
        })

    # Create the DataFrame
    df = pd.DataFrame(df_data)

    # Optional: Format datetime columns if needed (depends on API format)
    df['Created At'] = pd.to_datetime(df['Created At'])
    df['Updated At'] = pd.to_datetime(df['Updated At'])

    # Display the DataFrame as an interactive table
    # You can sort by clicking headers
    st.dataframe(df, width='stretch', hide_index=True)

    # Optional: Add a simple non-interactive table if you prefer
    # st.table(df)

else:
    st.info("No customers found. Create one below.")

# Create new customer
with st.expander('Add Customer', expanded=False): 
    with st.form("create_customer_form"):
        name = st.text_input("Customer Name")
        contact = st.text_input("Contact Email/Info")
        description = st.text_area("Description (optional)")
        
        # Fetch teams for association (optional)
        # Make sure you have added get_all_teams to your API_CLIENT
        teams = api_client.get_all_teams() or []
        team_options = {t['name']: t['id'] for t in teams}
        selected_team_ids = st.multiselect(
            "Associate with Teams (optional)",
            options=list(team_options.values()),
            format_func=lambda x: next(k for k, v in team_options.items() if v == x)
        )

        submitted = st.form_submit_button("Create Customer", type="primary")

        if submitted and name and contact:
            # Pass the selected team IDs to the API call
            result = api_client.create_customer(
                name=name,
                contact=contact,
                description=description,
                team_ids=selected_team_ids # Pass the list of team IDs
            )
            if result:
                st.rerun() # Refresh to show the new customer
        elif submitted:
            if not name:
                st.error("Customer name is required.")
            if not contact:
                st.error("Contact information is required.")

