"""v5

Revision ID: add_tags
Revises: add_limit_dag_sdim
Create Date: 2025-11-28 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'add_tags'
down_revision: Union[str, None] = 'add_limit_dag_sdim'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    tags = op.create_table(
        "tags",
        Column("id", UUID(as_uuid=True)),
        Column("name", String(length=100), nullable=False),
        Column("description", String(length=400)),
        Column("team_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("name", "team_id"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )

    control_tags = op.create_table(
        "dq_control_tags_stat",
        Column("control_id", Integer()),
        Column("tag_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("control_id", "tag_id"),
        if_not_exists=True,
        schema="ssdq"
    )


def downgrade() -> None:
    op.drop_table("tags", schema="ssdq")
    op.drop_table("dq_control_tags_stat", schema="ssdq")
    