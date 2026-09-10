from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from .data_config import resolve_dataset_path
from .data_pipeline import run_preprocessing_pipeline


def _safe_roc_auc(y_true: pd.Series | np.ndarray, y_prob: np.ndarray) -> float:
    """Calculate ROC-AUC while ignoring bad values or single-class outputs."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    if len(np.unique(y_true)) < 2:
        return 0.0
    return float(roc_auc_score(y_true, y_prob))


def _evaluate_classifier(name: str, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    """Evaluate a supervised classifier on the provided test data."""
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = y_pred.astype(float)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    return {
        "model": name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": _safe_roc_auc(y_test, y_prob),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def _evaluate_anomaly_detector(
    name: str,
    model: IsolationForest,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, Any]:
    """Evaluate an unsupervised anomaly detector using the fraud label as ground truth."""
    predictions = model.predict(X_test)
    y_pred = np.where(predictions == -1, 1, 0)
    anomaly_scores = -model.decision_function(X_test)
    normalized_scores = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min() + 1e-9)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    return {
        "model": name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": _safe_roc_auc(y_test, normalized_scores),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def train_and_compare_models(
    dataset_path: str | None = None,
    target_column: str | None = None,
) -> dict[str, Any]:
    """Train and compare Logistic Regression, Random Forest, Gradient Boosting, and Isolation Forest."""
    resolved_path = resolve_dataset_path(dataset_path)
    split = run_preprocessing_pipeline(dataset_path=resolved_path, target_column=target_column, test_size=0.2)

    X_train = split.X_train
    X_test = split.X_test
    y_train = split.y_train
    y_test = split.y_test

    models: list[tuple[str, Any]] = [
        ("Logistic Regression", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ("Random Forest", RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")),
        ("Gradient Boosting", GradientBoostingClassifier(random_state=42)),
    ]

    results: list[dict[str, Any]] = []
    for name, model in models:
        model.fit(X_train, y_train)
        results.append(_evaluate_classifier(name, model, X_test, y_test))

    anomaly_model = IsolationForest(
        n_estimators=300,
        contamination=0.05,
        random_state=42,
    )
    anomaly_model.fit(X_train)
    results.append(_evaluate_anomaly_detector("Isolation Forest", anomaly_model, X_test, y_test))

    ranked_results = sorted(
        results,
        key=lambda item: item["f1"],
        reverse=True,
    )

    return {
        "dataset_path": str(resolved_path),
        "target_column": split.target_column,
        "class_distribution": split.class_distribution,
        "imbalance_ratio": split.imbalance_ratio,
        "results": ranked_results,
    }


def print_model_comparison(summary: dict[str, Any]) -> None:
    """Print a concise model comparison summary."""
    print(f"Dataset: {summary['dataset_path']}")
    print(f"Target column: {summary['target_column']}")
    print(f"Class distribution: {summary['class_distribution']}")
    print(f"Imbalance ratio: {summary['imbalance_ratio']:.2f}")
    print("\nModel comparison results:\n")

    for result in summary["results"]:
        print(
            f"{result['model']}: "
            f"Accuracy={result['accuracy']:.4f}, "
            f"Precision={result['precision']:.4f}, "
            f"Recall={result['recall']:.4f}, "
            f"F1={result['f1']:.4f}, "
            f"ROC-AUC={result['roc_auc']:.4f}"
        )
        cm = result["confusion_matrix"]
        print(
            "  Confusion matrix: "
            f"TN={cm['tn']}, FP={cm['fp']}, FN={cm['fn']}, TP={cm['tp']}"
        )


if __name__ == "__main__":
    summary = train_and_compare_models()
    print_model_comparison(summary)
