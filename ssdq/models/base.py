from sqlalchemy import Column, Integer, String, Date, Text, Sequence, \
    DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from ..app.extensions import Base


class dq_control_sdim(Base):
    __tablename__ = 'dq_control_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(Integer, primary_key=True, default=Sequence('dq_control_sdim_id_seq', schema="ssdq"))
    name = Column(String(250))
    description = Column(String(500))
    conditions = Column(String(500))
    segment_id = Column(UUID(as_uuid=True))
    source_id = Column(UUID(as_uuid=True))
    status_id = Column(Integer)
    wiki = Column(String(400))
    team_id = Column(UUID(as_uuid=True))
    created_by = Column(UUID(as_uuid=True))
    deleted_flag = Column(String(1), default="N")
    updated_at = Column(DateTime, default=datetime.now())
    threshold_min = Column(Integer)
    threshold_max = Column(Integer)
    control_type_id = Column(UUID(as_uuid=True))
    subject_area_id = Column(UUID(as_uuid=True))
    critical_level = Column(String(10))
    alerting_type_id = Column(Integer)
    jira_mode_id = Column(Integer)
    characteristic_id = Column(UUID(as_uuid=True))
    team_attributes = Column(JSON)

    def __init__(self, id=None, name=None, description=None, conditions=None, segment_id=None, source_id=None,
                 status_id=None, wiki=None, team_id=None, created_by=None, deleted_flag=None,
                 updated_at=None, threshold_min=None, threshold_max=None, control_type_id=None, 
                 subject_area_id=None, critical_level=None, alerting_type_id=None, jira_mode_id=None,
                 characteristic_id=None, team_attributes=None,
                 **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.conditions = conditions
        self.segment_id = segment_id
        self.source_id = source_id
        self.status_id = status_id
        self.wiki = wiki
        self.team_id = team_id
        self.created_by = created_by
        self.deleted_flag = deleted_flag
        self.updated_at = updated_at
        self.threshold_min = threshold_min
        self.threshold_max = threshold_max
        self.control_type_id = control_type_id
        self.subject_area_id = subject_area_id
        self.critical_level = critical_level
        self.alerting_type_id = alerting_type_id
        self.jira_mode_id = jira_mode_id
        self.characteristic_id = characteristic_id
        self.team_attributes = team_attributes

    def __repr__(self):
        return '<dq_control_sdim %r>' % (self.id)


class dq_control_hist(Base):
    __tablename__ = 'dq_control_hist'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    description = Column(String(500))
    conditions = Column(String(500))
    segment_id = Column(UUID(as_uuid=True))
    source_id = Column(UUID(as_uuid=True))
    status_id = Column(Integer)
    wiki = Column(String(400))
    team_id = Column(UUID(as_uuid=True))
    created_by = Column(UUID(as_uuid=True))
    threshold_min = Column(Integer)
    threshold_max = Column(Integer)
    control_type_id = Column(UUID(as_uuid=True))
    subject_area_id = Column(UUID(as_uuid=True))
    critical_level = Column(String(10))
    alerting_type_id = Column(Integer)
    jira_mode_id = Column(Integer)
    effective_from = Column(DateTime)
    effective_to = Column(DateTime, default=datetime.now())
    characteristic_id = Column(UUID(as_uuid=True))
    team_attributes = Column(JSON)

    def __repr__(self):
        return '<dq_control_sdim %r>' % (self.id)


class dq_monitoring_view(Base):
    __tablename__ = 'dq_monitoring_view'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(4000))
    object_name = Column(String(255))
    owner = Column(UUID(as_uuid=True))
    owner_name = Column(String(255))
    status_name = Column(String(100))
    run_id = Column(Integer)
    last_start = Column(Date)
    last_result = Column(String(255))
    overflow_start = Column(Date)
    overflow_result = Column(String(255))
    description = Column(String(255))
    rule_description = Column(String(4000))
    overflow_run_id = Column(Integer)
    need_act = Column(String(3))
    dqi_id = Column(String(20), primary_key=True)
    status_id = Column(Integer)
    team_id = Column(UUID(as_uuid=True))
    team_name = Column(String(255))
    expiring_date = Column(Date)
    critical_level = Column(String(10))

    def __repr__(self):
        return '<dq_monitoring_view %r >' % self.id


class dq_detail_agg(Base):
    __tablename__ = 'dq_detail_agg'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    control_id = Column(Integer, primary_key=True)
    pm_workflow_run_id = Column(Integer, primary_key=True)
    description = Column(String(255))
    mistake_count = Column(Integer)
    report_date = Column(Date)
    start_time = Column(Date)
    end_time = Column(Date)
    error_flag = Column(String(1))
    out_of_margins_flag = Column(String(1))
    workflow_name = Column(String(155))
    error_name = Column(String(2000))

    def __repr__(self):
        return '<dq_detail_agg %r %r %r %r>' % (
            self.control_id, self.mistake_count, self.report_date, self.pm_workflow_run_id)


