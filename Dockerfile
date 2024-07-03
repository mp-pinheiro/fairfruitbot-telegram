# Use the specified base image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /usr/src/app

# Install Poetry and other necessary dependencies including Rust
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    make \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application code to the working directory
COPY . .

# Ensure the .env file is included in the working directory
COPY .env .env

# Run the application
CMD ["poetry", "run", "python", "src/bot.py"]
