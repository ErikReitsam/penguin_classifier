"""
Defines the visual structure of the Dash application.
Uses Dash Bootstrap Components (dbc) to create a responsive dashboard layout.
"""

# flake8: noqa: E501

import json
from typing import Literal

from dash import dcc, html
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

from src.penguin_classifier.config import (
    FEATURE_CONSTRAINTS,
    FEATURES,
    ISLAND_OPTIONS,
    METRICS_PATH,
    OFFSET,
    SEX_OPTIONS,
)

# Human-readable labels for the UI
FIELD_LABELS = {
    "island": "Island Location",
    "bill_length_mm": "Bill Length (mm)",
    "bill_depth_mm": "Bill Depth (mm)",
    "flipper_length_mm": "Flipper Length (mm)",
    "body_mass_g": "Body Mass (g)",
    "sex": "Sex",
}

# Example values shown in empty input fields
PLACEHOLDERS = {
    "island": "e.g. Torgersen",
    "bill_length_mm": "e.g. 38.5",
    "bill_depth_mm": "e.g. 18.1",
    "flipper_length_mm": "e.g. 180.0",
    "body_mass_g": "e.g. 3750.0",
    "sex": "female",
}


def _create_performance_card() -> dbc.Card:
    """
    Reads the metrics.json file and creates a card showing model performance.

    Displays Accuracy, Precision, Recall, F1-Score, and CV-Accuracy in a row.
    """
    try:
        with open(METRICS_PATH, "r") as f:
            report = json.load(f)

        macro_avg = report.get("macro avg", {})
        accuracy = report.get("accuracy", 0)

        # Format metrics as percentages
        acc_text = f"{accuracy:.1%}"
        f1_text = f"{macro_avg.get('f1-score', 0):.1%}"
        precision_text = f"{macro_avg.get('precision', 0):.1%}"
        recall_text = f"{macro_avg.get('recall', 0):.1%}"
        best_cv_score = f"{report.get('cross_val_accuracy', 0):.1%}"

        content = [
            html.H5(children="Model Performance", className="card-title"),
            html.P(
                children="Trained on historical data using optimized hyperparameters.",
                className="card-text text-muted small",
            ),
            html.Hr(),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            html.H2(acc_text, className="text-primary"),
                            html.Small("Accuracy"),
                        ],
                        width=3,
                        xs=6,
                    ),
                    dbc.Col(
                        children=[
                            html.H2(precision_text, className="text-info"),
                            html.Small("Precision"),
                        ],
                        width=3,
                        xs=6,
                    ),
                    dbc.Col(
                        children=[
                            html.H2(recall_text, className="text-info"),
                            html.Small("Recall"),
                        ],
                        width=3,
                        xs=6,
                    ),
                    dbc.Col(
                        children=[
                            html.H2(f1_text, className="text-info"),
                            html.Small("F1-Score"),
                        ],
                        width=3,
                        xs=6,
                    ),
                    dbc.Col(
                        children=[
                            html.H2(best_cv_score, className="text-info"),
                            html.Small("CV-Accuracy"),
                        ],
                        width=3,
                        xs=6,
                    ),
                ],
                className="text-center",
            ),
        ]
    except FileNotFoundError:
        content = [
            html.H5(children="Model Performance", className="card-title"),
            dbc.Alert(
                children="No metrics found. Please run train.py first.",
                color="warning",
            ),
        ]

    return dbc.Card(
        dbc.CardBody(content), className="shadow-sm border-1 h-100"
    )


def _create_select(
    label: str, options: list[dict], required: bool = False
) -> dbc.Select:
    """Helper to create a Bootstrap dropdown select component."""
    component_id = "{}_input".format(label)
    return dbc.Select(
        id=component_id,
        options=options,
        placeholder=PLACEHOLDERS[label],
        required=required,
    )


def _create_input(
    label: str, input_type: Literal["text", "number"]
) -> dbc.Input:
    """Helper to create a Bootstrap numeric or text input with validation constraints."""
    component_id = "{}_input".format(label)
    return dbc.Input(
        id=component_id,
        type=input_type,
        placeholder=PLACEHOLDERS[label],
        min=FEATURE_CONSTRAINTS[label]["min"],
        max=FEATURE_CONSTRAINTS[label]["max"],
        # value=FEATURE_CONSTRAINTS[label]["default"], # uncomment to use default-values
    )


def _create_input_card(
    label: str,
    input_component: Component,
    offset: str = OFFSET,
    help_text: str = "Select a value.",
) -> dbc.Card:
    """Wraps an input component into a styled Bootstrap card with labels and help texts."""
    if label in ["island", "sex"]:
        form_text = help_text
    else:
        form_text = f"Range: {FEATURE_CONSTRAINTS[label]['min']} to {FEATURE_CONSTRAINTS[label]['max']}"

    return dbc.Card(
        children=[
            dbc.CardBody(
                [
                    dbc.Label(
                        children=FIELD_LABELS[label],
                        html_for=input_component.id,
                    ),
                    input_component,
                    dbc.FormText(children=form_text, color="secondary"),
                ]
            )
        ],
        className="{}".format(offset),
    )


