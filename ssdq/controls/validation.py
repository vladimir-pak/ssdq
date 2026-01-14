from datetime import datetime, timedelta
from sqlalchemy import and_
from ..app.extensions import db
from ..logger.log import LogEvent
from ..models.base import dq_control_sdim, view_controls_last_results, dq_control_owner_stat, \
    dq_validation_stat, dq_control_hist
from ..models.user import Users
from ..models.dict import Config
from ..models.constants import ControlStatus, ValidationType
from ..integration.airflow import AirflowAPI
from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity


class Validation:
    def __init__(self):
        pass

    def validate(self) -> None:
        self.__validate()
        self.__validate_results()
        self.__pause_dags()
        self.__change_status()
        
        return None
    
    def disable_expired_controls(self) -> None:
        self.__disable_controls()

        return None

    def __change_status(self) -> None:
        """
        Method for changing status on ACTUALIZATION
        """
        try:
            now = datetime.now()

            controls = dq_control_sdim.query.join(
                dq_validation_stat, 
                and_(
                    dq_control_sdim.id == dq_validation_stat.control_id,
                    dq_validation_stat.disabled == False,
                    dq_validation_stat.disable_date <= now,
                    dq_validation_stat.validation_type_id == ValidationType.WARNING.value,
                )
            ).add_columns(
                dq_control_sdim.id,
                dq_control_sdim.name,
                dq_control_sdim.description,
                dq_control_sdim.conditions,
                dq_control_sdim.segment_id,
                dq_control_sdim.source_id,
                dq_control_sdim.status_id,
                dq_control_sdim.wiki,
                dq_control_sdim.team_id,
                dq_control_sdim.threshold_min,
                dq_control_sdim.threshold_max,
                dq_control_sdim.control_type_id,
                dq_control_sdim.subject_area_id,
                dq_control_sdim.critical_level,
                dq_control_sdim.alerting_type_id,
                dq_control_sdim.jira_mode_id,
                dq_control_sdim.updated_at
            ).filter(
                dq_control_sdim.status_id == ControlStatus.EXPLOITATION.value,
                dq_control_sdim.deleted_flag == "N"
            ).all()
            
            update_id = [int(cur.id) for cur in controls]

            if len(update_id) == 0:
                return None
            
            control_hist = [dq_control_hist(
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
                effective_to=datetime.now()
            ) for control in controls]
            db.session.add_all(control_hist)
            db.session.commit()

            update = dq_control_sdim.query.filter(
                dq_control_sdim.id.in_(update_id),
                dq_control_sdim.deleted_flag == "N"
            ).update(
                dict(
                    updated_at=now,
                    status_id=ControlStatus.ACTUALIZATION.value
                )
            )
            db.session.commit()

            update = dq_validation_stat.query.filter(
                dq_validation_stat.control_id.in_(update_id),
                ).update(
                    dict(
                        disabled=True,
                        validation_type_id=ValidationType.DISABLED.value,
                        updated_at=now,
                        emailed=False
                    )
                )
            db.session.commit()

            return None
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def __validate(self) -> None:
        """
        Method for inserting into dq_validation_stat controls that are approaching their update (actualizing) date
        """
        try:
            now = datetime.now()

            new_controls = dq_control_sdim.query.outerjoin(
                dq_validation_stat, 
                dq_control_sdim.id == dq_validation_stat.control_id
            ).add_columns(
                dq_control_sdim.id,
                dq_control_sdim.updated_at
            ).filter(
                dq_validation_stat.control_id == None,
                dq_control_sdim.status_id == ControlStatus.EXPLOITATION.value,
                dq_control_sdim.deleted_flag == "N"
            ).all()

            validation_param = int(Validation.get_config_param('actual_freq'))
            expiring_param = int(Validation.get_config_param('actual_alert'))

            bulk_insert = []
            for cur in new_controls:
                validation_date = cur.updated_at + timedelta(days=validation_param)
                expiring_date = validation_date - timedelta(days=expiring_param)
                if expiring_date <= now:
                    bulk_insert.append(
                        dict(
                            control_id=cur.id,
                            disabled=False,
                            disable_date=validation_date,
                            updated_at=now,
                            validation_type_id=ValidationType.WARNING.value,
                            emailed=False
                        )
                    )

            if len(bulk_insert) > 0:
                db.session.bulk_insert_mappings(dq_validation_stat, bulk_insert)
                db.session.commit()

            return None
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    def __validate_results(self) -> None:
        """
        Method for inserting into dq_validation_stat controls with execution error or stopped by timeout
        """
        try:
            controls_error = db.session.query(view_controls_last_results.id)\
                .filter(
                    view_controls_last_results.error_flag == 'Y',
                    view_controls_last_results.status_id == ControlStatus.EXPLOITATION.value
                ).all()

            if len(controls_error) == 0:
                return None
            
            now = datetime.now()
            bulk_insert = [
                dict(
                    control_id=cur.id,
                    disabled=False,
                    disable_date=now,
                    updated_at=now,
                    validation_type_id=ValidationType.WARNING.value,
                    emailed=False
                ) for cur in controls_error
            ]

            db.session.bulk_insert_mappings(dq_validation_stat, bulk_insert)
            db.session.commit()

            return None
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    def __pause_dags(self) -> None:
        try:
            now = datetime.now()
            controls = db.session.query(dq_validation_stat.control_id).filter(
                    dq_validation_stat.disabled == False,
                    dq_validation_stat.disable_date <= now,
                    dq_validation_stat.validation_type_id == ValidationType.WARNING.value
                ).all()

            if len(controls) == 0:
                return None
            
            for cur in controls:
                AirflowAPI().pause_dag(cur.control_id)

            return None
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    def __disable_controls(self):
        """
        Method for disabling expired controls
        """
        try:
            expired_duration = int(Validation.get_config_param('actual_duration'))
            now = datetime.now()
                
            expired_controls = dq_control_sdim.query.join(
                dq_validation_stat, 
                and_(
                    dq_control_sdim.id == dq_validation_stat.control_id,
                    dq_validation_stat.updated_at < now - timedelta(days=expired_duration),
                    dq_validation_stat.validation_type_id == ValidationType.DISABLED.value,
                    dq_validation_stat.disabled == True
                )
            ).add_columns(
                dq_control_sdim.id,
                dq_control_sdim.name,
                dq_control_sdim.description,
                dq_control_sdim.conditions,
                dq_control_sdim.segment_id,
                dq_control_sdim.source_id,
                dq_control_sdim.status_id,
                dq_control_sdim.wiki,
                dq_control_sdim.team_id,
                dq_control_sdim.threshold_min,
                dq_control_sdim.threshold_max,
                dq_control_sdim.control_type_id,
                dq_control_sdim.subject_area_id,
                dq_control_sdim.critical_level,
                dq_control_sdim.alerting_type_id,
                dq_control_sdim.jira_mode_id,
                dq_control_sdim.updated_at
            ).all()
            
            if len(expired_controls) == 0:
                return None
            
            control_hist = [dq_control_hist(
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
                effective_to=datetime.now()
            ) for control in expired_controls]
            db.session.add_all(control_hist)
            db.session.commit()
            
            expired_id = [int(cur.id) for cur in expired_controls]

            update = dq_control_sdim.query.filter(
                    dq_control_sdim.id.in_(expired_id),
                    dq_control_sdim.deleted_flag == "N"
                ).update(
                    dict(
                        updated_at=now,
                        status_id=ControlStatus.DISABLED.value
                    )
                )
            db.session.commit()

            update = dq_validation_stat.query.filter(
                dq_validation_stat.control_id.in_(expired_id)
            ).update(dict(validation_type_id=ValidationType.EXPIRED.value))
            db.session.commit()

            return None
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    @staticmethod
    def delete_validated(control_id:int) -> None:
        delete = dq_validation_stat.query.filter(
            dq_validation_stat.control_id == control_id
        ).delete()
        db.session.commit()

        return None
    
    @staticmethod
    def delete_expired() -> None:
        delete = dq_validation_stat.query.filter_by(
            validation_type_id=ValidationType.EXPIRED.value
        ).delete()
        db.session.commit()

        return None
    
    @staticmethod
    def get_config_param(param:str) -> str:
        conf = Config.query.order_by(Config.updated_at.desc()).first()
        return conf.json[param]
    

