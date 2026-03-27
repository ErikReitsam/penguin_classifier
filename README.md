# Penguin Species Classifier

An interactive Machine Learning web application to predict penguin species based on physical characteristics. Built with **Python**, **Dash**, **Scikit-Learn**, and **Docker**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#-quick-start-docker)
- [Local Development](#local-development)
- [Model Information](#model-information)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project implements a full end-to-end Machine Learning pipeline. It trains a **Logistic Regression** model on the Palmer Penguins dataset and serves it via a user-friendly web interface.

Users can input physical measurements (bill length, flipper length, etc.) to get a real-time prediction of the penguin species (*Adelie*, *Chinstrap*, or *Gentoo*). All predictions are saved locally for historical analysis.

## Key Features

* **Interactive Dashboard:** Built with Plotly Dash and Bootstrap components.
* **Real-time Inference:** Immediate classification results with probability scores.
* **Data Persistence:** User predictions are saved to `data/processed/` and visualized alongside historical data.
* **Containerized:** Fully Dockerized for "write once, run anywhere" deployment.
* **Robust Pipeline:** Automated data cleaning, feature engineering, and hyperparameter tuning using `GridSearchCV`.

---

## Project Structure

This project follows the **Cookiecutter Data Science** standard:

```text
├── .pre-commit-config.yaml     # Configuration for automated code quality checks
├── Dockerfile                  # Instructions to build the containerized app
├── LICENSE                     # Open-source license (e.g., MIT)
├── Makefile                    # Task runner for common commands (e.g., test, build)
├── poetry.lock                 # Locked dependencies for guaranteed reproducibility
├── pyproject.toml              # Modern Python project configuration and dependencies
├── start_app_windows.bat       # One-click Launcher for Windows
├── start_app_linux.sh          # One-click Launcher for Mac/Linux
├── data/                       # Local data storage (raw and user-processed)
├── docs/                       # Extended project documentation (MkDocs ready)
├── metrics/                    # Model performance metrics
├── models/                     # Serialized model artifacts (pipeline.joblib)
├── notebooks/                  # Jupyter notebooks for EDA
├── reports/                    # Generated evaluation metrics and figures
└── src/                        # Main application source code
    └── penguin_classifier/
        ├── app.py              # Application entry point
        ├── config.py           # Configuration & constants
        ├── dataset.py          # Data loading & persistence logic
        ├── features.py         # Feature engineering
        ├── plots.py            # Visualization logic
        ├── modeling/           # ML training, evaluation, and inference logic
        └── ui/                 # Dash layout components and interactive callbacks
└── tests/                      # Tests (Pytest for frontend & backend)
```

---

## Prerequisites

To run the application in the recommended mode, you only need:

* **Docker Desktop** (running)

*Note: No Python installation is required on your local machine if you use the provided scripts.*

---

## Quick Start (Docker)

Provided are automated scripts to build and run the application in a container.

### For Windows Users
1.  Ensure Docker Desktop is running.
2.  Double-click the file **`start_windows.bat`**.
3.  A console window will open, build the image, and automatically launch your default browser at `http://localhost:8050`.

### For Mac / Linux Users
1.  Open your terminal.
2.  Navigate to the project folder.
3.  Make the script executable (only needed once):
    ```bash
    chmod +x start_linux.sh
    ```
4.  Run the script:
    ```bash
    ./start_app_linux.sh
    ```

**Stopping the App:**
Simply close the terminal window or press `CTRL + C`. The container will automatically shut down and clean up.

---

## Local Development

If you wish to develop or run the code without Docker, you need **Python 3.10+** and **Poetry** (or pip).

1.  **Install Dependencies:**
    ```bash
    pip install .
    ```
    *Or using Poetry:*
    ```bash
    poetry install
    ```

2.  **Train the Model:**
    If you want to retrain the model with new parameters:
    ```bash
    python -m src.penguin_classifier.modeling.train
    ```
    This updates `models/pipeline.joblib` and `reports/metrics.json`.

3.  **Run the App:**
    ```bash
    python -m src.penguin_classifier.app
    ```

---

## Model Information

The classification model is a **Logistic Regression** pipeline optimized via 5-fold Cross-Validation.

* **Preprocessing:**
    * *Numerical Features:* Scaled using `StandardScaler`.
    * *Categorical Features:* Encoded using `OneHotEncoder`.
* **Performance:**
    * Metrics (Accuracy, F1-Score, Precision, Recall) are automatically tracked in `reports/metrics.json` after every training run.
    * Current Test Accuracy: **>98%** (depending on the random seed).

---

## Troubleshooting

**Problem: "Port 8050 is already in use"**
* **Cause:** Another instance of the app is already running.
* **Solution:** Close any open terminal windows running the app or run `docker stop $(docker ps -q)` to kill all containers.

**Problem: Docker script closes immediately**
* **Solution:** Open Docker Desktop and ensure the engine is running.