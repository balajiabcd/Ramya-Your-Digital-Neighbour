# Phase 1: Docker Support

## Context
Containerize the Ramya application for consistent deployment across environments. Docker enables easy scaling, reproducibility, and isolation.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- No Docker support
- Runs directly on host with `python app.py` or `python run_prod.py`
- Dependencies installed in local venv

## Brief Plan
1. Create `.dockerignore` to exclude unnecessary files
2. Create `Dockerfile` with Python 3.11, non-root user
3. Create `docker-compose.yml` to orchestrate services
4. Update `.env` for Docker environment paths
5. Test the Docker setup

---

## Detailed Step-by-Step Implementation

### Step 1: Create `.dockerignore`

Create file `.dockerignore` in project root to exclude unnecessary files from Docker build context:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.py[cod]
*$py.class

# Virtual environments
venv/
.venv/
env/
ENV/
env.bak/
venv.bak/

# Git
.git/
.gitignore

# Documentation
*.md
LICENSE
README*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Application specific
ramya_memory_db/
static/audio/
*.mp3
*.wav

# Testing
.pytest_cache/
htmlcov/
.coverage
```

---

### Step 2: Create `Dockerfile`

Create `Dockerfile` in project root with multi-stage build:

```dockerfile
# =============================================================================
# Stage 1: Builder
# =============================================================================
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


# =============================================================================
# Stage 2: Production
# =============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=Production \
    PORT=8080

# Create non-root user and group
RUN groupadd --gid 1000 ramya && \
    useradd --uid 1000 --gid ramya --shell /bin/bash --create-home ramya

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=ramya:ramya . .

# Create necessary directories
RUN mkdir -p /app/ramya_memory_db /app/logs /app/static/audio && \
    chown -R ramya:ramya /app

# Switch to non-root user
USER ramya

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Start application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
```

**Key Features:**
- Multi-stage build for smaller image
- Non-root user (security best practice)
- Virtual environment for clean dependency isolation
- Health check included
- Gunicorn for production-grade WSGI server

---

### Step 3: Create `docker-compose.yml`

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  # Main Ramya Application
  ramya:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ramya-app
    restart: unless-stopped
    ports:
      - "${RAMYA_PORT:-8080}:8080"
    environment:
      - APP_ENV=Production
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - CHROMADB_PATH=/app/ramya_memory_db
      - LOG_DIR=/app/logs
      - PORT=8080
    volumes:
      - ramya_data:/app/ramya_memory_db
      - ramya_audio:/app/static/audio
      - ramya_logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ramya-network

  # Redis (Optional - for Phase 2: Production Security)
  # Uncomment to enable Redis for rate limiting
  # redis:
  #   image: redis:7-alpine
  #   container_name: ramya-redis
  #   restart: unless-stopped
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   networks:
  #     - ramya-network
  #   command: redis-server --appendonly yes

networks:
  ramya-network:
    driver: bridge

volumes:
  ramya_data:
    driver: local
  ramya_audio:
    driver: local
  ramya_logs:
    driver: local
  # redis_data:
  #   driver: local
```

---

### Step 4: Update `.env` for Docker

Modify `.env` to ensure Docker-compatible paths:

```env
# API Keys & Secrets
OPENROUTER_API_KEY="your-api-key-here"
SECRET_KEY="your-production-secret-key-min-32-chars"

# Application Mode
APP_ENV=Production
PORT=8080

# File Paths (Docker container paths)
CHROMADB_PATH=/app/ramya_memory_db
LOG_DIR=/app/logs

# Optional: Redis (uncomment when enabling Redis)
# REDIS_URL=redis://redis:6379/0

# Model Rankings (keep existing)
MODEL_RANKING='{"1": "meta-llama/llama-3.3-70b-instruct:free", ...}'
```

---

### Step 5: Test the Docker Setup

#### 5.1 Build the Docker Image
```bash
docker build -t ramya-app .
```

#### 5.2 Run with Docker Compose
```bash
docker-compose up -d --build
```

#### 5.3 Verify Container is Running
```bash
# Check container status
docker ps

# View logs
docker-compose logs -f ramya

# Check health
curl http://localhost:8080/health
```

#### 5.4 Test the Application
- Open browser: `http://localhost:8080`
- Login page should load
- Test basic functionality

#### 5.5 Stop the Application
```bash
docker-compose down
```

---

### Step 6: Additional Optimizations (Future Phases)

| Optimization | Phase | Description |
|--------------|-------|-------------|
| Multi-stage build optimization | Phase 1 | Already included in Dockerfile |
| Redis for rate limiting | Phase 2 | Uncomment Redis in docker-compose.yml |
| Nginx reverse proxy | Phase 7 | Add nginx service |
| SSL/TLS certificates | Phase 7 | Let's Encrypt integration |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `.dockerignore` | Create | Exclude unnecessary files |
| `Dockerfile` | Create | Container image definition |
| `docker-compose.yml` | Create | Orchestration configuration |
| `.env` | Modify | Add Docker-compatible paths |

---

## Verification Checklist

- [ ] `.dockerignore` created with all exclusions
- [ ] `Dockerfile` builds successfully
- [ ] Non-root user (ramya) is used
- [ ] `docker-compose up` starts without errors
- [ ] Health check passes
- [ ] Application accessible at `http://localhost:8080`
- [ ] Volumes persist data between restarts
- [ ] Logs accessible in volume

---

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep 8080
   # Change port in docker-compose.yml
   ```

2. **Permission denied errors**
   - Ensure `.dockerignore` excludes problematic files
   - Check volume permissions

3. **Health check failing**
   - Verify the `/health` endpoint exists (Phase 6)
   - Increase `start_period` in health check

4. **Out of memory**
   - Reduce gunicorn workers: `--workers 2`
   - Use smaller Docker resources allocation

---

## Next Phase

After completing Phase 1, proceed to **Phase 2: Production Security** to add:
- Flask-Talisman for security headers
- CORS configuration
- Redis-based rate limiting
