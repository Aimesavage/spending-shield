import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import os
from django.conf import settings

# Load the trained model using absolute path
model_path = os.path.join(settings.BASE_DIR, '..', 'isolation_forest_model.pkl')
with open(model_path, "rb") as model_file:
    iso_forest = pickle.load(model_file)

def analyze_transaction(transaction_data):
    """Analyze transaction and return risk score"""
    df = pd.DataFrame([transaction_data])
    
    # Ensure feature order
    features = ['amount', 'merchant_category', 'merchant_type', 'num_transactions_last_hour', 'total_spent_last_hour']
    df = df[features]
    
    # Make prediction
    anomaly_score = iso_forest.predict(df)[0]
    
    # Calculate risk score
    amount_factor = (transaction_data['amount'] / 1000) * 30
    risk_score = (70 if anomaly_score == -1 else 30) + amount_factor
    risk_score = min(max(risk_score, 0), 100)
    
    return round(risk_score, 2)

def create_transaction_record(account_id, merchant_id, amount, description):
    """Create transaction record with risk analysis"""
    purchase_date = datetime.today().strftime('%Y-%m-%d')
    
    # Generate transaction data for analysis
    transaction_data = {
        "amount": amount,
        "merchant_category": 0,  # Placeholder, needs mapping
        "merchant_type": 0,  # Placeholder, needs mapping
        "num_transactions_last_hour": np.random.randint(0, 50),
        "total_spent_last_hour": np.random.uniform(10, 20000)
    }
    
    risk_score = analyze_transaction(transaction_data)
    
    transaction_info = {
        "Date": purchase_date,
        "Amount": amount,
        "Risk Score": risk_score,
        "Description": description,
        "account_id": account_id,
        "merchant_id": merchant_id
    }
    
    return transaction_info, risk_score