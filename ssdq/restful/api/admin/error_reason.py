from ....models.dict import error_reason_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from flask import request
from sqlalchemy import or_, String
from .wtforms import TeamDictForm


class AdminErrorReason():
    def __init__(self):
        pass
        
    @staticmethod
    def get_datatable():
        try:
            team_id = request.args.get("teamId")
            attributes = {
                0: error_reason_sdim.id,
                1: error_reason_sdim.name,
                2: error_reason_sdim.description,
                3: error_reason_sdim.deleted_flag
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
                order = error_reason_sdim.id
            
            query = db.session.query(
                error_reason_sdim.id,
                error_reason_sdim.name,
                error_reason_sdim.description,
                error_reason_sdim.deleted_flag
            )
            if search:
                query = query.filter(
                    error_reason_sdim.team_id == team_id,
                    or_(
                        error_reason_sdim.id.cast(String).ilike(search),
                        error_reason_sdim.name.ilike(search),
                        error_reason_sdim.description(search)
                    )
                )
            else:
                query = query.filter_by(team_id=team_id)
            
            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                name=row.name,
                description=row.description,
                deleted_flag=row.deleted_flag
            ) for row in dataset]
            
            total_records = int(error_reason_sdim.query.filter_by(team_id=team_id).count())
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
            form = TeamDictForm()
            if form.validate():
                entity = error_reason_sdim(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="error_reason", entityId=entity.id)
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
                entity = error_reason_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="error_reason", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            entity = error_reason_sdim.query.filter_by(id=id).update(dict(
                deleted_flag='N' if restore else 'Y'
            ))
            db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="error_reason", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def hard_delete(id:str):
        try:
            entity = error_reason_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="error_reason", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
