FROM python:alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies and curl for healthcheck
RUN apk add --no-cache curl && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]