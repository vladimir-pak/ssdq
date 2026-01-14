from ..logger.log import LogEvent
from ..security.verify import InputValidator
from ..models.base import dq_dag_crossdb_sdim, dq_dag_sdim, dq_control_sdim, dq_alerting_stat
from ..models.dict import dq_source_sdim
from ..models.user import Teams, Users
from ..app.extensions import db
from ..models.constants import AlertingType, DagType
from sqlalchemy import and_
from flask import current_app
import logging
import requests


class Dag:

    def __init__(self, id:str|int=None):
        _AIRFLOW_API_URL:str = current_app.config["AIRFLOW_API_URL"]
        self.AIRFLOW_API_URL = _AIRFLOW_API_URL if _AIRFLOW_API_URL.endswith('/') else (_AIRFLOW_API_URL + '/')
        self.AIRFLOW_CERT_PATH:str = current_app.config["AIRFLOW_CERT_PATH"]

        AIRFLOW_AUTH_CRED:str = current_app.config["AIRFLOW_AUTH_CRED"]
        auth = AIRFLOW_AUTH_CRED.split(":")
        self.auth = (auth[0], auth[1])
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        self.id = id

    def prepare_json(self) -> dict:
        try:
            dag_info = db.session.query(dq_control_sdim).join(
                dq_dag_sdim, dq_dag_sdim.control_id == dq_control_sdim.id
            ).join(
                dq_source_sdim, and_(
                    dq_dag_sdim.source == dq_source_sdim.id,
                    dq_source_sdim.deleted_flag == "N"
                ),
                isouter=True
            ).join(
                Teams, dq_control_sdim.team_id == Teams.id
            ).add_columns(
                dq_dag_sdim.dag_type,
                dq_dag_sdim.sql,
                dq_dag_sdim.cron,
                dq_dag_sdim.pattern_id,
                dq_dag_sdim.params,
                dq_dag_sdim.limit,
                dq_source_sdim.name.label("source_name"),
                Teams.name.label("team"),
                dq_control_sdim.threshold_min,
                dq_control_sdim.threshold_max,
                dq_control_sdim.alerting_type_id,
            ).filter(
                dq_control_sdim.id == self.id,
                dq_control_sdim.deleted_flag == "N"
            ).first()

            email_recepients = db.session.query(dq_alerting_stat).join(
                Users, Users.id == dq_alerting_stat.user_id
            ).add_columns(
                Users.email
            ).filter(
                dq_alerting_stat.control_id == self.id
            ).all()

            json_data = {
                "dag_id": f"dq_{self.id}",
                "control_id": self.id,
                "dag_type": DagType(dag_info.dag_type).name,
                "sql": str(dag_info.sql).replace('\"', '\\"'),
                "pattern_id": str(dag_info.pattern_id),
                "params": dag_info.params,
                "conn_id": str(dag_info.source_name),
                "team": str(dag_info.team),
                "threshold_min": dag_info.threshold_min,
                "threshold_max": dag_info.threshold_max,
                "mail": {
                    "mode": str(AlertingType(dag_info.alerting_type_id).name),
                    "recepients": [user.email for user in email_recepients]
                },
                "limit": dag_info.limit
            }
            if dag_info.cron:
                json_data["schedule"] = str(dag_info.cron)

            return json_data
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def deploy_dag(self) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/deploy"
            if InputValidator.validate_airflow_url(endpoint):
                json_data = self._prepare_json()

                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH, timeout=10)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "deployDag"
                        })
                    )
                    return None
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def remove_dag(self) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/delete"
            if InputValidator.validate_airflow_url(endpoint):
                params = {"dag_id": f"dq_{self.id}"}
                response = requests.delete(endpoint, headers=self.headers, params=params, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "deleteDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL failed validation")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def deploy_sql_template(self, team_id:str, pattern_id:str, sql:str) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/sql-template/deploy"
            if InputValidator.validate_airflow_url(endpoint):
                team_name = db.session.query(Teams.name).filter_by(id=team_id).first().name
                json_data = {
                    "team": team_name,
                    "pattern_id": pattern_id,
                    "sql": sql
                }

                response = requests.post(endpoint, headers=self.headers, 
                    json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH, timeout=10)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowSqlTemplate",
                        message=str({
                            "action": "deploySqlTemplate"
                        })
                    )
                    return None
                else:
                    logging.error(response.text)
                    return {"message": response.text}
            else:
                raise Exception("URL failed validation")
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    def remove_sql_template(self, team_id:str, pattern_id:str) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/sql-template/delete"
            if InputValidator.validate_airflow_url(endpoint):
                team_name = db.session.query(Teams.name).filter_by(id=team_id).first().name
                params = {
                    "team": team_name,
                    "patternid": pattern_id
                }
                response = requests.delete(endpoint, headers=self.headers, 
                    params=params, auth=self.auth, verify=self.AIRFLOW_CERT_PATH, timeout=10)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowSqlTemplate",
                        message=str({
                            "action": "deleteSqlTemplate"
                        })
                    )
                    return None
                else:
                    logging.error(response.text)
                    return {"message": response.text}
            else:
                raise Exception("URL failed validation")
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    def deploy_connection(self, conn_id:str, host:str, port:int, db_name:str, dbtype:str, sslmode:str=None) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/connection/deploy"
            if InputValidator.validate_airflow_url(endpoint):
                json_data = {
                    "conn_id": conn_id,
                    "host": host,
                    "port": port,
                    "db_name": db_name,
                    "dbtype": dbtype,
                    "sslmode": sslmode
                }
                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH, timeout=10)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="deployConnection",
                        message=str({
                            "action": "deployConnection"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL failed validation")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def upload_config(self, default_args:dict) -> None:
        try:
            endpoint = self.AIRFLOW_API_URL + "sdq/upload_config"
            if InputValidator.validate_airflow_url(endpoint):
                response = requests.post(endpoint, headers=self.headers, json=default_args, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowConfigDag",
                        message=str({
                            "action": "deployConfigDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex


class AirflowAPI:
    def __init__(self):
        url:str = current_app.config["AIRFLOW_API_URL"]
        self.url = url if url.endswith("/") else (url + "/")

        AIRFLOW_AUTH_CRED:str = current_app.config["AIRFLOW_AUTH_CRED"]
        auth = AIRFLOW_AUTH_CRED.split(":")

        self.AIRFLOW_CERT_PATH:str = current_app.config["AIRFLOW_CERT_PATH"]

        self.auth = (auth[0], auth[1])
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def get_status(self, id:str|int):
        try:
            endpoint = self.url + 'sdq/status'
            if InputValidator.validate_airflow_url(endpoint):
                params = {'dag_id': f"dq{id}"}
                response = requests.get(endpoint, headers=self.headers, params=params, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    return response.json()
                else:
                    return str(response.json()["error"])
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def get_status(self, id:str|int):
        try:
            id = int(id)
            id = str(id)
            current_status = self._get_status(id)
            if isinstance(current_status, str):
                return {"message": current_status}, 500
            elif isinstance(current_status, dict):
                if len(current_status["runs"]) > 0:
                    response = {
                        "result": current_status["runs"][0]["pipelineState"],
                        "startDate": current_status["runs"][0]["startDate"],
                        "endDate": current_status["runs"][0]["endDate"]
                    }
                else:
                    response = {
                        "result": "По данному контролю отсутствуют результаты выполнения",
                        "startDate": None,
                        "endDate": None
                    }
                response["status"] = "disabled" if current_status["is_paused"] else "enabled"
                return response, 200
            else:
                return {"message": "Не удалось получить данные из Airflow"}, 500
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def unpause_dag(self, id:str|int):
        """
        Check control's status. If status  then return None
        """
        try:
            id = int(id)
            id = str(id)
            endpoint = self.url + 'sdq/enable'
            if InputValidator.validate_airflow_url(endpoint):
                json_data = {'dag_id': f"dq_{str(id)}"}
                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "enableDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def pause_dag(self, id:str|int):
        try:
            id = int(id)
            id = str(id)
            endpoint = self.url + 'sdq/disable'
            if InputValidator.validate_airflow_url(endpoint):
                json_data = {'dag_id': f"dq_{str(id)}"}
                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth,
                                        verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "disableDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def trigger_dag(self, id:str|int):
        try:
            id = int(id)
            id = str(id)
            current_status = self._get_status(id)
            if len(current_status["runs"]) > 0 and current_status["runs"][0]["pipelineState"] in ["running", "queued"]:
                return {"message": "DAG уже выполняется или в очереди"}, 500

            endpoint = self.url + 'sdq/trigger'
            if InputValidator.validate_airflow_url(endpoint):
                json_data = {
                    "dag_id": f"dq_{id}"
                }
                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "triggerDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def kill_dag(self, id:str|int):
        try:
            id = int(id)
            id = str(id)
            endpoint = self.url + 'sdq/kill'
            if InputValidator.validate_airflow_url(endpoint):
                json_data = {'dag_id': f'dq_{id}'}
                response = requests.post(endpoint, headers=self.headers, json=json_data, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag",
                        message=str({
                            "action": "killDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def delete_dag(self, id:str|int):
        try:
            id = int(id)
            id = str(id)
            endpoint = self.url + 'sdq/delete'
            if InputValidator.validate_airflow_url(endpoint):
                params = {
                    "dag_id": f"dq_{id}"
                }
                response = requests.delete(endpoint, params=params, auth=self.auth, verify=self.AIRFLOW_CERT_PATH)
                if 200 <= response.status_code  < 300:
                    LogEvent.log_event(
                        eventName="airflowDag", 
                        message=str({
                            "action": "deleteDag"
                        })
                    )
                    return '', 204
                else:
                    return {"message": response.text}, 500
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        