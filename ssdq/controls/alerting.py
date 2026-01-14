from ..app.extensions import db
from ..models.base import dq_control_sdim, dq_alerting_stat
from ..models.user import Users
from ..models.constants import AlertingType
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from ..logger.log import LogEvent


class Alerting:

    @staticmethod
    def get_email_list(control_id:int) -> list:
        response = dq_alerting_stat.query.join(
            Users,
            Users.id == dq_alerting_stat.user_id
        ).add_columns(
            Users.email
        ).filter(
            dq_alerting_stat.control_id == control_id
        ).all()
        db.session.close()
        return [cur.email for cur in response]
    
    @staticmethod
    def get_alerting_type(control_id:int) -> int:
        response = db.session.query(dq_control_sdim.alerting_type_id).filter_by(
            id=control_id,
            deleted_flag="N"
        ).first()
        db.session.close()
        return int(response.alerting_type_id)
    
    @staticmethod
    def check_threshold(control_id:int, result:int) -> bool:
        threshold = db.session.query(dq_control_sdim.threshold_max).filter_by(
            id=control_id,
            deleted_flag="N",
        ).first()
        db.session.close()
        return True if result > int(threshold.threshold_max) else False


class AlertingArgs:
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('control_id', type=int, location='args', required=True)
        self.parser.add_argument('result', type=int, location='args')

    def get_args(self):
        return self.parser.parse_args()


class AlertingREST(Resource):
    @jwt_required()
    def get(self):
        try:
            args = AlertingArgs().get_args()
            control_id = args['control_id']
            result = args['result']
            alerting_type = Alerting.get_alerting_type(control_id)

            if alerting_type == AlertingType.NEVER.value:
                response = {
                    "send": False,
                    "emails": []
                }, 200
            elif alerting_type == AlertingType.ALWAYS.value:
                emails = Alerting.get_email_list(control_id)
                response = {
                    "send": True if len(emails)>0 else False,
                    "emails": emails
                }, 200
            elif alerting_type == AlertingType.EXCEEDED.value:
                check_threshold = Alerting.check_threshold(control_id=control_id, result=result)
                if not check_threshold:
                    response = {
                        "send": False,
                        "emails": []
                    }
                else:
                    emails = Alerting.get_email_list(control_id)
                    response = {
                        "send": True if len(emails)>0 else False,
                        "emails": emails
                    }, 200
            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
