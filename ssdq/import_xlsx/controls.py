import jsonschema
import json
import logging
from flask import request
from flask_login import current_user
from .schema import CONTROL_SCHEMA, CROSSDB_PARAMS_SCHEMA
from ..app.extensions import db
from ..logger.log import LogEvent
from ..models.constants import ControlStatus, AlertingType, JiraMode, DagType
from ..models.user import Users
from ..models.dict import dq_segment_sdim, dq_pattern_sdim, dq_control_type_sdim, \
    subject_area_sdim, dq_source_sdim, dq_object_sdim, tags, dq_characteristic_sdim
from ..controls.controls import Controls


class ImportControls:
    def __init__(self):
        pass

    def __get_attr(self, obj, entity:str=None, **kwargs) -> str:
        """
            Get entity ID by name
        """
        data = obj.query.filter_by(**kwargs).first()
        if data:
            return data.id
        else:
            raise Exception(f"Entity {entity if entity else obj.__name__} for '{kwargs}' not found")

    def __parse_pattern(self, pattern:str, params:dict, source_id:str, **kwargs) -> dict:
        response = {}
        try:
            db_pattern = db.session.query(
                dq_pattern_sdim.id,
                dq_pattern_sdim.params
            ).filter_by(
                name=pattern,
                deleted_flag="N"
            ).first()
            pattern_params = db_pattern.params
        except AttributeError:
            raise Exception(f"SQL шаблон с наименованием {pattern} не найден")
        try:
            if set(pattern_params.keys()) == set(params.keys()):
                response["pattern_id"] = db_pattern.id
                # del row["pattern"]
            else:
                raise Exception("Ключи в params не соответствуют шаблону SQL")
        except KeyError:
            raise Exception("Отсутствует params в файле")

        response["source_pattern"] = str(source_id)
        return response

    def create(self):
        try:
            data = request.get_json()

            control = Controls()
            response = []

            # Валидация файла на наличие обязательных атрибутов
            for index, row in enumerate(data):
                try:
                    jsonschema.validate(instance=row, schema=CONTROL_SCHEMA)
                except jsonschema.ValidationError as e:
                    LogEvent.log_error(e)
                    response.append({
                        "index": index,
                        "control_name": row["control_name"] if "control_name" in row else None,
                        "status": "failed",
                        "message": f"Ошибка валидации. {e.json_path}: {e.message}"
                    })
                    continue

                try:
                    # Поиск UUID для сущностей
                    team_id = current_user.team_id
                    row["team_id"] = team_id

                    segment_id = self.__get_attr(dq_segment_sdim, entity="segment", name=row["segment"], team_id=team_id)
                    row["segment_id"] = segment_id
                    del row["segment"]

                    source_id = self.__get_attr(dq_source_sdim, entity="source", name=row["source"])
                    row["source_id"] = str(source_id)
                    row["source"] = str(source_id)

                    status_id = ControlStatus.DEVELOPMENT.value
                    row["status_id"] = status_id

                    if not row["control_type"]:
                        control_type_id = self.__get_attr(dq_control_type_sdim, entity="control_type", name=row["control_type"])
                        row["control_type_id"] = control_type_id
                    del row["control_type"]

                    if "subject_area" in row:
                        subject_area_id = self.__get_attr(subject_area_sdim, entity="subject_area", name=row["subject_area"], team_id=team_id)
                        row["subject_area_id"] = subject_area_id
                        del row["subject_area"]
                        
                    if "characteristic" in row:
                        characteristic_id = self.__get_attr(dq_characteristic_sdim, entity="dq_characteristic", name=row["characteristic"])
                        row["characteristic_id"] = characteristic_id
                        del row["characteristic"]

                    alerting_type_id = AlertingType[row["alerting_type"]].value
                    row["alerting_type_id"] = alerting_type_id
                    del row["alerting_type"]

                    jira_mode_id = JiraMode[row["jira_mode"]].value
                    row["jira_mode_id"] = jira_mode_id
                    del row["jira_mode"]

                    row["dagType"] = row["dag_type"]
                    del row["dag_type"]

                    if row["dagType"] in [DagType.CROSSDATABASE.name, DagType.PATTERN.name]:
                        if "params" not in row:
                            raise Exception("params обязателен для заполнения, если выбран шаблонизированный или кросс-системный тип DAG")
                        row["params"] = json.loads(row["params"])

                    if row["dagType"] == DagType.CROSSDATABASE.name:
                        row["main_query"] = row["sql_query"]
                        for src in row["params"]:
                            try:
                                jsonschema.validate(instance=src, schema=CROSSDB_PARAMS_SCHEMA)
                            except jsonschema.ValidationError as e:
                                LogEvent.log_error(e)
                                raise Exception(f"Ошибка валидации params. {e.json_path}: {e.message}")

                    if row["dagType"] == DagType.PATTERN.name:
                        if "pattern" not in row or not row["pattern"]:
                            raise Exception("pattern обязателен для заполнения, если выбран шаблонизированный тип DAG")
                        parsed_pattern = self.__parse_pattern(**row)
                        row.update(parsed_pattern)
                        del row["pattern"]

                    owner_id = []
                    if row["owner"]:
                        for owner in row["owner"].split(" "):
                            owner_id.append(self.__get_attr(Users, entity="owner", login=owner))
                    else:
                        owner_id.append(current_user.id)
                    row["owner_id"] = owner_id

                    alerting = []
                    if row["mail_list"]:
                        for user in row["mail_list"].split(" "):
                            alerting.append(self.__get_attr(Users, entity="mail_list", login=user))
                    row["alerting"] = alerting

                    object_id = []
                    if row["objects"]:
                        for obj in row["objects"].split(" "):
                            search_obj = obj.split(".")
                            bd_id = db.session.query(dq_object_sdim.id).filter_by(
                                base_name=search_obj[0],
                                schema=search_obj[1],
                                table_name=search_obj[2]
                            ).first()
                            if bd_id:
                                object_id.append(bd_id.id)
                            else:
                                raise Exception(f"Entity object for '{obj}' not found")
                    row["object_id"] = object_id

                    tag_id = []
                    if "tags" in row and row["tags"]:
                        for tag in row["tags"].split(","):
                            bd_id = db.session.query(tags.id).filter_by(
                                name=tag
                            ).first()
                            if bd_id:
                                tag_id.append(bd_id.id)
                            else:
                                raise Exception(f"Entity tag for '{obj}' not found")
                    row["tag_id"] = tag_id

                    if "cron" in row:
                        row["cron"] = row["cron"] if row["cron"] else None
                    row["onlySpec"] = False

                    row["limit"] = True

                    # Создание контроля
                    created = control.create(row)
                    if created[1] != 201:
                        raise Exception(created[0])
                    response.append({
                        "index": index,
                        "control_name": row["control_name"],
                        "status": "success",
                        "message": ""
                    })

                except Exception as ex:
                    LogEvent.log_error(ex)
                    tb = ex.__traceback__
                    template = "An exception of type {0} occurred. Arguments: {1}"
                    message = template.format(
                        type(ex).__name__, 
                        ex.args)
                    response.append({
                        "index": index,
                        "control_name": row["control_name"],
                        "status": "failed",
                        "message": message
                    })
                    logging.info(f"Control {row['control_name']} did not create")

            return {"data": response}, 200

        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500
    