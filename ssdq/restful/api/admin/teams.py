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


class AdminTeams:
    def __init__(self):
        pass
    
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
    def get_datatable():
        try:
            attributes = {
                0: Teams.id,
                1: Teams.name,
                2: Teams.json["display_name"].cast(String),
                3: Teams.description,
                4: Teams.json["jira_project"].cast(String)
            }
            search_value = request.form['search[value]']
            search = None if search_value is None or search_value == '' else f'%%{search_value.lower()}%%'
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            if request.form.get('order[0][column]'):
                order_attr = attributes[int(request.form['order[0][column]'])]
                order_dir = request.form['order[0][dir]']
                order = order_attr if order_dir == 'asc' else order_attr.desc()
            else:
                order = Teams.id
            
            query = db.session.query(
                Teams.id,
                Teams.name,
                Teams.json["display_name"].label("display_name"),
                Teams.description,
                Teams.json["jira_project"].label("jira_project")
            )
            if search:
                query = query.filter(
                    or_(
                        Teams.id.cast(String).ilike(search),
                        Teams.name.ilike(search),
                        Teams.json["display_name"].cast(String).ilike(search),
                        Teams.json["jira_project"].cast(String).ilike(search),
                        Teams.description.ilike(search)
                    )
                )
            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                name=row.name,
                display_name=row.display_name,
                description=row.description,
                jira_project=row.jira_project
            ) for row in dataset]
            
            total_records = int(Teams.query.count())
            total_record_filtered = total_records if search is None else int(query.count())
            
            response = {
                'draw': request.form['draw'],
                'iTotalRecords': total_records,
                'iTotalDisplayRecords': total_record_filtered,
                'aaData': data,
            }
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
