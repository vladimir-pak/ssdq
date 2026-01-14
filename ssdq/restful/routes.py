from datetime import datetime, timezone
from flask import Blueprint, request, session, current_app
from flask_login import login_required
from .api.select import Select2API
from .api.monitoring import Monitoring
from .api.main import Main
from .api.report import Report, ReportJira
from ..integration.airflow import AirflowAPI
from ..integration.jira import JiraApi
from .api.admin import AdminUsers, AdminTeams, TeamConnection, \
    AdminObjects, AdminControlType, AdminErrorReason, AdminSegments, \
    AdminSources, AdminSubjectArea, PatternSql, Tags
from ..logger.log import log_route
from ..security.access import roles_accepted, control_accepted

api_routes = Blueprint('api_routes', __name__, template_folder='templates')

@api_routes.route('/api/select2', methods=['GET'])
@login_required
@log_route()
def get_select():
    return Select2API.get_data(request.args.get("entity"))

@api_routes.route('/api/monitoring', methods=['POST'])
@login_required
@log_route()
def get_monitoring_data():
    return Monitoring().get_data()

@api_routes.route('/api/main', methods=['GET'])
@login_required
@log_route()
def get_main_data():
    return Main.counts()

@api_routes.route('/api/main/charts', methods=['GET'])
@login_required
@log_route()
def get_main_charts():
    if request.args.get("type") == "main":
        return Main.charts()
    else:
        return Main.get_results()

@api_routes.route('/api/main/card', methods=['GET'])
@login_required
@log_route()
def get_main_card():
    return Main.controls_info()

@api_routes.route('/api/main/controls', methods=['GET', "POST", "DELETE"])
@login_required
@log_route()
def main_controls():
    if request.method == "GET":
        return Main.controls()
    elif request.method == "DELETE":
        return Main.remove_control()
    elif request.method == "POST":
        return Main.add_control()
    else:
        return {"response": "There is no data"}

@api_routes.route('/api/main/controls/results', methods=['GET', "POST", "DELETE"])
@login_required
@log_route()
def main_controls_results():
    return Main.get_results()

@api_routes.route('/api/report/<int:id>', methods=['GET', "POST"])
@login_required
@log_route()
def get_report_data(id:int):
    if request.method == "GET":
        return Report(id).agg_report()
    else:
        return Report(id).detail_report()

@api_routes.route('/api/report/<int:id>/edit/<int:wf_id>', methods=["GET", "PUT", "POST", "DELETE"])
@login_required
@log_route()
def report_edit(id:int, wf_id:int):
    if request.method == "GET":
        return ReportJira.get_data(id, wf_id)
    elif request.method == "POST":
        return Report(id, wf_id).get_jira_data()
    elif request.method == "PUT":
        return ReportJira().add(id, wf_id)
    elif request.method == "DELETE":
        return ReportJira().delete(wf_id)
    else:
        return {"response": "There is no data"}

@api_routes.route('/api/admin/users', methods=["GET", "POST"])
@login_required
@log_route()
def api_admin_users():
    if request.method == "GET":
        return AdminUsers.get_data()
    else:
        return AdminUsers.get_datatable()

@api_routes.route('/api/admin/users/<string:id>', methods=["GET", "PATCH", "DELETE"])
@login_required
@log_route()
def api_admin_users_id(id:str):
    if request.method == "GET":
        return AdminUsers.get_user_data(id)
    elif request.method == "PATCH":
        return AdminUsers.update_user(id)
    else:
        return AdminUsers.delete_user(id)

