from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .data_config import RANDOM_SEED, TARGET_COLUMN_CANDIDATES, resolve_dataset_path


@dataclass
class DatasetSplit:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_columns: list[str]
    target_column: str
    class_distribution: dict[str, int]
    imbalance_ratio: float


def load_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    """Load the credit-card fraud CSV dataset."""
    path = resolve_dataset_path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Credit-card fraud dataset not found at '{path}'. "
            "Place the real CSV file there or pass a valid dataset_path."
        )

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Dataset at '{path}' is empty.")

    return df


def detect_target_column(df: pd.DataFrame, target_column: str | None = None) -> str:
    """Detect the fraud label column from common credit-card fraud naming patterns."""
    if target_column:
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset columns.")
        return target_column

    for candidate in TARGET_COLUMN_CANDIDATES:
        if candidate in df.columns:
            return candidate

    for column in df.columns:
        values = df[column].dropna().unique()
        if set(values).issubset({0, 1}) and len(values) == 2:
            return column

    raise ValueError(
        "Could not identify the target fraud column. "
        "Expected a column such as 'Class', 'is_fraud', or 'label'."
    )


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values using column-wise defaults without changing the dataset shape."""
    cleaned = df.copy()

    for column in cleaned.columns:
        series = cleaned[column]

        if pd.api.types.is_numeric_dtype(series):
            median_value = series.median()
            cleaned[column] = series.fillna(median_value)
        else:
            mode_value = series.mode(dropna=True)
            fill_value = mode_value.iloc[0] if not mode_value.empty else "Unknown"
            cleaned[column] = series.fillna(fill_value)

    return cleaned


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows while preserving the original row order."""
    return df.drop_duplicates().reset_index(drop=True)


def analyze_class_imbalance(y: pd.Series) -> tuple[dict[str, int], float]:
    """Return class counts and the imbalance ratio (majority/minority)."""
    counts = y.value_counts().sort_index()
    class_distribution = {str(key): int(value) for key, value in counts.items()}

    if len(counts) < 2:
        return class_distribution, 1.0

    majority = counts.max()
    minority = counts.min()
    imbalance_ratio = float(majority / minority) if minority else float("inf")
    return class_distribution, imbalance_ratio


def prepare_features_and_target(
    df: pd.DataFrame,
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series]:
    """Split the dataset into features and target and convert target to a numeric form."""
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' is not present in the dataset.")

    X = df.drop(columns=[target_column]).copy()
    y = df[target_column].copy()

    categorical_columns = list(X.select_dtypes(include=["object", "category"]).columns)
    if categorical_columns:
        X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

    y = y.astype(int)
    return X, y


def create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = RANDOM_SEED,
    stratify: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """Split the data and scale numerical features for ML training."""
    if stratify:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
        )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index,
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index,
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def run_preprocessing_pipeline(
    dataset_path: str | Path | None = None,
    target_column: str | None = None,
    test_size: float = 0.2,
) -> DatasetSplit:
    """Run the full fraud-dataset preprocessing workflow and return clean train/test splits."""
    df = load_dataset(dataset_path)
    df = remove_duplicates(handle_missing_values(df))

    detected_target = detect_target_column(df, target_column)
    X, y = prepare_features_and_target(df, detected_target)

    class_distribution, imbalance_ratio = analyze_class_imbalance(y)
    X_train, X_test, y_train, y_test, _ = create_train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_SEED,
        stratify=True,
    )

    return DatasetSplit(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        feature_columns=list(X.columns),
        target_column=detected_target,
        class_distribution=class_distribution,
        imbalance_ratio=imbalance_ratio,
    )


def print_pipeline_summary(dataset_path: str | Path | None = None) -> None:
    """Print a short summary of the dataset preprocessing results."""
    split = run_preprocessing_pipeline(dataset_path)

    print(f"Target column: {split.target_column}")
    print(f"Feature count: {len(split.feature_columns)}")
    print(f"Train rows: {len(split.X_train)}")
    print(f"Test rows: {len(split.X_test)}")
    print(f"Class distribution: {split.class_distribution}")
    print(f"Imbalance ratio: {split.imbalance_ratio:.2f}")


if __name__ == "__main__":
    print_pipeline_summary()
