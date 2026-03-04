"""
Visualization module for the Penguin Classifier.
Uses Plotly to generate interactive charts for the Dash UI.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_scatter_plot(
    df_historic: pd.DataFrame,
    x_column: str = "flipper_length_mm",
    y_column: str = "bill_length_mm",
    size_column: str | None = None,
    new_data: pd.DataFrame = None,
) -> go.Figure:
    """
    Generates an interactive scatter plot of the penguin population.

    Historical data is displayed with partial transparency, while the latest
    prediction is highlighted as a distinct star icon.

    Args:
        df_historic (pd.DataFrame): The base dataset containing past observations.
        x_column (str): Feature to plot on the X-axis.
        y_column (str): Feature to plot on the Y-axis.
        size_column (str, optional): Feature to determine marker size.
        new_data (pd.DataFrame, optional): The single most recent prediction to highlight.

    Returns:
        go.Figure: A Plotly figure object ready for rendering in the Dash UI.
    """
    # Define a consistent color scheme for penguin species
    color_map = {
        "Adelie": "#636EFA",
        "Chinstrap": "#EF553B",
        "Gentoo": "#00CC96",
    }

    # Create the background scatter plot (historical data)
    fig = px.scatter(
        data_frame=df_historic,
        x=x_column,
        y=y_column,
        color="species",
        color_discrete_map=color_map,
        title="Penguin Data Distribution",
        size=size_column,
        template="simple_white",
        opacity=0.5,
    )

    # Overlay the latest prediction if available
    if new_data is not None:
        fig.add_trace(
            go.Scatter(
                x=new_data[x_column],
                y=new_data[y_column],
                mode="markers",
                marker=dict(
                    color="yellow",
                    size=15,
                    opacity=1,
                    symbol="star",
                    line=dict(width=1, color="black"),
                ),
                name="Latest Prediction",
            )
        )

    fig.update_layout(
        legend_title="Species",
    )

    return fig
