from __future__ import annotations

from typing import Any

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from .data_config import resolve_dataset_path
from .data_pipeline import (
    detect_target_column,
    handle_missing_values,
    prepare_features_and_target,
    remove_duplicates,
    run_preprocessing_pipeline,
)


def _detect_amount_column(df: pd.DataFrame) -> str:
    """Find the transaction amount column from common naming patterns."""
    for candidate in ("amount", "Amount", "TransactionAmt", "transaction_amount", "amt"):
        if candidate in df.columns:
            return candidate

    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_columns:
        raise ValueError("No numeric columns found in the dataset for amount analysis.")
    return numeric_columns[0]


def _normalize_binary_target(series: pd.Series) -> pd.Series:
    """Convert a 2-class target into 0/1 integer labels."""
    values = series.dropna().unique()
    if len(values) != 2:
        return series.astype(int)

    if set(values).issubset({0, 1}):
        return series.astype(int)

    if set(values).issubset({False, True}):
        return series.astype(int)

    sorted_values = sorted(values.tolist())
    mapping = {sorted_values[0]: 0, sorted_values[1]: 1}
    return series.map(mapping).astype(int)


def get_fraud_distribution(df: pd.DataFrame, target_column: str | None = None) -> dict[str, Any]:
    """Summarize the count of fraud vs legitimate transactions."""
    target = detect_target_column(df, target_column)
    normalized = _normalize_binary_target(df[target])
    counts = normalized.value_counts().sort_index()

    fraud_count = int(counts.get(1, 0))
    legitimate_count = int(counts.get(0, 0))
    total = int(fraud_count + legitimate_count)

    return {
        "target_column": target,
        "total_transactions": total,
        "legitimate_transactions": legitimate_count,
        "fraud_transactions": fraud_count,
        "fraud_rate_percent": round((fraud_count / total * 100), 4) if total else 0.0,
        "legitimate_rate_percent": round((legitimate_count / total * 100), 4) if total else 0.0,
        "distribution": {
            "legitimate": legitimate_count,
            "fraud": fraud_count,
        },
    }


def get_transaction_amount_distribution(
    df: pd.DataFrame,
    target_column: str | None = None,
) -> dict[str, Any]:
    """Compute the transaction amount distribution overall and by class."""
    target = detect_target_column(df, target_column)
    amount_column = _detect_amount_column(df)

    amount_series = pd.to_numeric(df[amount_column], errors="coerce")
    normalized_target = _normalize_binary_target(df[target])

    overall = amount_series.describe()
    by_class = (
        pd.DataFrame({"amount": amount_series, "target": normalized_target})
        .groupby("target")["amount"]
        .agg(["count", "mean", "median", "min", "max", "std"])
        .rename(index={0: "legitimate", 1: "fraud"})
    )

    return {
        "amount_column": amount_column,
        "overall_stats": {
            "count": int(overall["count"]),
            "mean": round(float(overall["mean"]), 4) if pd.notna(overall["mean"]) else None,
            "std": round(float(overall["std"]), 4) if pd.notna(overall["std"]) else None,
            "min": round(float(overall["min"]), 4) if pd.notna(overall["min"]) else None,
            "max": round(float(overall["max"]), 4) if pd.notna(overall["max"]) else None,
            "median": round(float(overall["50%"]), 4) if pd.notna(overall["50% "]) else None,
        },
        "by_class": by_class.round(4).to_dict(),
    }


def get_correlation_analysis(
    df: pd.DataFrame,
    target_column: str | None = None,
    top_n: int = 15,
) -> dict[str, Any]:
    """Compute feature-to-target correlation and return the strongest relationships."""
    target = detect_target_column(df, target_column)
    numeric_df = df.select_dtypes(include=[np.number]).copy()

    if target not in numeric_df.columns:
        numeric_df[target] = pd.to_numeric(df[target], errors="coerce")

    numeric_df[target] = _normalize_binary_target(numeric_df[target])
    corr = numeric_df.corr(numeric=False)
    target_corr = corr[target].drop(labels=target)
    strongest = target_corr.abs().sort_values(ascending=False).head(top_n)

    result = (
        strongest.rename_axis("feature")
        .reset_index(name="absolute_correlation")
        .rename(columns={"feature": "feature", "absolute_correlation": "absolute_correlation"})
    )
    result["correlation_with_target"] = result["feature"].map(target_corr)
    result = result[["feature", "correlation_with_target", "absolute_correlation"]]

    return {
        "target_column": target,
        "top_features": result.to_dict(orient="records"),
    }


def get_important_feature_analysis(
    dataset_path: str | None = None,
    target_column: str | None = None,
    top_n: int = 10,
) -> dict[str, Any]:
    """Train a random forest to identify the most important fraud features."""
    split = run_preprocessing_pipeline(dataset_path=dataset_path, target_column=target_column, test_size=0.2)
    X_train = split.X_train
    y_train = split.y_train

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    feature_importance = (
        pd.Series(model.feature_importances_, index=X_train.columns)
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    feature_importance.columns = ["feature", "importance"]

    return {
        "target_column": split.target_column,
        "top_features": feature_importance.to_dict(orient="records"),
    }


def run_eda_report(dataset_path: str | None = None, target_column: str | None = None) -> dict[str, Any]:
    """Generate a complete EDA summary for the fraud detection dataset."""
    dataset_path = resolve_dataset_path(dataset_path)
    df = pd.read_csv(dataset_path)
    df = remove_duplicates(handle_missing_values(df))
    target = detect_target_column(df, target_column)

    report = {
        "dataset_path": str(dataset_path),
        "target_column": target,
        "fraud_distribution": get_fraud_distribution(df, target),
        "transaction_amount_distribution": get_transaction_amount_distribution(df, target),
        "correlation_analysis": get_correlation_analysis(df, target),
        "important_features": get_important_feature_analysis(dataset_path=str(dataset_path), target_column=target),
    }
    return report


if __name__ == "__main__":
    report = run_eda_report()
    print("Fraud distribution:")
    print(report["fraud_distribution"])
    print("\nTop correlated features:")
    print(report["correlation_analysis"]["top_features"][:5])
    print("\nTop important features:")
    print(report["important_features"]["top_features"])
