# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import hashlib
import binascii
from ..models.user import Users, user_roles
from ..app.extensions import db
from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token
from ..logger.log import LogEvent


def hash_pass(password) -> bytes:
    """Hash a password for storing."""

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password) -> bool:
    """Verify a stored password against one provided by user"""
    # password_bytes = str.encode(stored_password)
    # stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def add_user(username, email, fullname, hashed_pass, role_id, team_id, **args) -> None:
    user = Users(email=email, name=fullname, login=username, password=hashed_pass, admin=False, team_id=team_id)
    db.session.add(user)
    db.session.commit()
    role = user_roles(user_id=user.id, role_id=role_id)
    db.session.add(role)
    db.session.commit()


class UserJWT(Resource):
    def post(self):
        try:
            json = request.get_json()
            username = json['username']
            password = json['password']
            user = Users.query.filter_by(login=username).first()
            if user and verify_pass(password, user.password):
                access_token = create_access_token(
                    identity={
                        'username': username,
                        'userId': user.id
                    },
                    expires_delta=False
                )
                LogEvent.log_event(eventName="getToken", sUser=username, sUserId=user.id, message="token generated successfull")
                return {'token': access_token}

            LogEvent.log_warning(sUser=username, sUserId=user.id if user is not None else "", route="/api/auth")
            return {'error': 'Invalid username and/or password'}
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
