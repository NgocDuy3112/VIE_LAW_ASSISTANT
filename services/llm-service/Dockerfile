FROM python:3.11-alpine

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set workdir
WORKDIR /src

# Install system dependencies
RUN apk add --no-cache curl

# Copy requirements first to use Docker layer cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code into container
COPY app/ .

# Copy entrypoint.sh into container
COPY entrypoint.sh .

# Ensure entrypoint.sh is executable
RUN chmod +x /src/entrypoint.sh

# Use entrypoint
ENTRYPOINT ["/src/entrypoint.sh"]