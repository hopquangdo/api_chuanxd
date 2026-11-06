FROM python:3.11.7-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry-cache \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Ho_Chi_Minh

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999", "--workers", "1"]
