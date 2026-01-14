from ....models.dict import dq_object_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from flask import request
from sqlalchemy import or_, String
from .wtforms import ObjectsForm


class AdminObjects():
    def __init__(self):
        pass
        
    @staticmethod
    def get_datatable():
        try:
            attributes = {
                0: dq_object_sdim.id,
                1: dq_object_sdim.base_name,
                2: dq_object_sdim.schema,
                3: dq_object_sdim.table_name,
                4: dq_object_sdim.description,
                5: dq_object_sdim.deleted_flag
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
                order = dq_object_sdim.id
            
            query = db.session.query(
                dq_object_sdim.id,
                dq_object_sdim.base_name,
                dq_object_sdim.schema,
                dq_object_sdim.table_name,
                dq_object_sdim.description,
                dq_object_sdim.deleted_flag
            )
            if search:
                query = query.filter(
                    or_(
                        dq_object_sdim.id.cast(String).ilike(search),
                        dq_object_sdim.base_name.ilike(search),
                        dq_object_sdim.schema.ilike(search),
                        dq_object_sdim.table_name.ilike(search),
                        dq_object_sdim.description.ilike(search)
                    )
                )
            
            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                base_name=row.base_name,
                schema=row.schema,
                table_name=row.table_name,
                description=row.description,
                deleted_flag=row.deleted_flag
            ) for row in dataset]
            
            total_records = int(dq_object_sdim.query.count())
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
