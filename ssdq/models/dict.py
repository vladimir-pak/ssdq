from sqlalchemy import Column, String, Date, JSON, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from ..app.extensions import Base
from datetime import datetime
from uuid import uuid4


class dq_control_type_sdim(Base):
    __tablename__ = 'dq_control_type_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(200))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default="N")

    def __init__(self, id=None, name=None, description=None, updated_at=None, deleted_flag=None):
        self.id = id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.deleted_flag = deleted_flag

    def __repr__(self):
        return '<dq_control_type_sdim %r>' % (self.id, self.name, self.description, self.updated_at, self.deleted_flag)


class dq_source_sdim(Base):
    __tablename__ = 'dq_source_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(200))
    deleted_flag = Column(String(1), default="N")
    updated_at = Column(DateTime, default=datetime.now())
    host = Column(String(100))
    port = Column(Integer)
    db_name = Column(String(100))
    dbtype = Column(String(100))
    sslmode = Column(String(100))

    def __init__(self, id=None, name=None, description=None,
                 deleted_flag=None, updated_at=None,
                 host=None, port=None, db_name=None,
                 dbtype=None, sslmode=None):
        self.id = id
        self.name = name
        self.description = description
        self.deleted_flag = deleted_flag
        self.updated_at = updated_at
        self.host = host
        self.port = port
        self.db_name = db_name
        self.dbtype = dbtype
        self.sslmode = sslmode

    def __repr__(self):
        return '<dq_source_sdim %r %r>' % (
            self.id, self.name)


class dq_object_sdim(Base):
    __tablename__ = 'dq_object_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    base_name = Column(String(50))
    schema = Column(String(100))
    table_name = Column(String(200))
    description = Column(String(255))
    deleted_flag = Column(String(1), default="N")
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, base_name=None, schema=None, table_name=None, description=None,
                 deleted_flag=None):
        self.id = id
        self.base_name = base_name
        self.schema = schema
        self.table_name = table_name
        self.description = description
        self.deleted_flag = deleted_flag

    def __repr__(self):
        return '<dq_object_hdim %r %r %r %r>' % (
        self.id, self.base_name, self.schema, self.table_name)


class dq_segment_sdim(Base):
    __tablename__ = 'dq_segment_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(200))
    deleted_flag = Column(String(1), default="N")
    updated_at = Column(DateTime, default=datetime.now())
    team_id = Column(UUID(as_uuid=True))

    def __init__(self, id=None, name=None, description=None, deleted_flag=None, 
                 updated_at=None, team_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.deleted_flag = deleted_flag
        self.updated_at = updated_at
        self.team_id = team_id

    def __repr__(self):
        return '<dq_segment_sdim %r %r>' % (self.id, self.name)


class subject_area_sdim(Base):
    __tablename__ = 'subject_area_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    updated_at = Column(Date, default=datetime.now())
    deleted_flag = Column(String(1), default="N")
    team_id = Column(UUID(as_uuid=True))

    def __init__(self, id=None, name=None, description=None, updated_at=None, deleted_flag=None, team_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.deleted_flag = deleted_flag
        self.team_id = team_id

    def __repr__(self):
        return '<subject_area_sdim %r %r %r %r %r %r>' % (self.id, self.name, self.description, self.updated_at, self.deleted_flag, self.team_id)


class error_reason_sdim(Base):
    __tablename__ = 'error_reason_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default='N')
    team_id = Column(UUID(as_uuid=True))

    def __init__(self, id=None, name=None, description=None, updated_at=None, deleted_flag=None, team_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.deleted_flag = deleted_flag
        self.team_id = team_id

    def __repr__(self):
        return '<error_reason_sdim %r %r %r %r %r %r>' % (self.id, self.name, self.description, self.updated_at, self.deleted_flag, self.team_id)


class Config(Base):
    __tablename__ = 'config'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    json = Column(JSON)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, json=None, updated_by=None, updated_at=None):
        self.id = id
        self.json = json
        self.updated_by = updated_by
        self.updated_at = updated_at

    def __repr__(self):
        return f'<config {self.json}>'


class dq_pattern_sdim(Base):
    __tablename__ = 'dq_pattern_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    sql = Column(Text)
    params = Column(JSON)
    team_id = Column(UUID(as_uuid=True))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default='N')

    def __init__(self, id=None, name=None, description=None, sql=None,
        params=None, team_id=None, updated_at=None, deleted_flag=None):
        self.id = id
        self.name = name
        self.description = description
        self.sql = sql
        self.params = params
        self.team_id = team_id
        self.updated_at = updated_at
        self.deleted_flag = deleted_flag

    def __repr__(self):
        return '<dq_pattern_sdim %r %r %r>' % (self.id, self.name, self.team_id)


class tags(Base):
    __tablename__ = 'tags'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    updated_at = Column(DateTime, default=datetime.now())
    team_id = Column(UUID(as_uuid=True))

    def __init__(self, id=None, name=None, description=None, 
                 updated_at=None, team_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.team_id = team_id

    def __repr__(self):
        return '<tags %r %r>' % (self.id, self.name)
