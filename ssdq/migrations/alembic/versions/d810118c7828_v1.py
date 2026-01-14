"""v1

Revision ID: d810118c7828
Revises: 39a07e5d0376
Create Date: 2025-07-22 20:06:39.038358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd810118c7828'
down_revision: Union[str, None] = '39a07e5d0376'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dq_source_sdim", sa.Column("host", sa.String(length=100)), schema="ssdq")
    op.add_column("dq_source_sdim", sa.Column("port", sa.Integer), schema="ssdq")
    op.add_column("dq_source_sdim", sa.Column("db_name", sa.String(length=100)), schema="ssdq")


def downgrade() -> None:
    op.drop_column("dq_source_sdim", "host", schema="ssdq")
    op.drop_column("dq_source_sdim", "port", schema="ssdq")
    op.drop_column("dq_source_sdim", "db_name", schema="ssdq")
