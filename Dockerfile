# ==========================================
# STAGE 1: Builder (Heavy, contains compilers)
# ==========================================
FROM python:3.11-slim as builder

ENV POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    # Erstellt .venv direkt im Projekt für sauberen Transfer zu Stage 2
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# Install compilers & Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       build-essential \
       cmake \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies (inkl. phik Compilation) into /app/.venv
RUN poetry install --without dev --no-root

# ==========================================
# STAGE 2: Production (Minimal & Secure)
# ==========================================
FROM python:3.11-slim

LABEL maintainer="Erik Reitsam"
LABEL description="Penguin Classifier App (Poetry)"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . .

EXPOSE 8050

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "src.penguin_classifier.app:server"]
