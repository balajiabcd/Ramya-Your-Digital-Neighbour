import os
from dotenv import load_dotenv
from flask import Flask

from src.routes.k_auth import auth_bp
from src.routes.l_home import home_bp
from src.routes.m_chat import chat_bp
from src.routes.n_tts import tts_bp
from src.routes.o_stt import stt_bp
from src.routes.health import health_bp
from src.p_error_handlers import errors_bp

from src.config import get_config, validate_config, ConfigError
from src.logging_config import setup_logging
from src.middleware.logging_middleware import setup_logging_middleware
from flask_talisman import Talisman
from src.security_config import get_security_headers
from src.routes.health import track_request_metrics




load_dotenv()

try:
    config = get_config()
    validate_config()
except ConfigError as e:
    print(f"CONFIG ERROR: {e}")
    import sys
    sys.exit(1)


# Validate API key explicitly
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("ERROR: OPENROUTER_API_KEY is missing. Please copy .env.example to .env and add your OpenRouter API key.")
    import sys
    sys.exit(1)
else:
    print("OK OPENROUTER_API_KEY is set")



app = Flask(__name__)

app.config['SECRET_KEY'] = config.security.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
app.config['SESSION_COOKIE_SECURE'] = config.security.session_cookie_secure
app.config['SESSION_COOKIE_HTTPONLY'] = config.security.session_cookie_httponly
app.config['SESSION_COOKIE_SAMESITE'] = config.security.session_cookie_samesite


# Setup logging
logger = setup_logging(app_env=config.env, log_dir=config.paths.log_dir)
logger.info(f"Ramya starting in {config.env} mode")
# Setup logging middleware
setup_logging_middleware(app)



try:
    security_headers = get_security_headers()
    
    Talisman(
        app,
        force_https=security_headers['force_https'],
        strict_transport_security=security_headers['strict_transport_security'],
        content_security_policy=security_headers['content_security_policy'],
        frame_options=security_headers['x_frame_options'],
        x_xss_protection=True if security_headers['x_xss_protection'] else False,
        x_content_type_options=True if security_headers['x_content_type_options'] else False,
        referrer_policy=security_headers['referrer_policy'],
        permissions_policy=security_headers['permissions_policy'],
    )
    print("Flask-Talisman security headers enabled")
    
except ImportError:
    print("WARNING: flask-talisman not installed. Run: pip install flask-talisman")



@app.context_processor
def override_url_for():
    from src.j_utils import dated_url_for
    return dict(url_for=dated_url_for)





app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(home_bp, url_prefix='')
app.register_blueprint(chat_bp, url_prefix='')
app.register_blueprint(tts_bp, url_prefix='')
app.register_blueprint(stt_bp, url_prefix='')
app.register_blueprint(health_bp, url_prefix='')
app.register_blueprint(errors_bp)

# Register metrics tracking

app.after_request(track_request_metrics)


if __name__ == '__main__':
    app.run(debug=config.debug, host=config.host, port=config.port)
