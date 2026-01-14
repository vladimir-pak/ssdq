from ...app.extensions import db
from ...models.dict import dq_object_sdim, dq_pattern_sdim, tags
from ...models.user import Users
from ...logger.log import LogEvent
from sqlalchemy import or_, String, func, literal_column
from flask import jsonify, request
from flask_login import current_user
from enum import Enum


class Select2Objects(Enum):
    users = Users
    objects = dq_object_sdim
    pattern = dq_pattern_sdim
    tags = tags


class Select2Attribiutes(Enum):
    users = [Users.id, Users.name, Users.email]
    objects = [dq_object_sdim.id, dq_object_sdim.table_name, dq_object_sdim.schema]
    pattern = [dq_pattern_sdim.id, dq_pattern_sdim.name]
    tags = [tags.id, tags.name]


class Select2API:
    def __init__(self):
        pass

    @staticmethod
    def get_filter(entity:str, attr_list:list, query):
        try:
            search_like = f"%%{str(request.args.get('search')).lower()}%%"
            SELECT_FILTERS = {
                "users": query.filter(
                            Users.team_id == current_user.team_id if not current_user.admin else True,
                            or_(
                                attr.cast(String).ilike(search_like) for attr in attr_list
                            )
                        ),
                "objects": query.filter(
                            dq_object_sdim.deleted_flag == "N",
                            func.concat(dq_object_sdim.schema, literal_column("'.'"), dq_object_sdim.table_name).ilike(search_like)
                        ),
                "pattern": query.filter(
                            dq_pattern_sdim.deleted_flag == "N",
                            dq_pattern_sdim.team_id == current_user.team_id if not current_user.admin else True,
                            dq_pattern_sdim.name.ilike(search_like)
                        ),
                "tags": query.filter(
                            tags.team_id == current_user.team_id if not current_user.admin else True,
                            tags.name.ilike(search_like)
                        )
            }
            return SELECT_FILTERS[entity]
        except KeyError:
            return query

    @staticmethod
    def get_data(entity:str):
        try:
            obj = Select2Objects[entity].value
            attr_list = Select2Attribiutes[entity].value

            page = int(request.args.get('page'))
            if page == 1:
                offset = 0
                limit = 11
            else:
                offset = page * 10 - 10
                limit = page * 10 + 1

            query = db.session.query(*attr_list)

            query = Select2API.get_filter(entity, attr_list, query)

            data = query.order_by(attr_list[0]).limit(limit).offset(offset).all()

            if len(data) > 10:
                more = 'true'
                data = data[:10]
            else:
                more = 'false'

            result = [Select2API.__get_text(entity, row) for row in data]
            response = dict(
                results=result,
                pagination=dict(
                    more=more
                )
            )

            return jsonify(response)

        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    @staticmethod
    def __get_text(entity:str, row):
        if entity == "users":
            response = dict(
                id=row.id,
                text=f"{row.name} ({row.email})"
            )
        elif entity == 'objects':
            response = dict(
                id=row.id,
                text=f"{row.schema}.{row.table_name}"
            )
        else:
            response = dict(
                id=row.id,
                text=f"{row.name}"
            )
        return response
    