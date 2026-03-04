"""
Central configuration module.
Defines file paths, model hyperparameters, UI constants, and validation
constraints.
"""

from pathlib import Path

# --- Path Definitions ---
PROJ_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJ_ROOT / "src"
DATA_DIR = PROJ_ROOT / "data"

RAW_DATA_PATH = DATA_DIR / "raw" / "data.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "prediction_history.csv"

MODEL_PATH = PROJ_ROOT / "models" / "pipeline.joblib"
REPORTS_DIR = PROJ_ROOT / "reports"
METRICS_DIR = PROJ_ROOT / "metrics"
METRICS_PATH = METRICS_DIR / "metrics.json"

# --- ML Constants ---
RANDOM_SEED = 42
TEST_SPLIT_SIZE = 0.2

# --- Feature Definitions ---
# Columns used for prediction and CSV exports
CSV_HEADER = [
    "species",
    "island",
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
    "sex",
]

NUMERICAL_FEATURES = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]

CATEGORICAL_FEATURES = ["island", "sex"]

# Complete list of features expected by the model pipeline
FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


# --- Validation Constraints ---
# Used by the UI to validate user input before sending it to the model
FEATURE_CONSTRAINTS = {
    "bill_length_mm": {"min": 25.0, "max": 65.0, "default": 40.0},
    "bill_depth_mm": {"min": 10.0, "max": 25.0, "default": 20.0},
    "flipper_length_mm": {"min": 150.0, "max": 250.0, "default": 200.0},
    "body_mass_g": {"min": 2000.0, "max": 7500.0, "default": 4000.0},
}


# --- UI Options ---
# Dropdown values for the Dash web interface
ISLAND_OPTIONS: list[dict] = [
    {"label": "Torgersen", "value": "Torgersen"},
    {"label": "Biscoe", "value": "Biscoe"},
    {"label": "Dream", "value": "Dream"},
]

SEX_OPTIONS: list[dict] = [
    {"label": "male", "value": "male"},
    {"label": "female", "value": "female"},
]

# Styling constant for Bootstrap components
OFFSET = "mb-3"
