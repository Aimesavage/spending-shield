import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle

# Create synthetic data for initial model
np.random.seed(42)
n_samples = 1000

data = {
    'amount': np.random.uniform(10, 5000, n_samples),
    'merchant_category': np.random.randint(0, 10, n_samples),
    'merchant_type': np.random.randint(0, 5, n_samples),
    'num_transactions_last_hour': np.random.randint(0, 50, n_samples),
    'total_spent_last_hour': np.random.uniform(10, 20000, n_samples)
}

df = pd.DataFrame(data)

# Train Isolation Forest model
features_for_model = ['amount', 'merchant_category', 'merchant_type', 'num_transactions_last_hour', 'total_spent_last_hour']
iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
iso_forest.fit(df[features_for_model])

# Save the model
with open("isolation_forest_model.pkl", "wb") as model_file:
    pickle.dump(iso_forest, model_file) 