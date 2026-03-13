# Ramya: Your Digital Neighbour - Production Deployment Guide

This guide covers deploying Ramya to production environments.

---

## Prerequisites

- Docker & Docker Compose installed
- Domain name (for SSL/TLS)
- OpenRouter API key
- Server with at least 2GB RAM

---

## Quick Start (Docker Compose)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd ramya
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with production values:

```env
APP_ENV=Production
SECRET_KEY=<generate-32-char-secret>
OPENROUTER_API_KEY=<your-api-key>
PORT=8080
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Build and Run

```bash
docker-compose up -d --build
```

### 4. Verify

```bash
curl http://localhost:8080/health
curl http://localhost:8080/health/ready
```

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `APP_ENV=Production`
- [ ] Configure `CORS_ALLOWED_ORIGINS` for your domain
- [ ] Enable SSL/TLS (see SSL Setup below)
- [ ] Use Redis for rate limiting in production

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | Yes | Set to `Production` |
| `SECRET_KEY` | Yes | 32+ character random string |
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `PORT` | No | Default: 8080 |
| `CORS_ALLOWED_ORIGINS` | Yes | Comma-separated allowed origins |
| `REDIS_URL` | No | Redis connection URL |
| `CHROMADB_PATH` | No | Path for ChromaDB data |

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: Reverse Proxy (nginx)

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
```

---

## Docker Production Commands

```bash
# Build
docker-compose build --no-cache

# Start
docker-compose up -d

# View logs
docker-compose logs -f ramya

# Restart
docker-compose restart ramya

# Update and redeploy
git pull
docker-compose up -d --build

# Stop
docker-compose down
```

---

## Backup & Recovery

### Backup ChromaDB

```bash
# Backup
docker exec ramya-app tar -czf /backup/chromadb.tar.gz /app/ramya_memory_db

# Copy to host
docker cp ramya-app:/app/ramya_memory_db ./backup/
```

### Restore

```bash
# Stop app
docker-compose stop ramya

# Restore
docker cp ./backup/ramya_memory_db ramya-app:/app/

# Start
docker-compose start ramya
```

---

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8080/health

# Readiness (includes dependency checks)
curl http://localhost:8080/health/ready

# Detailed status
curl http://localhost:8080/health/status
```

### Prometheus Metrics

```bash
curl http://localhost:8080/metrics
```

### Recommended Monitoring Stack

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Loki** - Log aggregation

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs ramya

# Check environment
docker-compose exec ramya env
```

### Out of memory

```bash
# Reduce gunicorn workers
# In Dockerfile, change: --workers 4 to --workers 2
```

### ChromaDB errors

```bash
# Reset ChromaDB
docker-compose down
rm -rf ramya_memory_db
docker-compose up -d
```

---

## Performance Tuning

### Gunicorn Workers

In Dockerfile:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
```

Recommended: `2 * CPU_CORES + 1`

### Resource Limits

In docker-compose.yml:
```yaml
services:
  ramya:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

---

## Docker Swarm / Kubernetes

For orchestration, see:
- `docker-compose.swarm.yml` - Docker Swarm config
- `k8s/` - Kubernetes manifests (if included)

---

## Support

- GitHub Issues: <your-repo>/issues
- Documentation: <your-repo>/README.md
