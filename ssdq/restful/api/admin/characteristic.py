from ....models.dict import dq_characteristic_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ..aggrid import AGGrid
from .wtforms import SysDictForm


ALLOWED_COLS = {
    "id": dq_characteristic_sdim.id,
    "name": dq_characteristic_sdim.name,
    "description": dq_characteristic_sdim.description
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class AdminCharacteristic():
    def __init__(self):
        self.grid = AGGrid(
            obj=dq_characteristic_sdim,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )

    @staticmethod
    def add():
        try:
            form = SysDictForm()
            if form.validate():
                entity = dq_characteristic_sdim(
                    name=form.name.data,
                    description=form.description.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="characteristic", entityId=entity.id)
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def update(id:str):
        try:
            form = SysDictForm()
            if form.validate():
                entity = dq_characteristic_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="characteristic", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def delete(id:str):
        try:
            entity = dq_characteristic_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="characteristic", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="dq_characteristic_sdim.csv"
        )
