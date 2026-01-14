import os
from flask import Flask, redirect
from flask_minify import Minify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restful import Api
from pathlib import Path
from importlib import import_module
from ..restful.register import register_rest_api
from ..restful.routes import api_routes
from ..views.base import app_routes
from ..logger.check_hashsum import check_config
from .extensions import db, oidc, login_manager, csrf
from ..models.user import Users


"""
    Init app
"""
if "SSDQ_HOME" not in os.environ:
    os.environ["SSDQ_HOME"] = str(Path(__file__).parent.parent.absolute())

app: Flask = Flask(__name__)
app.config.from_object("ssdq.config")


if "SSDQ_CONFIG" in os.environ:
    CONFIG_FILE_PATH = os.getenv("SSDQ_CONFIG")
    app.config.from_pyfile(CONFIG_FILE_PATH, silent=True)
else:
    cur_dir = str(Path(__file__).parent.parent.absolute())
    CONFIG_FILE_PATH = f"{cur_dir}/config.py"

csrf.init_app(app)

"""
    Logging configuration
"""
app.config["LOGGING_CONFIGURATOR"].configure_logging(
    app.config, app.debug
)

"""
    Init database
"""
db.init_app(app)
Migrate(app, db)


"""
    Init auth
"""
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def user_loader(id):
    query = Users.query.filter_by(id=id).first()
    return query if query else redirect('login')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(f'/') if app.config["AUTH_TYPE"] == "AUTH_OID" else redirect(f'/login')


@login_manager.request_loader
def request_loader(request):
    try:
        info = oidc.user_getinfo(['preferred_username'])
        login = info.get('preferred_username')
        user = Users.query.filter_by(login=login).first()
    except:
        user = None
    return user if user else None
    
    
"""
    Register routes (blueprints)
"""
if app.config["AUTH_TYPE"] == "AUTH_DB":
    from ..views.auth import blueprint
    app.register_blueprint(blueprint=blueprint)
elif app.config["AUTH_TYPE"] == "AUTH_OID":
    from ..views.keycloak import blueprint
    app.register_blueprint(blueprint=blueprint)
    oidc.init_app(app)

module = import_module('ssdq.app.{}.routes'.format('home'))
app.register_blueprint(module.blueprint)
app.register_blueprint(api_routes)
app.register_blueprint(app_routes)


@app.before_first_request
def initialize_database():
    # db.create_all()
    # db.create_all(bind="audit_db")
    check_config(CONFIG_FILE_PATH)

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


"""
    Init restful
"""
api = Api(
    app, 
    errors={
        'NoAuthorizationError': {
            'message': 'Invalid Authorization Header',
            'status': 401
        },
        'ExpiredSignatureError': {
            'message': 'Token has expired',
            'status': 401
        }
    },
    decorators=[csrf.exempt]
)
register_rest_api(api)

jwt = JWTManager(app)


if not app.config["DEBUG"]:
    Minify(app=app, html=True, js=False, cssless=False)


@app.context_processor
def context_sdq():
    return dict(
        superset_url=app.config["SUPERSET_URL"],
        streamlit_url=app.config["STREAMLIT_URL"],
        streamlit_acceptance=app.config["STREAMLIT_ACCEPTANCE"]
    )