@api_routes.route('/api/admin/teams', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_teams():
    if request.method == "POST":
        return AdminTeams.get_datatable()
    else:
        return AdminTeams.add()

@api_routes.route('/api/admin/teams/<string:id>', methods=["GET", "POST", "DELETE", "PATCH"])
@login_required
@log_route()
def api_admin_teams_id(id:str):
    if request.method == "DELETE":
        return AdminTeams.delete(id)
    elif request.method == "PATCH":
        return AdminTeams.update(id)
    elif request.method == "GET":
        return AdminTeams.get_data(id)
    elif request.method == "POST":
        return AdminUsers.get_datatable(team_id=id)

@api_routes.route('/api/admin/objects', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_objects():
    if request.method == "POST":
        return AdminObjects.get_datatable()
    else:
        return AdminObjects.add()

@api_routes.route('/api/admin/objects/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_objects_id(id:str):
    if request.method == "PATCH":
        return AdminObjects.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminObjects.hard_delete(id)
        else:
            return AdminObjects.delete_restore(id)
    elif request.method == "PUT":
        return AdminObjects.delete_restore(id, True)

@api_routes.route('/api/admin/sources', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_sources():
    if request.method == "POST":
        return AdminSources.get_datatable()
    else:
        return AdminSources.add()

@api_routes.route('/api/admin/sources/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_sources_id(id:str):
    if request.method == "PATCH":
        return AdminSources.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminSources.hard_delete(id)
        else:
            return AdminSources.delete_restore(id)
    elif request.method == "PUT":
        return AdminSources.delete_restore(id, True)

@api_routes.route('/api/admin/control-types', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_controltypes():
    if request.method == "POST":
        return AdminControlType.get_datatable()
    else:
        return AdminControlType.add()

@api_routes.route('/api/admin/control-types/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_controltypes_id(id:str):
    if request.method == "PATCH":
        return AdminControlType.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminControlType.hard_delete(id)
        else:
            return AdminControlType.delete_restore(id)
    elif request.method == "PUT":
        return AdminControlType.delete_restore(id, True)

@api_routes.route('/api/admin/error-reason', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_errorreason():
    if request.method == "POST":
        return AdminErrorReason.get_datatable()
    else:
        return AdminErrorReason.add()

@api_routes.route('/api/admin/error-reason/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_errorreason_id(id:str):
    if request.method == "PATCH":
        return AdminErrorReason.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminErrorReason.hard_delete(id)
        else:
            return AdminErrorReason.delete_restore(id)
    elif request.method == "PUT":
        return AdminErrorReason.delete_restore(id, True)

@api_routes.route('/api/admin/subject-area', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_subjectarea():
    if request.method == "POST":
        return AdminSubjectArea.get_datatable()
    else:
        return AdminSubjectArea.add()

@api_routes.route('/api/admin/subject-area/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_subjectarea_id(id:str):
    if request.method == "PATCH":
        return AdminSubjectArea.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminSubjectArea.hard_delete(id)
        else:
            return AdminSubjectArea.delete_restore(id)
    elif request.method == "PUT":
        return AdminSubjectArea.delete_restore(id, True)

@api_routes.route('/api/admin/segments', methods=["POST", "PUT"])
@login_required
@log_route()
def api_admin_segments():
    if request.method == "POST":
        return AdminSegments.get_datatable()
    else:
        return AdminSegments.add()

@api_routes.route('/api/admin/segments/<string:id>', methods=["PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_admin_segments_id(id:str):
    if request.method == "PATCH":
        return AdminSegments.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return AdminSegments.hard_delete(id)
        else:
            return AdminSegments.delete_restore(id)
    elif request.method == "PUT":
        return AdminSegments.delete_restore(id, True)

@api_routes.route('/api/admin/pattern-sql', methods=["POST", "PUT"])
@login_required
@log_route()
def api_pattern_sql():
    if request.method == "POST":
        return PatternSql.get_datatable()
    else:
        return PatternSql.add()

@api_routes.route('/api/admin/pattern-sql/<string:id>', methods=["GET", "PATCH", "PUT", "DELETE"])
@login_required
@log_route()
def api_pattern_sql_id(id:str):
    if request.method == "PATCH":
        return PatternSql.update(id)
    elif request.method == "DELETE":
        if request.args.get("hardDelete") == "True":
            return PatternSql.hard_delete(id)
        else:
            return PatternSql.delete_restore(id)
    elif request.method == "PUT":
        return PatternSql.delete_restore(id, True)
    elif request.method == "GET":
        return PatternSql.get_detail_info(id)

@api_routes.route('/api/admin/tags', methods=["POST", "PUT"])
@login_required
@log_route()
def api_tags():
    if request.method == "POST":
        return Tags.get_datatable()
    else:
        return Tags.add()

@api_routes.route('/api/admin/tags/<string:id>', methods=["PATCH", "DELETE"])
@login_required
@log_route()
def api_tags_id(id:str):
    if request.method == "PATCH":
        return Tags.update(id)
    elif request.method == "DELETE":
        return Tags.delete(id)

@api_routes.route('/api/dags/triggerDag', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted(key='id')
@log_route()
def trigger_dag():
    id = request.args.get('id')
    return AirflowAPI().trigger_dag(id)

@api_routes.route('/api/dags/statusDag', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted(key='id')
@log_route()
def status_dag():
    id = request.args.get('id')
    return AirflowAPI().get_status(id)

@api_routes.route('/api/dags/killDag', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted(key='id')
@log_route()
def kill_dag():
    id = request.args.get('id')
    return AirflowAPI().kill_dag(id)

@api_routes.route('/api/dags/pauseDag', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted(key='id')
@log_route()
def pause_dag():
    id = request.args.get('id')
    return AirflowAPI().pause_dag(id)

@api_routes.route('/api/dags/unpauseDag', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted(key='id')
@log_route()
def unpause_dag():
    id = request.args.get('id')
    response = AirflowAPI().unpause_dag(id)
    if not response:
        return "Control's status is not valid", 403
    else:
        return AirflowAPI().unpause_dag(id)

@api_routes.route('/api/jira/task',  methods=['GET', 'POST'])
@login_required
@log_route()
def jira_task():
    if request.method == 'GET':
        xk = int(request.args.get('xk'))
        wf_id = int(request.args.get('wfId'))
        return JiraApi().get_task(wf_id, xk)
    else:
        form = dict(request.form)
        control_id = form["controlId"]
        wf_id = form["wfId"]
        form["rows_id"] = list(map(int, request.form.getlist('rowsId[]')))
        return JiraApi().create_task(control_id, wf_id, form["rows_id"])

@api_routes.route('/api/admin/db-conn',  methods=['GET', 'POST'])
@login_required
@roles_accepted(["TeamOwner"])
@log_route()
def create_conn():
    if request.method == 'POST':
        form = dict(request.form)
        return TeamConnection().create_secret_conn(form=form)
    else:
        team = request.args.get('team')
        conn_id = request.args.get('connId')
        return TeamConnection().get_secret_conn(team=team, conn_id=conn_id)

@api_routes.before_request
def auto_refresh_session():
    if session.permanent:
        session.modified = True
        session['lifetime'] = datetime.now(timezone.utc) + current_app.config["PERMANENT_SESSION_LIFETIME"]
