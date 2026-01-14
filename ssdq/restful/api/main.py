import math
from flask_login import current_user
from flask import request
from sqlalchemy import and_, or_, case, cast, String, func
from ...app.extensions import db
from ...models.base import dq_control_sdim, dq_control_owner_stat, dq_control_object_stat, \
    featured_controls, dq_dag_sdim, dq_detail_agg, \
    view_all_controls_bymonth, view_controls_error_bymonth, dq_validation_stat, \
    dq_control_tags_stat
from ...models.dict import dq_object_sdim, tags
from ...models.constants import ControlStatus, ControlStatusRu
from ...models.user import Users
from ...logger.log import LogEvent


class Main:

    @staticmethod
    def counts():
        try:
            exp_cnt = Main.get_count_by_status(int(ControlStatus.EXPLOITATION.value))
            cncl_cnt = Main.get_count_by_status(int(ControlStatus.DISABLED.value))
            act_cnt = Main.get_count_by_status(int(ControlStatus.ACTUALIZATION.value))
            dev_cnt = Main.get_count_by_status(int(ControlStatus.DEVELOPMENT.value))

            user_controls = db.session.query(dq_control_owner_stat.control_id).filter_by(
                owner_id=current_user.id
            ).count()
            usr_cnt = int(user_controls)

            expiring_controls = dq_validation_stat.query.join(
                dq_control_sdim, and_(
                    dq_validation_stat.control_id == dq_control_sdim.id,
                    dq_control_sdim.deleted_flag == 'N',
                    dq_control_sdim.team_id == current_user.team_id
                )
            ).filter(
                dq_validation_stat.disabled == False
            ).count()
            expiring_cnt = int(expiring_controls)

            response = dict(
                exp_cnt=exp_cnt,
                cncl_cnt=cncl_cnt,
                act_cnt=act_cnt,
                dev_cnt=dev_cnt,
                usr_cnt=usr_cnt,
                expiring_cnt=expiring_cnt
            )

        except Exception as ex:
            LogEvent.log_error(ex)
            response = dict(
                exp_cnt=0,
                cncl_cnt=0,
                act_cnt=0,
                dev_cnt=0,
                usr_cnt=0,
                expiring_cnt=0
            )

        return response

    @staticmethod
    def get_count_by_status(status:int) -> int:
        try:
            data = db.session.query(
                func.count(dq_control_sdim.id).label("control_cnt"),
                dq_control_sdim.status_id
            ).filter_by(
                team_id=current_user.team_id,
                status_id=status,
                deleted_flag="N"
            ).group_by(
                dq_control_sdim.status_id
            ).first()
            return int(data.control_cnt) if data else 0
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def charts():
        try:
            if current_user.admin:
                controls = view_all_controls_bymonth.query.all()
                controls_error = view_controls_error_bymonth.query.all()
            else:
                controls = view_all_controls_bymonth.query.filter(
                    func.coalesce(view_all_controls_bymonth.team_id, current_user.team_id) == current_user.team_id
                ).all()
                controls_error = view_controls_error_bymonth.query.filter(
                    func.coalesce(view_controls_error_bymonth.team_id, current_user.team_id) == current_user.team_id
                ).all()

            controls_attributes = [attr for attr in view_all_controls_bymonth.__dict__ if not attr.startswith("_")]
            controls_error_attributes = [attr for attr in view_controls_error_bymonth.__dict__ if not attr.startswith("_")]

            controls_data = []
            for row in controls:
                krow = {}
                for key in controls_attributes:
                    krow[key] = row.__getattribute__(key)
                controls_data.append(krow)

            controls_error_data = []
            for row in controls_error:
                krow = {}
                for key in controls_error_attributes:
                    krow[key] = row.__getattribute__(key)
                controls_error_data.append(krow)

            response = {
                "controls": controls_data,
                "controls_error": controls_error_data
            }

            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def controls():
        try:
            page = int(request.args.get("page"))
            page_size = 10

            owner_type = request.args.get("owner")
            search = request.args.get("search")
            if search:
                search_string = Main.get_search_filter(search)
            else:
                search_string = None

            query = dq_control_sdim.query.join(
                dq_control_owner_stat, and_(
                    dq_control_owner_stat.control_id == dq_control_sdim.id,
                    dq_control_sdim.deleted_flag == "N"
                )
            ).join(
                dq_dag_sdim, and_(
                    dq_control_sdim.id == dq_dag_sdim.control_id,
                    dq_dag_sdim.deleted_flag == "N"
                ),
                isouter=True
            ).join(
                featured_controls, and_(
                    dq_control_sdim.id == featured_controls.control_id,
                    featured_controls.user_id == current_user.id
                ),
                isouter=True
            ).add_columns(
                dq_control_sdim.id,
                dq_control_sdim.name,
                dq_control_sdim.description,
                case(
                    *[(dq_control_sdim.status_id == cur.value, ControlStatusRu[cur.name].value) for cur in ControlStatus],
                    else_="None"
                ).label('status_name'),
                dq_dag_sdim.crossdb_flag,
                case(
                    (featured_controls.control_id.is_(None), "N"),
                    else_="Y"
                ).label('is_favorite')
            )

            if owner_type == 'USER':
                if search_string:
                    query = query.filter(
                        dq_control_owner_stat.owner_id == current_user.id,
                        *search_string
                    )
                else:
                    query = query.filter(
                        dq_control_owner_stat.owner_id == current_user.id
                    )
                data = query.order_by(dq_control_sdim.id.desc()).limit(page_size).offset(page*page_size).all()

            elif owner_type == 'TEAM':
                if search_string:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        dq_control_sdim.team_id == current_user.team_id,
                        *search_string
                    )
                else:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        dq_control_sdim.team_id == current_user.team_id
                    )
                data = query.order_by(dq_control_sdim.id.desc()).limit(page_size).offset(page*page_size).all()

            elif owner_type == 'FAVORITES':
                if search_string:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        featured_controls.control_id.isnot(None)
                        *search_string
                    )
                else:
                    query =  query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        featured_controls.control_id.isnot(None)
                    )
                data = query.order_by(dq_control_sdim.id.desc()).limit(page_size).offset(page*page_size).all()
            else:
                data = []

            row_count = int(query.count())
            pages = math.floor(row_count / page_size)
            pages = pages - 1 if (row_count % page_size) == 0 else pages
            response = dict(
                data=[
                    dict(
                        id=cur.id,
                        name=cur.name,
                        description=cur.description,
                        status_name=cur.status_name,
                        crossdb_flag=cur.crossdb_flag,
                        is_favorite=cur.is_favorite,
                        last_result=Main.get_last_result(int(cur.id))
                    ) for cur in data
                ],
                pages=pages
            )

            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def get_search_filter(search:str) -> list:
        search = "%%"+search.lower()+"%%"
        search_string = [
            or_(
                cast(dq_control_sdim.id, String).like(search),
                dq_control_sdim.name.ilike(search),
                dq_control_sdim.description.ilike(search)
            )
        ]
        return search_string

    @staticmethod
    def controls_info():
        try:
            id = int(request.args.get("controlId"))
            objects = dq_control_object_stat.query.join(
                dq_object_sdim, and_(
                    dq_control_object_stat.object_id == dq_object_sdim.id,
                    dq_object_sdim.deleted_flag == "N"
                )
            ).add_columns(
                dq_object_sdim.base_name,
                dq_object_sdim.schema,
                dq_object_sdim.table_name
            ).filter(
                dq_control_object_stat.control_id == id
            ).all()

            users = dq_control_owner_stat.query.join(
                Users, Users.id == dq_control_owner_stat.owner_id
            ).add_columns(
                Users.name,
                Users.email
            ).filter(
                dq_control_owner_stat.control_id == id
            ).all()

            tags_list = dq_control_tags_stat.query.join(
                tags, tags.id == dq_control_tags_stat.tag_id
            ).add_columns(
                tags.name
            ).filter(
                dq_control_tags_stat.control_id == id
            ).all()

            last_results = Main.get_last_result(id)
            control_name = db.session.query(dq_control_sdim.name).filter_by(id=id).first()

            response = {
                'owners': [dict(name=cur.name, email=cur.email) for cur in users],
                'objects': [dict(name=cur.base_name+'.'+cur.schema+'.'+cur.table_name) for cur in objects],
                'tags': [dict(name=cur.name) for cur in tags_list],
                'lastResults': {
                    'reportDate': last_results['report_date'] if last_results is not None else None,
                    'mistakeCount': last_results['mistake_count'] if last_results is not None else None
                },
                'controlName': control_name.name
            }
            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def get_results() -> list[dict]:
        try:
            control_id = int(request.args.get("controlId"))
            data = db.session.query(
                dq_detail_agg.mistake_count,
                dq_detail_agg.report_date
            ).filter(
                dq_detail_agg.control_id == control_id,
                dq_detail_agg.error_flag != 'Y'
            ).order_by(
                dq_detail_agg.end_time.desc()
            ).limit(30).all()

            if data:
                return [dict(
                    report_date=cur.report_date,
                    mistake_count=cur.mistake_count
                ) for cur in data]
            else:
                return "", 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return None

    @staticmethod
    def get_last_result(control_id:int) -> dict:
        try:
            data = db.session.query(
                dq_detail_agg.control_id,
                dq_detail_agg.error_flag,
                dq_detail_agg.mistake_count,
                dq_detail_agg.report_date
            ).filter(
                dq_detail_agg.control_id == control_id
            ).order_by(dq_detail_agg.end_time.desc()).first()

            if data:
                return dict(
                    control_id=data.control_id,
                    report_date=data.report_date,
                    mistake_count=data.mistake_count,
                    error_flag=data.error_flag
                )
            else:
                return None
        except Exception as ex:
            LogEvent.log_error(ex)
            return None

    @staticmethod
    def add_control():
        try:
            form = dict(request.form)
            control_id = int(form["controlId"])
            control = featured_controls(user_id=current_user.id, control_id=control_id)
            db.session.add(control)
            db.session.commit()
            LogEvent.log_event(eventName="createEntity", entityName="featuredControl", entityId=str(control_id))
            return  {'response': f'Контроль {control_id} добавлен в избранное!'}
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def remove_control():
        try:
            form = dict(request.form)
            control_id = int(form["controlId"])
            control = featured_controls.query.filter_by(
                control_id=control_id, user_id=current_user.id
            ).delete()
            db.session.commit()
            LogEvent.log_event(eventName="deleteEntity", entityName="featuredControl", entityId=str(control_id))
            return  {'response': f'Контроль {control_id} исключен из избранного!'}
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
