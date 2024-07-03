# Use the specified base image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /usr/src/app

# Install necessary dependencies including Rust and curl
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    make \
    curl

# Install Poetry in an isolated environment
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application code to the working directory
COPY . .

# Run the application
CMD ["poetry", "run", "python", "src/bot.py"]
