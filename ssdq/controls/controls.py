from ..app.extensions import db
from ..models.base import dq_control_sdim, dq_control_object_stat, dq_control_owner_stat, \
    dq_dag_sdim, dq_alerting_stat, dq_control_hist, \
    dq_validation_stat, dq_control_tags_stat
from ..models.dict import dq_control_type_sdim, dq_source_sdim, subject_area_sdim, \
    dq_object_sdim, dq_segment_sdim, dq_pattern_sdim, tags, dq_team_attributes_dim, \
    dq_characteristic_sdim
from ..models.constants import JiraMode, JiraModeRu, critical_level, \
    ControlStatus, ControlStatusRu, AlertingType, AlertingTypeRu, DagType, \
    DagTypeRu
from ..models.user import Teams, Users
from ..logger.log import LogEvent
from .validation import Validation
from .utils import from_cron
from .dags import ControlDagMap, ControlDag
from flask import request, render_template, redirect
from flask_login import current_user
from sqlalchemy import and_, case
from datetime import datetime
import json


class Controls:
    def __init__(self):
        pass
    
    @staticmethod
    def get_team_attributes(team_id:str):
        try:
            attributes = db.session.query(
                dq_team_attributes_dim.name,
                dq_team_attributes_dim.description,
                dq_team_attributes_dim.is_required
            ).filter_by(
                team_id=team_id
            ).all()
            return [dict(
                key=at.name,
                description=at.description,
                is_required=at.is_required
            ) for at in attributes]
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def render():
        try:
            id = request.args.get("id")
            if current_user.admin:
                controls = db.session.query(
                    dq_control_sdim.id,
                    dq_control_sdim.name
                ).filter_by(
                    deleted_flag="N"
                ).all()
            else:
                controls = db.session.query(
                    dq_control_sdim.id,
                    dq_control_sdim.name
                ).filter_by(
                    team_id=current_user.team_id,
                    deleted_flag="N"
                ).all()

            if id:
                card = dq_control_sdim.query.join(
                    dq_control_type_sdim, and_(
                        dq_control_type_sdim.id == dq_control_sdim.control_type_id,
                        dq_control_type_sdim.deleted_flag == 'N'
                    ),
                    isouter=True
                ).join(
                    dq_source_sdim, and_(
                        dq_source_sdim.id == dq_control_sdim.source_id,
                        dq_source_sdim.deleted_flag == 'N'
                    ),
                    isouter=True
                ).join(
                    subject_area_sdim, and_(
                        subject_area_sdim.id == dq_control_sdim.subject_area_id,
                        subject_area_sdim.deleted_flag == 'N'
                    ),
                    isouter=True
                ).join(
                    dq_characteristic_sdim, dq_characteristic_sdim.id == dq_control_sdim.characteristic_id,
                    isouter=True
                ).join(
                    Teams, Teams.id == dq_control_sdim.team_id
                ).add_columns(
                    dq_control_sdim.id,
                    dq_control_sdim.name,
                    dq_control_sdim.description,
                    dq_control_sdim.conditions,
                    case(
                        *[(dq_control_sdim.critical_level == str(cur.name), str(cur.value)) for cur in critical_level]
                    ).label("critical_level"),
                    dq_control_sdim.threshold_min,
                    dq_control_sdim.threshold_max,
                    dq_control_sdim.status_id,
                    dq_control_sdim.jira_mode_id,
                    dq_control_type_sdim.name.label("control_type_name"),
                    dq_source_sdim.description.label("source_name"),
                    subject_area_sdim.name.label("subject_area_name"),
                    Teams.json["display_name"].label("team_name"),
                    dq_characteristic_sdim.name.label("characteristic_name"),
                    dq_control_sdim.team_attributes
                ).filter(
                    dq_control_sdim.id == id,
                    dq_control_sdim.deleted_flag == 'N'
                ).first()

                status = ControlStatusRu[ControlStatus(int(card.status_id)).name].value

                jira_mode = JiraModeRu[JiraMode(int(card.jira_mode_id)).name].value if int(card.jira_mode_id) != 0 else None

                owners = dq_control_owner_stat.query.join(
                    Users, Users.id == dq_control_owner_stat.owner_id
                ).add_columns(
                    Users.name,
                    Users.email
                ).filter(
                    dq_control_owner_stat.control_id == id
                ).all()

                objects = dq_control_object_stat.query.join(
                    dq_object_sdim, and_(
                        dq_object_sdim.id == dq_control_object_stat.object_id,
                        dq_object_sdim.deleted_flag == 'N'
                    )
                ).add_columns(
                    dq_object_sdim.schema,
                    dq_object_sdim.table_name
                ).filter(
                    dq_control_object_stat.control_id == id
                ).all()

                try:
                    dag_type_id = db.session.query(dq_dag_sdim.dag_type).filter_by(
                        control_id=id, deleted_flag='N'
                    ).first()
                    dag_type = str(DagTypeRu[DagType(dag_type_id.dag_type).name].value) if dag_type_id.dag_type else None
                except AttributeError:
                    dag_type = None

                tags_db = dq_control_tags_stat.query.join(
                    tags, tags.id == dq_control_tags_stat.tag_id
                ).add_columns(
                    tags.name
                ).filter(
                    dq_control_tags_stat.control_id == id
                ).all()
                tags_list = [str(tag.name) for tag in tags_db]
            else:
                card = None
                owners = None
                objects = None
                status = None
                jira_mode = None
                dag_type = None
                tags_list = None

            return render_template('home/controls.html', 
                                   controls=controls, card=card, owners=owners, jira_mode=jira_mode,
                                   objects=objects, dag_type=dag_type, status=status, control_id=id,
                                   tags=tags_list)
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def render_crud(action:str, control_id:int|str|None=None):
        """
            Parameter action: create, update
        """
        try:
            filters = dict(deleted_flag="N") if current_user.admin else dict(deleted_flag="N", team_id=current_user.team_id)

            segments =  db.session.query(
                dq_segment_sdim.id, dq_segment_sdim.name, dq_segment_sdim.team_id
            ).filter_by(
                **filters
            ).all()

            statuses = [dict(id=cur.value, name=cur.name, display_name=ControlStatusRu[cur.name].value) for cur in ControlStatus]

            sources = db.session.query(
                dq_source_sdim.id, dq_source_sdim.name, dq_source_sdim.description
            ).filter_by(
                deleted_flag="N"
            ).all()

            control_types = db.session.query(
                dq_control_type_sdim.id, dq_control_type_sdim.name
            ).filter_by(
                deleted_flag="N"
            ).all()

            subject_area = db.session.query(
                subject_area_sdim.id, subject_area_sdim.name, subject_area_sdim.team_id
            ).filter_by(
                **filters
            ).all()

            alerting_type = [dict(id=cur.value, name=cur.name, display_name=AlertingTypeRu[cur.name].value) for cur in AlertingType]

            jira_mode = [dict(id=cur.value, name=cur.name, display_name=JiraModeRu[cur.name].value) for cur in JiraMode]
            
            characteristic = db.session.query(
                    dq_characteristic_sdim.id,
                    dq_characteristic_sdim.name
                ).all()

            if current_user.admin:
                team_list = db.session.query(
                    Teams.id, Teams.json["display_name"].label("display_name")
                ).all()
            else:
                team_list = db.session.query(
                    Teams.id, Teams.json["display_name"].label("display_name")
                ).filter_by(
                    id=current_user.team_id
                ).all()

            minutes, hours, days_in_month = [], [], []
            for x in range(60):
                minutes.append(str(x).zfill(2))
            for x in range(24):
                hours.append(str(x).zfill(2))
            for x in range(1, 32):
                days_in_month.append(str(x).zfill(2))
                
            if action == "create":
                return render_template('home/create-control.html',
                                       segments=segments, statuses=statuses, sources=sources, 
                                       minutes=minutes, hours=hours, days_in_month=days_in_month, teams=team_list,
                                       control_types=control_types, subject_area=subject_area, alerting_type=alerting_type,
                                       jira_mode=jira_mode, critical_level=critical_level, characteristic=characteristic)
            elif action == "update":
                if control_id is None:
                    return redirect("/controls")

                control = dq_control_sdim.query.filter_by(id=control_id).first()
                owners = dq_control_owner_stat.query.join(
                    Users, Users.id == dq_control_owner_stat.owner_id
                ).add_columns(
                    Users.id,
                    Users.name,
                    Users.email
                ).filter(
                    dq_control_owner_stat.control_id == control_id
                ).all()

                objects = dq_control_object_stat.query.join(
                    dq_object_sdim, dq_object_sdim.id == dq_control_object_stat.object_id
                ).add_columns(
                    dq_object_sdim.id,
                    dq_object_sdim.schema,
                    dq_object_sdim.table_name
                ).filter(
                    dq_control_object_stat.control_id == control_id
                ).all()

                alerting_users = dq_alerting_stat.query.join(
                    Users, Users.id == dq_alerting_stat.user_id
                ).add_columns(
                    Users.id,
                    Users.name,
                    Users.email
                ).filter(
                    dq_alerting_stat.control_id == control_id
                ).all()

                dag = dq_dag_sdim.query.filter_by(control_id=control_id, deleted_flag="N").first()
                created_user = db.session.query(Users.name, Users.email).filter_by(id=control.created_by).first()

                schedule = from_cron(dag.cron) if dag else None

                try:
                    dag_type_id = db.session.query(dq_dag_sdim.dag_type).filter_by(
                        control_id=control_id, deleted_flag='N'
                    ).first()
                    dag_type = str(DagType(dag_type_id.dag_type).name) if dag_type_id.dag_type else None
                except AttributeError:
                    dag_type = None

                if dag_type == DagType.PATTERN.name:
                    sql_pattern = db.session.query(
                        dq_pattern_sdim.sql,
                        dq_pattern_sdim.name,
                        dq_pattern_sdim.id,
                        dq_pattern_sdim.params
                    ).filter_by(id=dag.pattern_id).first()
                else:
                    sql_pattern = None

                tags_list = dq_control_tags_stat.query.join(
                    tags, tags.id == dq_control_tags_stat.tag_id
                ).add_columns(
                    tags.id,
                    tags.name
                ).filter(
                    dq_control_tags_stat.control_id == control_id
                ).all()

                return render_template(
                    'home/update-control.html',
                    segments=segments, statuses=statuses, sources=sources, hours=hours, minutes=minutes,
                    days_in_month=days_in_month, teams=team_list, control_types=control_types, subject_area=subject_area,
                    alerting_type=alerting_type, jira_mode=jira_mode,critical_level=critical_level, dag_type=dag_type,
                    characteristic=characteristic,
                    # controls info
                    control=control, owners=owners, objects=objects, created_user=created_user, alerting_users=alerting_users,
                    dag=dag, schedule=schedule, sql_pattern=sql_pattern, tags=tags_list
                )
            else:
                redirect("/controls")

        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def create(self, data:dict=None):
        try:
            if not data:
                data = request.get_json()
            team_attributes = json.loads(data['team_attributes'])
            del data['team_attributes']
            
            control = dq_control_sdim(
                name=data["control_name"],
                created_by=current_user.id,
                team_attributes=team_attributes,
                **data
            )
            db.session.add(control)
            db.session.commit()
            control_id = int(control.id)

            self.__insert_owners(control_id, data["owner_id"])

            self.__insert_objects(control_id, data["object_id"])

            self.__insert_alerting(control_id, data["alerting"])

            self.__insert_tags(control_id, data["tag_id"])

            if not data['onlySpec']:
                dag_type = DagType[data["dagType"]]
                dag_class = ControlDagMap.get_dag_class(dag_type, control_id)
                dag_class.create(**data)
                dag_class.deploy_dag(control_id)
                
            db.session.commit()

            LogEvent.log_event(eventName="createEntity", entityName="DQControl", entityId=str(control_id))
            return {"control_id": control_id}, 201

        except Exception as ex:
            LogEvent.log_error(ex)
            db.session.rollback()
            dq_control_sdim.query.filter_by(id=control_id).delete()
            db.session.commit()
            return {"message": str(ex)}, 500

    def update(self, id:str|int):
        try:
            now = datetime.now()

            data = request.get_json()
            team_attributes = json.loads(data['team_attributes'])
            del data['team_attributes']

            control_sdim:bool = data['dq_control_sdim']
            control_owner_stat:bool = data['dq_control_owner_stat']
            control_object_stat:bool = data['dq_control_object_stat']
            dag_sdim:bool = data['dq_dag_sdim']
            alerting_sdim:bool = data['dq_alerting_stat']
            control_tags_stat:bool = data['dq_control_tags_stat']

            need_to_deploy = False

            if control_sdim:
                control = dq_control_sdim.query.filter_by(id=id).first()

                prev_status = int(control.status_id)

                control_hist = dq_control_hist(
                    id=control.id,
                    name=control.name,
                    description=control.description,
                    conditions=control.conditions,
                    segment_id=control.segment_id,
                    source_id=control.source_id,
                    status_id=control.status_id,
                    wiki=control.wiki,
                    team_id=control.team_id,
                    threshold_min=control.threshold_min,
                    threshold_max=control.threshold_max,
                    control_type_id=control.control_type_id,
                    subject_area_id=control.subject_area_id,
                    critical_level=control.critical_level,
                    alerting_type_id=control.alerting_type_id,
                    jira_mode_id=control.jira_mode_id,
                    effective_from=control.updated_at,
                    effective_to=now,
                    team_attributes=control.team_attributes,
                    characteristic_id=control.characteristic_id
                )
                db.session.add(control_hist)
                # db.session.commit()

                control = dq_control_sdim.query.filter_by(
                    id=id
                )
                control_attributes = [name for name, value in dq_control_sdim.__dict__.items() 
                    if not name.startswith("__") and not callable(value)]

                filtered_data = {k: data[k] for k in control_attributes if k in data}

                control.update(dict(
                    name=data["control_name"],
                    updated_at=now,
                    team_attributes=team_attributes,
                    **filtered_data
                ))
                # db.session.commit()

                """Check previous status. If it was disabled or actualization and exploitation now then delete from validation list"""
                disabled_status = [ControlStatus.ACTUALIZATION, ControlStatus.DISABLED]
                if prev_status in disabled_status and int(data["status_id"]) not in disabled_status:
                    Validation.delete_validated(id)

                need_to_deploy = True

            if control_owner_stat:
                delete = dq_control_owner_stat.query.filter_by(control_id=id).delete()
                # db.session.commit()
                self.__insert_owners(id, data["owner_id"])

            if control_object_stat:
                delete = dq_control_object_stat.query.filter_by(control_id=id).delete()
                # db.session.commit()
                self.__insert_objects(id, data["object_id"])

            if alerting_sdim:
                delete = dq_alerting_stat.query.filter_by(control_id=id).delete()
                # db.session.commit()
                self.__insert_alerting(id, data["alerting"])

                need_to_deploy = True

            if control_tags_stat:
                delete = dq_control_tags_stat.query.filter_by(control_id=id).delete()
                # db.session.commit()
                self.__insert_tags(id, data["tag_id"])

            if not data['onlySpec'] and dag_sdim:
                dag_type = DagType[data["dagType"]]
                dag_class = ControlDagMap.get_dag_class(dag_type, id)
                dag_class.update(**data)

                need_to_deploy = True
            
            db.session.commit()

            LogEvent.log_event(eventName="updateEntity", entityName="DQControl", entityId=str(id))
            
            if need_to_deploy and not data['onlySpec']:
                ControlDag.deploy_dag(id)
            return '', 204

        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    def delete(self, id:int|str):
        try:
            now = datetime.now()
            update = dq_control_sdim.query.filter_by(id=id).update(dict(deleted_flag='Y', updated_at=now))
            db.session.commit()

            delete = dq_alerting_stat.query.filter_by(control_id=id).delete()
            db.session.commit()

            delete = dq_control_owner_stat.query.filter_by(control_id=id).delete()
            db.session.commit()

            delete = dq_control_object_stat.query.filter_by(control_id=id).delete()
            db.session.commit()

            delete = dq_control_tags_stat.query.filter_by(control_id=id).delete()
            db.session.commit()

            dag_class = ControlDag(id)
            dag_class.delete()

            LogEvent.log_event(eventName="deleteEntity", entityName="DQControl", entityId=str(id))

            dag_class.delete_dag(id)

            return '', 204

        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    def actualize(self, id:int|str):
        try:
            update = dq_control_sdim.query.filter_by(id=id).update(
                dict(
                    updated_at=datetime.now(),
                    status_id=ControlStatus.EXPLOITATION.value
                )
            )
            db.session.commit()

            delete = dq_validation_stat.query.filter_by(control_id=id).delete()
            db.session.commit()

            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    def __insert_owners(self, control_id:int|str, owner_list:list) -> None:
        owners = [dq_control_owner_stat(control_id=control_id, owner_id=cur) for cur in owner_list]
        db.session.add_all(owners)
        # db.session.commit()

    def __insert_objects(self, control_id:int|str, object_list:list) -> None:
        objects = [dq_control_object_stat(control_id=control_id, object_id=cur) for cur in object_list]
        db.session.add_all(objects)
        # db.session.commit()

    def __insert_alerting(self, control_id:int|str, alerting_list:list) -> None:
        if alerting_list:
            alerting = [dq_alerting_stat(control_id=control_id, user_id=cur) for cur in alerting_list]
            db.session.add_all(alerting)
            # db.session.commit()

    def __insert_tags(self, control_id:int|str, tags_list:list) -> None:
        if tags_list:
            tags = [dq_control_tags_stat(control_id=control_id, tag_id=cur) for cur in tags_list]
            db.session.add_all(tags)
            # db.session.commit()
