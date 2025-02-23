import streamlit as st
import requests
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Load the pre-trained Isolation Forest model
with open("isolation_forest_model.pkl", "rb") as model_file:
    iso_forest = pickle.load(model_file)

# Define feature names used in the model
features_for_model = ['amount', 'merchant_category', 'merchant_type', 'num_transactions_last_hour', 'total_spent_last_hour']

# Streamlit App Title
st.title("💰 FinTech Dashboard: Customer, Account & Purchase Simulation")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Create Customer", "Create Account", "Create Merchant", "Simulate Purchase", "View Purchases"])

# -----------------------------------
# 🚀 Create a New Customer
# -----------------------------------
if page == "Create Customer":
    st.header("Create a New Customer")

    first_name = st.text_input("First Name", placeholder="e.g., John")
    last_name = st.text_input("Last Name", placeholder="e.g., Doe")

    street_number = st.text_input("Street Number", placeholder="e.g., 123")
    street_name = st.text_input("Street Name", placeholder="e.g., Main St")
    city = st.text_input("City", placeholder="e.g., New York")
    state = st.text_input("State", placeholder="e.g., NY")
    zip_code = st.text_input("ZIP Code", placeholder="e.g., 10001")

    if st.button("Create Customer"):
        url = f"{BASE_URL}/customers?key={API_KEY}"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "address": {
                "street_number": street_number,
                "street_name": street_name,
                "city": city,
                "state": state,
                "zip": zip_code
            }
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            customer_id = response.json()["objectCreated"]["_id"]
            st.success(f"✅ Customer Created Successfully! ID: {customer_id}")
        else:
            st.error("❌ Error Creating Customer")
            st.write(response.text)

# -----------------------------------
# 💳 Create a New Account
# -----------------------------------
if page == "Create Account":
    st.header("Create a New Account")

    # Store the last created Customer ID for auto-fill
    if "last_created_customer_id" not in st.session_state:
        st.session_state.last_created_customer_id = ""

    customer_id = st.text_input("Customer ID", value=st.session_state.last_created_customer_id, placeholder="Paste Customer ID here")
    nickname = st.text_input("Account Nickname", placeholder="e.g., Savings")
    balance = st.number_input("Initial Balance", min_value=0.0, step=10.0)

    if st.button("Create Account"):
        if not customer_id.strip():
            st.error("❌ Customer ID cannot be empty!")
            st.stop()

        customer_id = customer_id.strip()

        url = f"{BASE_URL}/customers/{customer_id}/accounts?key={API_KEY}"
        payload = {
            "type": "Credit Card",
            "nickname": nickname,
            "rewards": 0,
            "balance": balance
        }

        response = requests.post(url, json=payload)

        if response.status_code == 201:
            response_json = response.json()
            if "objectCreated" in response_json:
                account_id = response_json["objectCreated"]["_id"]
                st.session_state.last_created_account_id = account_id  # Store ID
                st.success(f"✅ Account Created Successfully! **Account ID: {account_id}**")
                st.code(account_id, language="plaintext")
            else:
                st.warning("Account created, but no ID found in the response.")
        else:
            st.error(f"❌ Error Creating Account: {response.text}")




# -----------------------------------
# 🏬 Create a New Merchant
# -----------------------------------

