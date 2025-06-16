import os
import yaml
from rich.console import Console
from rich.table import Table

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file) 
        self.APP_SECRET_KEY = config['app']['secret_key']
        self.REMEMBER_COOKIE_DURATION = config['app']['remember_cookie_duration']
        self.MAINTENANCE_MODE = config['app']['maintenance_mode']
        self.GITHUB_MODE = config['app']['github_mode']
        self.GITHUB_PAT = config['github']['personal_access_token']
        self.GITHUB_REPO_NAME = config['github']['repo_name']
        self.GITHUB_NEW_REPO_NAME = config['github']['new_repo_name']
        self.GITHUB_REPO_IP_ROUTE = config['github']['repo_ip_routes']
        self.GITHUB_PATHS = config['github']['paths']
        self.GITHUB_PATHS_ABONNEMENTS = config['github']['paths']['abonnements']
        self.GITHUB_PATHS_DATABASE_CHANGE = config['github']['paths']['database_changes']
        self.GITHUB_PATHS_KEY_OBFUSCATION = config['github']['paths']['key_obfuscation']
        self.GITHUB_PATHS_KEY_GUI = config['github']['paths']['key_gui']
        self.GITHUB_PATHS_KEY_GUI_SECOND = config['github']['paths']['key_gui_second']
        self.GITHUB_PATHS_KEY_GUI_TROISIEME = config['github']['paths']['key_gui_troisieme']
        self.GITHUB_PATHS_KEY_WEBSITE = config['github']['paths']['key_website']
        self.GITHUB_PATHS_HASH = config['github']['paths']['hash']
        self.GITHUB_PATHS_ERRORS = config['github']['paths']['errors']
        self.GITHUB_DEFAULTS = config['github']['paths']['defaults']
        self.GITHUB_NOTIFICATIONS = config['github']['paths']['notifications']
        self.GITHUB_UPDATE_INFO = config['github']['paths']['update_info']
        self.GITHUB_VISITS = config['github']['paths']['visits']
        self.GITHUB_CONFIGJSON = config['github']['paths']['config']
        self.GITHUB_SUMONERWARS = config['github']['paths']['sumoners_wars']
        self.GITHUB_ROUTES = config['github']['paths']['routes']
        self.GITHUB_IP = config['github']['paths']['ip']
        self.GITHUB_ROUTES_DEUX = config['github']['paths']['routes_deux']
        self.GITHUB_IP_DEUX = config['github']['paths']['ip_deux']
        self.DISCORD_WEBHOOK_URL = config['discord']['webhook_url']
        self.DISCORD_WEBHOOK_URL_DISCORD = config['discord']['webhook_url_discord']
        self.DISCORD_WEBHOOK_INSCRIPTION = config['discord']['webhook_inscription']
        self.DISCORD_BOT_TOKEN = config['discord']['bot_token']
        self.PAYPAL_API_KEY = config['paypal']['api_key']
        self.PAYPAL_SECRET_KEY = config['paypal']['secret_key']
        self.CAPTCHA_STORE = config['captcha']['store']
        self.CAPTCHA_OPTION = config['captcha']['option']
        self.CAPTCHA_DIFFICULTIES = config['captcha']['difficulties']
        self.KEYS_EXPIRATION_DURATION = config['keys']['expiration_duration']
        self.KEYS_FILE = config['keys']['keys_file']
        self.ERROR_CODES = config['errors']['codes']
        self.ROBOTO_FONT_PATH = config['image']['roboto_font_path']
        self.CAPTCHA_BACKGROUND_COLOR = config['image']['captcha_background_color']
        self.CAPTCHA_LETTER_COLOR = config['image']['captcha_letter_color']
        self.LINE_COLOR = config['image']['line_color']
        self.SPACING = config['image']['spacing']
        self.LOGO = config['website_ressource']['logoUrl']
        self.BACKGROUND = config['website_ressource']['backgroundUrl']
        self.GITHUB_URL = config['website_ressource']['githubUrl']
        self.DISCORD_URL = config['website_ressource']['discordUrl']
        self.EMAIL = config['website_ressource']['supportEmail']
        self.GITHUB_ADMIN_USERS = config['github']['paths']['admin']
        self.DB_HOST = config['database']['host']
        self.DB_USER = config['database']['user']
        self.DB_PASSWORD = config['database']['password']
        self.DB_NAME = config['database']['name']
        self.DOMAINS = config['domains']

config = Config()
