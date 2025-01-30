# --------------> The build image
FROM python:3.12.3-bullseye AS builder_be

RUN pip install poetry==1.8.2 && poetry cache clear --all pypi

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /home/app

ARG BUILD_PACKAGES='\
    g++ \
    python3-dev \
    libpq-dev \
    libpq5 \
    '

RUN echo "Install build packages" && \
    apt-get update && \
    apt-get install -y --no-install-recommends $BUILD_PACKAGES && \
    rm -rf /var/lib/apt/lists/*

# Create a new user
RUN useradd -m app

COPY pyproject.toml ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# --------------> The runtime image
FROM python:3.12.3-slim-bullseye AS runtime

ARG RUNTIME_PACKAGES='\
    curl \
    wget \
    vim \
    python3-dev \
    libpq-dev \
    libpq5 \
    '

RUN echo "Install runtime packages" && \
    apt update && \
    apt install -y --no-install-recommends $RUNTIME_PACKAGES && \
    rm -rf /var/lib/apt/lists/*

# Create a new user
RUN useradd -m app
WORKDIR /home/app/

ENV VIRTUAL_ENV=/home/app/.venv \
    PATH="/home/app/.venv/bin:$PATH" \
    PYTHONPATH="$PYTHONPATH:/home/app" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder_be ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY --chown=app:app api ./api

# Set user
USER app

# Set the final working directory
WORKDIR /home/app
