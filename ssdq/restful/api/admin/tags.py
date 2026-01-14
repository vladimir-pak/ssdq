from ....models.dict import tags
from ....models.base import dq_control_tags_stat
from ....logger.log import LogEvent
from ....app.extensions import db
from flask import request
from sqlalchemy import or_, String
from .wtforms import TeamDictForm


class Tags():
    def __init__(self):
        pass

    @staticmethod
    def get_datatable():
        try:
            team_id = request.args.get("teamId")
            attributes = {
                0: tags.id,
                1: tags.name,
                2: tags.description
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
                order = tags.id

            query = db.session.query(
                tags.id,
                tags.name,
                tags.description
            )
            if search:
                query = query.filter(
                    tags.team_id == team_id,
                    or_(
                        tags.id.cast(String).ilike(search),
                        tags.name.ilike(search),
                        tags.description.ilike(search)
                    )
                )
            else:
                query = query.filter_by(team_id=team_id)

            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                name=row.name,
                description=row.description
            ) for row in dataset]

            total_records = int(tags.query.filter_by(team_id=team_id).count())
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
                entity = tags(
                    name=form.name.data,
                    description=form.description.data,
                    team_id=form.team_id.data
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
                    description=form.description.data
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