class ValidationEmails:
    @staticmethod
    def get_emails(validation_type_id:int) -> list|None:
        """
        Method for getting emails and controls
        """
        controls = dq_validation_stat.query.join(
            dq_control_owner_stat, dq_validation_stat.control_id == dq_control_owner_stat.control_id
        ).join(
            Users, dq_control_owner_stat.owner_id == Users.id
        ).add_columns(
            dq_validation_stat.control_id,
            dq_validation_stat.disable_date,
            dq_validation_stat.updated_at,
            Users.email
        ).filter(
            dq_validation_stat.validation_type_id == validation_type_id,
            dq_validation_stat.emailed == False
        ).all()

        db.session.close()

        response = []
        uniq_controls = []

        for cur in controls:
            if cur.control_id not in uniq_controls:
                if validation_type_id == ValidationType.WARNING.value:
                    expire_date = cur.disable_date.strftime('%d.%m.%Y')
                elif validation_type_id == ValidationType.DISABLED.value:
                    act_duration = int(Validation.get_config_param('actual_duration'))
                    expire_date = (cur.updated_at + timedelta(days=act_duration)).strftime('%d.%m.%Y')
                else:
                    expire_date = None
                emails = {
                    'expire_date': expire_date,
                    'control_id': cur.control_id,
                    'emails': [cur.email]
                }
                uniq_controls.append(cur.control_id)
                response.append(emails)
            else:
                index = uniq_controls.index(cur.control_id)
                response[index]['emails'].append(cur.email)
        
        return response
    
    @staticmethod
    def mark_emailed(controls:list) -> None:
        now = datetime.now()
        try:
            controls:list[int] = list(map(int, controls))
            
            update = dq_validation_stat.query.filter(
                dq_validation_stat.control_id.in_(controls)
            ).update(
                dict(
                    emailed=True,
                    updated_at=now
                )
            )
            db.session.commit()
        except Exception as ex:
            LogEvent.log_error(ex)
            raise
        return None


