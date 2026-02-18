"""
Training module for the Penguin Classifier.
Orchestrates data loading, preprocessing, model training, and evaluation.
"""
import json
import warnings

import joblib
import pandas as pd
from loguru import logger
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline

from src.penguin_classifier.config import (
    METRICS_PATH,
    MODEL_PATH,
    RANDOM_SEED,
    RAW_DATA_PATH,
    TEST_SPLIT_SIZE,
)
from src.penguin_classifier.dataset import (
    clean_data,
    load_data,
    split_feature_from_target,
)
from src.penguin_classifier.features import build_preprocessor

# Suppress annoying warning from pkg_resources
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")


def build_pipeline() -> Pipeline:
    """
    Constructs the ML pipeline with preprocessor and classifier.

    Returns:
        Pipeline: Unfitted scikit-learn pipeline.
    """
    preprocessor = build_preprocessor()
    classifier = LogisticRegression(
        random_state=RANDOM_SEED,
        max_iter=1000,
        solver="lbfgs"  # Explicit default
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def load_and_split_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Loads raw data, cleans it, and performs a stratified train-test split.

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    df_raw = load_data(filepath=RAW_DATA_PATH)
    df_cleaned = clean_data(df=df_raw)
    X, y = split_feature_from_target(df=df_cleaned)

    # Returning the result of train_test_split directly unpacks into the tuple
    return train_test_split(
        X,
        y,
        test_size=TEST_SPLIT_SIZE,
        random_state=RANDOM_SEED,
        stratify=y,
    )


def run_grid_search(
    X_train: pd.DataFrame, y_train: pd.Series
) -> tuple[Pipeline, float]:
    """
    Optimizes hyperparameters using GridSearchCV.

    Args:
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series): Training labels.

    Returns:
        tuple[Pipeline, float]: The best fitted pipeline and its CV score.
    """
    pipeline = build_pipeline()

    param_grid = {
        "classifier__C": [0.1, 1.0, 10.0],
        "classifier__solver": ["lbfgs", "newton-cg"],
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_SEED
    )

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=cv,
        scoring="accuracy",
        n_jobs=-1,
        verbose=1,
    )

    logger.info("Starting Grid Search...")
    grid_search.fit(X=X_train, y=y_train)

    best_score = float(grid_search.best_score_)
    logger.success(f"Best CV Accuracy: {best_score:.2%}")

    return grid_search.best_estimator_, best_score


def evaluate_model(
    pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> dict:
    """
    Predicts on test data and generates a classification report.

    Args:
        pipeline (Pipeline): Fitted model.
        X_test (pd.DataFrame): Test features.
        y_test (pd.Series): Test labels.

    Returns:
        dict: Classification report as a dictionary.
    """
    preds = pipeline.predict(X=X_test)

    print("\n" + classification_report(y_true=y_test, y_pred=preds))

    print(confusion_matrix(y_true=y_test, y_pred=preds))

    return classification_report(
        y_true=y_test,
        y_pred=preds,
        output_dict=True
    )


def save_artifacts(
    pipeline: Pipeline, metrics: dict, cv_score: float
) -> None:
    """
    Saves the trained model and metrics to disk.

    Args:
        pipeline (Pipeline): The trained model.
        metrics (dict): The evaluation report.
        cv_score (float): The best cross-validation score.
    """
    metrics["cross_val_accuracy"] = round(cv_score, 4)

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
    logger.success(f"Metrics saved to {METRICS_PATH}")

    joblib.dump(value=pipeline, filename=MODEL_PATH)
    logger.success(f"Model saved to {MODEL_PATH}")


def train_model() -> None:
    """Main execution function for the training workflow."""

    # 1. Load Data
    X_train, X_test, y_train, y_test = load_and_split_data()

    # 2. Train (Grid Search)
    best_pipeline, best_cv_score = run_grid_search(
        X_train=X_train,
        y_train=y_train
    )

    # 3. Evaluate
    metrics = evaluate_model(
        pipeline=best_pipeline,
        X_test=X_test,
        y_test=y_test
    )

    # 4. Save
    save_artifacts(
        pipeline=best_pipeline,
        metrics=metrics,
        cv_score=best_cv_score
    )


if __name__ == "__main__":
    train_model()