from flask import current_app, Response
from flask import session, redirect, request
from urllib.parse import urlparse
from datetime import datetime, timezone
from ..app.extensions import db
from ..models.user import Users, user_login, user_roles, Teams, Roles
from ..logger.log import LogEvent


class KeyCloakLogin:
    def __init__(self, name:str, login:str, email:str, token_id:str, groups:list):
        self.name =  name
        self.login = login
        self.email = email
        self.token_id = token_id
        self.groups = [cur.replace("/", "") for cur in groups]
        self.GROUP_MAPPING: dict[str: dict] = current_app.config["GROUP_MAPPING"]
        self.PERMANENT_SESSION_LIFETIME = current_app.config["PERMANENT_SESSION_LIFETIME"]

    def authorize(self):
        user = Users.query.filter_by(login=self.login).first()
        if user:
            parsed_group = self.__handle_groups()
            if self.__verify_changes(user=user, **parsed_group):
                self.__update_user(user.id, **parsed_group)

            self.user_login(user, self.token_id)
            
            LogEvent.log_event(eventName="login")
            session['lifetime'] = datetime.now(timezone.utc) + self.PERMANENT_SESSION_LIFETIME
            return redirect('main')
        else:
            create = self.__create_user()
            if not create:
                redirect('/groups-error')
            LogEvent.log_event(eventName="login")
            session['lifetime'] = datetime.now(timezone.utc) + self.PERMANENT_SESSION_LIFETIME
            return redirect('main')
        
    def __verify_changes(self, user:Users, roles:list[str], team:str) -> bool:
        try:
            current_team:str = str(Teams.query.filter_by(id=user.team_id).first().name)
            if team != current_team:
                return True
            
            current_roles:list = [str(row.name) for row in user_roles.query.join(
                    Roles, Roles.id == user_roles.role_id
                ).add_columns(
                    Roles.name
                ).filter(
                    user_roles.user_id == user.id
                ).all()
            ]

            if set(current_roles).difference(set(roles)):
                return True
            
            if self.name != user.name or self.email != user.name:
                return True
            
            return False
        
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    @staticmethod
    def user_login(user:Users, access_token:str|None) -> None:
        user_login_info = user_login(user_id=user.id, login_timestamp=datetime.now(), access_token=access_token)
        db.session.add(user_login_info)
        db.session.commit()
    
    def __update_user(self, user_id:str, roles:list[str], team:str) -> None:
        try:
            team_id:str = str(Teams.query.filter_by(name=team).first().id)
            is_admin:bool = True if "Admin" in roles else False
            roles_id:list = [str(Roles.query.filter_by(name=cur).first().id) for cur in roles]

            delete = user_roles.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            update = Users.query.filter_by(id=user_id).update(
                dict(
                    team_id=team_id,
                    admin=is_admin,
                    name=self.name,
                    email=self.email
                )
            )
            db.session.commit()

            roles_bulk= [user_roles(user_id=user_id, role_id=cur) for cur in roles_id]
            db.session.add_all(roles_bulk)
            db.session.commit()

            LogEvent.log_event(
                eventName="updateEntity",
                entityName="user",
                entityId=user_id,
                message=str({
                    "action": f"changed users info {user_id}"
                })
            )
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    def __handle_groups(self) -> dict|Response:
        for key, val in self.GROUP_MAPPING.items():
            if key in self.groups:
                return val
        return None
    
    def __create_user(self) -> None:
        try:
            parsed_group = self.__handle_groups()
            if not parsed_group:
                return None
            roles:list = parsed_group["roles"]
            team:str = parsed_group["team"]
            team_id:str = str(Teams.query.filter_by(name=team).first().id)
            roles_id:list = [str(Roles.query.filter_by(name=cur).first().id) for cur in roles]
            is_admin:bool = True if "Admin" in roles else False

            user = Users(email=self.email, name=self.name, login=self.login, admin=is_admin, team_id=team_id)
            db.session.add(user)
            db.session.commit()

            roles_bulk= [user_roles(user_id=user.id, role_id=cur) for cur in roles_id]
            db.session.add_all(roles_bulk)
            db.session.commit()

            self.user_login(user, self.token_id)
            
            LogEvent.log_event(
                eventName="createEntity",
                entityName="user",
                entityId=user.id,
                sUser=user.login,
                message=str({
                    "action": f"created user {user.id}"
                })
            )
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
