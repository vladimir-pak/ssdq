from ....models.dict import dq_segment_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from flask import request
from sqlalchemy import or_, String
from .wtforms import TeamDictForm


class AdminSegments():
    def __init__(self):
        pass
        
    @staticmethod
    def get_datatable():
        try:
            team_id = request.args.get("teamId")
            attributes = {
                0: dq_segment_sdim.id,
                1: dq_segment_sdim.name,
                2: dq_segment_sdim.description,
                3: dq_segment_sdim.deleted_flag
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
                order = dq_segment_sdim.id
            
            query = db.session.query(
                dq_segment_sdim.id,
                dq_segment_sdim.name,
                dq_segment_sdim.description,
                dq_segment_sdim.deleted_flag
            )
            if search:
                query = query.filter(
                    dq_segment_sdim.team_id == team_id,
                    or_(
                        dq_segment_sdim.id.cast(String).ilike(search),
                        dq_segment_sdim.name.ilike(search),
                        dq_segment_sdim.description.ilike(search)
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
            
            total_records = int(dq_segment_sdim.query.filter_by(team_id=team_id).count())
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
                entity = dq_segment_sdim(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data
                )
                db.session.add(entity)
                db.session.commit()
                LogEvent.log_event(eventName="createEntity", entityName="segment", entityId=entity.id)
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
                entity = dq_segment_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="segment", entityId=str(id))
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403 
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            entity = dq_segment_sdim.query.filter_by(id=id).update(dict(
                deleted_flag='N' if restore else 'Y'
            ))
            db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="segment", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def hard_delete(id:str):
        try:
            entity = dq_segment_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="segment", entityId=str(id))
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
