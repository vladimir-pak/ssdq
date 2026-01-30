from ....models.dict import dq_object_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ..aggrid import AGGrid
from .wtforms import ObjectsForm


ALLOWED_COLS = {
    "id": dq_object_sdim.id,
    "base_name": dq_object_sdim.base_name,
    "schema": dq_object_sdim.schema,
    "table_name": dq_object_sdim.table_name,
    "description": dq_object_sdim.description,
    "deleted_flag": dq_object_sdim.deleted_flag
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class AdminObjects():
    def __init__(self):
        self.grid = AGGrid(
            obj=dq_object_sdim,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )

    @staticmethod
    def add():
        try:
            form = ObjectsForm()
            if form.validate():
                entity = dq_object_sdim(
                    base_name=form.base_name.data,
                    schema=form.schema.data,
                    table_name=form.table_name.data,
                    description=form.description.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="dbobject", entityId=entity.id)
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def update(id:str):
        try:
            form = ObjectsForm()
            if form.validate():
                entity = dq_object_sdim.query.filter_by(id=id).update(dict(
                    base_name=form.base_name.data,
                    schema=form.schema.data,
                    table_name=form.table_name.data,
                    description=form.description.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="dbobject", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            entity = dq_object_sdim.query.filter_by(id=id).update(dict(
                deleted_flag='N' if restore else 'Y'
            ))
            db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="dbobject", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def hard_delete(id:str):
        try:
            entity = dq_object_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="dbobject", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="dq_object_sdim.csv"
        )
