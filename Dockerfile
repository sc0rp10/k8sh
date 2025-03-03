# Stage 1: Test
FROM python:3.11-slim AS test

WORKDIR /app

# Install necessary tools for testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Set environment variables for mock testing
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV K8SH_MOCK=1

# Run tests
RUN python -m pytest -n auto

# Stage 2: Package with FPM
FROM ruby:3.1-slim AS build

WORKDIR /app

# Install FPM and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install FPM
RUN gem install --no-document fpm

# Copy the source code
COPY . .

# Create directories for packaging
RUN mkdir -p /app/package/usr/lib/k8sh
RUN mkdir -p /app/package/usr/bin

# Copy application files to the package structure
RUN cp -r command k8s_client state utils main.py requirements.txt /app/package/usr/lib/k8sh/

# Create the launcher script
RUN echo '#!/bin/bash' > /app/package/usr/bin/k8sh && \
    echo 'cd /usr/lib/k8sh' >> /app/package/usr/bin/k8sh && \
    echo 'python3 main.py "$@"' >> /app/package/usr/bin/k8sh && \
    chmod +x /app/package/usr/bin/k8sh

# Create an after-install script to install Python dependencies
RUN echo '#!/bin/bash' > /app/after-install.sh && \
    echo 'pip3 install --no-cache-dir -r /usr/lib/k8sh/requirements.txt' >> /app/after-install.sh && \
    chmod +x /app/after-install.sh

# Build the package with FPM
RUN fpm \
    --input-type dir \
    --output-type deb \
    --name k8sh \
    --version 1.0.0 \
    --architecture all \
    --depends python3 \
    --depends python3-pip \
    --maintainer "K8sh Team <k8sh@example.com>" \
    --description "Kubernetes Terminal Emulator - A shell-like interface to Kubernetes" \
    --after-install /app/after-install.sh \
    --chdir /app/package \
    --package /app/k8sh.deb \
    .

# Create output directory for BuildKit
FROM scratch AS export-stage
COPY --from=build /app/k8sh.deb /
