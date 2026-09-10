from app import database


def transaction_record() -> dict:
    return {
        "amount": 125.5,
        "hour": 9,
        "distance_from_home": 8.2,
        "merchant_risk": 0.4,
        "device_trust": 0.8,
        "international": 0,
        "velocity_24h": 3,
        "account_age_days": 400,
        "fraud_probability": 0.2,
        "prediction": "LEGITIMATE",
    }


def test_database_initializes_and_creates_transactions_table(isolated_database):
    with database.get_connection() as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        ).fetchone()

    assert table[0] == "transactions"


def test_transactions_can_be_inserted_and_retrieved(isolated_database):
    transaction_id = database.insert_transaction(transaction_record())

    records = database.list_transactions()

    assert transaction_id == 1
    assert len(records) == 1
    assert records[0]["amount"] == 125.5
    assert records[0]["prediction"] == "LEGITIMATE"


def test_dashboard_statistics_are_calculated_correctly(isolated_database):
    legitimate = transaction_record()
    fraud = transaction_record()
    fraud.update(fraud_probability=0.8, prediction="FRAUD")
    database.insert_transaction(legitimate)
    database.insert_transaction(fraud)

    assert database.count_transactions() == 2
    assert database.count_fraud() == 1
    assert database.average_probability() == 0.5