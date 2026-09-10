import pandas as pd

from app.data_pipeline import (
    create_train_test_split,
    detect_target_column,
    handle_missing_values,
    load_dataset,
    prepare_features_and_target,
    remove_duplicates,
    run_preprocessing_pipeline,
)
from app.ml import FEATURES


def test_sample_dataset_loads_with_expected_columns():
    dataset = load_dataset()

    assert len(dataset) == 1200
    assert set(FEATURES + ["is_fraud"]).issubset(dataset.columns)


def test_missing_values_are_filled_without_changing_shape():
    dataset = pd.DataFrame({"amount": [10.0, None], "merchant": ["shop", None]})

    cleaned = handle_missing_values(dataset)

    assert cleaned.shape == dataset.shape
    assert not cleaned.isna().any().any()
    assert cleaned.loc[1, "amount"] == 10.0
    assert cleaned.loc[1, "merchant"] == "shop"


def test_duplicate_rows_are_removed():
    dataset = pd.DataFrame({"amount": [10, 10, 20], "is_fraud": [0, 0, 1]})

    cleaned = remove_duplicates(dataset)

    assert len(cleaned) == 2
    assert cleaned.iloc[0]["amount"] == 10
    assert list(cleaned.index) == [0, 1]


def test_features_and_target_are_separated_and_encoded():
    dataset = pd.DataFrame(
        {"amount": [10, 20], "merchant": ["shop", "store"], "is_fraud": [0, 1]}
    )

    features, target = prepare_features_and_target(dataset, "is_fraud")

    assert "is_fraud" not in features.columns
    assert "amount" in features.columns
    assert len(features.columns) == 2
    assert target.tolist() == [0, 1]
    assert target.dtype.kind == "i"


def test_train_test_split_returns_scaled_features_and_labels():
    dataset = load_dataset()
    features, target = prepare_features_and_target(dataset, "is_fraud")

    X_train, X_test, y_train, y_test, scaler = create_train_test_split(
        features, target, test_size=0.25
    )

    assert len(X_train) + len(X_test) == len(dataset)
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)
    assert list(X_train.columns) == list(features.columns)
    assert scaler.n_features_in_ == len(features.columns)


def test_full_preprocessing_pipeline_handles_sample_dataset():
    split = run_preprocessing_pipeline()

    assert split.target_column == "is_fraud"
    assert set(split.feature_columns) == set(FEATURES)
    assert len(split.X_train) + len(split.X_test) == 1200
    assert sum(split.class_distribution.values()) == 1200