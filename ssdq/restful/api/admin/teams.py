import configparser
import os
from cryptography.fernet import Fernet
from flask import request, current_app
from flask_login import current_user
from sqlalchemy import String, or_
from ....app.extensions import db
from ....models.user import Teams
from ....models.dict import dq_source_sdim
from ....logger.log import LogEvent
from ....security.verify import InputValidator
from ....vault.utils import Vault
from ..aggrid import AGGrid


ALLOWED_COLS = {
    "id": Teams.id,
    "name": Teams.name,
    "display_name": Teams.json["display_name"].as_string(),
    "description": Teams.description,
    "jira_project": Teams.json["jira_project"].as_string()
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


# custom query for grid
def users_base_query(payload):
    q = db.session.query(
        Teams.id,
        Teams.name,
        Teams.json["display_name"].label("display_name"),
        Teams.description,
        Teams.json["jira_project"].label("jira_project")
    )
    return q


class AdminTeams:
    def __init__(self):
        self.grid = AGGrid(
            obj=Teams,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS,
            base_query_fn=users_base_query
        )
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="teams.csv"
        )
        
    @staticmethod
    def get_data(id:str):
        try:
            team_info = db.session.query(
                Teams.name,
                Teams.description,
                Teams.json["display_name"].label("display_name"),
                Teams.json["jira_project"].label("jira_project")
            ).filter_by(id=id).first()
            sources = db.session.query(
                dq_source_sdim.name, dq_source_sdim.description
            ).all()
            response = dict(
                sources=[dict(
                    name=row.name, description=row.description
                    ) for row in sources],
                data=dict(
                    name=team_info.name,
                    display_name=team_info.display_name,
                    jira_project=team_info.jira_project,
                    description=team_info.description
                )
            )
            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def add():
        try:
            entity = Teams(
                name=request.form["name"],
                description=request.form["description"],
                json=dict(
                    display_name=request.form["display_name"],
                    jira_project=request.form["jira_project"]
                )
            )
            db.session.add(entity)
            db.session.commit()
            
            LogEvent.log_event(eventName="updateEntity", entityName="team", entityId=entity.id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def update(id:str):
        try:
            update = Teams.query.filter_by(id=id).update(
                dict(
                    name=request.form["name"],
                    description=request.form["description"],
                    json=dict(
                        display_name=request.form["display_name"],
                        jira_project=request.form["jira_project"]
                    )
                )
            )
            db.session.commit()
            
            LogEvent.log_event(eventName="updateEntity", entityName="team", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete(id:str):
        try:
            delete = Teams.query.filter_by(id=id).delete()
            db.session.commit()
            
            LogEvent.log_event(eventName="deleteEntity", entityName="team", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    

class TeamConnection:
    def __init__(self):
        ssdq_home = os.getenv('SSDQ_HOME')
        vault = configparser.ConfigParser()
        vault.read(f'{ssdq_home}/config/vault.conf')

        self.vault_url = vault['global']['VAULT_URL']
        self.environment = vault['global']['ENVIRONMENT']
        self.path = vault['global']['PATH']
        self.project = vault['global']['PROJECT']
        self.version = vault['global']['VERSION'] if int(vault['global']['VERSION']) != 0 else ""
        
        vault.read(f'{ssdq_home}/config/secret.conf')
        self.role_id = vault["global"]["role_id"]
        self.secret_id = vault["global"]["secret_id"]
        
        self.fernet = Fernet(current_app.config["FERNET_KEY"])
        
    def encrypt(self, data:str) -> str:
        data = str.encode(data)
        return self.fernet.encrypt(data)
    
    def decrypt(self, data:str) -> str:
        return self.fernet.decrypt(data).decode('utf-8')
    
    def get_token(self) -> str:
        url = f"{self.vault_url}/v1/auth/approle_{self.environment}_{self.project}/login"
        if InputValidator.validate_vault_url(url=url, env=self.environment, secret_type='login'):
            return Vault.get_token(url=url, role_id=self.role_id, secret_id=self.secret_id)
        else:
            raise Exception("URL is not correct")
    
    def get_secret_conn(self, team:str, conn_id:str) -> tuple[dict, int]:
        try:
            token = self.get_token()
            url = f"{self.vault_url}/v1/secret_v2_{self.environment}/data/{self.project}/{self.path}/connections/{team}/{conn_id}" + self.version
            if InputValidator.validate_vault_url(url=url, env=self.environment, secret_type='secret', path=self.path.split('/')[0]):
                response = Vault.get_secret(url=url, token=token)
                response['password'] = self.decrypt(response['password'])
                return dict(response=response), 200
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    def create_secret_conn(self, form:dict) -> tuple[dict, int]:
        try:
            encrypted_pass = self.encrypt(form['password'])
            data = {
                "data": {
                    # "host": form['host'],
                    # "port": form['port'],
                    # "db": form['db_name'],
                    "username": form['username'],
                    "password": encrypted_pass.decode('utf-8')
                }
            }
            token = self.get_token()
            url = f"{self.vault_url}/v1/secret_v2_{self.environment}/data/{self.project}/{self.path}/connections/{form['team']}/{form['conn_id']}"
            if InputValidator.validate_vault_url(url=url, env=self.environment, secret_type='secret', path=self.path.split('/')[0]):
                response = Vault.create_secret(url=url, token=token, data=data)
                LogEvent.log_event(
                    eventName="TeamConnection",
                    sUser=current_user.login,
                    sUserId=current_user.id,
                    message=f"TeamConnection {form['team']} created"
                )
                return dict(response=response), 200
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