def _create_axis_dropdown(
    label: str, component_id: str, default_value: str
) -> dbc.Col:
    """Helper for plot axis selection dropdowns."""
    return dbc.Col(
        children=[
            dbc.Label(label),
            dcc.Dropdown(
                id=component_id,
                options=[
                    {"label": FIELD_LABELS[feat], "value": feat}
                    for feat in FEATURES
                ],
                value=default_value,
                clearable=False,
            ),
        ],
        width=6,
    )


def create_layout() -> dbc.Container:
    """
    Assembles the complete dashboard layout.

    Structured into a sidebar for data input and a main area for results,
    visualizations, and historical data.
    """
    return dbc.Container(
        children=[
            dcc.Store(id="latest_prediction_store"),
            dbc.Row(
                children=[
                    # --- SIDEBAR: USER INPUT ---
                    dbc.Col(
                        width=3,
                        children=[
                            html.H4(children="Input Data", className="mb-3"),
                            _create_input_card(
                                label="island",
                                input_component=_create_select(
                                    label="island",
                                    options=ISLAND_OPTIONS,
                                    required=True,
                                ),
                            ),
                            _create_input_card(
                                label="bill_length_mm",
                                input_component=_create_input(
                                    label="bill_length_mm", input_type="number"
                                ),
                            ),
                            _create_input_card(
                                label="bill_depth_mm",
                                input_component=_create_input(
                                    label="bill_depth_mm", input_type="number"
                                ),
                            ),
                            _create_input_card(
                                label="flipper_length_mm",
                                input_component=_create_input(
                                    label="flipper_length_mm",
                                    input_type="number",
                                ),
                            ),
                            _create_input_card(
                                label="body_mass_g",
                                input_component=_create_input(
                                    label="body_mass_g", input_type="number"
                                ),
                            ),
                            _create_input_card(
                                label="sex",
                                input_component=_create_select(
                                    label="sex", options=SEX_OPTIONS
                                ),
                            ),
                            dbc.Card(
                                dbc.CardBody(
                                    dbc.Button(
                                        children="Classify Penguin",
                                        id="classify_button",
                                        color="primary",
                                        className="w-100",
                                        size="lg",
                                    )
                                ),
                                className="shadow-sm border-0",
                            ),
                        ],
                    ),
                    # --- MAIN CONTENT: RESULTS & ANALYSIS ---
                    dbc.Col(
                        width=9,
                        children=[
                            # Section: Classification Output
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H3(
                                                children="Penguin Classifier",
                                                className="mb-3",
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        children="Result",
                                                        className="fw-bold",
                                                    ),
                                                    dbc.CardBody(
                                                        dbc.Alert(
                                                            id="classification_result",
                                                            is_open=False,
                                                            dismissable=False,
                                                            color="info",
                                                            className="text-center fw-bold m-0",
                                                        )
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ]
                            ),
                            html.Br(),
                            # Section: Visualizations & Table
                            dbc.Row(
                                children=[
                                    # Column: Interactive Scatter Plot
                                    dbc.Col(
                                        width=6,
                                        children=[
                                            dbc.Card(
                                                children=[
                                                    dbc.CardHeader(
                                                        children="Population Analysis",
                                                        className="fw-bold",
                                                    ),
                                                    dbc.CardBody(
                                                        children=[
                                                            dcc.Graph(
                                                                id="scatter_graph",
                                                                style={
                                                                    "height": "450px"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                children=[
                                                                    _create_axis_dropdown(
                                                                        label="Y-Axis",
                                                                        component_id="scatter_y_axis",
                                                                        default_value="bill_length_mm",
                                                                    ),
                                                                    _create_axis_dropdown(
                                                                        label="X-Axis",
                                                                        component_id="scatter_x_axis",
                                                                        default_value="flipper_length_mm",
                                                                    ),
                                                                ],
                                                                className="mt-3",
                                                            ),
                                                        ],
                                                        className="p-1",
                                                    ),
                                                ],
                                                className="shadow-sm border-1 h-100",
                                            )
                                        ],
                                    ),
                                    # Column: Prediction History
                                    dbc.Col(
                                        width=6,
                                        children=[
                                            dbc.Card(
                                                children=[
                                                    dbc.CardHeader(
                                                        children="Prediction History",
                                                        className="fw-bold",
                                                    ),
                                                    dbc.CardBody(
                                                        html.Div(
                                                            id="table_container",
                                                            style={
                                                                "maxHeight": "430px",
                                                                "overflowY": "auto",
                                                            },
                                                        )
                                                    ),
                                                ],
                                                className="shadow-sm border-1 h-100",
                                            )
                                        ],
                                    ),
                                ],
                                className="g-3",
                            ),
                            html.Br(),
                            # Section: Global Model Performance
                            dbc.Row(
                                [
                                    dbc.Col(
                                        width=12,
                                        children=[_create_performance_card()],
                                    )
                                ]
                            ),
                        ],
                    ),
                ],
                className="g-4",
            ),
        ],
        fluid=True,
        className="p-4 bg-light",
    )
