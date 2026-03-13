"""
Security configuration for Ramya application.
Phase 2: Production Security
"""

import os


def get_security_headers():
    """
    Get security headers configuration based on environment.
    """
    is_production = os.getenv('APP_ENV') == 'Production'
    
    return {
        'force_https': is_production,
        'force_https_permanent': False,
        'strict_transport_security': 'max-age=31536000; includeSubDomains',
        'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: blob:; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self' https://openrouter.ai; media-src 'self' blob:;",
        'content_security_policy_report_uri': None,
        'content_security_policy_report_only': False,
        'content_security_policy_nonce_in': [],
        'x_frame_options': 'DENY',
        'x_xss_protection': '1; mode=block',
        'x_content_type_options': 'nosniff',
        'referrer_policy': 'strict-origin-when-cross-origin',
        'permissions_policy': 'geolocation=(), microphone=(), camera=()',
        'cross_origin_opener_policy': 'same-origin',
        'cross_origin_resource_policy': 'same-origin',
        'cross_origin_embedder_policy': 'require-corp',
    }


def get_cors_config():
    """
    Get CORS configuration.
    """
    allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    
    if not allowed_origins or allowed_origins == ['']:
        allowed_origins = ['http://localhost:8080', 'http://127.0.0.1:8080']
    
    return {
        'origins': allowed_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'expose_headers': ['Content-Length', 'Content-Type'],
        'supports_credentials': True,
        'max_age': 3600,
    }


def get_rate_limit_config():
    """
    Get rate limiting configuration.
    """
    return {
        'chat': {
            'limit': int(os.getenv('RATE_LIMIT_CHAT', '5')),
            'window': int(os.getenv('RATE_LIMIT_CHAT_WINDOW', '60')),
        },
        'tts': {
            'limit': int(os.getenv('RATE_LIMIT_TTS', '10')),
            'window': int(os.getenv('RATE_LIMIT_TTS_WINDOW', '60')),
        },
        'stt': {
            'limit': int(os.getenv('RATE_LIMIT_STT', '10')),
            'window': int(os.getenv('RATE_LIMIT_STT_WINDOW', '60')),
        },
    }


def get_session_config():
    """
    Get session security configuration.
    """
    return {
        'cookie_name': 'ramya_session',
        'cookie_secure': os.getenv('APP_ENV') == 'Production',
        'cookie_httponly': True,
        'cookie_samesite': 'Lax' if os.getenv('APP_ENV') == 'Production' else 'None',
        'permanent_session_lifetime': 3600 * 24 * 7,
    }


def get_ip_config():
    """
    Get IP whitelist/blacklist configuration.
    """
    whitelist = os.getenv('IP_WHITELIST', '').split(',')
    blacklist = os.getenv('IP_BLACKLIST', '').split(',')
    
    return {
        'whitelist': [ip.strip() for ip in whitelist if ip.strip()],
        'blacklist': [ip.strip() for ip in blacklist if ip.strip()],
    }
