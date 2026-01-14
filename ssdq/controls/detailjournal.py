from sqlalchemy import delete
from datetime import datetime, timedelta
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..app.extensions import db
from ..models.base import dq_detailjournal_web, dq_detail_agg
from ..models.dict import Config
from ..logger.log import LogEvent


class DetailJournal:

    def __init__(self):
        pass

    @staticmethod
    def get_config_param(param:str) -> str:
        conf = Config.query.order_by(Config.id.desc()).first()
        return conf.json[param]

    @staticmethod
    def delete_results():
        results_depth = int(DetailJournal.get_config_param('result_depth'))
        param_date = datetime.now() - timedelta(days=results_depth)
        
        delete = dq_detailjournal_web.query.filter(
            dq_detailjournal_web.report_time <= param_date
        ).delete()
        db.session.commit()
        
        delete = dq_detail_agg.query.filter(
            dq_detail_agg.report_date <= param_date
        ).delete()
        db.session.commit()

        return None


class DetailJournalREST(Resource):
    @jwt_required()
    def delete(self):
        try:
            DetailJournal().delete_results()
            LogEvent.log_event(
                eventName="deleteControlsResults",
                sUser=get_jwt_identity()['username'],
                sUserId=get_jwt_identity()['userId'],
                message="control results deleted successful"
            )
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
        return {'response': 'dq controls results deleted'}, 200
