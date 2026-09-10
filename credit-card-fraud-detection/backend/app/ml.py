from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "amount", "hour", "distance_from_home", "merchant_risk",
    "device_trust", "international", "velocity_24h", "account_age_days"
]
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_transactions.csv"

model = None
anomaly_model = None
scaler = None
model_metrics = None

def train():
    global model, anomaly_model, scaler, model_metrics
    df = pd.read_csv(DATA_PATH)
    X, y = df[FEATURES], df["is_fraud"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=180, max_depth=10, class_weight="balanced", random_state=42
    )
    model.fit(X_train_s, y_train)

    probability = model.predict_proba(X_test_s)[:, 1]
    prediction = (probability >= 0.50).astype(int)
    model_metrics = {
        "precision": float(precision_score(y_test, prediction, zero_division=0)),
        "recall": float(recall_score(y_test, prediction, zero_division=0)),
        "f1": float(f1_score(y_test, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probability)),
    }

    anomaly_model = IsolationForest(
        n_estimators=150, contamination=0.08, random_state=42
    )
    anomaly_model.fit(X_train_s)

def predict(transaction):
    if model is None:
        train()

    values = pd.DataFrame([transaction])[FEATURES]
    scaled = scaler.transform(values)
    probability = float(model.predict_proba(scaled)[0, 1])
    raw = float(anomaly_model.decision_function(scaled)[0])
    anomaly_score = float(np.clip(0.5 - raw, 0, 1))

    reasons = []
    if transaction["amount"] >= 1000:
        reasons.append("Unusually high transaction amount")
    if transaction["merchant_risk"] >= 0.70:
        reasons.append("High-risk merchant")
    if transaction["device_trust"] <= 0.30:
        reasons.append("Low device trust")
    if transaction["distance_from_home"] >= 200:
        reasons.append("Large distance from normal location")
    if transaction["velocity_24h"] >= 8:
        reasons.append("High transaction velocity")
    if transaction["international"] == 1:
        reasons.append("International transaction")
    if not reasons:
        reasons.append("No major risk signal detected")

    return {
        "fraud_probability": probability,
        "prediction": "FRAUD" if probability >= 0.50 else "LEGITIMATE",
        "anomaly_score": anomaly_score,
        "reasons": reasons,
    }

def metrics():
    if model is None:
        train()
    return model_metrics
