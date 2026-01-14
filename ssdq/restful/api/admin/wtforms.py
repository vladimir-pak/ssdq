from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SysDictForm(FlaskForm):
    id = StringField('id')
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    host = StringField('host')
    port = StringField('port')
    db_name = StringField('db_name')
    dbtype = StringField('dbtype')
    sslmode = StringField('sslmode')


class TeamDictForm(FlaskForm):
    id = StringField('id')
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    team_id = StringField('team_id')


class ObjectsForm(FlaskForm):
    id = StringField('id')
    base_name = StringField('base_name')
    schema = StringField('schema', validators=[DataRequired()])
    table_name = StringField('table_name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])


class PatternDictForm(FlaskForm):
    id = StringField('id')
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    sql = StringField('sql')
    params = StringField('params')
    team_id = StringField('team_id')
