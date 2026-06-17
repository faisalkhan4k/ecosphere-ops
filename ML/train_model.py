import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import mlflow
import mlflow.xgboost
import os

def train_leak_detector():
    # 1. Start MLflow tracking (our scientist notebook)
    mlflow.set_experiment("Smart_City_Water_Management")
    
    with mlflow.start_run():
        print("Reading sensor data...")
        # Find our data file
        data_path = os.path.join(os.path.dirname(__file__), "water_sensors.csv")
        df = pd.read_csv(data_path)
        
        # 2. Split data into Features (X) and Target Label (y)
        # We drop timestamp and sector_id because XGBoost only wants raw numbers
        X = df.drop(columns=["timestamp", "sector_id", "anomaly"])
        y = df["anomaly"]
        
        # Split into training set (80%) and testing set (20%)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("Training XGBoost Anomaly Detector...")
        # 3. Initialize and train the traditional ML model
        model_params = {
            "max_depth": 5,
            "n_estimators": 50,
            "learning_rate": 0.1,
            "objective": "binary:logistic",
            "eval_metric": "logloss"
        }
        
        model = xgb.XGBClassifier(**model_params)
        model.fit(X_train, y_train)
        
        # 4. Evaluate how smart our model is
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
        print("\nClassification Report:")
        print(classification_report(y_test, predictions))
        
        # 5. Log everything to MLOps (MLflow) automatically!
        mlflow.log_params(model_params)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.xgboost.log_model(model, "model")
        
        print("\nSuccess! Model and metrics successfully logged to MLflow.")

if __name__ == "__main__":
    train_leak_detector()