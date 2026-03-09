"""
Defines the reactive logic for the Dash application.
Handles user inputs, validation, model predictions, and UI updates.
"""

from dash import Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc
from loguru import logger
import pandas as pd

from src.penguin_classifier.config import FEATURE_CONSTRAINTS
from src.penguin_classifier.dataset import load_combined_data, save_prediction
from src.penguin_classifier.modeling.predict import (
    predict_single_penguin_proba,
)
from src.penguin_classifier.plots import create_scatter_plot

# Load initial dataset for session start
prediction_history = load_combined_data()


@callback(
    Output(
        component_id="classification_result", component_property="children"
    ),
    Output(component_id="classification_result", component_property="is_open"),
    Output(component_id="classification_result", component_property="color"),
    Output(component_id="scatter_graph", component_property="figure"),
    Output(component_id="table_container", component_property="children"),
    Output(component_id="latest_prediction_store", component_property="data"),
    Input(component_id="classify_button", component_property="n_clicks"),
    Input(component_id="scatter_x_axis", component_property="value"),
    Input(component_id="scatter_y_axis", component_property="value"),
    State(component_id="island_input", component_property="value"),
    State(component_id="bill_length_mm_input", component_property="value"),
    State(component_id="bill_depth_mm_input", component_property="value"),
    State(component_id="flipper_length_mm_input", component_property="value"),
    State(component_id="body_mass_g_input", component_property="value"),
    State(component_id="sex_input", component_property="value"),
    State(component_id="latest_prediction_store", component_property="data"),
)
def classify_penguin(
    n_clicks,
    x_axis,
    y_axis,
    island,
    bill_length_mm,
    bill_depth_mm,
    flipper_length_mm,
    body_mass_g,
    sex,
    latest_prediction,
):
    """
    Main callback that manages UI updates based on user interaction.

    Processes three main scenarios:
    1. Initial page load (setup).
    2. Dynamic plot axis changes.
    3. Classification of a new penguin observation.
    """
    msg = "Please enter values and press Classify"
    new_penguin_data = None
    trigger_id = ctx.triggered_id

    # --- Scenario 1: Initial Page Load ---
    if (
        trigger_id
        not in ["classify_button", "scatter_x_axis", "scatter_y_axis"]
        and n_clicks is None
    ):
        current_data = load_combined_data()
        fig = create_scatter_plot(
            df_historic=current_data,
            x_column=x_axis or "flipper_length_mm",
            y_column=y_axis or "bill_length_mm",
            size_column="body_mass_g",
            new_data=new_penguin_data,
        )
        try:
            updated_data = load_combined_data()
            table = dbc.Table.from_dataframe(
                updated_data, striped=True, bordered=True, hover=True
            )
        except FileNotFoundError:
            table = "No historical data available yet."

        logger.info("Initial callback complete")
        return msg, True, "info", fig, table, no_update

    # --- Scenario 2: Dynamic Plot Update (X/Y Axis change) ---
    if trigger_id in ["scatter_x_axis", "scatter_y_axis"]:
        current_data = load_combined_data()
        new_data = None
        if latest_prediction:
            try:
                new_data = pd.DataFrame(latest_prediction)
            except Exception:
                logger.warning("Could not restore classification from store")

        fig = create_scatter_plot(
            df_historic=current_data,
            x_column=x_axis,
            y_column=y_axis,
            size_column="body_mass_g",
            new_data=new_data,
        )
        logger.info("Dynamic plot axes updated")
        return no_update, no_update, no_update, fig, no_update, no_update

    # --- Scenario 3: Classification Process (Button Click) ---
    if trigger_id == "classify_button":
        # Validate Island Selection
        if not island:
            logger.warning("Missing island input")
            msg = "Please select an island."
            return msg, True, "danger", no_update, no_update, no_update

        # Validate Numerical Inputs (client-side via dbc.Input)
        inputs_to_validate = {
            "bill_length_mm": bill_length_mm,
            "bill_depth_mm": bill_depth_mm,
            "flipper_length_mm": flipper_length_mm,
            "body_mass_g": body_mass_g,
        }
        for feature_name, value in inputs_to_validate.items():
            msg = f"Please enter a valid value for '{feature_name}'."
            if value is None or value == "":
                logger.warning(f"Missing or invalid value for {feature_name}")

                return msg, True, "danger", no_update, no_update, no_update

            # Server-Side validation
            constraints = FEATURE_CONSTRAINTS.get(feature_name)
            if constraints:
                if value < constraints["min"] or value > constraints["max"]:
                    logger.warning(
                        f"Validation failed for {feature_name}: {value}"
                    )
                    return msg, True, "danger", no_update, no_update, no_update

        try:
            # Prepare data for prediction
            penguin_attributes = pd.DataFrame(
                {
                    "island": [island],
                    "bill_length_mm": [float(bill_length_mm)],
                    "bill_depth_mm": [float(bill_depth_mm)],
                    "flipper_length_mm": [float(flipper_length_mm)],
                    "body_mass_g": [float(body_mass_g)],
                    "sex": [sex],
                }
            )

            # Execute prediction
            try:
                species, proba = predict_single_penguin_proba(
                    features=penguin_attributes
                )
            except FileNotFoundError:
                error_msg = "No trained model found. Please run train.py."
                logger.exception("No trained Model found. Please run train.py")
                return (
                    error_msg,
                    True,
                    "danger",
                    no_update,
                    no_update,
                    no_update,
                )

            msg = (
                f"Species: {species} --- Confidence: {round(proba * 100, 2)}%"
            )
            if not sex:
                msg += " - (Note: No sex provided)"

            logger.info(f"Successful prediction: {species}")

            # Save prediction to history
            penguin_attributes["species"] = species
            save_prediction(penguin_attributes)

            # Update Store and Visuals
            store_data = penguin_attributes.to_dict("records")
            refreshed_data = load_combined_data()

            figure = create_scatter_plot(
                df_historic=refreshed_data,
                x_column=x_axis,
                y_column=y_axis,
                size_column="body_mass_g",
                new_data=penguin_attributes,
            )

            table = dbc.Table.from_dataframe(
                refreshed_data,
                striped=True,
                bordered=True,
                hover=True,
            )

            return msg, True, "success", figure, table, store_data

        except Exception as e:
            logger.exception("Error in Classification Callback:")
            return (
                f"System Error: {str(e)}",
                True,
                "danger",
                no_update,
                no_update,
                no_update,
            )

    return no_update, no_update, no_update, no_update, no_update, no_update
