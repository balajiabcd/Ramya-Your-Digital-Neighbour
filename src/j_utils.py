import os
from flask import url_for, session


def get_bot():
    """Helper to get or initialize the bot with the current user's email."""
    from src.a_ai_engine import RamyaBot
    from src.h_config import OPEN_ROUTER_API_KEY
    
    user = session.get('user', {})
    user_email = user.get('email')
    return RamyaBot(api_key=OPEN_ROUTER_API_KEY, user_email=user_email)


def dated_url_for(endpoint, **values):
    """Add cache-busting version query to static files."""
    from flask import current_app
    
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(current_app.root_path, endpoint, filename)
            try:
                values['v'] = int(os.stat(file_path).st_mtime)
            except OSError:
                pass
    return url_for(endpoint, **values)
