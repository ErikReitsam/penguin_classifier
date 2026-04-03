"""
Main entry point for the Dash application.
Configures the UI layout, initializes callbacks, and starts the web server.
"""

import os
from threading import Timer
import webbrowser

from dash import Dash
import dash_bootstrap_components as dbc

# Import callbacks to ensure they are registered with the Dash app
# noinspection PyUnusedImports
from src.penguin_classifier.ui import callbacks  # noqa: F401
from src.penguin_classifier.ui.layout import create_layout


def open_browser():
    """
    Opens the default web browser to the application's local address.
    """
    webbrowser.open_new("http://127.0.0.1:8050/")


# Initialize Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Penguin Classifier"
app.layout = create_layout()

server = app.server


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") is None:
        Timer(interval=2, function=open_browser).start()

    app.run(debug=False, port=8050)
