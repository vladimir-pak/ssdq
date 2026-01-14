from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from ..app.extensions import Base


class sdq_logs(Base):
    __bind_key__ = "audit_db"
    __tablename__ = 'sdq_logs'
    __table_args__ = {"schema": "audit", 'extend_existing': True}

    deviceeventclassid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start = Column(DateTime)
    eventtype = Column(String(256))
    name = Column(String(256))
    eventobj = Column(String(256))
    eventobjid = Column(String(256))
    suser = Column(String(256))
    suserid = Column(String(256))
    spt = Column(String(50))
    app = Column(String(50))
    msg = Column(JSONB)
    src = Column(String(50))
    shost = Column(String(50))
    dhostname = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.now())

    def __init__(self, deviceeventclassid=None, start=None, eventtype=None, name=None, eventobj=None,
                 eventobjid=None, suser=None, suserid=None, spt=None, app=None, msg=None, src=None,
                 shost=None, dhostname=None, uploaded_at=None):
        self.deviceeventclassid = deviceeventclassid
        self.start = start
        self.eventtype = eventtype
        self.name = name
        self.eventobj = eventobj
        self.eventobjid = eventobjid
        self.suser = suser
        self.suserid = suserid
        self.spt = spt
        self.app = app
        self.msg = msg
        self.src = src
        self.shost = shost
        self.dhostname = dhostname
        self.uploaded_at = uploaded_at

    def __repr__(self):
        return '<sdq_logs %r>' % (self.deviceeventclassid)
    

class sdq_config_checksum(Base):
    __tablename__ = "sdq_config_checksum"
    __table_args__ = {"schema": "ssdq_admin", 'extend_existing': True}

    externalid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    updated_at = Column(DateTime, default=datetime.now())
    config_name = Column(String(100))
    checksum = Column(String(256))

    def __init__(self, externalid=None, updated_at=datetime.now(), config_name=None, checksum=None):
        self.externalid = externalid
        self.updated_at = updated_at
        self.config_name = config_name
        self.checksum = checksum

    def __repr__(self):
        return '<sdq_config_checksum %r>' % (self.externalid)
