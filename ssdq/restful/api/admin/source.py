from ....models.dict import dq_source_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ....integration.airflow import Dag
from flask import request
from sqlalchemy import or_, String
from .wtforms import SysDictForm


class AdminSources():
    def __init__(self):
        pass

    @staticmethod
    def get_datatable():
        try:
            attributes = {
                0: dq_source_sdim.id,
                1: dq_source_sdim.name,
                2: dq_source_sdim.description,
                3: dq_source_sdim.host,
                4: dq_source_sdim.port,
                5: dq_source_sdim.db_name,
                6: dq_source_sdim.dbtype,
                7: dq_source_sdim.sslmode
            }
            search_value = request.form['search[value]']
            search = None if search_value is None or search_value == '' else f'%%{search_value.lower()}%%'
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            if request.form.get('order[0][column]'):
                order_attr = attributes[int(request.form['order[0][column]'])]
                order_dir = request.form['order[0][dir]']
                order = order_attr if order_dir == 'asc' else order_attr.desc()
            else:
                order = dq_source_sdim.id

            query = db.session.query(
                dq_source_sdim.id,
                dq_source_sdim.name,
                dq_source_sdim.description,
                dq_source_sdim.host,
                dq_source_sdim.port,
                dq_source_sdim.db_name,
                dq_source_sdim.dbtype,
                dq_source_sdim.sslmode,
                dq_source_sdim.deleted_flag
            )
            if search:
                query = query.filter(
                    or_(
                        dq_source_sdim.id.cast(String).ilike(search),
                        dq_source_sdim.name.ilike(search),
                        dq_source_sdim.host.ilike(search),
                        dq_source_sdim.port.ilike(search),
                        dq_source_sdim.db_name.ilike(search),
                        dq_source_sdim.description.ilike(search),
                        dq_source_sdim.dbtype.ilike(search),
                        dq_source_sdim.sslmode.ilike(search)
                    )
                )

            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                name=row.name,
                description=row.description,
                host=row.host,
                port=row.port,
                db_name=row.db_name,
                dbtype=row.dbtype,
                sslmode=row.sslmode,
                deleted_flag=row.deleted_flag
            ) for row in dataset]

            total_records = int(dq_source_sdim.query.count())
            total_record_filtered = total_records if search is None else int(query.count())

            response = {
                'draw': request.form['draw'],
                'iTotalRecords': total_records,
                'iTotalDisplayRecords': total_record_filtered,
                'aaData': data,
            }
            return response

        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

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
