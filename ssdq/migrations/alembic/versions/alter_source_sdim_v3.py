"""v3

Revision ID: alter_source_sdim
Revises: 20dc8e3d51be
Create Date: 2025-09-15 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision: str = 'alter_source_sdim'
down_revision: Union[str, None] = '20dc8e3d51be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dq_source_sdim", Column("dbtype", String(length=100)), schema="ssdq")
    op.add_column("dq_source_sdim", Column("sslmode", String(length=100)), schema="ssdq")


def downgrade() -> None:
    op.drop_column("dq_source_sdim", "dbtype", schema="ssdq")
    op.drop_column("dq_source_sdim", "sslmode", schema="ssdq")
    