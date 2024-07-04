FROM python:3.10-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    make \
    cmake \
    ninja \
    curl

RUN pip install --no-cache-dir pipx && pipx ensurepath && pipx install poetry

ENV PATH="/root/.local/bin:/root/.local/pipx/venvs/poetry/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .

CMD ["poetry", "run", "python", "src/bot.py"]
