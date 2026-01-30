from ....models.dict import subject_area_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ..aggrid import AGGrid
from flask import request
from sqlalchemy import or_, String
from .wtforms import TeamDictForm


ALLOWED_COLS = {
    "id": subject_area_sdim.id,
    "name": subject_area_sdim.name,
    "description": subject_area_sdim.description,
    "deleted_flag": subject_area_sdim.deleted_flag
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class AdminSubjectArea():
    def __init__(self):
        self.grid = AGGrid(
            obj=subject_area_sdim,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )
        
    def get_grid(self):
        return self.grid.get_grid(base_filters={"teamId": subject_area_sdim.team_id})

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            base_filters={"teamId": subject_area_sdim.team_id},
            filename="subject_area_sdim.csv"
        )
    
    @staticmethod
    def add():
        try:
            form = TeamDictForm()
            if form.validate():
                entity = subject_area_sdim(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="subject_area", entityId=entity.id)
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def update(id:str):
        try:
            form = TeamDictForm()
            if form.validate():
                entity = subject_area_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="subject_area", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            entity = subject_area_sdim.query.filter_by(id=id).update(dict(
                deleted_flag='N' if restore else 'Y'
            ))
            db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="subject_area", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def hard_delete(id:str):
        try:
            entity = subject_area_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="subject_area", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
