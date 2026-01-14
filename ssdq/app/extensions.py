from flask_sqlalchemy import SQLAlchemy
from flask_login.login_manager import LoginManager
from flask_oidc import OpenIDConnect
from flask_wtf import CSRFProtect


db = SQLAlchemy()
Base = db.Model
login_manager = LoginManager()
oidc = OpenIDConnect()
csrf = CSRFProtect()
