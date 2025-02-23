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
BASE_URL = "http://api.nessieisreal.com"

# Load the trained Isolation Forest model
with open("isolation_forest_model.pkl", "rb") as model_file:
    iso_forest = pickle.load(model_file)

# Define feature names used in the model
features_for_model = ['amount', 'merchant_category', 'merchant_type',
    'num_transactions_last_hour', 'total_spent_last_hour']

# Category and Type Mapping
category_mapping = {
    'Restaurant': ['fast_food', 'premium', 'casual'],
    'Entertainment': ['gaming', 'events', 'streaming'],
    'Grocery': ['physical', 'online'],
    'Gas': ['major', 'local'],
    'Healthcare': ['medical', 'pharmacy'],
    'Education': ['online', 'supplies'],
    'Travel': ['hotels', 'airlines', 'booking', 'transport'],
    'Retail': ['online', 'physical']
}

# Streamlit App Title
st.title("💰 FinTech Dashboard: Customer, Account & Purchase Simulation")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", [
                        "Create Customer", "Create Account", "Create Merchant", "Simulate Purchase"])

# Store transaction history
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

# -----------------------------------
# 🚀 Create a New Customer
# -----------------------------------
if page == "Create Customer":
    st.header("Create a New Customer")
    first_name = st.text_input(
        "First Name", placeholder="e.g., John", value="string")
    last_name = st.text_input(
        "Last Name", placeholder="e.g., Doe", value="string")
    state = st.text_input("State", placeholder="e.g., NY")
    zip_code = st.text_input("ZIP Code", placeholder="e.g., 10001")

    if st.button("Create Customer"):
        url = f"{BASE_URL}/customers?key={API_KEY}"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "address": {
                "street_number": "string",
                "street_name": "string",
                "city": "string",
                "state": state,
                "zip": zip_code
            }
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            customer_id = response.json()["objectCreated"]["_id"]
            st.session_state.last_created_customer_id = customer_id
            st.success(f"✅ Customer Created Successfully! ID: {customer_id}")
        else:
            st.error("❌ Error Creating Customer")
            st.write(response.text)

