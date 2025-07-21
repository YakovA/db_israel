# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install essential system tools only in the build stage
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to /install, not directly to site-packages
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Add dependencies from the previous stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Extra health: install tini to manage signals and zombie processes
RUN apt-get update && apt-get install -y --no-install-recommends tini && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Specify non-root user (optional — add USER in Dockerfile if you create one)
# USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
