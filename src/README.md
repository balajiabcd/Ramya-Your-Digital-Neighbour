# Src Folder - Source Code Documentation

## Overview

The `src/` folder contains all the core application logic, engines, routes, and utilities for the Ramya AI chatbot application. This is the brain of the application.

---

## Folder Structure

```
src/
├── __init__.py              # Package initialization
├── a_ai_engine.py          # AI chatbot engine with OpenRouter
├── b_stt_engine.py          # Speech-to-Text engine (Whisper)
├── c_rag_engine.py          # RAG (Retrieval-Augmented Generation)
├── config.py                # Centralized configuration management
├── d_security_utils.py       # Security utilities
├── e_cache.py               # Caching functionality
├── f_auth.py                # Authentication decorator
├── h_config.py              # Legacy config (deprecated)
├── j_utils.py               # Utility functions
├── logging_config.py        # Logging configuration
├── p_error_handlers.py       # Error handlers
├── rate_limiter.py          # Redis-based rate limiting
├── security_config.py       # Security headers configuration
├── middleware/               # Request/response middleware
│   ├── __init__.py
│   └── logging_middleware.py
├── models/                  # Data models
│   ├── __init__.py
│   └── user_model.py       # User authentication model
└── routes/                  # Flask blueprints/routes
    ├── __init__.py
    ├── health.py           # Health check endpoints
    ├── k_auth.py           # Authentication routes
    ├── l_home.py           # Home page route
    ├── m_chat.py           # Chat functionality
    ├── n_tts.py            # Text-to-Speech
    └── o_stt.py            # Speech-to-Text
```

---

## Core Engines

### 1. AI Engine (`a_ai_engine.py`)

**Purpose:** Main chatbot logic using OpenRouter API with model fallback

**Key Features:**
- Integration with OpenRouter API (36+ free models)
- Automatic model fallback when primary model fails
- Daily model reset capability
- Streaming responses support
- Multi-model ranking system

**Key Classes:**
- `RamyaBot` - Main chatbot class

**Functions:**
- `get_bot()` - Factory function to get bot instance

---

### 2. STT Engine (`b_stt_engine.py`)

**Purpose:** Speech-to-Text using Faster Whisper

**Key Features:**
- Local Whisper model execution
- English language optimization
- Audio transcription from bytes

**Key Classes:**
- `STTEngine` - Speech recognition engine

---

### 3. RAG Engine (`c_rag_engine.py`)

**Purpose:** Retrieval-Augmented Generation for memory

**Key Features:**
- ChromaDB integration for vector storage
- Semantic search over conversation history
- Memory persistence

---

## Configuration

### `config.py` (NEW - Phase 4)

**Purpose:** Centralized environment-based configuration

**Features:**
- Environment-aware settings (Development/Staging/Production)
- Validation on startup
- Secure defaults per environment

**Key Classes:**
- `AppConfig` - Main configuration dataclass
- `SecurityConfig` - Security settings
- `APIConfig` - API keys and secrets
- `PathsConfig` - File paths
- `ModelConfig` - AI model settings

---

### `security_config.py`

**Purpose:** Security headers and CORS configuration

**Functions:**
- `get_security_headers()` - Flask-Talisman configuration
- `get_cors_config()` - CORS settings
- `get_rate_limit_config()` - Rate limit settings

---

### `d_security_utils.py`

**Purpose:** Security utilities

**Features:**
- Input sanitization
- Injection detection
- API key validation
- Rate limiting (in-memory fallback)

**Key Classes:**
- `RateLimiter` - Token bucket rate limiter

---

## Utilities

### `e_cache.py`
Caching functionality for the application.

### `j_utils.py`
General utility functions including:
- URL generation with versioning
- Bot instance management

### `logging_config.py` (NEW - Phase 5)
- JSON and plain text formatters
- File rotation handlers
- Environment-aware log levels

---

## Middleware (`middleware/`)

### `logging_middleware.py` (NEW - Phase 5)

**Purpose:** Request/response logging

**Features:**
- Request ID generation and tracking
- Response duration tracking
- User identification in logs
- X-Request-ID header injection

---

## Models (`models/`)

### `user_model.py` (NEW - Phase 3)

**Purpose:** User authentication and management

**Features:**
- Password hashing with bcrypt
- User creation/verification
- ChromaDB storage
- Password update capability

**Key Classes:**
- `UserModel` - User data management

---

## Routes (`routes/`)

### `health.py` (NEW - Phase 6)

**Purpose:** Health monitoring endpoints

**Endpoints:**
| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic liveness |
| `/health/live` | Kubernetes liveness |
| `/health/ready` | Readiness probe |
| `/health/status` | Detailed status |
| `/metrics` | Prometheus metrics |

---

### `k_auth.py` (MODIFIED - Phase 3)

**Purpose:** Authentication routes

**Endpoints:**
| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/register` | POST | User registration |
| `/change_password` | POST | Password change |
| `/session` | GET | Session check |

---

### `l_home.py`

**Purpose:** Home page route

**Endpoints:**
| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/` | GET | Index page |
| `/home` | GET | Home page (authenticated) |

---

### `m_chat.py`

**Purpose:** Chat functionality

**Endpoints:**
| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/start_chat` | POST | Start new chat |
| `/delete_chat` | POST | Delete chat |
| `/chat_history/<name>` | GET | Get chat history |
| `/send_message` | POST | Send message & get AI response |
| `/stream_chat` | GET | Stream AI responses |

**Features:**
- Redis-based rate limiting (with fallback)
- Input sanitization
- Injection detection

---

### `n_tts.py`

**Purpose:** Text-to-Speech using Edge TTS

**Endpoints:**
| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/tts` | POST | Generate TTS audio |
| `/tts_stream` | POST | Stream TTS audio |

**Features:**
- Multiple voice options
- Rate and pitch control
- Streaming support

---

### `o_stt.py`

**Purpose:** Speech-to-Text

**Endpoints:**
| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/stt` | POST | Transcribe audio |

**Features:**
- Faster Whisper integration
- Audio validation

---

## Error Handling (`p_error_handlers.py`)

**Purpose:** Global error handlers

**Handled Errors:**
- 400 - Bad Request
- 401 - Unauthorized
- 403 - Forbidden
- 404 - Not Found
- 429 - Rate Limited
- 500 - Internal Server Error
- 503 - Service Unavailable

---

## Dependencies Flow

```
User Request
    ↓
Routes (k_auth, m_chat, n_tts, etc.)
    ↓
Middleware (logging, security)
    ↓
Engines (AI, STT, RAG)
    ↓
Models (User, ChromaDB)
    ↓
External Services (OpenRouter, Edge TTS, Whisper)
```

---

## Important Notes

1. **Naming Convention:** Route files are prefixed alphabetically (`k_`, `l_`, `m_`, etc.) to maintain order

2. **Phase Additions:**
   - Phase 2: security_config.py, rate_limiter.py
   - Phase 3: models/user_model.py, k_auth.py updates
   - Phase 4: config.py
   - Phase 5: logging_config.py, middleware/
   - Phase 6: health.py

3. **Security:** All routes (except /login, /register, /health) require authentication via `@login_required` decorator

4. **Rate Limiting:** Chat, TTS, and STT endpoints have rate limiting enabled

---

## Integration Points

| Component | Integration |
|-----------|------------|
| ChromaDB | Memory storage |
| OpenRouter | AI responses |
| Edge TTS | Voice output |
| Faster Whisper | Voice input |
| Redis | Rate limiting (optional) |

---

For more details, see the main project documentation or PRODUCTION_DEPLOYMENT.md
