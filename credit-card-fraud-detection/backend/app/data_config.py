from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DEFAULT_DATASET_PATHS = [
    DATA_DIR / "creditcard.csv",
    DATA_DIR / "credit_card_fraud.csv",
    DATA_DIR / "creditcard_fraud_dataset.csv",
    DATA_DIR / "sample_transactions.csv",
]

TARGET_COLUMN_CANDIDATES = (
    "Class",
    "is_fraud",
    "label",
    "fraud",
    "Fraud",
    "target",
)

RANDOM_SEED = 42


def resolve_dataset_path(dataset_path: str | Path | None = None) -> Path:
    """Return the configured dataset path or the first matching real dataset file."""
    if dataset_path is not None:
        return Path(dataset_path)

    env_path = os.getenv("FRAUD_DATASET_PATH")
    if env_path:
        return Path(env_path)

    for candidate in DEFAULT_DATASET_PATHS:
        if candidate.exists():
            return candidate

    return DEFAULT_DATASET_PATHS[0]
