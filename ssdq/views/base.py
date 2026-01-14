from datetime import datetime, timezone
from flask_login import current_user, login_required
from flask import render_template, Blueprint, current_app, request, session
from ..controls.controls import Controls
from ..logger.log import LogEvent, log_route
from ..models.user import Teams
from ..models.constants import DbType
from ..app.dbconfig import ConfigSSDQ
from ..security.access import roles_accepted, control_accepted, teams_accepted
from ..import_xlsx.controls import ImportControls


app_routes = Blueprint('app_routes', __name__, template_folder='templates')


@app_routes.errorhandler(Exception)
def handle_exception(e):
    current_app.logger.error(f'Exception: {e}', exc_info=True)
    return 'Internal Server Error', 500

@app_routes.route('/controls', methods=['GET'])
@login_required
@log_route()
def controls():
    return Controls.render()

@app_routes.route('/controls/create', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@log_route()
def create_control():
    if request.method == "GET":
        return Controls.render_crud(action="create")
    else:
        return Controls().create()

@app_routes.route('/controls/<int:id>', methods=['POST', 'GET', 'DELETE', 'PUT'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted()
@log_route()
def update_control(id):
    if request.method == "GET":
        return Controls.render_crud(action="update", control_id=id)
    elif request.method == "POST":
        return Controls().update(id)
    elif request.method == "DELETE":
        return Controls().delete(id)
    elif request.method == "PUT":
        return Controls().actualize(id)

@app_routes.route('/controls/<int:id>/clone', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@log_route()
def clone_control(id):
    if request.method == 'GET':
        return Controls.render_crud(action="update", control_id=id)
    else:
        return Controls().create()

@app_routes.route('/import/controls', methods=['POST'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@log_route()
def import_controls():
    return ImportControls().create()

@app_routes.route('/monitoring/<string:flt>', methods=['GET'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@log_route()
def monitoring(flt:str):
    return render_template('home/monitoring.html', filter=flt)

@app_routes.route('/main', methods=['GET'])
@login_required
@log_route()
def main_page():
    return render_template('home/main.html')

@app_routes.route('/report/<int:id>', methods=['GET'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted()
@log_route()
def report(id):
    return render_template('home/report.html', control_id=id)

@app_routes.route('/report/<int:id>/edit/<int:wf_id>', methods=['GET'])
@login_required
@roles_accepted(["User", "TeamOwner"])
@control_accepted()
@log_route()
def report_edit(id, wf_id):
    return render_template('home/report-edit.html', 
                    control_id=id, 
                    wf_id=wf_id,
                    jira_url=current_app.config["JIRA_URL"])

"""Admin routes"""
@app_routes.route('/admin', methods=['GET'])
@login_required
@log_route()
def admin_pn():
    return render_template('home/admin/admin.html')

@app_routes.route('/admin/users', methods=['GET'])
@login_required
@roles_accepted(["AdminSec"])
@log_route()
def admin_users():
    return render_template('home/admin/users.html')

@app_routes.route('/admin/teams', methods=['GET'])
@login_required
@roles_accepted(["AdminSec"])
@log_route()
def admin_teams():
    return render_template('home/admin/teams.html')

@app_routes.route('/admin/teams/<string:id>', methods=['GET'])
@login_required
@roles_accepted(["User", "TeamOwner", "AdminSec"])
@log_route()
def admin_change_team(id:str):
    return render_template('home/admin/change-team.html', id=id)

@app_routes.route('/admin/objects', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "TeamOwner", "AdminSec"])
@log_route()
def adm_objects():
    return render_template('home/admin/objects.html')

@app_routes.route('/admin/sources', methods=['POST', 'GET'])
@login_required
@roles_accepted(["AdminSec"])
@log_route()
def adm_sources():
    dbtypes = [cur.value for cur in DbType]
    return render_template('home/admin/sources.html', dbtypes=dbtypes)

@app_routes.route('/admin/segments', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_segments():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/segments.html', teams=team_list)

@app_routes.route('/admin/control-types', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_controltypes():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/control-types.html', teams=team_list)

@app_routes.route('/admin/error-reason', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_errorreason():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/error-reason.html', teams=team_list)

@app_routes.route('/admin/subject-area', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_subjectarea():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/subject-area.html', teams=team_list)

@app_routes.route('/admin/pattern-sql', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_sqlpattern():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/pattern-sql.html', teams=team_list)

@app_routes.route('/admin/tags', methods=['POST', 'GET'])
@login_required
@roles_accepted(["User", "AdminSec", "TeamOwner"])
@log_route()
def adm_tags():
    if current_user.admin or current_user.role_name == "AdminSec":
        team_list = Teams.query.all()
    else:
        team_list = Teams.query.filter_by(id=current_user.team_id).all()
    return render_template('home/admin/tags.html', teams=team_list)

@app_routes.route('/config', methods=['GET','POST'])
@login_required
@roles_accepted(["AdminSec"], "GET")
@log_route()
def get_conf():
    conf = ConfigSSDQ()
    if request.method == 'GET':
        return render_template('home/config.html', conf=conf.config_json)
    else:
        return conf.update_config()

@app_routes.route('/session/refresh', methods=['POST'])
@login_required
@log_route()
def refresh_session():
    """
        Обновление сессии осуществляется в app.before_request
    """
    return {"lifetime": session["lifetime"]}, 200

@app_routes.route('/groups-error', methods=['GET'])
def groups_error():
    LogEvent.log_warning()
    return render_template('home/insufficient-privileges.html')

@app_routes.route('/superset', methods=['GET'])
def redirect_superset():
    return render_template('home/superset.html')

@app_routes.route('/streamlit', methods=['GET'])
@teams_accepted(current_app.config['STREAMLIT_ACCEPTANCE'])
def redirect_streamlit():
    return render_template('home/streamlit.html')

@app_routes.before_request
def auto_refresh_session():
    if not request.path.startswith('/static/'):
        if session.permanent:
            session.modified = True
            session['lifetime'] = datetime.now(timezone.utc) + current_app.config["PERMANENT_SESSION_LIFETIME"]
