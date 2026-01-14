from ..models.base import dq_control_sdim, dq_control_object_stat, dq_control_owner_stat, \
    dq_dag_sdim, dq_alerting_stat, dq_dag_crossdb_sdim, dq_control_hist
from ..models.constants import DagType
from ..app.extensions import db
from ..integration.airflow import Dag
from .utils import to_cron
from uuid import UUID
from typing import Optional


class ControlDag:
    def __init__(self, control_id:int|str):
        self.control_id = control_id

    def _get_cron(self, **data) -> Optional[str]:
        try:
            cron_schedule = to_cron(
                data['select_sch'], 
                data['minute_select'],
                data['hour_select'], 
                data['time_hour_day_select'],
                data['time_minute_day_select'],
                data['time_hour_week_select'],
                data['time_minute_week_select'],
                data['day_of_week_select'],
                data['time_minute_month_select'],
                data['time_hour_month_select'],
                data['day_of_month_select']
            )
        except Exception:
            cron_schedule = None
        return cron_schedule if cron_schedule is not None else None

    def create(self) -> None:
        pass

    def update(self, **data) -> None:
        to_delete = dq_dag_sdim.query.filter_by(control_id=self.control_id).delete()
        db.session.commit()

        self.create(**data)

    def delete(self) -> None:
        to_delete = dq_dag_sdim.query.filter_by(control_id=self.control_id).update(
            dict(deleted_flag="Y")
        )
        db.session.commit()

    @staticmethod
    def deploy_dag(control_id:int|str):
        dag = Dag(str(control_id))
        return dag.deploy_dag()

    @staticmethod
    def delete_dag(control_id:int|str):
        dag = Dag(control_id)
        return dag.remove_dag()


class SimpleControl(ControlDag):
    def __init__(self, control_id:int|str):
        super().__init__(control_id)

    def create(self, data, cron:str=None) -> None:
        dag = dq_dag_sdim(
            control_id=self.control_id,
            sql=data["sql_query"],
            cron=cron if cron else self._get_cron(data),
            source=str(UUID(data["source"])),
            dag_type=DagType.SIMPLE.value,
            limit=data['limit']
        )
        db.session.add(dag)
        db.session.commit()


class CrossDbControl(ControlDag):
    def __init__(self, control_id:int|str):
        super().__init__(control_id)

    def create(self, data, cron:str=None) -> None:
        dag = dq_dag_sdim(
            control_id=self.control_id,
            dag_type=DagType.CROSSDATABASE.value,
            sql=data['main_query'],
            params=data['params'],
            cron=cron if cron else self._get_cron(data),
            limit=data['limit']
        )
        db.session.add(dag)
        db.session.commit()


class PatternControl(ControlDag):
    def __init__(self, control_id:int|str):
        super().__init__(control_id)

    def create(self, data, cron:str=None) -> None:
        dag = dq_dag_sdim(
            control_id=self.control_id,
            cron=cron if cron else self._get_cron(data),
            source=str(UUID(data["source_pattern"])),
            dag_type=DagType.PATTERN.value,
            pattern_id=data["pattern_id"],
            params=data['params'],
            limit=data['limit']
        )
        db.session.add(dag)
        db.session.commit()


class ControlDagMap:
    def __init__(self):
        pass

    @staticmethod
    def get_dag_class(dag_type:DagType, control_id:int|str) -> ControlDag:
        _class_name = {
            DagType.SIMPLE: SimpleControl,
            DagType.CROSSDATABASE: CrossDbControl,
            DagType.PATTERN: PatternControl
        }
        if dag_type not in _class_name:
            raise ValueError(f"Invalid Dag type: {dag_type}")
        return _class_name[dag_type](control_id)
    