from ....models.dict import dq_pattern_sdim
from ....models.base import dq_dag_sdim
from ....logger.log import LogEvent
from ....app.extensions import db
from ....integration.airflow import Dag
from ..aggrid import AGGrid
from flask import request
from sqlalchemy import or_, String
from .wtforms import PatternDictForm
import json


ALLOWED_COLS = {
    "id": dq_pattern_sdim.id,
    "name": dq_pattern_sdim.name,
    "description": dq_pattern_sdim.description,
    "deleted_flag": dq_pattern_sdim.deleted_flag,
    "sql": dq_pattern_sdim.sql,
    "params": dq_pattern_sdim.params
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


class PatternSql():
    def __init__(self):
        self.grid = AGGrid(
            obj=dq_pattern_sdim,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            set_ops=SET_OPS
        )
        
    def get_grid(self):
        return self.grid.get_grid(base_filters={"teamId": dq_pattern_sdim.team_id})

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="dq_pattern_sdim.csv",
            base_filters={"teamId": dq_pattern_sdim.team_id},
        )

    @staticmethod
    def get_datatable():
        try:
            team_id = request.args.get("teamId")
            attributes = {
                0: dq_pattern_sdim.id,
                1: dq_pattern_sdim.name,
                2: dq_pattern_sdim.description,
                3: dq_pattern_sdim.deleted_flag
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
                order = dq_pattern_sdim.id

            query = db.session.query(
                dq_pattern_sdim.id,
                dq_pattern_sdim.name,
                dq_pattern_sdim.description,
                dq_pattern_sdim.deleted_flag
            )
            if search:
                query = query.filter(
                    dq_pattern_sdim.team_id == team_id,
                    or_(
                        dq_pattern_sdim.id.cast(String).ilike(search),
                        dq_pattern_sdim.name.ilike(search),
                        dq_pattern_sdim.description.ilike(search)
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

            total_records = int(dq_pattern_sdim.query.filter_by(team_id=team_id).count())
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
    def get_detail_info(id:str):
        try:
            data = db.session.query(
                dq_pattern_sdim.sql, 
                dq_pattern_sdim.params
            ).filter_by(id=id).first()

            response = {
                'id': id,
                'sql': data.sql,
                'params': data.params
            }
            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    @staticmethod
    def add():
        try:
            form = PatternDictForm()
            if form.validate():
                entity = dq_pattern_sdim(
                    name=form.name.data,
                    description=form.description.data,
                    sql=form.sql.data,
                    params=json.loads(form.params.data),
                    team_id=form.team_id.data
                )
                db.session.add(entity)
                db.session.commit()

                dag = Dag()
                deploy_response = dag.deploy_sql_template(
                    team_id=entity.team_id,
                    pattern_id=str(entity.id),
                    sql=entity.sql)
                if deploy_response:
                    return deploy_response, 500
                LogEvent.log_event(eventName="createEntity", entityName="pattern_sql", entityId=entity.id)

                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    @staticmethod
    def update(id:str):
        try:
            form = PatternDictForm()
            if form.validate():
                dag = Dag()
                deploy_response = dag.deploy_sql_template(
                    team_id=form.team_id.data,
                    pattern_id=id,
                    sql=form.sql.data)
                if deploy_response:
                    return deploy_response, 500

                entity = dq_pattern_sdim.query.filter_by(id=id).update(dict(
                    name=form.name.data,
                    description=form.description.data,
                    sql=form.sql.data,
                    params=json.loads(form.params.data)
                ))
                db.session.commit()
                LogEvent.log_event(eventName="updateEntity", entityName="pattern_sql", entityId=id)
                return '', 204
            else:
                return {"message": "CSRF Token Missing or Invalid"}, 403
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    @staticmethod
    def delete_restore(id:str, restore=False):
        try:
            if restore:
                dag = Dag()
                deploy_response = dag.deploy_sql_template(
                    team_id=request.form["team_id"],
                    pattern_id=id,
                    sql=request.form["sql"])
                if deploy_response:
                    return deploy_response, 500

                entity = dq_pattern_sdim.query.filter_by(id=id).update(dict(
                    deleted_flag='N'
                ))
                db.session.commit()
            else:
                if not PatternSql.check_sql_templates(id):
                    return {"message": "Удалить невозможно. Данный шаблон используется в контролях"}, 400
                dag = Dag()
                deploy_response = dag.remove_sql_template(team_id=request.form["team_id"], pattern_id=id)
                if deploy_response:
                    return deploy_response, 500

                entity = dq_pattern_sdim.query.filter_by(id=id).update(dict(
                    deleted_flag='N' if restore else 'Y'
                ))
                db.session.commit()
            LogEvent.log_event(eventName="updateEntity" if restore else "deleteEntity", entityName="pattern_sql", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    @staticmethod
    def hard_delete(id:str):
        try:
            if not PatternSql.check_sql_templates(id):
                return {"message": "Удалить невозможно. Данный шаблон используется в контролях"}, 400
            dag = Dag()
            deploy_response = dag.remove_sql_template(team_id=request.form["team_id"], pattern_id=id)
            if deploy_response:
                return deploy_response, 500

            entity = dq_pattern_sdim.query.filter_by(id=id).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="pattern_sql", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"message": str(ex)}, 500

    @staticmethod
    def check_sql_templates(pattern_id:str) -> bool:
        data = db.session.query(dq_dag_sdim.control_id).filter_by(pattern_id=pattern_id).first()
        return False if data else True
    