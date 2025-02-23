from fastapi import FastAPI
import pickle
import pandas as pd

# Load the trained model
with open("isolation_forest_model.pkl", "rb") as model_file:
    iso_forest = pickle.load(model_file)

app = FastAPI()

@app.post("/predict/")
def predict(transaction: dict):
    # Convert the transaction to DataFrame
    df = pd.DataFrame([transaction])
    
    # Ensure feature order
    features = ['amount', 'merchant_category', 'merchant_type', 'num_transactions_last_hour', 'total_spent_last_hour']
    df = df[features]

    # Make prediction
    prediction = iso_forest.predict(df)[0]
    
    # Convert model output
    result = {"overspending_flag": 1 if prediction == -1 else 0}
    
    return result
