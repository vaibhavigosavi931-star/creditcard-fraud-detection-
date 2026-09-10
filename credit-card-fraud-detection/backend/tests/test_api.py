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


def test_registration_returns_analyst_without_exposing_password(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/auth/register",
        json={
            "username": "new-analyst",
            "email": "new@example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "analyst"
    assert "password" not in body
    assert "password_hash" not in body


def test_registration_stores_only_a_password_hash(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register",
        json={"username": "hashed-user", "email": "hashed@example.com", "password": "secure-password"},
    )
    from app.database import get_user_by_login

    user = get_user_by_login("hashed@example.com")
    assert user["password_hash"] != "secure-password"
    assert user["password_hash"].startswith("$argon2")


def test_login_and_me_return_authenticated_user(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register",
        json={"username": "login-user", "email": "login@example.com", "password": "secure-password"},
    )

    login = unauthenticated_client.post(
        "/api/auth/login",
        json={"login": "login@example.com", "password": "secure-password"},
    )
    token = login.json()["access_token"]
    me = unauthenticated_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert me.status_code == 200
    assert me.json()["email"] == "login@example.com"
    assert me.json()["role"] == "analyst"


def test_invalid_credentials_are_rejected(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register",
        json={"username": "wrong-password", "email": "wrong@example.com", "password": "secure-password"},
    )

    response = unauthenticated_client.post(
        "/api/auth/login",
        json={"login": "wrong@example.com", "password": "incorrect-password"},
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_missing_and_invalid_tokens(unauthenticated_client):
    missing = unauthenticated_client.get("/api/transactions")
    invalid = unauthenticated_client.get(
        "/api/transactions", headers={"Authorization": "Bearer invalid-token"}
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_analyst_can_use_fraud_endpoints(client):
    assert client.get("/api/dashboard").status_code == 200
    assert client.get("/api/transactions").status_code == 200
    assert client.post("/api/predict", json=valid_transaction()).status_code == 200


def test_analyst_cannot_access_admin_model_endpoint(client):
    response = client.get("/api/admin/model")

    assert response.status_code == 403


def test_admin_can_access_admin_model_endpoint(unauthenticated_client):
    from app.auth import hash_password
    from app.database import create_user

    create_user("admin-user", "admin@example.com", hash_password("admin-password"), role="admin")
    login = unauthenticated_client.post(
        "/api/auth/login",
        json={"login": "admin@example.com", "password": "admin-password"},
    )
    token = login.json()["access_token"]

    response = unauthenticated_client.get(
        "/api/admin/model", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_endpoint_returns_model_and_database_metrics(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["total_transactions"] == 0
    assert body["fraud_transactions"] == 0
    assert body["fraud_rate"] == 0
    assert 0 <= body["avg_fraud_probability"] <= 1
    for metric in ("precision", "recall", "f1", "roc_auc"):
        assert 0 <= body[metric] <= 1


def test_predict_endpoint_returns_prediction_and_persists_transaction(client):
    response = client.post("/api/predict", json=valid_transaction())

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["fraud_probability"] <= 1
    assert body["prediction"] in {"FRAUD", "LEGITIMATE"}
    assert 0 <= body["anomaly_score"] <= 1
    assert body["reasons"]

    transactions = client.get("/api/transactions")
    assert transactions.status_code == 200
    assert len(transactions.json()) == 1
    assert transactions.json()[0]["amount"] == valid_transaction()["amount"]


def test_transactions_endpoint_returns_newest_records_first(client):
    client.post("/api/predict", json=valid_transaction())
    second = valid_transaction()
    second["amount"] = 1800
    client.post("/api/predict", json=second)

    response = client.get("/api/transactions")

    assert response.status_code == 200
    records = response.json()
    assert len(records) == 2
    assert records[0]["id"] > records[1]["id"]
    assert records[0]["amount"] == 1800


def test_predict_rejects_invalid_transaction_values(client):
    invalid = valid_transaction()
    invalid["merchant_risk"] = 2

    response = client.post("/api/predict", json=invalid)

    assert response.status_code == 422


def test_predict_rejects_missing_required_fields(client):
    invalid = valid_transaction()
    del invalid["amount"]

    response = client.post("/api/predict", json=invalid)

    assert response.status_code == 422


def test_predict_rejects_invalid_numerical_values(client):
    invalid = valid_transaction()
    invalid["amount"] = "not-a-number"

    response = client.post("/api/predict", json=invalid)

    assert response.status_code == 422


def test_predict_rejects_unexpected_out_of_range_values(client):
    invalid = valid_transaction()
    invalid["hour"] = 24

    response = client.post("/api/predict", json=invalid)

    assert response.status_code == 422