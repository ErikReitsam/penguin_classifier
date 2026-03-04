"""
Logic for loading the trained model and performing predictions.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.penguin_classifier.config import MODEL_PATH


def _load_pipeline(path: Path) -> Pipeline:
    """
    Loads a trained scikit-learn pipeline from a joblib file.

    Args:
        path (str): File path to the saved pipeline.

    Returns:
        Pipeline: The loaded scikit-learn Pipeline object.
    """
    return joblib.load(path)


def predict_batch_species(
    features: pd.DataFrame, pipeline: Pipeline
) -> list[str]:
    """
    Predicts species for a collection of penguin observations.

    Args:
        features (pd.DataFrame): Input features for multiple penguins.
        pipeline (Pipeline): The trained model pipeline to use.

    Returns:
        list[str]: Predicted species names for each observation.
    """
    return pipeline.predict(X=features)


def predict_single_penguin_proba(features: pd.DataFrame) -> tuple[str, float]:
    """
    Predicts species and confidence score for a single penguin.

    Args:
        features (pd.DataFrame): A single-row DataFrame with penguin features.

    Returns:
        tuple[str, float]: Predicted species name and the highest probability score.
    """
    pipeline = _load_pipeline(MODEL_PATH)
    predicted_species = pipeline.predict(X=features)[0]

    all_probabilities = pipeline.predict_proba(X=features)
    max_confidence = np.max(all_probabilities).round(4)

    return predicted_species, max_confidence


if __name__ == "__main__":
    from src.penguin_classifier.dataset import (
        RAW_DATA_PATH,
        clean_data,
        load_data,
    )

    df = load_data(RAW_DATA_PATH)
    cleaned_df = clean_data(df)
    species, proba = predict_single_penguin_proba(
        features=cleaned_df.iloc[[0]]
    )
    print(f"Species: {species}, Probability: {proba}")