class dq_detailjournal_web(Base):
    __tablename__ = 'dq_detailjournal_web'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    control_id = Column(Integer)
    error_flag = Column(String(1), default='Y')
    report_time = Column(DateTime, default=datetime.now())
    xk = Column(Integer, primary_key=True, default=Sequence("dq_detailjournal_web_seq", schema="ssdq"))
    pm_workflow_run_id = Column(Integer)
    json = Column(JSON)

    def __repr__(self):
        return '<dq_detailjournal_web %r %r>' % (self.control_id, self.pm_workflow_run_id)


class dq_alerting_stat(Base):
    __tablename__ = 'dq_alerting_stat'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    control_id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_alerting_stat %r %r>' % (self.control_id, self.user_id)


class dq_dag_sdim(Base):
    __tablename__ = 'dq_dag_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    control_id = Column(Integer, primary_key=True)
    sql = Column(Text)
    cron = Column(String(100))
    load_end = Column(String(100))
    source = Column(UUID(as_uuid=True))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default="N")
    crossdb_flag = Column(String(1), default="N") # will deprecate
    dag_type = Column(Integer)
    pattern_id = Column(UUID(as_uuid=True))
    params = Column(JSON)
    limit = Column(Boolean, default=True)

    def __repr__(self):
        return '<dq_dag_sdim %r %r>' % (
            self.control_id,
            self.crossdb_flag,
            self.dag_type)


class dq_dag_crossdb_sdim(Base):
    __tablename__ = 'dq_dag_crossdb_sdim'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}
    control_id = Column(Integer, primary_key=True)
    sql = Column(Text)
    source = Column(UUID(as_uuid=True))
    custom_source_name = Column(String(100), primary_key=True)
    main_sql = Column(String(1))
    updated_at = Column(DateTime, default=datetime.now())
    deleted_flag = Column(String(1), default="N")

    def __repr__(self):
        return '<dq_dag_crossdb_sdim %r>' % (
            self.control_id)


class view_all_controls_bymonth(Base):
    __tablename__ = 'view_all_controls_bymonth'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    thedate = Column(Date, primary_key=True)
    id = Column(Integer, primary_key=True)
    status_id = Column(Integer)
    team_id = Column(UUID(as_uuid=True))

    def __repr__(self):
        return '<view_all_controls_bymonth %r %r %r>' % (self.thedate, self.id, self.status_id)


class view_controls_error_bymonth(Base):
    __tablename__ = 'view_controls_error_bymonth'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    report_date = Column(Date, primary_key=True)
    id = Column(Integer, primary_key=True)
    team_id = Column(UUID(as_uuid=True))

    def __repr__(self):
        return '<view_controls_error_bymonth %r %r>' % (
            self.report_date, self.id)


class view_controls_last_results(Base):
    __tablename__ = 'view_controls_last_results'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    id = Column(Integer, primary_key=True)
    pm_workflow_run_id = Column(String(255))
    mistake_count = Column(Integer)
    end_time = Column(Date)
    error_flag = Column(String(1))
    status_id = Column(Integer)

    def __repr__(self):
        return '<view_controls_last_results %r %r %r %r %r %r>' % (
            self.id, self.pm_workflow_run_id, self.mistake_count, self.end_time, self.error_flag, self.status_id)


class dq_control_owner_stat(Base):
    __tablename__ = 'dq_control_owner_stat'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    control_id = Column(Integer, primary_key=True)
    owner_id = Column(UUID(as_uuid=True), primary_key=True)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_control_owner_stat %r>' % (self.control_id, self.owner_id)


class dq_control_object_stat(Base):
    __tablename__ = 'dq_control_object_stat'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    control_id = Column(Integer, primary_key=True)
    object_id = Column(UUID(as_uuid=True), primary_key=True)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_control_object_stat %r>' % (self.control_id, self.object_id)


class dq_jira_issues(Base):
    __tablename__ = 'dq_jira_issues'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    pm_workflow_run_id = Column(Integer, primary_key=True)
    xk = Column(Integer, primary_key=True)
    jira_issue = Column(String(50))
    json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_jira_issues %r>' % (self.pm_workflow_run_id, self.xk, self.jira_issue)


class featured_controls(Base):
    __tablename__ = 'featured_controls'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    control_id = Column(Integer)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<featured_controls %r>' % (self.user_id, self.control_id)


class dq_validation_stat(Base):
    __tablename__ = 'dq_validation_stat'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    control_id = Column(Integer, primary_key=True)
    disabled = Column(Boolean)
    disable_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now())
    emailed = Column(Boolean, default=False)
    validation_type_id = Column(Integer)

    def __repr__(self):
        return '<dq_validation_stat %r>' % (self.control_id)


class dq_control_tags_stat(Base):
    __tablename__ = 'dq_control_tags_stat'
    __table_args__ = {"schema": "ssdq", 'extend_existing': True}

    control_id = Column(Integer, primary_key=True)
    tag_id = Column(UUID(as_uuid=True), primary_key=True)
    updated_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return '<dq_control_tags_stat %r>' % (self.control_id, self.tag_id)
