# Tests Folder - Test Suite Documentation

## Overview

The `tests/` folder contains comprehensive unit and integration tests for the Ramya application.

---

## Folder Structure

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Shared pytest fixtures
├── test_config.py                 # Configuration tests
├── test_security_utils.py          # Security utilities tests
├── test_security_config.py         # Security config tests
├── test_rate_limiter.py           # Rate limiter tests
├── test_logging_config.py         # Logging tests
├── test_auth_routes.py            # Auth routes tests
├── test_health_routes.py          # Health endpoint tests
└── README.md                      # This file
```

---

## Test Files

| Test File | Description | Status |
|-----------|-------------|--------|
| `test_config.py` | Configuration loading and validation | ✅ Complete |
| `test_security_utils.py` | Input sanitization, rate limiter | ✅ Complete |
| `test_rate_limiter.py` | Redis rate limiter | ✅ Complete |
| `test_security_config.py` | Security headers, CORS | ✅ Complete |
| `test_logging_config.py` | JSON logging, formatters | ✅ Complete |
| `test_auth_routes.py` | Login, register, logout | ✅ Complete |
| `test_health_routes.py` | Health check endpoints | ✅ Complete |

---

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-flask pytest-mock
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_config.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

---

## Test Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `app` | Flask application for testing |
| `client` | Flask test client |
| `runner` | Flask CLI runner |
| `authenticated_client` | Authenticated test client |
| `mock_redis` | Mocked Redis client |
| `mock_chromadb` | Mocked ChromaDB |
| `mock_openrouter` | Mocked OpenRouter API |

---

## Test Categories

### 1. Unit Tests
- Configuration tests
- Security utilities tests
- Logging tests

### 2. Integration Tests
- Auth routes tests
- Health endpoint tests
- Chat routes tests (future)

---

## Adding New Tests

1. Create test file: `tests/test_<module_name>.py`
2. Import necessary fixtures from `conftest.py`
3. Write test functions with `test_` prefix
4. Run tests to verify

Example:
```python
def test_example(client):
    response = client.get('/health')
    assert response.status_code == 200
```

---

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-flask
      - name: Run tests
        run: pytest tests/ -v
```

---

## Test Coverage

Current coverage areas:
- Configuration management
- Security utilities
- Rate limiting
- Authentication routes
- Health endpoints
- Logging

---

## Notes

- Tests use mocking for external services (Redis, ChromaDB, OpenRouter)
- In-memory rate limiter is used for testing
- Test database is ephemeral (resets on restart)
