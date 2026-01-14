"""v4

Revision ID: add_limit_dag_sdim
Revises: alter_source_sdim
Create Date: 2025-10-14 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, Boolean


# revision identifiers, used by Alembic.
revision: str = 'add_limit_dag_sdim'
down_revision: Union[str, None] = 'alter_source_sdim'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dq_dag_sdim", Column("limit", Boolean), schema="ssdq")


def downgrade() -> None:
    op.drop_column("dq_dag_sdim", "limit", schema="ssdq")
    