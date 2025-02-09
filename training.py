import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
import sys

# Load CSV file
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    
    # Drop specified columns if they exist
    df = df.drop(columns=['address', 'defi_staking'], axis=1, errors='ignore')
    df = df[df["balance"] > 0]
    return df

# Train anomaly detection models
def train_models(data):
    models = {
        "isolation_forest": IsolationForest(n_estimators=100, contamination=0.1, random_state=42),
        "local_outlier_factor": LocalOutlierFactor(n_neighbors=20, contamination=0.1, novelty=True),
        "one_class_svm": OneClassSVM(nu=0.1, kernel="rbf", gamma="scale")
    }
    
    trained_models = {}
    
    for name, model in models.items():
        model.fit(data)
        trained_models[name] = model
        joblib.dump(model, f"{name}.pkl")  # Save the model
    
    return trained_models

if __name__ == "__main__":
    csv_file = "wallet_analysis.csv"
    df = load_data(csv_file)
    
    # Ensure the dataset contains only numerical values
    df = df.select_dtypes(include=["number"]).dropna()
    
    # Train and save models
    train_models(df)
    
    
    print("Models saved successfully!")