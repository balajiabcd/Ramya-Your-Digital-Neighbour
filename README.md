# Ramya: Your Digital Neighbour

> **Your Digital Neighbour** -- A production-grade AI digital neighbour with memory, multi-model fallback, and enterprise security.

[![Build Status](https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

---

## Quick Links

| Guide                                   | Description                    |
| --------------------------------------- | ------------------------------ |
| **[INSTALL.md](./INSTALL.md)**       | How to install and run the app |
| **[USER_GUIDE.md](./USER_GUIDE.md)** | How to use the app             |

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [AI Engine &amp; RAG Pipeline](#ai-engine--rag-pipeline)
- [Security](#security)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Logging &amp; Monitoring](#logging--monitoring)
- [Future Roadmap](#future-roadmap)

---

Ramya Bot is an AI-powered conversational assistant that combines the power of **15 large language models** with **Retrieval-Augmented Generation (RAG)** to deliver intelligent, context-aware responses. It remembers past conversations using a local **ChromaDB** vector database, streams responses to audio, and is secured with local **Username/Password authentication** and per-user data isolation.

The entire stack is containerized with Docker, tested with pytest, and automated via GitHub Actions.

---

## Key Features

| Feature                         | Description                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------- |
| **Multi-Model Fallback**  | 32 AI models ranked by priority; automatic failover guarantees near-100% uptime |
| **RAG Long-Term Memory**  | ChromaDB stores and retrieves semantically relevant past conversations          |
| **Real-Time Streaming**   | Token-by-token SSE streaming with a stop-generation button                      |
| **Local Auth System**     | Secure username and password based registration and login                       |
| **Rate Limiting**         | Sliding-window limiter (5 req/60s) with Redis support                           |
| **Security Headers**      | Robust CSP and security headers via Flask-Talisman                              |
| **Cloud Voice (TTS)**     | High-quality streaming voice using Microsoft Edge TTS                           |
| **Voice Input (STT)**     | Fast transcription using Faster-Whisper                                         |
| **Dockerized Deployment** | Multi-stage Dockerfile with non-root user and persistent volumes                |
| **CI/CD Pipeline**        | GitHub Actions runs automated tests on every push                               |

---

## System Architecture

![System Architecture](static\app_architeture.png)

### Layer Breakdown

| Layer                  | Component                                     | Responsibility                                           |
| ---------------------- | --------------------------------------------- | -------------------------------------------------------- |
| **Presentation** | `templates/`, `static/`                   | Glassmorphic UI, streaming audio, real-time chat display |
| **Application**  | `src/routes/`, `app.py`                   | Modular routing, authentication controllers, middleware  |
| **Intelligence** | `src/a_ai_engine.py`                        | AI orchestration, model fallback, RAG pipeline           |
| **Audio**        | `src/routes/n_tts.py`, `src/routes/o_stt` | Edge TTS streaming and Whisper STT processing            |
| **Data**         | `src/c_rag_engine.py`                       | ChromaDB vector storage and semantic search              |
| **Security**     | `src/d_security_utils.py`                   | Input sanitization, injection detection, rate limiting   |

---

## Project Structure

```
ramya-bot/
|
|-- app.py                          # Flask application entry point
|-- run_prod.py                     # Production server (Waitress WSGI)
|-- requirements.txt                # Python dependencies
|-- Dockerfile                      # Multi-stage container build
|-- docker-compose.yml              # Orchestration with persistent volumes
|-- .env                            # API keys & secrets (gitignored)
|-- .gitignore                      # Git exclusion rules
|
|-- src/                            # Modularized core logic
|   |-- routes/                     # Blueprint-based API endpoints
|   |   |-- k_auth.py               # Authentication (Register/Login)
|   |   |-- m_chat.py               # Chat session management
|   |   |-- health.py               # Monitoring & Prometheus metrics
|   |-- models/                     # Data models
|   |   |-- user_model.py           # User management with bcrypt
|   |-- a_ai_engine.py              # LLM orchestration & fallback
|   |-- c_rag_engine.py             # Memory retrieval logic
|   |-- d_security_utils.py         # Validation & injection detection
|   |-- config.py                   # Centralized configuration management
|
|-- templates/
|   |-- index.html                  # Main chat interface
|   |-- login.html                  # Local login & registration
|   |-- home.html                   # User dashboard / chat selection
|
|-- static/
|   |-- global.css                  # Shared CSS tokens
|   |-- chat.css                    # Chat-specific styles
|   |-- script.js                   # Frontend JS (streaming, TTS/STT)
|
|-- tests/
|   |-- test_security_utils.py       # Security validation tests
|   |-- test_app_logic.py           # Core application tests
```

---

## Technology Stack

| Technology     | Version | Role                        |
| -------------- | ------- | --------------------------- |
| Python         | 3.11    | Core runtime                |
| Flask          | 3.1.3   | Web framework               |
| ChromaDB       | 1.5.2   | Vector database for RAG     |
| Edge TTS       | 7.2.7   | Cloud-grade voice streaming |
| Faster-Whisper | 1.2.1   | Fast local speech-to-text   |
| Flask-Talisman | 1.0.0   | Security headers management |
| Bcrypt         | 4.1.2   | Password hashing            |
| Redis          | 7.3.0   | Production rate limiting    |
| Waitress       | 3.0.0   | Production WSGI server      |
| Prometheus     | 0.24.1  | Metrics & monitoring        |
| Docker         | latest  | Containerization            |
| GitHub Actions | v5      | CI/CD automation            |

---

## Getting Started

### Prerequisites

- Python 3.11+
- An [OpenRouter](https://openrouter.ai/) API key
- Redis (optional, for production rate limiting)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour.git
cd ramya-bot

# 2. Create virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
source venv/bin/activate

# 3. Configure environment variables
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY and SECRET_KEY
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SECRET_KEY=your-secure-random-secret-key
```

### Running Locally

```bash
# Development mode (with auto-reload)
python app.py

# Production mode (Waitress, 6 threads)
python run_prod.py
```

---

## Configuration

### config.yaml

Model rankings and app settings are externalized into `config.yaml` (gitignored for security):

```yaml
models:
  ranking:
    1: "meta-llama/llama-3.3-70b-instruct:free"
    2: "nousresearch/hermes-3-llama-3.1-405b:free"
    3: "google/gemma-3-27b-it:free"
    # ... up to 15 models

settings:
  app_name: "Ramya Bot"
  debug_mode: true
```

If this file is missing, the engine falls back to a hardcoded default ranking.

### Environment-Driven Configuration

| Variable          | Default                          | Description                       |
| ----------------- | -------------------------------- | --------------------------------- |
| `PORT`          | `5000` (dev) / `8080` (prod) | Server port                       |
| `APP_ENV`       | `Development`                  | `Development` or `Production` |
| `CHROMADB_PATH` | `ramya_memory_db`              | ChromaDB storage path             |
| `LOG_DIR`       | `logs`                         | Log file directory                |
| `LOG_FILE_NAME` | `ramya_prod.log`               | Log file name                     |
| `CONFIG_PATH`   | Auto-detected                    | Path to config.yaml               |

---

## AI Engine & RAG Pipeline

### Model Fallback System

The `RamyaBot._call_with_fallback()` method iterates through 15 ranked models. If a model returns an error (rate limit, timeout, or API failure), it automatically retries with the next model:

```
Request --> Model #1 (llama-3.3-70b) --> FAIL
        --> Model #2 (hermes-405b)   --> FAIL
        --> Model #3 (gemma-3-27b)   --> SUCCESS --> Response
```

### RAG Memory Flow

```
1. User sends message
2. rag_engine.py queries ChromaDB for semantically similar past interactions
3. Top 2 most recent memories are injected into the AI prompt
4. AI generates a response with full conversation context
5. Response + conversation summary are saved back to ChromaDB
```

### Conversation Summarization

After each exchange, a secondary AI call (Google Gemini) generates a concise summary. This summary is stored alongside the raw interaction, enabling efficient retrieval for future queries without needing to replay entire conversation histories.

### User Isolation

Each user's data is namespaced with a prefix derived from their username:

```
user_johndoe_chatname  -->  Belongs to john
user_janedoe_chatname  -->  Belongs to jane
```

This ensures complete data privacy between authenticated users.

---

## Security

### Defense Layers

```
Layer 1: Local Credential Auth     --> Username/Password login required
Layer 2: Input Sanitization        --> HTML tags stripped, whitespace trimmed
Layer 3: Prompt Injection Detection --> Adversarial patterns blocked (400)
Layer 4: Rate Limiting             --> 5 requests / 60 seconds (Redis-backed)
Layer 5: Password Security         --> Bcrypt hashing with random salt
Layer 6: Security Headers          --> XSS, Clickjacking, MIME-sniffing protection
Layer 7: CSRF & Session Protection --> Secure cookie management
Layer 8: Per-User Data Isolation   --> Namespaced ChromaDB collections
```

### Prompt Injection Patterns Blocked

```python
PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"your (secret )?instructions",
    r"forget (everything )?i said",
    r"new (role|persona)"
]
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

**Trigger:** Push to `main` or pull request targeting `main`

```
+----------+     +------------+     +--------+     +---------+
| Checkout | --> | Install    | --> | Lint   | --> | Test    |
|          |     | Deps       |     | Flake8 |     | pytest  |
+----------+     +------------+     +--------+     +---------+
```

**Stages:**

1. **Checkout** -- `actions/checkout@v4`
2. **Python Setup** -- `actions/setup-python@v5` (Python 3.10)
3. **Dependencies** -- `pip install -r requirements.txt`
4. **Lint** -- Flake8 with critical errors as blockers, style warnings as info
5. **Test** -- Full pytest suite with a mocked `.env`

---

## Deployment

### Local Self-Hosted Setup (Docker)

Run Ramya on your own machine with your own API key:

```bash
# 1. Clone the repository
git clone https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour.git
cd Ramya-Your-Digital-Neighbour

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env and add your OpenRouter API key
# Get a free key from https://openrouter.ai/
# Generate a secret key: python -c "import secrets; print(secrets.token_hex(32))"

# 4. Start the application
docker-compose up -d --build

# 5. Open in browser
# Visit http://localhost:8080
```

**First-time setup:**

- Edit `.env` and set `OPENROUTER_API_KEY` (get from https://openrouter.ai/)
- Set `SECRET_KEY` to a secure random string

**Data persistence:** Your chats and memory are stored in Docker volumes and persist across restarts.

### Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Dockerfile Highlights

- **Multi-stage build**: Builder stage compiles wheels, final stage is clean
- **Non-root user**: Application runs as `ramya` user (not root)
- **Built-in healthcheck**: Pings `/status` every 30s via Python's `http.client`
- **Base image**: `python:3.11-slim` for minimal attack surface

### Data Persistence (docker-compose.yml)

```yaml
volumes:
  ramya_memories:   # ChromaDB data survives restarts
  ramya_logs:       # Log files survive restarts
```

### Cloud Platforms

| Platform          | Method                                               |
| ----------------- | ---------------------------------------------------- |
| Render            | **Docker (Recommended)** - Use `render.yaml` |
| Heroku            | `git push` (uses `Procfile`)                     |
| AWS / GCP / Azure | `docker-compose up -d`                             |
| Any VPS           | `docker-compose up -d`                             |

### Setting up on Render

1. **Connect GitHub:** Link your repository to Render.
2. **Use Blueprints:** Render will detect the `render.yaml` file automatically.
3. **Environment Variables:**
   - `OPENROUTER_API_KEY`: Your OpenRouter key (Found in OpenRouter settings).
   - `SECRET_KEY`: Automatically generated (or set manually).
4. **Persistence:**
   - On the **Free Tier**, the `ramya_memory_db` is ephemeral and will reset on every redeploy.
   - For long-term memory, upgrade to a **Starter** plan and enable the **Persistent Disk** (see `render.yaml`).

> **Remember:** Set your `OPENROUTER_API_KEY`, `GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET` as environment variables on the platform.

---

## API Endpoints

| Method   | Route                    | Auth | Description                              |
| -------- | ------------------------ | ---- | ---------------------------------------- |
| `GET`  | `/`                    | Yes  | Home page (redirected from login)        |
| `GET`  | `/login`               | No   | Login page                               |
| `POST` | `/login`               | No   | Authenticate user                        |
| `POST` | `/register`            | No   | Register new account                     |
| `GET`  | `/logout`              | No   | Clears session and redirects             |
| `POST` | `/start_chat`          | Yes  | Creates a new chat session               |
| `GET`  | `/chats`               | Yes  | Lists all user's chat sessions           |
| `POST` | `/delete_chat`         | Yes  | Deletes a chat session                   |
| `GET`  | `/chat_history/<name>` | Yes  | Retrieves chat history                   |
| `POST` | `/chat`                | Yes  | Sends message, returns streamed response |
| `POST` | `/change_password`     | Yes  | Update user password                     |
| `GET`  | `/tts`                 | Yes  | Generate streaming voice for text        |
| `POST` | `/stt`                 | Yes  | Transcribe audio to text                 |
| `GET`  | `/health/status`       | No   | Detailed health and system status        |

---

## Testing

### Running Tests

```bash
# Run full suite
pytest tests/ -v

# Run a specific test
pytest tests/test_app_logic.py::test_status_endpoint -v
```

### Test Suite

| Test                                   | What It Verifies                                      |
| -------------------------------------- | ----------------------------------------------------- |
| `test_index_page`                    | Home page returns 200 with "Ramya" in response        |
| `test_status_endpoint`               | `/status` returns valid JSON with dependency health |
| `test_security_injection_protection` | Injection attacks are blocked with 400                |
| `test_invalid_chat_request`          | Empty/malformed requests return 400                   |
| `test_chat_rate_limiting`            | 6th rapid request is throttled with 429               |

---

## Logging & Monitoring

### Production Logging

- **Handler**: `RotatingFileHandler`
- **Location**: `logs/ramya_prod.log`
- **Rotation**: 5 MB per file, 10 backup files max
- **Format**: `%(asctime)s - %(levelname)s - %(message)s`

### Health Check

```bash
curl http://localhost:8080/status
```

```json
{
  "status": "healthy",
  "dependencies": {
    "database": {"status": "online"},
    "ai_engine": {"status": "online"}
  }
}
```

---

## Future Roadmap

- [ ] **Frontend Health Dashboard** -- Real-time dependency status in the UI
- [ ] **Advanced Test Coverage** -- Integration tests for streaming, RAG pipeline
- [ ] **Multi-Provider OAuth** -- GitHub and Microsoft SSO support
- [ ] **Admin Analytics Panel** -- User engagement metrics dashboard
- [ ] **Conversation Export** -- Download chat history as PDF/Markdown
- [ ] **Dynamic Model Ranking** -- Auto-reorder models based on live performance data

---

<p align="center">
  <b>Built with care by the Ramya Bot Team</b><br>
  <i>Making AI feel like a neighbour, not a machine.</i>
</p>
