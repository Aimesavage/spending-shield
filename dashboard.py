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

# Load the improved model and its components
with open("improved_isolation_forest_model.pkl", "rb") as model_file:
    model_data = pickle.load(model_file)
    iso_forest = model_data['model']
    features_for_model = model_data['features']
    label_encoders = model_data['label_encoders']
    scaler = model_data['scaler']

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
page = st.sidebar.radio("Navigation", ["Create Customer", "Create Account", "Create Merchant", "Simulate Purchase"])

# Store transaction history
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

# -----------------------------------
# Create a New Customer
# -----------------------------------
if page == "Create Customer":
    st.header("Create a New Customer")
    first_name = st.text_input("First Name", placeholder="e.g., John", value="string")
    last_name = st.text_input("Last Name", placeholder="e.g., Doe", value="string")
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
# Create a New Account
# -----------------------------------
if page == "Create Account":
    st.header("Create a New Account")
    if "last_created_customer_id" not in st.session_state:
        st.session_state.last_created_customer_id = ""
    customer_id = st.text_input("Customer ID", value=st.session_state.last_created_customer_id)
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
            st.success(f"✅ Account Created Successfully! **Account ID: {account_id}**")
            st.code(account_id, language="plaintext")
        else:
            st.error(f"❌ Error Creating Account: {response.text}")

# -----------------------------------
# Create a New Merchant
# -----------------------------------
if page == "Create Merchant":
    st.header("Create a New Merchant")
    merchant_name = st.text_input("Merchant Name", placeholder="e.g., Starbucks", value="string")
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
            st.success(f"✅ Merchant Created Successfully! **Merchant ID: {merchant_id}**")
            st.code(merchant_id, language="plaintext")
        else:
            st.error(f"❌ Error Creating Merchant: {response.text}")

# -----------------------------------
# 🚀 Simulate a Purchase
# -----------------------------------
elif page == "Simulate Purchase":
    st.header("Simulate a Purchase")
    
    if "last_created_account_id" not in st.session_state:
        st.session_state.last_created_account_id = ""
    if "last_created_merchant_id" not in st.session_state:
        st.session_state.last_created_merchant_id = ""



    account_id = st.text_input("Account ID", value=st.session_state.last_created_account_id)
    merchant_id = st.text_input("Merchant ID", value=st.session_state.last_created_merchant_id)
    amount = st.number_input("Purchase Amount", min_value=1.0, step=5.0)
    
    cat_options = list(category_mapping.keys())
    selected_cat = st.selectbox("Merchant Category", cat_options)
    selected_type = st.selectbox("Merchant Type", category_mapping[selected_cat])
    
    # New fields for improved model
    num_transactions_last_hour = st.number_input("Transactions in Last Hour", min_value=0, step=1)
    total_spent_last_hour = st.number_input("Total Spent in Last Hour", min_value=0.0, step=10.0)
    distance_from_home = st.slider("Distance from Home (normalized)", 0.0, 1.0, 0.1)
    transaction_hour = st.number_input("Hour of Day (0-23)", min_value=0, max_value=23, value=datetime.now().hour)
    
    description = st.text_input("Purchase Description", placeholder="e.g., Coffee at Starbucks")
    purchase_date = datetime.today().strftime('%Y-%m-%d')

    if st.button("Simulate Purchase"):
        if not account_id.strip() or not merchant_id.strip():
            st.error("❌ Account ID and Merchant ID are required!")
            st.stop()

        # Prepare transaction data for model
        transaction_data = {
            'amount': amount,
            'merchant_category': label_encoders['merchant_category'].transform([selected_cat])[0],
            'merchant_type': label_encoders['merchant_type'].transform([selected_type])[0],
            'num_transactions_last_hour': num_transactions_last_hour,
            'total_spent_last_hour': total_spent_last_hour,
            'amount_to_average_ratio': amount / 100,  # simplified ratio for demo
            'transaction_hour': transaction_hour,
            'is_weekend': 1 if datetime.now().weekday() >= 5 else 0,
            'distance_from_home': distance_from_home
        }

        # Create DataFrame for scaling
        numerical_features = ['amount', 'distance_from_home', 'num_transactions_last_hour', 'total_spent_last_hour', 'amount_to_average_ratio']
        numerical_data = [[transaction_data[feature] for feature in numerical_features]]
        scaled_features = scaler.transform(numerical_data)

        # Update transaction_data with scaled values
        for i, feature in enumerate(numerical_features):
            transaction_data[feature] = scaled_features[0][i]

        # Create DataFrame for prediction
        pred_df = pd.DataFrame([transaction_data])
        
        # Get model prediction
        model_prediction = iso_forest.predict(pred_df[features_for_model])[0]

        # Apply business rules
        high_risk_conditions = [
            transaction_data['amount_to_average_ratio'] > 3,
            transaction_data['distance_from_home'] > 0.8,
            transaction_data['num_transactions_last_hour'] > 5
        ]
        business_rules_flag = 1 if any(high_risk_conditions) else 0

        # Combined risk assessment
        is_risky = (model_prediction == -1) or (business_rules_flag == 1)
        
        # Calculate risk score
        if is_risky:
            risk_score = 50 + min(amount / 20, 50)
        else:
            risk_score = max(10, min(amount / 20, 50))
        risk_score = min(max(risk_score, 0), 100)

        # Store transaction info
        transaction_info = {
            "Date": purchase_date,
            "Amount": amount,
            "Risk Score": round(risk_score, 2),
            "Description": description,
            "Model Flag": "High Risk" if model_prediction == -1 else "Normal",
            "Business Rules Flag": "High Risk" if business_rules_flag == 1 else "Normal"
        }
        st.session_state.transaction_history.append(transaction_info)

        # Create purchase in API
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
            # Define colors based on risk levels
            score_color = "rgba(255, 87, 87, 0.2)" if risk_score > 50 else "rgba(87, 255, 87, 0.2)"
            model_color = "rgba(255, 87, 87, 0.2)" if model_prediction == -1 else "rgba(87, 255, 87, 0.2)"
            rules_color = "rgba(255, 87, 87, 0.2)" if business_rules_flag == 1 else "rgba(87, 255, 87, 0.2)"
            
            # Create styled boxes using HTML/CSS
            st.markdown("""
                <style>
                .risk-box {
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="risk-box" style="background-color: {score_color}">
                    ✨ Spending Security Score: {round(risk_score, 2)}
                </div>
                <div class="risk-box" style="background-color: {model_color}">
                    🤖 Model Assessment: {"High Risk" if model_prediction == -1 else "Normal"}
                </div>
                <div class="risk-box" style="background-color: {rules_color}">
                    📋 Business Rules Assessment: {"High Risk" if business_rules_flag == 1 else "Normal"}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ Error Creating Purchase: {response.text}")