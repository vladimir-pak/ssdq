from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from .log import LogEvent
import re
import os
import socket
from datetime import datetime, timedelta
# from ..models import Log
from ..models.audit import sdq_logs
from ..app.extensions import db
from ..models.dict import Config
from ..app.dbconfig import ConfigClass


class LogLoad:
    def __init__(self):
        self.dq_session = db.session

    def insert_logs(self):
        logs = self.parse_logs()
        self.dq_session.add_all(logs)
        self.dq_session.commit()
        LogEvent.log_event(
            eventName="logsUpload",
            sUser=get_jwt_identity()['username'],
            sUserId=get_jwt_identity()['userId'],
            message="logs uploaded to database successful"
        )
        return {'response': 'logs has been uploaded'}, 204

    def delete_logs(self):
        try:
            conf = Config.query.order_by(Config.id.desc()).first()
            depth = conf.json['logs_depth']
        except:
            conf = ConfigClass()
            depth = conf.config_json['logs_depth']
            
        storage_depth = datetime.now() - timedelta(days=int(depth))
        self.dq_session.query(sdq_logs).filter(sdq_logs.uploaded_at < storage_depth).delete()
        LogEvent.log_event(
            eventName="logsDeleted",
            sUser=get_jwt_identity()['username'],
            sUserId=get_jwt_identity()['userId'],
            message="logs deleted in database successful"
        )
        return {'logs': 'logs has been deleted'}, 204

    @staticmethod
    def parse_logs():
        last_row: sdq_logs | None = sdq_logs.query.order_by(sdq_logs.uploaded_at.desc()).first()
        last_date = last_row.uploaded_at if last_row is not None else datetime(2000, 1, 1, 0, 0, 0)
        logs = []
        
        f = open(current_app.config["FILENAME"], 'r')
        for row in f:
            search = re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d*', row)
            error_log = False
            if not search:
                search = re.search('\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}\]', row)
                error_log = True
            date = datetime.strptime(search.group(0), ('[%Y-%m-%d %H:%M:%S +%f]' if error_log else '%Y-%m-%d %H:%M:%S,%f')) if search is not None else None

            if date is None or date <= last_date:
                continue

            search = re.search('sUser:[^;]+;', row)
            user = search.group(0).strip()[7:-1] if search is not None else None

            search = re.search('sUserId:[^;]+;', row)
            user_id = search.group(0).strip()[9:-1] if search is not None else None

            search = re.search('eventName:[^;]+;', row)
            event = search.group(0).strip()[11:-1] if search is not None else None

            search = re.search('entityName:[^;]+;', row)
            entity_name = search.group(0).strip()[12:-1] if search is not None else None

            search = re.search('entityId:[^;]+;', row)
            entity_id = search.group(0).strip()[10:-1] if search is not None else None

            search = re.search('sHost:[^;]+;', row)
            src_host = search.group(0).strip()[7:-1] if search is not None else None

            search = re.search('message:[^;]+;', row)
            if search:
                message = search.group(0).strip()[9:-1] if search is not None else None
                msg = dict(msg=message) if message is not None else None
            else:
                msg = dict(msg=row)
                
            search = re.search('Shutting down: Master$', row)
            if search:
                event = "stopServer"
                msg = dict(msg="stop SSDQ server")

            spt = os.getenv("FLASK_RUN_PORT")
            app = "https"
            dhostname = socket.gethostname()

            logs.append(sdq_logs(
                start=date,
                eventtype=event,
                name=event,
                eventobj=entity_name,
                eventobjid=entity_id,
                suser=user,
                suserid=user_id,
                spt=spt,
                app=app,
                msg=msg,
                src=src_host,
                shost=src_host,
                dhostname=dhostname
            ))

        return logs
    


class RestLog(Resource):
    @jwt_required()
    def post(self):
        try:
            return LogLoad().insert_logs()
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
    
    @jwt_required()
    def delete(self):
        try:
            return LogLoad().delete_logs()
        except Exception as ex:
            LogEvent.log_error(ex)
            return {'response': str(ex)}, 500
