"""v7

Revision ID: version_7
Revises: version_6
Create Date: 2026-01-23 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'version_7'
down_revision: Union[str, None] = 'version_6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dq_team_attributes_dim = op.create_table(
        "dq_team_attributes_dim",
        Column("id", UUID(as_uuid=True)),
        Column("name", String(length=100), nullable=False),
        Column("description", String(length=400)),
        Column("is_required", Boolean),
        Column("team_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("name", "team_id"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.add_column("dq_control_sdim", Column("team_attributes", JSON), schema="ssdq")
    op.add_column("dq_control_hist", Column("team_attributes", JSON), schema="ssdq")
    op.add_column("dq_control_sdim", Column("characteristic_id", UUID(as_uuid=True)), schema="ssdq")
    op.add_column("dq_control_hist", Column("characteristic_id", UUID(as_uuid=True)), schema="ssdq")


def downgrade() -> None:
    op.drop_table("dq_team_attributes_dim", schema="ssdq")
    
    op.drop_column("dq_control_sdim", "team_attributes", schema="ssdq")
    op.drop_column("dq_control_hist", "team_attributes", schema="ssdq")
    op.drop_column("dq_control_sdim", "characteristic_id", schema="ssdq")
    op.drop_column("dq_control_hist", "characteristic_id", schema="ssdq")
    