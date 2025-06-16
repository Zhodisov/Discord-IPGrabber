#                                https://safemarket.xyz/
#__| |_____________________________________________________________________________| |__
#__   _____________________________________________________________________________   __
#  | |                                                                             | |  
#  | | ____     _     _____  _____      __  __     _     ____   _  __ _____  _____ | |  
#  | |/ ___|   / \   |  ___|| ____|    |  \/  |   / \   |  _ \ | |/ /| ____||_   _|| |  
#  | |\___ \  / _ \  | |_   |  _|      | |\/| |  / _ \  | |_) || ' / |  _|    | |  | |  
#  | | ___) |/ ___ \ |  _|  | |___     | |  | | / ___ \ |  _ < | . \ | |___   | |  | |  
#  | ||____//_/   \_\|_|    |_____|    |_|  |_|/_/   \_\|_| \_\|_|\_\|_____|  |_|  | |  
#__| |_____________________________________________________________________________| |__
#__   _____________________________________________________________________________   __
#  | |                                                                             | |  
#                               https://github.com/Zhodisov                           

# Used in Safemarket V2


import hashlib
import hmac
from utils.config.Config import config
import time
from flask import Flask, request, jsonify, render_template_string, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin
from itsdangerous import URLSafeTimedSerializer
import requests
from datetime import timedelta
import logging
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)
app.logger.setLevel(logging.DEBUG)
app.config["SECRET_KEY"] = config.APP_SECRET_KEY
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
login_manager = LoginManager()
login_manager.init_app(app)
KEY_EXPIRATION_DURATION = timedelta(minutes=1)
active_tokens = {}
client_last_contact = {}
connected_clients = {}
allowed_hosts_api = ['Main-SafeMarket']
new_connections = []
SECRET_KEY = "SafeMarket-23489756231156789743-SafeMarket"
WEBHOOK_URL = config.DISCORD_WEBHOOK_URL
url_prefix = '/api/v2-safemarket'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def validate_token(token):
    try:
        token, timestamp = token.split(':')
        timestamp = int(timestamp)
        current_time = int(time.time())
        if current_time - timestamp > 300:
            return False
        message = f'{timestamp}'
        expected_token = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_token, token)
    except Exception as e:
        return False

# @app.before_request
# def limit_api_to_subdomain():
#     token = request.args.get('safemarket')
#     if not validate_token(token):
#         app.logger.info(f"Заблокирован запрос от {request.host} без действительного токена источника")
#         return jsonify({"status": "error", "message": "Неверный доступ, используйте https://safemarket.xyz/discord"}), 404
@app.before_request
def block_bots():
    user_agent = request.headers.get('User-Agent')
    if not user_agent or 'bot' in user_agent.lower():
        return abort(403)

def get_real_ip():
    if 'CF-Connecting-IP' in request.headers:
        ip = request.headers['CF-Connecting-IP']
    elif 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

def get_client_type(user_agent):
    if any(bot in user_agent.lower() for bot in ["discordbot", "bot", "crawl", "spider"]):
        return "Bot"
    elif any(mobile in user_agent for mobile in ["Android", "iPhone", "iPad"]):
        return "Mobile App"
    elif "Electron" in user_agent:
        return "Desktop App"
    elif any(web in user_agent for web in ["Windows", "Macintosh", "Linux"]):
        return "Web"
    else:
        return "Unknown"
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeMarket - Discord</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #272525 0%, #1a1a1a 100%);
            color: #ffffff;
        }
        .container {
            text-align: center;
            background: rgba(0, 0, 0, 0.6);
            padding: 2em;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        h1 { 
            margin-bottom: 0.5em; 
        }
        button {
            background-color: #4CAF50;
            border: none;
            color: #fff;
            padding: 15px 30px;
            font-size: 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }
        button:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }
        button:active {
            transform: scale(0.98);
        }
        #status {
            margin-top: 1em;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Safemarket Invitation</h1>
        <form id="inviteForm">
            <div class="g-recaptcha" data-sitekey="6Ldg6t8qAAAAABXW0zDGOb91mBdsS0duCupzo-Ki"></div>
            <br/>
            <button type="button" onclick="submitForm()">Get link</button>
        </form>
        <div id="status"></div>
    </div>
    <script>
        function submitForm() {
            var recaptchaResponse = grecaptcha.getResponse();
            if (!recaptchaResponse) {
                document.getElementById("status").innerText = "Complete the captcha";
                return;
            }
            var clientInfo = {
                userAgent: navigator.userAgent,
                language: navigator.language,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                "g-recaptcha-response": recaptchaResponse
            };
            document.getElementById("status").innerText = "Processing...";
            fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(clientInfo)
            })
            .then(response => response.json())
            .then(data => {
                if (data.api_url) {
                    document.getElementById("status").innerText = "Waiting...";
                    window.location.href = data.api_url;
                } else {
                    document.getElementById("status").innerText = "Error.";
                    console.error("Error");
                }
            });
        }
    </script>
</body>
</html>

"""
        return render_template_string(html_content)
    else:
        c_info = request.json
        r_rep = c_info.get("g-recaptcha-response")
        if not r_rep:
            return jsonify({"error": "Captcha non complété"}), 400
        pl = {
            "secret": "", # Secret Key Captcha
            "response": r_rep,
            "remoteip": get_real_ip()
        }
        captcha_verify = requests.post("https://www.google.com/recaptcha/api/siteverify", data=pl)
        captcha_result = captcha_verify.json()
        if not captcha_result.get("success"):
            return jsonify({"error": "Неверная капча"}), 400
        ip_ad = get_real_ip()
        connection_info = {
            "ip_ad": ip_ad,
            "user_agent": c_info.get("userAgent"),
            "client_type": get_client_type(c_info.get("userAgent")),
            "language": c_info.get("language"),
            "timezone": c_info.get("timezone"),

        }

        new_connections.append(connection_info)

        data = {
            "content": "Обнаружено новое соединение",
            "embeds": [
                {
                    "title": "Информация об устройстве",
                    "fields": [
                        {"name": "Публичный IP-адрес", "value": ip_ad, "inline": True},
                        {"name": "User-Agent", "value": c_info.get("userAgent"), "inline": False},
                        {"name": "Тип клиента", "value": connection_info["client_type"], "inline": True},
                        {"name": "Язык", "value": c_info.get("language"), "inline": True},
                        {"name": "Часовой пояс", "value": c_info.get("timezone"), "inline": True}
                    ]
                }
            ]
        }

        try:
            requests.post(config.DISCORD_WEBHOOK_URL_DISCORD, json=data)
        except Exception as e:
            return jsonify({"error": "Ошибка при отправке данных в вебхук Discord"}), 500

        try:
            response = requests.post('http://127.0.0.1:7813/d', json={"_____": ip_ad})
            if response.status_code == 200:
                invite_data = response.json()
                return jsonify({"api_url": invite_data['api_url']})
            else:
                return jsonify({"error": "Ошибка при создании приглашения"}), 500
        except Exception as e:
            return jsonify({"error": "Ошибка связи с ботом Discord"}), 500
