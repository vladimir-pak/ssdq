from sqlalchemy import Column, String, Date, JSON, DateTime, Integer, Text, Boolean
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
    team_id = Column(UUID(as_uuid=True))

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

    def __repr__(self):
        return '<subject_area_sdim %r %r>' % (self.id, self.name)


class error_reason_sdim(Base):
    __tablename__ = 'error_reason_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default='N')
    team_id = Column(UUID(as_uuid=True))

    def __repr__(self):
        return '<error_reason_sdim %r %r>' % (self.id, self.name)


class Config(Base):
    __tablename__ = 'config'
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    json = Column(JSON)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(DateTime, default=datetime.now())

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
    tag_type = Column(String(50))

    def __repr__(self):
        return '<tags %r %r>' % (self.id, self.name)


class dq_characteristic_sdim(Base):
    __tablename__ = 'dq_characteristic_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_characteristic_sdim %r %r>' % (self.id, self.name)


class dq_team_attributes_dim(Base):
    __tablename__ = 'dq_team_attributes_dim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100))
    description = Column(String(400))
    is_required = Column(Boolean, default=False)
    team_id = Column(UUID(as_uuid=True))
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_team_attributes_dim %r %r>' % (self.id, self.name)
    