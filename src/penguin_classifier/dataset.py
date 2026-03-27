"""
Utility functions for data ingestion, cleaning, and persistence.
Handles both the initial dataset and the history of user predictions.
"""

from pathlib import Path

from loguru import logger
import pandas as pd

from src.penguin_classifier.config import (
    CSV_HEADER,
    NUMERICAL_FEATURES,
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
)


def fetch_and_save_raw_data() -> None:
    """
    Downloads the palmerpenguins dataset if it doesn't exist locally.

    Saves the data as a CSV to the path defined in the configuration.
    """
    if RAW_DATA_PATH.exists():
        logger.info(
            f"Raw data already exists at {RAW_DATA_PATH}, skipping fetch."
        )
        return None

    from palmerpenguins import load_penguins

    raw_data = load_penguins()
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw_data.to_csv(RAW_DATA_PATH, index=False)
    logger.info(f"Raw data saved to {RAW_DATA_PATH}")
    return None


def load_data(filepath: Path) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame.

    Args:
        filepath (Path): Path to the target CSV file.

    Returns:
        pd.DataFrame: The loaded dataset.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
    """
    if filepath == RAW_DATA_PATH and not filepath.exists():
        logger.info(f"File not found at {filepath}. Attempting download...")
        fetch_and_save_raw_data()
    try:
        data = pd.read_csv(filepath)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"No data found at {filepath}") from None


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preprocessing to handle missing values and drop unnecessary columns.

    Args:
        df (pd.DataFrame): The raw input DataFrame.

    Returns:
        pd.DataFrame: Cleaned data ready for visualization or splitting.
    """
    df = df.dropna(subset=NUMERICAL_FEATURES + ["species"], axis="rows")
    return df.drop(
        columns=["year"],
    )


def split_feature_from_target(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    Separates the target labels from the input features.

    Args:
        df (pd.DataFrame): Cleaned dataset.

    Returns:
        tuple[pd.DataFrame, list]: Features (X) and Target labels (y).
    """
    target = df["species"]
    features = df.drop("species", axis=1)
    logger.success("Data split into features and target.")
    return features, target


def save_prediction(new_data: pd.DataFrame = None):
    """
    Appends a new prediction record to the processed history CSV.

    Args:
        new_data (pd.DataFrame): A single-row DataFrame containing the features and the predicted species.
    """
    file_exists = Path(PROCESSED_DATA_PATH).exists()

    # Ensure columns are in the correct order before saving
    new_data_ordered = new_data[CSV_HEADER]

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    new_data_ordered.to_csv(
        PROCESSED_DATA_PATH, mode="a", header=not file_exists, index=False
    )


def load_combined_data():
    """
    Merges historical raw data with user-generated prediction history.

    Used for updating the UI dashboard to show both original data
    points and new predictions in the plots and tables.

    Returns:
        pd.DataFrame: Concatenated dataset, reversed for chronological display.
    """
    raw_data = load_data(RAW_DATA_PATH)
    cleaned_data = clean_data(raw_data)

    if not PROCESSED_DATA_PATH.exists():
        return cleaned_data.iloc[::-1]

    prediction_history = load_data(PROCESSED_DATA_PATH)
    if prediction_history.notna().any().any():
        updated_data = pd.concat(
            [cleaned_data, prediction_history], axis="rows"
        )
        return updated_data.iloc[::-1]

    return cleaned_data.iloc[::-1]