# -----------------------------------
# 💳 Create a New Account
# -----------------------------------
if page == "Create Account":
    st.header("Create a New Account")
    if "last_created_customer_id" not in st.session_state:
        st.session_state.last_created_customer_id = ""
    customer_id = st.text_input(
        "Customer ID", value=st.session_state.last_created_customer_id)
    balance = st.number_input("Initial Balance", min_value=0.0, step=10.0)

    if st.button("Create Account"):
        url = f"{BASE_URL}/customers/{customer_id}/accounts?key={API_KEY}"
        payload = {
            "type": "Credit Card",
            "nickname": "string",
            "rewards": 0,
            "balance": balance
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            account_id = response.json()["objectCreated"]["_id"]
            st.session_state.last_created_account_id = account_id
            st.success(
                f"✅ Account Created Successfully! **Account ID: {account_id}**")
            st.code(account_id, language="plaintext")
        else:
            st.error(f"❌ Error Creating Account: {response.text}")

# -----------------------------------
# 🏬 Create a New Merchant
# -----------------------------------
if page == "Create Merchant":
    st.header("Create a New Merchant")
    merchant_name = st.text_input(
        "Merchant Name", placeholder="e.g., Starbucks", value="string")
    category = st.selectbox("Category", list(category_mapping.keys()))
    merchant_type = st.selectbox("Merchant Type", category_mapping[category])
    state = st.text_input("State", placeholder="e.g., GA")
    zip_code = st.text_input("ZIP Code", placeholder="e.g., 10001")

    if st.button("Create Merchant"):
        url = f"{BASE_URL}/merchants?key={API_KEY}"
        payload = {
            "name": merchant_name,
            "category": category,
            "address": {
                "street_number": "string",
                "street_name": "string",
                "city": "string",
                "state": state,
                "zip": zip_code
            },
            "geocode": {"lat": 0, "lng": 0}
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            merchant_id = response.json()["objectCreated"]["_id"]
            st.session_state.last_created_merchant_id = merchant_id
            st.success(
                f"✅ Merchant Created Successfully! **Merchant ID: {merchant_id}**")
            st.code(merchant_id, language="plaintext")
        else:
            st.error(f"❌ Error Creating Merchant: {response.text}")


# -----------------------------------
# 🚀 Simulate a Purchase
# -----------------------------------
elif page == "Simulate Purchase":
    st.header("Simulate a Purchase")

    # Initialize session state variables for IDs if not present
    if "last_created_account_id" not in st.session_state:
        st.session_state.last_created_account_id = ""
    if "last_created_merchant_id" not in st.session_state:
        st.session_state.last_created_merchant_id = ""

    # Display available IDs
    st.write("### Available IDs for Easy Copy")
    if st.session_state.last_created_account_id:
        st.code(st.session_state.last_created_account_id, language="plaintext")
    else:
        st.warning("No Account ID available. Please create an account first.")
    if st.session_state.last_created_merchant_id:
        st.code(st.session_state.last_created_merchant_id, language="plaintext")
    else:
        st.warning("No Merchant ID available. Please create a merchant first.")

    # Capture purchase details using a form
    with st.form("purchase_form"):
        account_id = st.text_input("Account ID", value=st.session_state.last_created_account_id)
        merchant_id = st.text_input("Merchant ID", value=st.session_state.last_created_merchant_id)
        amount = st.number_input("Purchase Amount", min_value=1.0, step=5.0)
        cat_options = list(category_mapping.keys())
        selected_cat = st.selectbox("Merchant Category", cat_options)
        selected_type = st.selectbox("Merchant Type", category_mapping[selected_cat])
        num_transactions_last_hour = st.number_input("Transactions in Last Hour", min_value=0, step=1)
        total_spent_last_hour = st.number_input("Total Spent in Last Hour", min_value=0.0, step=10.0)
        description = st.text_input("Purchase Description", placeholder="e.g., Coffee at Starbucks")
        purchase_date = datetime.today().strftime('%Y-%m-%d')
        submitted = st.form_submit_button("Simulate Purchase")

    if submitted:
        if not account_id.strip() or not merchant_id.strip():
            st.error("❌ Account ID and Merchant ID are required!")
        else:
            # Prepare transaction data for anomaly detection
            transaction_data = {
                "amount": amount,
                "merchant_category": cat_options.index(selected_cat),
                "merchant_type": category_mapping[selected_cat].index(selected_type),
                "num_transactions_last_hour": num_transactions_last_hour,
                "total_spent_last_hour": total_spent_last_hour
            }
            anomaly_score = iso_forest.predict(pd.DataFrame([transaction_data]))[0]

            # For very low-value transactions, ignore anomalies
            if amount < 5:
                anomaly_score = 1

            if anomaly_score == -1:
                # Suspicious transaction: calculate risk and prompt confirmation
                risk_score = min(60 + (amount / 10), 100)
                st.warning(f"⚠️ Suspicious activity detected! Risk Score: {round(risk_score, 2)}")
                # Save details for later confirmation
                st.session_state.purchase_data = {
                    "account_id": account_id,
                    "merchant_id": merchant_id,
                    "amount": amount,
                    "selected_cat": selected_cat,
                    "selected_type": selected_type,
                    "num_transactions_last_hour": num_transactions_last_hour,
                    "total_spent_last_hour": total_spent_last_hour,
                    "description": description,
                    "purchase_date": purchase_date,
                    "risk_score": risk_score,
                    "anomaly_score": anomaly_score
                }
            else:
                # No anomaly: automatically process purchase
                risk_score = max(10, min(30 + (amount / 50), 60))
                if "transaction_history" not in st.session_state:
                    st.session_state.transaction_history = []
                transaction_info = {
                    "Date": purchase_date,
                    "Amount": amount,
                    "Risk Score": round(risk_score, 2),
                    "Description": description
                }
                st.session_state.transaction_history.append(transaction_info)
                url = f"{BASE_URL}/accounts/{account_id}/purchases?key={API_KEY}"
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
                    st.success(f"✅ Purchase Created Successfully! Spending Security Score: {round(risk_score, 2)}")
                else:
                    st.error(f"❌ Error Creating Purchase: {response.text}")

    # Conditionally display confirmation only if an anomaly was detected
    if "purchase_data" in st.session_state:
        st.write("### Confirm Suspicious Purchase")
        col1, col2 = st.columns(2)
        if col1.button("Proceed Anyway"):
            try:
                data = st.session_state.purchase_data
                risk_score = data["risk_score"]
                if "transaction_history" not in st.session_state:
                    st.session_state.transaction_history = []
                transaction_info = {
                    "Date": data["purchase_date"],
                    "Amount": data["amount"],
                    "Risk Score": round(risk_score, 2),
                    "Description": data["description"]
                }
                st.session_state.transaction_history.append(transaction_info)
                url = f"{BASE_URL}/accounts/{data['account_id']}/purchases?key={API_KEY}"
                payload = {
                    "merchant_id": data["merchant_id"].strip(),
                    "medium": "balance",
                    "purchase_date": data["purchase_date"],
                    "amount": data["amount"],
                    "status": "pending",
                    "description": data["description"]
                }
                response = requests.post(url, json=payload)
                if response.status_code == 201:
                    st.success(f"✅ Purchase Created Successfully! Spending Security Score: {round(risk_score, 2)}")
                else:
                    st.error(f"❌ Error Creating Purchase: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Clear the purchase data to hide confirmation buttons
                del st.session_state.purchase_data

        if col2.button("Cancel Purchase"):
            st.info("🏁 Purchase simulation cancelled")
            del st.session_state.purchase_data

