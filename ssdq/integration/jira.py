from ..app.extensions import db
from ..logger.log import LogEvent
from ..security.verify import InputValidator
from ..models.user import Users, Teams
from ..models.base import dq_control_sdim, dq_control_owner_stat, dq_jira_issues, \
    dq_detailjournal_web, dq_detail_agg
from ..models.constants import JiraMode
from flask_restful import Resource
from flask import request, current_app
from flask_jwt_extended import jwt_required
import requests
import json


class JiraApi:
    def __init__(self):
        JIRA_AUTH_CRED:str = current_app.config["JIRA_AUTH_CRED"]
        self.JIRA_CERT_PATH:str = current_app.config["JIRA_CERT_PATH"]

        self.headers = {
            'Content-Type': 'application/json'
        }
        self.data = {
            'fields': {
                "project": {
                    "key": "JIRA_PROJECT"
                },
                "issuetype": {
                    "name": "Задача"
                },
                "assignee": {
                    "name": ""
                },
                # "reporter": {
                #     "name": ""
                # }
            }
        }
        auth = JIRA_AUTH_CRED.split(":")
        self.auth = (auth[0], auth[1])
        self.url:str = current_app.config["JIRA_API_URL"]

    def insert_task(self, wf_id:int, xk:int, jira_issue:str) -> None:
        try:
            isExist = dq_jira_issues.query.filter_by(
                pm_workflow_run_id=wf_id,
                xk=xk
            ).first()

            if isExist:
                task = dq_jira_issues.query.filter_by(
                    pm_workflow_run_id=wf_id,
                    xk=xk
                ).update(
                    dict(
                        jira_issue=jira_issue
                    )
                )
                db.session.commit()
            else:
                task = dq_jira_issues(
                    pm_workflow_run_id=wf_id,
                    xk=xk,
                    jira_issue=jira_issue
                )
                db.session.add(task)
                db.session.commit()

        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def create_task(self, control_id:str, wf_id:int, rows_id:list[int]|None=None):
        try:
            wf_id = str(int(wf_id))
            control_info = db.session.query(
                dq_control_sdim.team_id,
                dq_control_sdim.name,
                dq_control_sdim.description,
                dq_control_sdim.jira_mode_id,
                dq_control_sdim.threshold_max
            ).filter_by(
                id=control_id,
                deleted_flag="N"
            ).first()

            agg = db.session.query(
                dq_detail_agg.mistake_count,
                dq_detail_agg.report_date
            ).filter_by(
                control_id=control_id,
                pm_workflow_run_id=wf_id
            ).first()

            is_exceeded = True if int(control_info.threshold_max) < int(agg.mistake_count) else False

            owner = dq_control_owner_stat.query.join(
                Users, Users.id == dq_control_owner_stat.owner_id
            ).add_columns(
                Users.login
            ).filter(
                dq_control_owner_stat.control_id == control_id
            ).first()

            team_id = control_info.team_id
            teams_data = db.session.query(Teams.json).filter_by(
                id=team_id,
                deleted_flag="N"
            ).first().json

            form_data = {
                "control_id": control_id,
                "project": teams_data["jira_project"],
                "owner": owner.login,
                "name": control_info.name,
                "description": control_info.description,
                "report_date": agg.report_date,
                "report_url": f"{request.root_url}report/{control_id}?wfId={wf_id}"
            }
            if rows_id:
                form_data['rows_id'] = rows_id
                response = self.post_task(form_data)
                for cur in rows_id:
                    self.insert_task(wf_id, cur, response['key'])
            elif control_info.jira_mode_id == JiraMode.REGISTRY.value and is_exceeded:
                response = self.post_task(form_data)
                self.insert_task(wf_id, 0, response['key'])
            elif control_info.jira_mode_id == JiraMode.SINGLE.value and is_exceeded:
                detail_data = db.session.query(
                    dq_detailjournal_web.xk
                ).filter_by(
                    control_id=control_id,
                    pm_workflow_run_id=wf_id
                ).order_by(dq_detailjournal_web.report_time.desc()).limit(10).offset(0).all()

                # bulk_tasks = []
                for cur in detail_data:
                    form_data['rows_id'] = cur.xk
                    # bulk_tasks.append(form_data)

                    response = self.post_task(form_data)
                    self.insert_task(wf_id, cur.xk, response['key'])
            else:
                return {'response': 'Task(s) has not created'}, 200

            return {'response': 'task(s) created'}, 200
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def post_task(self, form_data:dict) -> dict:
        endpoint:str = "issue" if self.url.endswith('/') else "/issue"
        self.data['fields']['project']['key'] = form_data['project']
        # self.data['fields']['reporter']['name'] = form_data['owner'] Нет доступа для ТУЗ на смену автора
        self.data['fields']['summary'] = f"Контроль КД {form_data['control_id']}. {form_data['name']} от {form_data['report_date']}"
        self.data['fields']['description'] = (
            'Наименование контроля: ' + form_data['name'] + '\n' +
            'Описание контроля: ' + form_data['description'] + '\n' +
            (f"ID записей: {form_data['rows_id']} \n" if 'rows_id' in form_data else '') +
            'Результат доступен по ссылке: ' +  '\n' + 
            form_data['report_url']
        )
        if InputValidator.validate_jira_url(url=self.url+endpoint):
            try:
                response = requests.post(self.url+endpoint, verify=self.JIRA_CERT_PATH, json=self.data, headers=self.headers, auth=self.auth)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as ex:
                LogEvent.log_error(ex)
                raise ex
            except json.JSONDecodeError as ex:
                LogEvent.log_error(ex)
                raise ex
        else:
            raise Exception("URL is not correct")

    def get_task(self, wf_id:int, xk:int):
        try:
            params:str = "?fields=key,summary,description,assignee,project,status"
            endpoint:str = "issue/" if self.url.endswith('/') else "/issue/"
            key = db.session.query(dq_jira_issues.jira_issue).filter_by(xk=xk, pm_workflow_run_id=wf_id).first().jira_issue

            url:str = self.url + endpoint + key + params
            if InputValidator.validate_jira_url(url=url):
                try:
                    response = requests.get(url, verify=self.JIRA_CERT_PATH, headers=self.headers, auth=self.auth)
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as ex:
                    LogEvent.log_error(ex)
                    return ex
                except json.JSONDecodeError as ex:
                    LogEvent.log_error(ex)
                    return ex
            else:
                raise Exception("URL is not correct")
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex


class JiraREST(Resource):
    @jwt_required()
    def post(self) -> dict:
        control_id = request.json['control_id']
        wf_id = request.json['wf_id']
        jira = JiraApi()
        return jira.create_task(control_id, wf_id)
    