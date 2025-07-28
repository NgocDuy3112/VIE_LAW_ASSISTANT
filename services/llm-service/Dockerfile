FROM python:3.11

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    cmake \
    libopenblas-dev \
    libomp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to cache dependencies
COPY requirements.txt .

# Install PyTorch separately with correct CPU wheels
RUN pip install --upgrade pip

# Then install the rest of the requirements
RUN pip install -r requirements.txt

# Copy app code
COPY app/ .

# Copy and make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x /src/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/src/entrypoint.sh"]