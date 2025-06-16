import hashlib
import hmac
import platform
import socket
import psutil
from utils.config.Config import config
import time
from flask_session import Session
import cachetools
from flask import (
    Blueprint,
    Flask,
    Response,
    make_response,
    url_for,
    send_from_directory,
    request,
    jsonify,
    send_file,
    abort,
    render_template,
    render_template_string,
    redirect,
    session,
    # make_response,
    flash,
    g,
    
)
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, logout_user
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
import os
import json
import zipfile
from github import Github, UnknownObjectException, GithubException
import json
import base64
import tempfile
import io
from gtts import gTTS
from io import BytesIO
import requests
from datetime import datetime, timedelta, timezone
import uuid
import logging
from PIL import Image, ImageDraw, ImageFont
import random
import string
import numpy as np
from user_agents import parse
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'Captcha'))
import threading
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
version = "7.9.2"
#url_prefix = f'/v2/api-market/{version}'

app = Flask(__name__, template_folder='../sheeeeesh', static_folder='../sheeeeeeesh')
app.logger.setLevel(logging.DEBUG)
#app.config["SECRET_KEY"] = config.APP_SECRET_KEY
app.config['SECRET_KEY'] = "SafeMarketZhodyve"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(api_bp)
SECRET_KEY_key = "SafeMarket-23489756231156789743-SafeMarket"
def generate_token():
    timestamp = int(time.time())
    message = f'{timestamp}'
    token = hmac.new(SECRET_KEY_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{token}:{timestamp}"
  
@app.route('/discord')
def discord():
    token = generate_token()
    target_url = f"https://discord.lamoukate.lol?safemarket={token}" # Discord Server URL
    return redirect(target_url)