if page == "Create Merchant":
    st.header("Create a New Merchant")

    merchant_name = st.text_input("Merchant Name", placeholder="e.g., Starbucks")
    category = st.text_input("Category", placeholder="e.g., coffee_shop")

    street_number = st.text_input("Merchant Street Number", placeholder="e.g., 456")
    street_name = st.text_input("Merchant Street Name", placeholder="e.g., Market St")
    city = st.text_input("Merchant City", placeholder="e.g., San Francisco")
    state = st.text_input("Merchant State", placeholder="e.g., GA")
    zip_code = st.text_input("Merchant ZIP Code", placeholder="e.g., 94103")

    lat = st.number_input("Latitude", value=0.0)
    lng = st.number_input("Longitude", value=0.0)

    if st.button("Create Merchant"):
        url = f"{BASE_URL}/merchants?key={API_KEY}"
        payload = {
            "name": merchant_name,
            "category": category,
            "address": {
                "street_number": street_number,
                "street_name": street_name,
                "city": city,
                "state": state,
                "zip": zip_code
            },
            "geocode": {"lat": lat, "lng": lng}
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            response_json = response.json()
            if "objectCreated" in response_json:
                merchant_id = response_json["objectCreated"]["_id"]
                st.session_state.last_created_merchant_id = merchant_id  # Store ID
                st.success(f"✅ Merchant Created Successfully! **Merchant ID: {merchant_id}**")
                st.code(merchant_id, language="plaintext")
            else:
                st.warning("Merchant created, but no ID found in the response.")
        else:
            st.error(f"❌ Error Creating Merchant: {response.text}")





# -----------------------------------
# 🛒 Simulate a Purchase
# -----------------------------------
elif page == "Simulate Purchase":
    st.header("Simulate a Purchase")

    # Ensure last created IDs persist
    if "last_created_account_id" not in st.session_state:
        st.session_state.last_created_account_id = ""
    if "last_created_merchant_id" not in st.session_state:
        st.session_state.last_created_merchant_id = ""

    st.write("### Available IDs for Easy Copy")
    
    # Display last created Account ID
    if st.session_state.last_created_account_id:
        st.write("**Last Created Account ID:**")
        st.code(st.session_state.last_created_account_id, language="plaintext")
    else:
        st.warning("No Account ID available. Please create an account first.")

    # Display last created Merchant ID
    if st.session_state.last_created_merchant_id:
        st.write("**Last Created Merchant ID:**")
        st.code(st.session_state.last_created_merchant_id, language="plaintext")
    else:
        st.warning("No Merchant ID available. Please create a merchant first.")

    # Auto-fill input fields with stored values
    account_id = st.text_input("Account ID", value=st.session_state.last_created_account_id)
    merchant_id = st.text_input("Merchant ID", value=st.session_state.last_created_merchant_id)
    amount = st.number_input("Purchase Amount", min_value=1.0, step=5.0)
    description = st.text_input("Purchase Description", placeholder="e.g., Coffee at Starbucks")
    purchase_date = datetime.today().strftime('%Y-%m-%d')

    if st.button("Simulate Purchase"):
        if not account_id.strip() or not merchant_id.strip():
            st.error("❌ Account ID and Merchant ID are required!")
            st.stop()

        # Debugging Output
        st.write(f"Debug: Account ID Sent `{account_id.strip()}`")
        st.write(f"Debug: Merchant ID Sent `{merchant_id.strip()}`")

        url = f"{BASE_URL}/accounts/{account_id.strip()}/purchases?key={API_KEY}"
        payload = {
            "merchant_id": merchant_id.strip(),
            "medium": "balance",
            "purchase_date": purchase_date,
            "amount": amount,
            "status": "pending",
            "description": description
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            st.success("✅ Purchase Created Successfully!")
            st.write(response.json())
        else:
            st.error(f"❌ Error Creating Purchase: {response.text}")




# -----------------------------------
# 🔍 View Purchases & Detect Overspending
# -----------------------------------
elif page == "View Purchases":
    st.header("View Purchases & Detect Overspending")

    account_id = st.text_input("Enter Account ID to View Purchases", placeholder="Paste Account ID here")

    if st.button("Fetch Purchases"):
        url = f"{BASE_URL}/accounts/{account_id}/purchases?key={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            transactions = response.json()

            if not transactions:
                st.warning("No transactions found for this account.")
            else:
                df = pd.DataFrame(transactions)

                # Simulated placeholders for missing features
                df['merchant_category'] = 0  
                df['merchant_type'] = 0  
                df['num_transactions_last_hour'] = np.random.randint(0, 50, len(df))
                df['total_spent_last_hour'] = np.random.uniform(10, 20000, len(df))

                # Predict overspending
                df['overspending_flag'] = iso_forest.predict(df[features_for_model])
                df['overspending_flag'] = df['overspending_flag'].apply(lambda x: 1 if x == -1 else 0)

                st.write("### Transactions")
                st.dataframe(df)

                flagged = df[df['overspending_flag'] == 1]
                if not flagged.empty:
                    st.error("🚨 Overspending Alert! These transactions were flagged:")
                    st.dataframe(flagged)
                else:
                    st.success("✅ No overspending detected.")
