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
features_for_model = ['amount', 'merchant_category', 'merchant_type', 'num_transactions_last_hour', 'total_spent_last_hour']

# Streamlit App Title
st.title("💰 FinTech Dashboard: Customer, Account & Purchase Simulation")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Create Customer", "Create Account", "Create Merchant", "Simulate Purchase", "View Purchases", "View Spending Security Score"])

# Store transaction history
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

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

    customer_id = st.text_input("Customer ID", value=st.session_state.last_created_customer_id, placeholder="Paste Customer ID here")
    nickname = st.text_input("Account Nickname", placeholder="e.g., Savings")
    balance = st.number_input("Initial Balance", min_value=0.0, step=10.0)

    if st.button("Create Account"):
        if not customer_id.strip():
            st.error("❌ Customer ID cannot be empty!")
            st.stop()

        url = f"{BASE_URL}/customers/{customer_id}/accounts?key={API_KEY}"
        payload = {
            "type": "Credit Card",
            "nickname": nickname,
            "rewards": 0,
            "balance": balance
        }

        response = requests.post(url, json=payload)

        if response.status_code == 201:
            account_id = response.json()["objectCreated"]["_id"]
            st.session_state.last_created_account_id = account_id
            st.success(f"✅ Account Created Successfully! **Account ID: {account_id}**")
            st.code(account_id, language="plaintext")
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
            merchant_id = response.json()["objectCreated"]["_id"]
            st.session_state.last_created_merchant_id = merchant_id
            st.success(f"✅ Merchant Created Successfully! **Merchant ID: {merchant_id}**")
            st.code(merchant_id, language="plaintext")
        else:
            st.error(f"❌ Error Creating Merchant: {response.text}")



# -----------------------------------
# 🚀 Simulate a Purchase
# -----------------------------------
if page == "Simulate Purchase":
    st.header("Simulate a Purchase")
    
    # Ensure IDs persist
    if "last_created_account_id" not in st.session_state:
        st.session_state.last_created_account_id = ""
    if "last_created_merchant_id" not in st.session_state:
        st.session_state.last_created_merchant_id = ""
    
    # Display stored IDs for easy copy
    st.write("### Available IDs for Easy Copy")
    if st.session_state.last_created_account_id:
        st.write("**Last Created Account ID:**")
        st.code(st.session_state.last_created_account_id, language="plaintext")
    else:
        st.warning("No Account ID available. Please create an account first.")
    
    if st.session_state.last_created_merchant_id:
        st.write("**Last Created Merchant ID:**")
        st.code(st.session_state.last_created_merchant_id, language="plaintext")
    else:
        st.warning("No Merchant ID available. Please create a merchant first.")
    
    # User input
    account_id = st.text_input("Account ID", value=st.session_state.last_created_account_id)
    merchant_id = st.text_input("Merchant ID", value=st.session_state.last_created_merchant_id)
    amount = st.number_input("Purchase Amount", min_value=1.0, step=5.0)
    description = st.text_input("Purchase Description", placeholder="e.g., Coffee at Starbucks")
    purchase_date = datetime.today().strftime('%Y-%m-%d')
    
    if st.button("Simulate Purchase"):
        if not account_id.strip() or not merchant_id.strip():
            st.error("❌ Account ID and Merchant ID are required!")
            st.stop()
        
        # Predict spending risk using Isolation Forest
        transaction_data = {
            "amount": amount,
            "merchant_category": 0,  # Placeholder, needs mapping
            "merchant_type": 0,  # Placeholder, needs mapping
            "num_transactions_last_hour": np.random.randint(0, 50),
            "total_spent_last_hour": np.random.uniform(10, 20000)
        }
        anomaly_score = iso_forest.predict(pd.DataFrame([transaction_data]))[0]
        
        # Calculate risk score
        amount_factor = (amount / 1000) * 30  # Scale amount influence
        risk_score = (70 if anomaly_score == -1 else 30) + amount_factor
        risk_score = min(max(risk_score, 0), 100)  # Ensure within 0-100
        
        # Store transaction in session
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
            if risk_score > 80:
                st.error("🚨 High-Risk Transaction! Consider reviewing before proceeding.")
                st.warning("🔔 ALERT: High-risk transaction detected! Please verify manually.")
            elif risk_score > 50:
                st.warning("⚠️ Medium Risk: Spending above usual patterns.")
            else:
                st.success("✅ Low Risk: Normal spending behavior.")
        else:
            st.error(f"❌ Error Creating Purchase: {response.text}")

# -----------------------------------
# 📊 View Spending Security Score
# -----------------------------------
elif page == "View Spending Security Score":
    st.header("📊 Spending Security Score Over Time")
    
    if len(st.session_state.transaction_history) > 0:
        df_history = pd.DataFrame(st.session_state.transaction_history)
        df_history = df_history.sort_values(by="Date")
        
        # Plot risk score trend
        fig, ax = plt.subplots()
        ax.plot(df_history["Date"], df_history["Risk Score"], marker='o', linestyle='-', color='red')
        ax.set_title("Spending Security Score Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Risk Score (0-100)")
        ax.grid()
        st.pyplot(fig)
        
        # Display latest transactions
        st.write("### Recent Transactions & Risk Scores")
        st.dataframe(df_history.sort_values(by="Date", ascending=False))
    else:
        st.warning("No transactions available. Simulate purchases to see the Spending Security Score trend.")
