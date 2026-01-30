from flask import request
from ....app.extensions import db
from ....models.user import Users, user_roles, Roles, Teams
from ....logger.log import LogEvent
from ..aggrid import AGGrid


ALLOWED_COLS = {
    "id": Users.id,
    "name": Users.name,
    "email": Users.email,
    "role_id": Roles.id,
    "role_name": Roles.description,
    "team_id": Teams.id,
    "team_name": Teams.json["display_name"].as_string()
}

TEXT_OPS = {"contains", "notContains", "equals", "notEqual", "startsWith", "endsWith", "blank", "notBlank"}
DATE_OPS = {"equals", "lessThan", "greaterThan", "inRange", "blank", "notBlank"}
SET_OPS = {"set"}  # agSetColumnFilter

# custom query for grid
def users_base_query(payload):
    team_id = payload.get("teamId")

    q = db.session.query(
        Users.id.label("id"),
        Users.name.label("name"),
        Users.email.label("email"),
        Roles.id.label("role_id"),
        Roles.description.label("role_name"),
        Teams.id.label("team_id"),
        Teams.json["display_name"].label("team_name"),
    ).join(
        Teams, Users.team_id == Teams.id
    ).join(
        user_roles, Users.id == user_roles.user_id
    ).join(
        Roles, user_roles.role_id == Roles.id
    )

    if team_id:
        q = q.filter(Teams.id == team_id)

    return q
    

class AdminUsers:
    def __init__(self):
        self.grid = AGGrid(
            obj=Users,
            allowed_cols=ALLOWED_COLS,
            text_ops=TEXT_OPS,
            date_ops=DATE_OPS,
            base_query_fn=users_base_query,
            set_ops=SET_OPS,
        )

    @staticmethod
    def update_user(id):
        try:
            update = user_roles.query.filter_by(user_id=id).update(dict(role_id=request.form["role"]))
            db.session.commit()
            
            role_name = db.session.query(Roles.name).filter_by(id=request.form["role"]).first().name

            update = Users.query.filter_by(id=id).update(dict(
                team_id=request.form["team_id"],
                admin=True if role_name == "Admin" else False
            ))
            db.session.commit()
            
            LogEvent.log_event(eventName="updateEntity", entityName="user", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    @staticmethod
    def delete_user(id):
        try:
            delete = user_roles.query.filter_by(user_id=id).delete()
            db.session.commit()

            delete = Users.query.filter_by(id=id).delete()
            db.session.commit()
            
            LogEvent.log_event(eventName="deleteEntity", entityName="user", entityId=id)
            return '', 204
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        
    def get_grid(self):
        return self.grid.get_grid()

    def export_csv_stream(self):
        return self.grid.export_csv_stream(
            filename="users.csv"
        )
