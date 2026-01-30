from ...models.dict import dq_object_sdim, dq_segment_sdim, dq_source_sdim, \
    dq_control_type_sdim, subject_area_sdim, tags
from ...models.base import dq_control_sdim, dq_control_owner_stat, dq_validation_stat, \
    dq_control_object_stat, dq_detail_agg, dq_control_tags_stat
from ...models.constants import MonitoringFilter, ControlStatus, ControlStatusRu, \
    AlertingType, AlertingTypeRu, JiraMode, JiraModeRu
from ...models.user import Users, Teams
from sqlalchemy import and_, func, case
from ...app.extensions import db
from .aggrid import AGGrid
from flask_login import current_user


ALLOWED_COLS = {}
TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter


# custom query for grid
def base_query_fn(payload):
    flt = payload.get("flt")
    
    last_results_subquery = db.session.query(
        dq_detail_agg.control_id.label("control_id"),
        dq_detail_agg.report_date.label("report_date"),
        dq_detail_agg.mistake_count.label("mistake_count"),
        func.row_number().over(
            partition_by=dq_detail_agg.control_id,
            order_by=dq_detail_agg.report_date.desc()
        ).label("rn")
    ).subquery("last_results")
    
    owner_subquery = db.session.query(
        dq_control_owner_stat.control_id.label("control_id"),
        func.string_agg(Users.name, ", ").label("owner"),
    ).join(Users, Users.id == dq_control_owner_stat.owner_id) \
        .group_by(dq_control_owner_stat.control_id) \
        .subquery("owners")

    object_subquery = db.session.query(
        dq_control_object_stat.control_id.label("control_id"),
        func.string_agg(
            dq_object_sdim.base_name + "." + dq_object_sdim.schema + "." + dq_object_sdim.table_name,
            ", "
        ).label("object_name")
    ).join(
        dq_object_sdim,
        and_(dq_object_sdim.id == dq_control_object_stat.object_id,
             dq_object_sdim.deleted_flag == "N")
    ).group_by(dq_control_object_stat.control_id) \
        .subquery("objects")
        
    tags_subquery = db.session.query(
        dq_control_tags_stat.control_id,
        func.string_agg(tags.name, ", ").label("tags"),
    ).join(tags, tags.id == dq_control_tags_stat.tag_id) \
        .group_by(dq_control_tags_stat.control_id) \
        .subquery("tags")
    
    status_expr = case(
        *[(dq_control_sdim.status_id == cur.value, ControlStatusRu[cur.name].value) for cur in ControlStatus],
        else_="None"
    ).label("status_name")

    alerting_expr = case(
        *[(dq_control_sdim.alerting_type_id == cur.value, AlertingTypeRu[cur.name].value) for cur in AlertingType],
        else_="None"
    ).label("alerting_type")

    jira_expr = case(
        *[(dq_control_sdim.jira_mode_id == cur.value, JiraModeRu[cur.name].value) for cur in JiraMode],
        else_="None"
    ).label("jira_mode")

    q = dq_control_sdim.query.join(
        owner_subquery, and_(
            owner_subquery.c.control_id == dq_control_sdim.id
        )
    ).join(
        object_subquery, and_(
            object_subquery.c.control_id == dq_control_sdim.id
        )
    ).join(
        tags_subquery, and_(
            tags_subquery.c.control_id == dq_control_sdim.id
        ),
        isouter=True
    ).join(
        last_results_subquery, and_(
            last_results_subquery.c.control_id == dq_control_sdim.id,
            last_results_subquery.c.rn == 1
        ),
        isouter=True
    ).join(
        Teams, Teams.id == dq_control_sdim.team_id
    ).join(
        dq_segment_sdim, and_(
            dq_control_sdim.segment_id == dq_segment_sdim.id, 
            dq_segment_sdim.deleted_flag == "N"
        ),
        isouter=True
    ).join(
        dq_source_sdim, and_(
            dq_control_sdim.source_id == dq_source_sdim.id,
            dq_source_sdim.deleted_flag == "N"
        ),
        isouter=True
    ).join(
        dq_control_type_sdim, and_(
            dq_control_sdim.control_type_id == dq_control_type_sdim.id,
            dq_control_type_sdim.deleted_flag == "N"
        ),
        isouter=True
    ).join(
        subject_area_sdim, and_(
            dq_control_sdim.subject_area_id == subject_area_sdim.id,
            subject_area_sdim.deleted_flag == "N"
        ),
        isouter=True
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
        dq_control_sdim.conditions,
        dq_segment_sdim.name.label("segment"),
        dq_source_sdim.name.label("source"),
        status_expr,
        dq_control_sdim.wiki,
        Teams.json["display_name"].label("team_name"),
        dq_control_sdim.threshold_min,
        dq_control_sdim.threshold_max,
        dq_control_type_sdim.name.label("control_type"),
        subject_area_sdim.name.label("subject_area"),
        dq_control_sdim.critical_level,
        alerting_expr,
        jira_expr,
        object_subquery.c.object_name,
        owner_subquery.c.owner,
        tags_subquery.c.tags,
        last_results_subquery.c.report_date,
        last_results_subquery.c.mistake_count
    )
    
    if flt in [MonitoringFilter.ALL.name, MonitoringFilter.TEAM.name]:
        q = q.filter(dq_control_sdim.team_id == current_user.team_id)
    elif flt == "EXPIRING":
        q = q.filter(
            dq_control_sdim.team_id == current_user.team_id,
            dq_validation_stat.disable_date.isnot(None)
        )
    elif flt in [MonitoringFilter.DEVELOPMENT.name, MonitoringFilter.EXPLOITATION.name, 
                    MonitoringFilter.DISABLED.name, MonitoringFilter.ACTUALIZATION.name]:
        q = q.filter(
            dq_control_sdim.team_id == current_user.team_id,
            dq_control_sdim.status_id == ControlStatus[flt].value
        )
        
    allowed_cols = {
        "id": dq_control_sdim.id,
        "name": dq_control_sdim.name,
        "description": dq_control_sdim.description,
        "conditions": dq_control_sdim.conditions,
        "segment": dq_segment_sdim.name,
        "source": dq_source_sdim.name,
        "status_name": status_expr,
        "wiki": dq_control_sdim.wiki,
        "team_name": Teams.json["display_name"],
        "threshold_min": dq_control_sdim.threshold_min,
        "threshold_max": dq_control_sdim.threshold_max,
        "control_type": dq_control_type_sdim.name,
        "subject_area": subject_area_sdim.name,
        "critical_level": dq_control_sdim.critical_level,
        "alerting_type": alerting_expr,
        "jira_mode": jira_expr,
        "object_name": object_subquery.c.object_name,
        "owner": owner_subquery.c.owner,
        "tags": tags_subquery.c.tags,
        "report_date": last_results_subquery.c.report_date,
        "mistake_count": last_results_subquery.c.mistake_count,
    }

    return q, allowed_cols


class Monitoring:
    def __init__(self):
        self.grid = AGGrid(
            obj=Users,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            base_query_fn=base_query_fn,
            set_ops=SET_OPS,
        )
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="monitoring.csv"
        )
        
    def get_ids(self):
        return self.grid.get_field_values()
        