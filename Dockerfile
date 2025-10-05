# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install temporary build dependencies (Debian style)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        gcc \
        g++ \
        libffi-dev \
        libpq-dev \
        mariadb-client libmariadb-dev-compat libmariadb-dev \
        unixodbc-dev pkg-config make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Runtime environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false \
    STREAMLIT_SERVER_HEADLESS=true

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        mariadb-client libmariadb-dev-compat libmariadb-dev \
        unixodbc \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and app code
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
