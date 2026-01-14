# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, Blueprint, request
from ..auth.keycloak import KeyCloakLogin
from ..app.extensions import login_manager, oidc
from ..logger.log import LogEvent
from ..models.user import Users


blueprint = Blueprint(
    'authentication',
    __name__,
    url_prefix='',
    template_folder='templates'
)


@blueprint.route('/private', methods=['GET', 'POST'])
@oidc.require_login
def auth():
    user_info = oidc.user_getinfo(['preferred_username', 'email', 'given_name', 'family_name', 'middle_name', 'GroupMapper'])
    user = {
        "name": f"{user_info.get('family_name')} {user_info.get('given_name')} {user_info.get('middle_name')}",
        "login": user_info.get('preferred_username'),
        "email": user_info.get('email'),
        "groups": user_info.get('GroupMapper'),
        "token_id": oidc.get_access_token()
    }
    return KeyCloakLogin(**user).authorize()


@blueprint.route('/')
def red():
    logged = oidc.user_loggedin
    next_url = request.args.get('next')
    return redirect('main') if logged else render_template('accounts/login_keycloak.html', next_url=next_url) 


@blueprint.route('/oidc/logout')
def logout():
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
