# Use the specified base image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /usr/src/app

# Install necessary dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    gfortran \
    build-base \
    bash \
    cmake \
    git

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Run the application
CMD ["python", "src/bot.py"]
