from ....models.dict import dq_team_attributes_dim
from ....logger.log import LogEvent
from ....app.extensions import db
from ..aggrid import AGGrid
from .wtforms import TeamDictForm


ALLOWED_COLS = {
    "id": dq_team_attributes_dim.id,
    "name": dq_team_attributes_dim.name,
    "description": dq_team_attributes_dim.description,
    "is_required": dq_team_attributes_dim.is_required
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class AdminTeamAttributes():
    def __init__(self):
        self.grid = AGGrid(
            obj=dq_team_attributes_dim,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="dq_team_attributes_dim.csv"
        )

    @staticmethod
    def add():
        try:
            form = TeamDictForm()
            if form.validate():
                entity = dq_team_attributes_dim(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data,
                    is_required=True if form.is_required.data == "on" else False
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="team_attributes", entityId=entity.id)
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
                entity = dq_team_attributes_dim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data,
                    is_required=True if form.is_required.data == "on" else False
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="team_attributes", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def delete(id:str):
        try:
            entity = dq_team_attributes_dim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="team_attributes", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
