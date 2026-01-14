"""Init

Revision ID: 39a07e5d0376
Revises: 
Create Date: 2025-02-24 09:53:49.048086

"""
from typing import Sequence, Union
import logging
from datetime import datetime
from pathlib import Path
import hashlib
import binascii
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Text, Sequence, JSON, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from ssdq.app import app


# revision identifiers, used by Alembic.
revision: str = '39a07e5d0376'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("create schema if not exists ssdq")
    op.execute("create schema if not exists ssdq_admin")
    
    users = op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=255), nullable=False),
        sa.Column("email", String(length=100), nullable=False),
        sa.Column("login", String(length=20), nullable=False),
        sa.Column("admin", Boolean),
        sa.Column("password", String(length=1000)),
        sa.Column("team_id", UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    roles = op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=200)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    try:
        op.bulk_insert(
            roles,
            [
                {
                    "id": uuid4(),
                    "name": "Admin",
                    "description": "Прикладной администратор"
                },
                {
                    "id": uuid4(),
                    "name": "AdminSec",
                    "description": "Администратор ИБ"
                },
                {
                    "id": uuid4(),
                    "name": "TeamOwner",
                    "description": "Лидер команды"
                },
                {
                    "id": uuid4(),
                    "name": "User",
                    "description": "Пользователь"
                },
            ]
        )
        
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', app.config["API_BOT_PASSWORD"].encode('utf-8'),
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        apibot_password = (salt + pwdhash)
        op.bulk_insert(
            users,
            [
                {
                    "id": uuid4(),
                    "name": "API bot",
                    "email": "apibot@mail.com",
                    "login": "apibot",
                    "admin": False,
                    "password": apibot_password.decode("utf-8")
                }
            ]
        )
        
    except Exception as ex:
        logging.error(str(ex))
    
    op.create_table(
        "user_roles",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("user_id", "role_id"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    op.create_table(
        "user_login",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("login_timestamp", DateTime(), nullable=False),
        sa.Column("access_token", String(3000)),
        sa.UniqueConstraint("user_id", "login_timestamp"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    teams = op.create_table(
        "teams",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=200)),
        sa.Column("json", JSON),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    try:
        op.bulk_insert(
            teams,
            [
                {
                    "id": uuid4(),
                    "name": "admin",
                    "description": "Прикладные администраторы",
                    "json": {
                        "display_name": "admin",
                        "jira_project": "JIRA_PROJECT"
                    },
                    "updated_at": datetime.now(),
                    "deleted_flag": "N"
                },
                {
                    "id": uuid4(),
                    "name": "adminsec",
                    "description": "Администраторы ИБ",
                    "json": {
                        "display_name": "adminsec",
                        "jira_project": "JIRA_PROJECT"
                    },
                    "updated_at": datetime.now(),
                    "deleted_flag": "N"
                }
            ]
        )
    except Exception as ex:
        logging.error(str(ex))
    
    op.create_table(
        "dq_control_type_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=200)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_source_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=200)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_segment_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=200)),
        sa.Column("team_id", UUID(as_uuid=True)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "team_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "subject_area_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=400)),
        sa.Column("team_id", UUID(as_uuid=True)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "team_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "error_reason_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", String(length=100), nullable=False),
        sa.Column("description", String(length=400)),
        sa.Column("team_id", UUID(as_uuid=True)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "team_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_object_sdim",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("base_name", String(length=50), nullable=False),
        sa.Column("schema", String(length=100), nullable=False),
        sa.Column("table_name", String(length=200), nullable=False),
        sa.Column("description", String(length=255)),
        sa.Column("updated_at", DateTime()),
        sa.Column("deleted_flag", String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "config",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("json", JSON, nullable=False),
        sa.Column("updated_by", UUID(as_uuid=True)),
        sa.Column("updated_at", DateTime()),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    
    op.create_table(
        "dq_control_sdim",
        Column("id", Integer()),
        Column("name", String(length=250)),
        Column("description", String(length=500)),
        Column("conditions", String(length=500)),
        Column("segment_id", UUID(as_uuid=True)),
        Column("source_id", UUID(as_uuid=True)),
        Column("status_id", Integer()),
        Column("wiki", String(length=400)),
        Column("team_id", UUID(as_uuid=True)),
        Column("created_by", UUID(as_uuid=True)),
        Column("deleted_flag", String(length=1)),
        Column("updated_at", DateTime()),
        Column("threshold_min", Integer()),
        Column("threshold_max", Integer()),
        Column("control_type_id", UUID(as_uuid=True)),
        Column("subject_area_id", UUID(as_uuid=True)),
        Column("critical_level", String(length=10)),
        Column("alerting_type_id", Integer()),
        Column("jira_mode_id", Integer()),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_control_hist",
        Column("id", Integer()),
        Column("name", String(length=250)),
        Column("description", String(length=500)),
        Column("conditions", String(length=500)),
        Column("segment_id", UUID(as_uuid=True)),
        Column("source_id", UUID(as_uuid=True)),
        Column("status_id", Integer()),
        Column("wiki", String(length=400)),
        Column("team_id", UUID(as_uuid=True)),
        Column("created_by", UUID(as_uuid=True)),
        Column("threshold_min", Integer()),
        Column("threshold_max", Integer()),
        Column("control_type_id", UUID(as_uuid=True)),
        Column("subject_area_id", UUID(as_uuid=True)),
        Column("critical_level", String(length=10)),
        Column("alerting_type_id", Integer()),
        Column("jira_mode_id", Integer()),
        Column("effective_from", DateTime()),
        Column("effective_to", DateTime()),
        sa.UniqueConstraint("id", "effective_from"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_detail_agg",
        Column("control_id", Integer()),
        Column("pm_workflow_run_id", Integer()),
        Column("description", String(length=255)),
        Column("mistake_count", Integer()),
        Column("report_date", DateTime()),
        Column("start_time", DateTime()),
        Column("end_time", DateTime()),
        Column("error_flag", String(length=1)),
        Column("out_of_margins_flag", String(length=1)),
        Column("workflow_name", String(length=155)),
        Column("error_name", String(length=2000)),
        sa.UniqueConstraint("control_id", "pm_workflow_run_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_detailjournal_web",
        Column("control_id", Integer()),
        Column("error_flag", String(length=1), server_default='Y'),
        Column("report_time", DateTime, server_default=sa.func.current_timestamp()),
        Column("xk", Integer()),
        Column("pm_workflow_run_id", Integer()),
        Column("json", JSON),
        sa.PrimaryKeyConstraint("xk"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_alerting_stat",
        Column("control_id", Integer()),
        Column("user_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("control_id", "user_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_dag_sdim",
        Column("control_id", Integer()),
        Column("sql", Text()),
        Column("cron", String(length=100)),
        Column("load_end", String(length=100)),
        Column("source", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        Column("deleted_flag", String(length=1)),
        Column("crossdb_flag", String(length=1)),
        sa.UniqueConstraint("control_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_dag_crossdb_sdim",
        Column("control_id", Integer()),
        Column("sql", Text()),
        Column("source", UUID(as_uuid=True)),
        Column("custom_source_name", String(length=100)),
        Column("main_sql", String(length=1)),
        Column("updated_at", DateTime()),
        Column("deleted_flag", String(length=1)),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_control_owner_stat",
        Column("control_id", Integer()),
        Column("owner_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("control_id", "owner_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_control_object_stat",
        Column("control_id", Integer()),
        Column("object_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("control_id", "object_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_jira_issues",
        Column("pm_workflow_run_id", Integer()),
        Column("xk", Integer()),
        Column("jira_issue", String(length=50)),
        Column("json", JSON),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("pm_workflow_run_id", "xk"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "featured_controls",
        Column("user_id", UUID(as_uuid=True)),
        Column("control_id", Integer()),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("control_id", "user_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "dq_validation_stat",
        Column("control_id", Integer()),
        Column("disabled", Boolean()),
        Column("disable_date", DateTime()),
        Column("updated_at", DateTime()),
        Column("emailed", Boolean()),
        Column("validation_type_id", Integer()),
        sa.UniqueConstraint("control_id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.create_table(
        "sdq_config_checksum",
        Column("externalid", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        Column("config_name", String(length=100)),
        Column("checksum", String(length=256)),
        sa.PrimaryKeyConstraint("externalid"),
        if_not_exists=True,
        schema="ssdq_admin"
    )
    
    # op.execute(sa.schema.CreateSequence(Sequence('dq_control_sdim_seq', schema="ssdq"), if_not_exists=True))
    op.execute(sa.schema.CreateSequence(Sequence('dq_detailjournal_web__pm_workflow_run_id_seq', schema="ssdq"), if_not_exists=True))
    # op.execute(sa.schema.CreateSequence(Sequence('dq_detailjournal_web_seq', schema="ssdq"), if_not_exists=True))
    
    dump_path = Path(__file__).parent.parent.absolute() / 'sql/views.sql'

    with open(dump_path, 'r') as sqlreader:
        op.execute(text(sqlreader.read()))


def downgrade() -> None:
    pass
