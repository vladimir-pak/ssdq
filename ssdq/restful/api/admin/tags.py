from ....models.dict import tags
from ....models.base import dq_control_tags_stat
from ....logger.log import LogEvent
from ....app.extensions import db
from ..aggrid import AGGrid
from flask import request
from sqlalchemy import or_, String
from .wtforms import TeamDictForm


ALLOWED_COLS = {
    "id": tags.id,
    "name": tags.name,
    "description": tags.description,
    "tag_type": tags.tag_type
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class Tags():
    def __init__(self):
        self.grid = AGGrid(
            obj=tags,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )
        
    def get_grid(self):
        return self.grid.get_grid(base_filters={"teamId": tags.team_id})

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="tags.csv",
            base_filters={"teamId": tags.team_id},
        )

    @staticmethod
    def add():
        try:
            form = TeamDictForm()
            if form.validate():
                entity = tags(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data,
                    tag_type=form.tag_type.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="tags", entityId=entity.id)
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
                entity = tags.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data,
                    tag_type=form.tag_type.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="tags", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def delete(id:str):
        try:
            controls = dq_control_tags_stat.query.filter_by(tag_id=id).delete()
            db.session.commit()
            entity = tags.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="tags", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
