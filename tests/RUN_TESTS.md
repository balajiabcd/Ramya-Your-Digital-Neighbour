# Running Tests - Complete Guide

This guide explains how to run the test suite and what each test file does.

---

## Prerequisites

### Install Test Dependencies

```bash
pip install pytest pytest-flask pytest-mock
```

---

## Running Tests

### Run All Tests

```bash
# From project root
pytest tests/ -v
```

### Run Specific Test File

```bash
# Test configuration module
pytest tests/test_config.py -v

# Test security utilities
pytest tests/test_security_utils.py -v

# Test auth routes
pytest tests/test_auth_routes.py -v

# Test health routes
pytest tests/test_health_routes.py -v
```

### Run Tests with Coverage

```bash
# With HTML coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Tests Matching Pattern

```bash
# Run only tests containing "rate"
pytest tests/ -k "rate" -v

# Run only tests containing "auth"
pytest tests/ -k "auth" -v
```

---

## Test Files Overview

### 1. test_config.py

**What it tests:**
- Configuration loading from environment variables
- Development vs Production mode settings
- Port, CORS, and rate limit configurations
- Path configurations
- Session cookie security settings
- Config validation warnings

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_config_loads_development` | Verifies config loads in development mode |
| `test_config_loads_production` | Verifies config loads in production mode |
| `test_config_invalid_env` | Tests error handling for invalid APP_ENV |
| `test_config_port` | Tests custom port configuration |
| `test_config_cors_origins` | Tests CORS origins from env |
| `test_config_rate_limits` | Tests rate limit settings |
| `test_config_paths` | Tests path configurations |
| `test_config_validation_warnings` | Tests validation warnings |
| `test_session_cookie_secure_production` | Tests secure cookies in production |
| `test_session_cookie_insecure_development` | Tests cookies in development |

**Run:**
```bash
pytest tests/test_config.py -v
```

---

### 2. test_security_utils.py

**What it tests:**
- Input string sanitization
- SQL injection detection
- API key validation
- In-memory rate limiter functionality

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_sanitize_string_basic` | Tests basic string passes through |
| `test_sanitize_string_special_chars` | Tests XSS characters are removed |
| `test_sanitize_string_empty` | Tests empty string handling |
| `test_detect_injection_sql` | Tests SQL injection detection |
| `test_detect_injection_normal` | Tests normal text doesn't trigger |
| `test_validate_api_key_valid` | Tests valid API key format |
| `test_validate_api_key_empty` | Tests empty API key raises error |
| `test_validate_api_key_none` | Tests None API key raises error |
| `test_rate_limiter_allows_within_limit` | Tests requests within limit |
| `test_rate_limiter_blocks_over_limit` | Tests blocking over limit |
| `test_rate_limiter_different_keys` | Tests separate keys get separate limits |

**Run:**
```bash
pytest tests/test_security_utils.py -v
```

---

### 3. test_rate_limiter.py

**What it tests:**
- Redis-based rate limiter with fallback
- In-memory fallback when Redis unavailable
- Check rate limit function

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_rate_limiter_fallback_to_memory` | Tests fallback when Redis fails |
| `test_rate_limiter_creation` | Tests limiter can be created |
| `test_check_rate_limit_function` | Tests rate limit check function |
| `test_rate_limiter_in_memory_fallback` | Tests in-memory fallback logic |

**Run:**
```bash
pytest tests/test_rate_limiter.py -v
```

---

### 4. test_security_config.py

**What it tests:**
- Security headers for development/production
- CORS configuration
- Rate limiting configuration

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_get_security_headers_development` | Tests dev headers (no HTTPS) |
| `test_get_security_headers_production` | Tests prod headers (HTTPS enforced) |
| `test_get_cors_config_default` | Tests default CORS origins |
| `test_get_cors_config_custom` | Tests custom CORS origins |
| `test_get_rate_limit_config` | Tests rate limit config structure |

**Run:**
```bash
pytest tests/test_security_config.py -v
```

---

### 5. test_logging_config.py

**What it tests:**
- Logging setup for development and production
- JSON and plain text formatters
- Logger creation

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_setup_logging_development` | Tests logging setup in dev mode |
| `test_setup_logging_production` | Tests logging setup in prod mode |
| `test_get_logger` | Tests logger creation |
| `test_json_formatter` | Tests JSON formatter output |
| `test_plain_formatter` | Tests plain formatter output |

**Run:**
```bash
pytest tests/test_logging_config.py -v
```

---

### 6. test_auth_routes.py

**What it tests:**
- Login page loading
- User registration
- Input validation
- Session management
- Logout functionality

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_login_page_loads` | Tests login page returns 200 |
| `test_register_user_success` | Tests successful user registration |
| `test_register_user_invalid_username` | Tests short username rejected |
| `test_register_user_short_password` | Tests short password rejected |
| `test_session_endpoint_unauthenticated` | Tests unauthenticated session check |
| `test_session_endpoint_authenticated` | Tests authenticated session check |
| `test_logout_redirect` | Tests logout redirects |

**Run:**
```bash
pytest tests/test_auth_routes.py -v
```

---

### 7. test_health_routes.py

**What it tests:**
- All health check endpoints
- Prometheus metrics endpoint
- Liveness and readiness probes
- Status endpoint

**Test Functions:**
| Test | Description |
|------|-------------|
| `test_health_endpoint` | Tests /health returns healthy |
| `test_liveness_endpoint` | Tests /health/live returns alive |
| `test_readiness_endpoint` | Tests /health/ready checks dependencies |
| `test_status_endpoint` | Tests /health/status returns details |
| `test_metrics_endpoint` | Tests /metrics returns Prometheus format |
| `test_health_includes_timestamp` | Tests timestamp in response |

**Run:**
```bash
pytest tests/test_health_routes.py -v
```

---

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-flask pytest-mock
      
      - name: Run tests
        run: pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Debugging Tests

### Show Print Statements

```bash
pytest tests/ -v -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Drop into PDB on Failure

```bash
pytest tests/ --pdb
```

---

## Test Environment Variables

Tests automatically set:
```
APP_ENV=Testing
SECRET_KEY=test-secret-key-for-testing
CHROMADB_PATH=:memory:
```

---

## Coverage Report

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html

# View terminal report
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Common Issues

### Import Errors

If you get import errors, ensure you're in the project root:
```bash
cd /path/to/project
pytest tests/ -v
```

### Redis Connection Errors

Tests use in-memory fallback when Redis unavailable - these are expected warnings.

### ChromaDB Errors

Tests use mocked ChromaDB - real database not affected.
