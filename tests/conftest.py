"""
Pytest configuration and shared fixtures for Ramya tests.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ['APP_ENV'] = 'Testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing'
os.environ['CHROMADB_PATH'] = 'test_db'


@pytest.fixture
def app():
    """Create Flask app for testing."""
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.config import get_config, reset_config
    reset_config()
    
    from flask import Flask
    import os
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
        
    from src.config import AppConfig
    config = AppConfig.from_env()
    app.config['SECRET_KEY'] = config.security.secret_key
    app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
    app.config['SESSION_COOKIE_SECURE'] = config.security.session_cookie_secure
    app.config['SESSION_COOKIE_HTTPONLY'] = config.security.session_cookie_httponly
    app.config['SESSION_COOKIE_SAMESITE'] = config.security.session_cookie_samesite
    
    from src.routes.k_auth import auth_bp
    from src.routes.health import health_bp
    from src.p_error_handlers import errors_bp
    
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(health_bp)
    app.register_blueprint(errors_bp)
    
    yield app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['user'] = {
            'username': 'testuser',
            'email': 'testuser@test.app'
        }
    return client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('src.rate_limiter.redis.Redis') as mock:
        redis_mock = MagicMock()
        redis_mock.ping.return_value = True
        redis_mock.zremrangebyscore.return_value = 0
        redis_mock.zcard.return_value = 0
        redis_mock.zadd.return_value = 1
        redis_mock.expire.return_value = True
        mock.from_url.return_value = redis_mock
        yield redis_mock


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB client."""
    with patch('src.c_rag_engine.chromadb.Client') as mock:
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = MagicMock()
        yield mock_client


@pytest.fixture
def mock_openrouter():
    """Mock OpenRouter API calls."""
    with patch('src.a_ai_engine.openai.OpenAI') as mock:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for tests."""
    return tmp_path
