# Use the specified base image
FROM python:3.10-alpine

WORKDIR /usr/src/app

# Install necessary dependencies including Rust, curl, and pipx
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    make \
    curl \
    && pip install --no-cache-dir pipx

# Install Poetry using pipx
RUN pipx install poetry

# Add pipx and Poetry to PATH
ENV PATH="/root/.local/bin:/root/.local/pipx/venvs/poetry/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application code to the working directory
COPY . .

# Run the application
CMD ["poetry", "run", "python", "src/bot.py"]
