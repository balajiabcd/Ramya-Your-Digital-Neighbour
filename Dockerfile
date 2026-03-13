# =============================================================================
# Ramya: Your Digital Neighbour - Docker Configuration
# =============================================================================
# Build: docker build -t ramya-app .
# Run: docker-compose up -d
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2: Production
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=Production \
    PORT=8080

# Create non-root user and group for security
RUN groupadd --gid 1000 ramya && \
    useradd --uid 1000 --gid ramya --shell /bin/bash --create-home ramya

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=ramya:ramya . .

# Create necessary directories for persistent data
RUN mkdir -p /app/ramya_memory_db /app/logs /app/static/audio && \
    chown -R ramya:ramya /app

# Switch to non-root user
USER ramya

# Expose port
EXPOSE 8080

# Health check - will be implemented in Phase 6
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Start application with gunicorn
# - 4 workers for concurrent request handling
# - 120s timeout for long-running AI responses
# - Access/error logs to stdout for docker logging
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
