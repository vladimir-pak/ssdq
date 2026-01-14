from ...models.dict import dq_object_sdim
from ...models.base import dq_control_sdim, dq_control_owner_stat, dq_validation_stat, \
    dq_control_object_stat, dq_detail_agg
from ...models.constants import MonitoringFilter, ControlStatus, ControlStatusRu
from ...models.user import Users, Teams
from ...logger.log import LogEvent
from sqlalchemy import or_, and_, String, func, case
from ...app.extensions import db
from flask import request
from flask_login import current_user


class Monitoring:
    def __init__(self):
        pass

    def get_data(self):
        try:
            filter = str(request.args.get("filter")).upper()
            search_value = request.form['search[value]']
            search = None if search_value is None or search_value == '' else f'%%{search_value.lower()}%%'
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])

            owner_subquery = db.session.query(dq_control_owner_stat).join(
                Users, Users.id == dq_control_owner_stat.owner_id
            ).add_columns(
                dq_control_owner_stat.control_id,
                Users.name.label("owner"),
                func.row_number().over(partition_by=dq_control_owner_stat.control_id, order_by=Users.name).label("rn")
                # func.max(Users.name).label("owner")
            ).filter(
                (dq_control_owner_stat.owner_id == current_user.id) if filter == MonitoringFilter.USER.name else True
            ).subquery()

            object_subquery = db.session.query(dq_control_object_stat).join(
                dq_object_sdim, and_(
                    dq_object_sdim.id == dq_control_object_stat.object_id,
                    dq_object_sdim.deleted_flag == "N"
                )
            ).add_columns(
                dq_control_object_stat.control_id,
                (dq_object_sdim.base_name + "." + dq_object_sdim.schema + "." + dq_object_sdim.table_name).label("object_name"),
                func.row_number().over(partition_by=dq_control_object_stat.control_id, order_by=dq_object_sdim.base_name).label("rn")
            ).subquery()

            last_results_subquery = db.session.query(
                dq_detail_agg.control_id,
                dq_detail_agg.report_date,
                dq_detail_agg.mistake_count,
                func.row_number().over(partition_by=dq_detail_agg.control_id, order_by=dq_detail_agg.report_date.desc()).label("rn")
            ).subquery()

            query = dq_control_sdim.query.join(
                owner_subquery, and_(
                    owner_subquery.c.control_id == dq_control_sdim.id,
                    owner_subquery.c.rn == 1
                )
            ).join(
                object_subquery, and_(
                    object_subquery.c.control_id == dq_control_sdim.id,
                    object_subquery.c.rn == 1
                )
            ).join(
                last_results_subquery, and_(
                    last_results_subquery.c.control_id == dq_control_sdim.id,
                    last_results_subquery.c.rn == 1
                ),
                isouter=True
            ).join(
                Teams, Teams.id == dq_control_sdim.team_id
            ).join(
                dq_validation_stat, and_(
                    dq_validation_stat.control_id == dq_control_sdim.id,
                    dq_validation_stat.disabled == False
                ),
                isouter=True
            ).add_columns(
                dq_control_sdim.id,
                dq_control_sdim.name,
                dq_control_sdim.description,
                object_subquery.c.object_name,
                owner_subquery.c.owner,
                last_results_subquery.c.report_date,
                last_results_subquery.c.mistake_count,
                Teams.json["display_name"].label("team_name"),
                case(
                    *[(dq_control_sdim.status_id == cur.value, ControlStatusRu[cur.name].value) for cur in ControlStatus],
                    else_="None"
                ).label('status_name')
            )
            
            attributes = {
                0: dq_control_sdim.id,
                1: dq_control_sdim.name,
                2: dq_control_sdim.description,
                3: object_subquery.c.object_name,
                4: owner_subquery.c.owner,
                5: last_results_subquery.c.report_date,
                6: last_results_subquery.c.mistake_count,
                7: Teams.json["display_name"].cast(String)
            }
            if request.form.get('order[0][column]'):
                order_attr = attributes[int(request.form['order[0][column]'])]
                order_dir = request.form['order[0][dir]']
                order = order_attr if order_dir == 'asc' else order_attr.desc()
            else:
                order = dq_control_sdim.id.desc()

            if filter in [MonitoringFilter.ALL.name, MonitoringFilter.TEAM.name]:
                flt = [dq_control_sdim.team_id == current_user.team_id]
            elif filter == "EXPIRING":
                flt = [
                    dq_control_sdim.team_id == current_user.team_id,
                    dq_validation_stat.disable_date.isnot(None)
                ]
            elif filter in [MonitoringFilter.DEVELOPMENT.name, MonitoringFilter.EXPLOITATION.name, 
                            MonitoringFilter.DISABLED.name, MonitoringFilter.ACTUALIZATION.name]:
                flt = [
                    dq_control_sdim.team_id == current_user.team_id,
                    dq_control_sdim.status_id == ControlStatus[filter].value
                ]
            else:
                flt = None

            if search:
                if flt:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        or_(
                            dq_control_sdim.id.cast(String).ilike(search),
                            dq_control_sdim.name.ilike(search),
                            dq_control_sdim.description.ilike(search),
                            object_subquery.c.object_name.ilike(search),
                            owner_subquery.c.owner.ilike(search),
                            last_results_subquery.c.report_date.cast(String).ilike(search),
                            last_results_subquery.c.mistake_count.cast(String).ilike(search),
                            Teams.json["display_name"].cast(String).ilike(search)
                        ),
                        *flt
                    )
                else:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        or_(
                            dq_control_sdim.id.cast(String).ilike(search),
                            dq_control_sdim.name.ilike(search),
                            dq_control_sdim.description.ilike(search),
                            object_subquery.c.object_name.ilike(search),
                            owner_subquery.c.owner.ilike(search),
                            last_results_subquery.c.report_date.cast(String).ilike(search),
                            last_results_subquery.c.mistake_count.cast(String).ilike(search),
                            Teams.json["display_name"].cast(String).ilike(search)
                        )
                    )
                total_record_filtered = int(query.count())
            else:
                if flt:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N",
                        *flt
                    )
                else:
                    query = query.filter(
                        dq_control_sdim.deleted_flag == "N"
                    )
                total_record_filtered = None

            dataset = query.order_by(order).limit(rowperpage).offset(row).all()

            data = [dict(
                id=row.id,
                name=row.name,
                description=row.description,
                object_name=row.object_name,
                owner=row.owner,
                report_date=row.report_date,
                mistake_count=row.mistake_count,
                team_name=row.team_name,
                status_name=row.status_name
            ) for row in dataset]

            total_records = int(query.count())
            total_record_filtered = total_records if search is None else total_record_filtered

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
        