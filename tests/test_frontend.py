import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from dash import no_update

from src.penguin_classifier.ui.callbacks import classify_penguin


# --- Fixtures ---
def get_default_args():
    return {
        "n_clicks": 1,
        "x_axis": "bill_length_mm",
        "y_axis": "body_mass_g",
        "island": "Torgersen",
        "bill_length_mm": 40.0,
        "bill_depth_mm": 18.0,
        "flipper_length_mm": 190.0,
        "body_mass_g": 3500.0,
        "sex": "male",
        "latest_prediction": None,
    }


# --- Tests ---


@patch(
    "src.penguin_classifier.ui.callbacks.ctx"
)
def test_callback_missing_island(mock_ctx):
    """Test for missing island."""

    mock_ctx.triggered_id = "classify_button"

    args = get_default_args()
    args["island"] = None

    output = classify_penguin(**args)

    text, is_open, color, _, _, _ = output

    assert is_open is True
    assert color == "danger"
    assert "Please select an island." in text


@patch("src.penguin_classifier.ui.callbacks.ctx")
def test_callback_invalid_number(mock_ctx):
    """Test value out of bounds."""

    mock_ctx.triggered_id = "classify_button"

    args = get_default_args()
    args["bill_length_mm"] = 9999.0

    output = classify_penguin(**args)

    text, is_open, color, _, _, _ = output

    assert is_open is True
    assert color == "danger"
    assert "Please enter a valid value for" in text
    assert "bill_length_mm" in text


@patch("src.penguin_classifier.ui.callbacks.ctx")
@patch(
    "src.penguin_classifier.ui.callbacks.predict_single_penguin_proba"
)  # Mock ML
@patch("src.penguin_classifier.ui.callbacks.save_prediction")  # Mock CSV-Save
@patch(
    "src.penguin_classifier.ui.callbacks.load_combined_data"
)  # Mock CSV-Load
@patch("src.penguin_classifier.ui.callbacks.create_scatter_plot")  # Mock Plot
def test_callback_success(
    mock_plot, mock_load, mock_save, mock_predict, mock_ctx
):
    """Test happy path."""
    mock_ctx.triggered_id = "classify_button"
    mock_predict.return_value = ("Adelie", 0.95)

    dummy_df = pd.DataFrame({"species": ["Adelie"], "body_mass_g": [4000]})
    mock_load.return_value = dummy_df

    mock_plot.return_value = {"data": []}

    args = get_default_args()
    output = classify_penguin(**args)

    text, is_open, color, fig, table, store_data = output

    assert is_open is True
    assert color == "success"
    assert "Adelie" in text
    assert "95.0%" in text

    mock_save.assert_called_once()

    assert store_data is not None
    assert store_data[0]["species"] == "Adelie"