from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, DateTime, Boolean, JSON, Column
from ..app.extensions import Base, db
from uuid import uuid4
from datetime import datetime


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), unique=True)
    description = Column(String(200))

    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<roles %r %r>' % (self.id, self.name)


class Users(Base, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(100), unique=True)
    name = Column(String(255))
    login = Column(String(20), unique=True)
    admin = Column(Boolean)
    password = Column(String(1000))
    team_id = Column(UUID(as_uuid=True))

    def __init__(self, id=None, email=None, name=None, login=None, admin=None, password=None, team_id=None):
        self.id = id
        self.email = email
        self.name = name
        self.login = login
        self.admin = admin
        self.password = password
        self.team_id = team_id

    def __repr__(self):
        return str(self.id, self.name)

    @property
    def role_name(self):
        data = user_roles.query.join(
            Roles, user_roles.role_id == Roles.id
        ).add_columns(
            Roles.name
        ).filter(
            user_roles.user_id == self.id        ).first().name
        print(data)
        return str(data)

    @property
    def team_name(self):
        data = db.session.query(Teams.json["display_name"].label("name")).filter_by(id=self.team_id).first()
        return str(data.name)

    @property
    def team_eng_name(self):
        data = db.session.query(Teams.name).filter_by(id=self.team_id).first()
        return str(data.name)


class user_roles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    role_id = Column(UUID(as_uuid=True), unique=True)

    def __init__(self, user_id=None, role_id=None):
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self):
        return '<user_roles %r %r>' % (self.user_id, self.role_id)


class user_login(Base):
    __tablename__ = 'user_login'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    login_timestamp = Column(DateTime, primary_key=True, default=datetime.now())
    access_token = Column(String(3000))

    def __init__(self, user_id=None, login_timestamp=None, access_token=None):
        self.user_id = user_id
        self.login_timestamp = login_timestamp
        self.access_token = access_token

    def __repr__(self):
        return '<user_login %r %r>' % (self.user_id, self.login_timestamp)


class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(UUID(as_uuid=True), unique=True)
    description = Column(String(1000))
    deleted_flag = Column(String(1), default='N')
    updated_at = Column(DateTime, default=datetime.now())
    json = Column(JSON)

    def __init__(self, id=None, name=None, description=None, deleted_flag=None, updated_at=None, json=None):
        self.id = id
        self.name = name
        self.description = description
        self.deleted_flag = deleted_flag
        self.updated_at = updated_at
        self.json = json

    def __repr__(self):
        return '<teams %r %r>' % (self.id, self.name)
