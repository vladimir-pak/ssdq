from ..models.dict import Config
from .extensions import db
from flask import render_template, request
from flask_login import current_user
from datetime import datetime
from ..integration.airflow import Dag
from ..logger.log import LogEvent


class ConfigClass():
    default_conf = {
            'actual_freq': 180,
            'actual_alert': 10,
            'actual_duration': 30,
            'retry_count': 5,
            'control_duration': 30,
            'result_depth': 90,
            'logs_depth': 365
        }

    def __init__(
        self, 
        actual_freq:int=None, 
        actual_alert:int=None, 
        actual_duration:int=None, 
        retry_count:int=None, 
        control_duration:int=None, 
        result_depth:int=None,
        logs_depth:int=None
    ):
        
        self.config_json = {
            'actual_freq': actual_freq if actual_freq is not None else ConfigClass.default_conf['actual_freq'], #Actualization's frequency (days)
            'actual_alert': actual_alert if actual_alert is not None else ConfigClass.default_conf['actual_alert'], #Actualization's alerting (days)
            'actual_duration': actual_duration if actual_duration is not None else ConfigClass.default_conf['actual_duration'], #Actualization's duration before disable control (days)
            'retry_count': retry_count if retry_count is not None else ConfigClass.default_conf['retry_count'], #Retry count of control
            'control_duration': control_duration if control_duration is not None else ConfigClass.default_conf['control_duration'], #Control's duration (minutes)
            'result_depth': result_depth if result_depth is not None else ConfigClass.default_conf['result_depth'], #Depth of storage controls results
            'logs_depth': logs_depth if logs_depth is not None else ConfigClass.default_conf['logs_depth'] #Depth of storege logs
        }

    def get_param(self, param:str) -> int:
        return self.config_json[param]


class ConfigSSDQ(ConfigClass):
    
    def __init__(self):
        try:
            db_conf = Config.query.order_by(Config.id.desc()).first()
            super().__init__(
                db_conf.json['actual_freq'], 
                db_conf.json['actual_alert'], 
                db_conf.json['actual_duration'], 
                db_conf.json['retry_count'], 
                db_conf.json['control_duration'], 
                db_conf.json['result_depth'],
                db_conf.json['logs_depth']
            )
        except:
            super().__init__()

    def update_config(self):
        params = {
            'actual_freq': request.form.get('actual_freq'), 
            'actual_alert': request.form.get('actual_alert'), 
            'actual_duration': request.form.get('actual_duration'), 
            'retry_count': request.form.get('retry_count'), 
            'control_duration': request.form.get('control_duration'), 
            'result_depth': request.form.get('result_depth'),
            'logs_depth': request.form.get('logs_depth')
        }
        return self.set_params(**params)

    def set_params(self, **params):

        self.config_json.update(**params)
        updated_by = current_user.id
        updated_at = datetime.now()

        conf = Config(
            json=self.config_json,
            updated_by=updated_by,
            updated_at=updated_at
        )

        db.session.add(conf)
        db.session.commit()
        LogEvent.log_event(eventName="updateEntity", entityName="configSSDQ", entityId=conf.id)

        self.__upload_config_airflow(**params)

        return render_template('home/config.html', conf=self.config_json)
    
    def __upload_config_airflow(self, **params):
        default_args = {
            "retries": int(params['retry_count']),
            "execution_timeout": int(params['control_duration'])
        }

        try:
            Dag().upload_config(default_args)
        except Exception as ex:
            LogEvent.log_error(ex)

        return None
    