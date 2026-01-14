# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import session, render_template, redirect, request, Blueprint, current_app
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from ..app.extensions import login_manager
from ..logger.log import LogEvent
from ..auth.forms import LoginForm, CreateAccountForm
from ..models.user import Users, user_login, Roles, Teams
from ..app.extensions import db
from datetime import datetime, timezone
from ..auth.utils import verify_pass, hash_pass, add_user
from ..security.verify import InputValidator
from urllib.parse import urlparse


blueprint = Blueprint(
    'authentication',
    __name__,
    url_prefix='',
    template_folder='templates'
)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        login = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(login=login).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            user_login_info = user_login(user_id=user.id, login_timestamp=datetime.now())
            db.session.add(user_login_info)
            db.session.commit()

            session['lifetime'] = datetime.now(timezone.utc) + current_app.config["PERMANENT_SESSION_LIFETIME"]
            LogEvent.log_event(eventName="login", message="success")
            return redirect('main')

        # Something (user or pass) is not ok
        LogEvent.log_event(eventName="login", message="failed")
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect('main')


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    try:
        create_account_form = CreateAccountForm(request.form)
        if 'register' in request.form:

            login = request.form['username']
            email = request.form['email']

            hashed_pass = hash_pass(request.form['password'])
            str_pass = hashed_pass.decode("utf-8")

            # Check usename exists
            user = Users.query.filter_by(login=login).first()
            if user:
                return render_template('accounts/register.html',
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

            # Check email exists
            user = Users.query.filter_by(email=email).first()
            if user:
                return render_template('accounts/register.html',
                                    msg='Email already registered',
                                    success=False,
                                    form=create_account_form)

            # else we can create the user
            role_id = str(Roles.query.filter_by(name=current_app.config["DEFAULT_USER_ROLE"]).first().id)
            team_id = str(db.session.query(Teams.id).filter_by(name="admin").first().id)
            add_user(hashed_pass=str_pass, role_id=role_id, team_id=team_id, **request.form)

            return render_template('accounts/register.html',
                                msg='User created please <a href="/login">login</a>',
                                success=True,
                                form=create_account_form)

        else:
            return render_template('accounts/register.html', form=create_account_form)
    except Exception as ex:
        LogEvent.log_error(ex)
        raise ex


@blueprint.route('/')
def red():
    return redirect(f'/login')


@blueprint.route('/logout')
def logout():
    # cache.delete(f'user_{current_user.id}')
    logout_user()
    return redirect('login')


@blueprint.route('/oidc/logout')
def oidc_logout():
    LogEvent.log_event(eventName='logout')
    return redirect('/logout')

# Errors


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


@login_manager.user_loader
def user_loader(id):
    query = Users.query.filter_by(id=id).first()
    return query # user_obj


@login_manager.unauthorized_handler
def unauthorized_handler():
    next_url = request.url
    return redirect(f'/login?next={next_url}')