class ValidationArgs:
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('validationTypeId', type=int, location='args', required=True)

    def get_args(self):
        return self.parser.parse_args()


class PostValidate(Resource):
    @jwt_required()
    def post(self):
        try:
            Validation().validate()
            LogEvent.log_event(
                eventName="validation",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="Not updated controls disabled successful"
            )
            return {'response': 'Not updated controls disabled'}, 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
    
    @jwt_required()
    def delete(self):
        try:
            Validation().disable_expired_controls()
            LogEvent.log_event(
                eventName="validation",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="Expired controls disabled successful"
            )
            return {'response': 'Expired controls disabled'}, 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
    

class ValidationEmailsRest(Resource):
    @jwt_required()
    def get(self):
        try:
            args = ValidationArgs().get_args()
            validation_type_id = args['validationTypeId']
            response = ValidationEmails.get_emails(validation_type_id)
            LogEvent.log_event(
                eventName="validationEmails",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="get emails with validation controls"
            )
            return response, 200
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
        
    @jwt_required()
    def post(self):
        args = request.json
        try:
            ValidationEmails.mark_emailed(args['controls'])
            LogEvent.log_event(
                eventName="validationEmails",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="validation controls marked with emailed flag"
            )
            return None, 200
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
    
    @jwt_required()
    def delete(self):
        try:
            Validation.delete_expired()
            LogEvent.log_event(
                eventName="validationEmails",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="expired controls deleted from validation list"
            )
            return None, 200
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
    