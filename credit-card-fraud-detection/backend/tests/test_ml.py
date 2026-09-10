import numpy as np

from app import ml


def valid_transaction() -> dict:
    return {
        "amount": 250.0,
        "hour": 14,
        "distance_from_home": 12.0,
        "merchant_risk": 0.25,
        "device_trust": 0.85,
        "international": 0,
        "velocity_24h": 2,
        "account_age_days": 600,
    }


def test_model_trains_and_loads_successfully():
    ml.train()

    assert ml.model is not None
    assert ml.anomaly_model is not None
    assert ml.scaler is not None
    assert ml.model_metrics is not None


def test_valid_transaction_produces_prediction():
    result = ml.predict(valid_transaction())

    assert result["prediction"] in {"FRAUD", "LEGITIMATE"}
    assert 0 <= result["fraud_probability"] <= 1
    assert 0 <= result["anomaly_score"] <= 1
    assert isinstance(result["reasons"], list)
    assert result["reasons"]


def test_risky_transaction_returns_risk_information():
    transaction = valid_transaction()
    transaction.update(
        amount=1800,
        merchant_risk=0.9,
        device_trust=0.1,
        distance_from_home=400,
        velocity_24h=10,
        international=1,
    )

    result = ml.predict(transaction)

    assert result["fraud_probability"] >= 0
    assert result["anomaly_score"] >= 0
    assert len(result["reasons"]) >= 4
    assert any("high" in reason.lower() for reason in result["reasons"])


def test_model_metrics_are_valid_probabilities():
    metrics = ml.metrics()

    assert set(metrics) == {"precision", "recall", "f1", "roc_auc"}
    assert all(0 <= value <= 1 for value in metrics.values())
    assert np.isfinite(list(metrics.values())).all()