from flask import render_template, session, Blueprint, jsonify, redirect, url_for, request
from src.f_auth import login_required


home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@home_bp.route('/index')
@login_required
def index():
    """Root route - redirects to home if logged in."""
    return home()


@home_bp.route('/chat')
@home_bp.route('/chat_page')
@login_required
def chat_page():
    """Chat page route."""
    user = session.get('user')
    return render_template('index.html', user=user)


@home_bp.route('/home')
@login_required
def home():
    """Home page route."""
    user = session.get('user')
    return render_template('home.html', user=user)
