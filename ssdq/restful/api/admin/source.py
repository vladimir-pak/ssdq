from ....models.dict import dq_source_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ....integration.airflow import Dag
from ..aggrid import AGGrid
from .wtforms import SysDictForm


ALLOWED_COLS = {
    "id": dq_source_sdim.id,
    "name": dq_source_sdim.name,
    "description": dq_source_sdim.description,
    "host": dq_source_sdim.host,
    "port": dq_source_sdim.port,
    "db_name": dq_source_sdim.db_name,
    "dbtype": dq_source_sdim.dbtype,
    "sslmode": dq_source_sdim.sslmode,
    "deleted_flag": dq_source_sdim.deleted_flag
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class AdminSources():
    def __init__(self):
        self.grid = AGGrid(
            obj=dq_source_sdim,
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
                entity = dq_source_sdim(
                    name=form.name.data,
                    description=form.description.data,
                    host=form.host.data,
                    port=form.port.data,
                    db_name=form.db_name.data,
                    dbtype=form.dbtype.data,
                    sslmode=form.sslmode.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="source", entityId=entity.id)

                return AdminSources.deploy_conn(form.name.data, form.host.data, form.port.data, form.db_name.data, form.dbtype.data, form.sslmode.data)
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
                entity = dq_source_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data,
                    host=form.host.data,
                    port=form.port.data,
                    db_name=form.db_name.data,
                    dbtype=form.dbtype.data,
                    sslmode=form.sslmode.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="source", entityId=str(id))

                return AdminSources.deploy_conn(form.name.data, form.host.data, form.port.data, form.db_name.data, form.dbtype.data, form.sslmode.data)
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            entity = dq_source_sdim.query.filter_by(id=id).update(dict(
                deleted_flag='N' if restore else 'Y'
            ))
            db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="source", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def hard_delete(id:str):
        try:
            entity = dq_source_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="source", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def deploy_conn(conn_id:str, host:str, port:str, db_name:str, dbtype:str, sslmode:str=None):
        try:
            airflow = Dag()
            return airflow.deploy_connection(conn_id, host, port, db_name, dbtype, sslmode)
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="dq_source_sdim.csv"
        )
