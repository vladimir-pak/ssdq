from flask_login import current_user
from flask import request, render_template
from functools import wraps
from ..logger.log import LogEvent
from ..app.extensions import db
from ..models.base import dq_control_sdim
from ..models.user import Teams


def roles_accepted(roles:list[str]=None, method:str=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            def call(*args, **kwargs):
                return fn(*args, **kwargs)
            def denied(*args, **kwargs):
                LogEvent.log_warning()
                return render_template('home/insufficient-privileges.html')
                # raise PermissionError
            if current_user.admin:
                return call(*args, **kwargs)
            elif roles is None:
                return denied(*args, **kwargs)
            elif current_user.role_name in roles:
                if method:
                    return call(*args, **kwargs) if method == request.method else denied(*args, **kwargs)
                return call(*args, **kwargs)
            else:
                return denied(*args, **kwargs)
        return decorated_view
    return wrapper


def control_accepted(key:str=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            def call(*args, **kwargs):
                return fn(*args, **kwargs)
            def denied(*args, **kwargs):
                LogEvent.log_warning()
                return render_template('home/insufficient-privileges.html')
            if current_user.admin:
                return call(*args, **kwargs)
            else:
                try:
                    control_id = kwargs['id']
                except:
                    control_id = int(request.args.get(key))
                if get_controls_team(control_id=control_id) == str(current_user.team_id):
                    return call(*args, **kwargs)
                else:
                    return denied(*args, **kwargs)
        return decorated_view
    return wrapper


def get_controls_team(control_id:int) -> str:
    return str(db.session.query(dq_control_sdim.team_id).filter_by(
        id=control_id,
        deleted_flag="N"
    ).first().team_id)


def teams_accepted(teams:list[str]=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            def call(*args, **kwargs):
                return fn(*args, **kwargs)
            def denied(*args, **kwargs):
                LogEvent.log_warning()
                return render_template('home/insufficient-privileges.html')
                # raise PermissionError
            if current_user.admin:
                return call(*args, **kwargs)

            team_name = db.session.query(Teams.name).filter_by(id=current_user.team_id).first().name
            if team_name in teams:
                return call(*args, **kwargs)
            else:
                return denied(*args, **kwargs)
        return decorated_view
    return wrapper
