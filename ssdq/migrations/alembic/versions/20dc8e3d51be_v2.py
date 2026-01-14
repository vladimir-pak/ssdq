"""v2

Revision ID: 20dc8e3d51be
Revises: d810118c7828
Create Date: 2025-08-14 18:19:02.010486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, JSON, Text, String, DateTime
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20dc8e3d51be'
down_revision: Union[str, None] = 'd810118c7828'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dq_dag_sdim", Column("dag_type", Integer), schema="ssdq")
    op.add_column("dq_dag_sdim", Column("params", JSON), schema="ssdq")
    op.add_column("dq_dag_sdim", Column("pattern_id", UUID(as_uuid=True)), schema="ssdq")

    dq_pattern_sdim = op.create_table(
        "dq_pattern_sdim",
        Column("id", UUID(as_uuid=True)),
        Column("name", String(length=100), nullable=False),
        Column("description", String(length=400)),
        Column("sql", Text()),
        Column("params", JSON),
        Column("team_id", UUID(as_uuid=True)),
        Column("updated_at", DateTime()),
        Column("deleted_flag", String(length=1)),
        sa.UniqueConstraint("name", "team_id"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
        schema="ssdq"
    )

    # Миграция кросс-системных контролей
    op.execute("""update ssdq.dq_dag_sdim
        set dag_type = case when crossdb_flag = 'Y' then 2 else 1 end""")

    op.execute("""update ssdq.dq_dag_sdim dag
	set params = tt.params,
		"sql" = tt.main_sql
	from (
		select cr.control_id
			, json_agg(
				json_build_object(
					'source', cr."source",
					'source_name', cr.custom_source_name,
					'sql', cr."sql"
				) 
			) as params
			, cr2."sql" as main_sql
		from ssdq.dq_dag_crossdb_sdim cr
		left join ssdq.dq_dag_crossdb_sdim cr2
			on cr.control_id = cr2.control_id 
			and cr2.main_sql = 'Y'
		where cr.main_sql != 'Y'
		group by cr.control_id, cr2."sql"
	) tt
	where dag.crossdb_flag = 'Y'
	and dag.control_id = tt.control_id""")


def downgrade() -> None:
    op.drop_column("dq_dag_sdim", "dag_type", schema="ssdq")
    op.drop_column("dq_dag_sdim", "params", schema="ssdq")
    op.drop_column("dq_dag_sdim", "pattern_id", schema="ssdq")
    op.drop_table("dq_pattern_sdim", schema="ssdq")
    