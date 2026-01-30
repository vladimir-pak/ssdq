"""v6

Revision ID: version_6
Revises: add_tags
Create Date: 2026-01-22 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


# revision identifiers, used by Alembic.
revision: str = 'version_6'
down_revision: Union[str, None] = 'add_tags'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dq_characteristic_sdim = op.create_table(
        "dq_characteristic_sdim",
        Column("id", UUID(as_uuid=True)),
        Column("name", String(length=100), nullable=False),
        Column("description", String(length=400)),
        Column("updated_at", DateTime()),
        sa.UniqueConstraint("name"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )
    
    op.bulk_insert(
        dq_characteristic_sdim,
        [
            {
                "id": uuid4(),
                "name": "Полнота",
                "description": "Полнота"
            },
            {
                "id": uuid4(),
                "name": "Актуальность",
                "description": "Актуальность"
            },
            {
                "id": uuid4(),
                "name": "Согласованность",
                "description": "Согласованность"
            },
            {
                "id": uuid4(),
                "name": "Точность и достоверность",
                "description": "Точность и достоверность"
            },
            {
                "id": uuid4(),
                "name": "Уникальность",
                "description": "Уникальность"
            },
            {
                "id": uuid4(),
                "name": "Целостность",
                "description": "Целостность"
            },
        ]
    )
    
    op.add_column("tags", Column("tag_type", String(length=50)), schema="ssdq")
    op.add_column("dq_control_type_sdim", Column("team_id", UUID(as_uuid=True)), schema="ssdq")


def downgrade() -> None:
    op.drop_table("dq_characteristic_sdim", schema="ssdq")
    op.drop_column("tags", "tag_type", schema="ssdq")
    op.drop_column("dq_control_type_sdim", "team_id", schema="ssdq")
    