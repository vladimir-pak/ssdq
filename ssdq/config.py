import os
import json
import logging
from pathlib import Path
from functools import partial
from datetime import timedelta
from .logging import DefaultLoggingConfigurator

basedir = os.path.abspath(os.path.dirname(__file__))

# Application config
APP_PORT = 5000
WORKERS = 4
CERT_FILE = "/opt/ssdq/cert/certfile.cert"
CERT_KEY = "/opt/ssdq/cert/decrypted.key"

# Your App secret key
SECRET_KEY = "Bwa3ZaGPqY0wLj13D_7fb8LMRgPgY-TMptjOcXAK8q0="
FERNET_KEY = "Bwa3ZaGPqY0wLj13D_7fb8LMRgPgY-TMptjOcXAK8q0="

# The SQLAlchemy connection string.

SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_BINDS = {
    "audit_db": ''
}
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "json_serializer": partial(json.dumps, ensure_ascii=False)}

SQLALCHEMY_TRACK_MODIFICATIONS = False

SUPERSET_URL = "https://superset/"
JIRA_URL = "https://jira/api/v1/"
AIRFLOW_API_URL = "https://airflow/api/v1/"
AIRFLOW_AUTH_CRED = "admin:admin"
AIRFLOW_CERT_PATH = "/opt/ssdq/cert/airflow.crt"
STREAMLIT_ACCEPTANCE = ["ckkd", "cokd", "nsi"]

JIRA_API_URL = "https://jira/api/v2/"
JIRA_AUTH_CRED = "user:pass"
JIRA_CERT_PATH = "/opt/ssdq/cert/jira.crt"

API_BOT_PASSWORD = "apibot"

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# ------------------------------
# GLOBALS FOR APP Builder
# ------------------------------
# Uncomment to setup Your App name
APP_NAME = "SSDQ"

# Uncomment to setup Setup an App icon
# APP_ICON = "static/img/logo.jpg"

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database (username/password()
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server
AUTH_TYPE = "AUTH_DB"

# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
# AUTH_USER_REGISTRATION = True

# The default user self registration role
# AUTH_USER_REGISTRATION_ROLE = "Public"

# When using LDAP Auth, setup the ldap server
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
# Setup default language
BABEL_DEFAULT_LOCALE = "en"
# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
}
# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
# The file upload folder, when using models with files
UPLOAD_FOLDER = basedir + "/app/static/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/app/static/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

# Theme configuration
# these are located on static/appbuilder/css/themes
# you can create your own and easily use them placing them on the same dir structure to override
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "cerulean.css"
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('SSDQ_DEBUG', 'False') == 'True')
if "SSDQ_HOME" in os.environ:
    DATA_DIR = os.environ["SSDQ_HOME"]
else:
    DATA_DIR = Path(__file__).parent.absolute()

# Logging
LOGGING_CONFIGURATOR = DefaultLoggingConfigurator()

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
# FILENAME = os.path.join(DATA_DIR, "ssdq.log")
FILENAME = "/Users/vladimirpak/Desktop/ssdq/app/logs/ssdq.log"
ROLLOVER = "midnight"
INTERVAL = 1
BACKUP_COUNT = 30

OIDC_CLIENT_SECRETS = {
    "web": {
        "issuer": "http://localhost/auth/realms/users",
        "auth_uri": "http://localhost/auth/realms/users/protocol/openid-connect/auth",
        "client_id": "data-quality",
        "client_secret": "9cc794e5-fea0-4c9a-96f5-39c29ffd2160",
        "redirect_uris": [
            "http://localhost:5000/oidc_callback"
        ],
        "userinfo_uri": "http://localhost/auth/realms/users/protocol/openid-connect/userinfo",
        "token_uri": "http://localhost/auth/realms/users/protocol/openid-connect/token",
        "token_introspection_uri": "http://localhost/auth/realms/users/protocol/openid-connect/token/introspect"
    }
}
AUTH_GROUP_MAPPING = {
    "admin": {
        "roles": ["admin"],
        "team": "admin"
    },
    "core": {
        "roles": ["user"],
        "team": "core"
    },
    "core-lead": {
        "roles": ["lead"],
        "team": "core"
    }
}

DEFAULT_USER_ROLE = "User"

OIDC_ID_TOKEN_COOKIE_SECURE = False
OIDC_USER_INFO_ENABLED = True
OIDC_INTROSPECTION_AUTH_METHOD = 'client_secret_post'
OIDC_TOKEN_TYPE_HINT = 'acces_token'
CACHE_TYPE="SimpeCache"
CACHE_DEFAULT_TIMEOUT=300
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=40)
PERMANENT_SESSION_LIFETIME = timedelta(minutes=40)

# Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_DURATION = 3600
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_TIMEOUT = 300
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "json_serializer": partial(json.dumps, ensure_ascii=False)}

