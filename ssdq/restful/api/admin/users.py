from flask import request
from sqlalchemy import String, or_, and_
from ....app.extensions import db
from ....models.user import Users, user_roles, Roles, Teams
from ....logger.log import LogEvent


class AdminUsers:
    """
    Class with users
    """

    def __init__(self):
        pass
    
    @staticmethod
    def get_data():
        try:
            roles = Roles.query.all()
            roles_dict = [dict(id=row.id, name=row.name) for row in roles]
            
            team_list = Teams.query.all()
            teams_dict = [dict(id=row.id, name=row.json["display_name"]) for row in team_list]
            return dict(roles=roles_dict, teams=teams_dict)
        
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def get_datatable(team_id:str|None=None):
        try:
            attributes = {
                0: Users.id,
                1: Users.name,
                2: Users.email,
                3: Roles.description,
                4: Teams.json["display_name"].cast(String)
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
                order = Users.id
            
            query = Users.query.join(
                Teams, and_(
                    Users.team_id == Teams.id,
                    Teams.id == team_id if team_id else True
                )
            ).join(
                user_roles, Users.id == user_roles.user_id
            ).join(
                Roles, user_roles.role_id == Roles.id
            ).add_columns(
                Users.id,
                Users.name,
                Users.email,
                Roles.description.label("role_name"),
                Teams.json["display_name"].label("team_name")
            )
            if search:
                query = query.filter(
                    or_(
                        Users.id.cast(String).ilike(search),
                        Users.name.ilike(search),
                        Users.email.ilike(search),
                        Teams.json["display_name"].cast(String).ilike(search),
                        Roles.description.ilike(search)
                    )
                )
            
            dataset = query.order_by(order).limit(rowperpage).offset(row).all()
            data = [dict(
                id=row.id,
                name=row.name,
                email=row.email,
                team_name=row.team_name,
                role_name=row.role_name
            ) for row in dataset]
            
            total_records = int(Users.query.filter_by(team_id=team_id).count()) if team_id else int(Users.query.filter(Users.team_id.isnot(None)).count())
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
    def get_user_data(id):
        try:
            # role = user_roles.query.join(
            #     Roles, user_roles.role_id == Roles.id
            # ).add_columns(
            #     user_roles.role_id,
            #     Roles.name
            # ).filter_by(user_id=id).first().name
            # roles_dict = [dict(id=row.role_id, name=row.name) for row in roles]
            role_id = db.session.query(user_roles.role_id).filter_by(user_id=id).first().role_id
            
            team_id = db.session.query(Users.team_id).filter_by(id=id).first().team_id
            return dict(role_id=role_id, team_id=team_id)
        
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

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
