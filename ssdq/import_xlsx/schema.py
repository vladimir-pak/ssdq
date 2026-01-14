from ..models.constants import critical_level, \
    AlertingType, JiraMode, DagType


# Допустимые значения из справочников
critical_levels = [cur.name for cur in critical_level]
alerting_types = [cur.name for cur in AlertingType]
jira_modes = [cur.name for cur in JiraMode]
dag_types = [cur.name for cur in DagType]


# Схема для создания контролей
CONTROL_SCHEMA = {
    "type": "object",
    "properties": {
        "control_name": {"type": "string", "maxLength": 250, "minLength": 1},
        "description": {"type": "string", "maxLength": 500, "minLength": 1},
        "conditions": {"type": "string", "maxLength": 500, "minLength": 1},
        "segment": {"type": "string", "minLength": 1},
        "source": {"type": "string", "minLength": 1},
        "wiki": {"type": "string"},
        "threshold_min": {"type": "integer", "minLength": 1},
        "threshold_max": {"type": "integer", "minLength": 1},
        "control_type": {"type": "string", "minLength": 1},
        "subject_area": {"type": "string"},
        "critical_level": {"type": "string", "enum": critical_levels},
        "alerting_type": {"type": "string", "enum": alerting_types},
        "jira_mode": {"type": "string", "enum": jira_modes},
        "dag_type": {"type": "string", "enum": dag_types},
        "owner": {"type": "string"},
        "mail_list": {"type": "string"},
        "objects": {"type": "string", "minLength": 1},
        "sql_query": {"type": "string"},
        "main_query": {"type": "string"},
        "cron": {"type": "string"},
        "pattern": {"type": "string"},
        "params": {"type": "string"},
        "tags": {"type": "string"}
    },
    "required": [
        "control_name", 
        "description",
        "conditions",
        "segment",
        "source",
        "threshold_min",
        "threshold_max",
        "control_type",
        "critical_level",
        "alerting_type",
        "jira_mode",
        "dag_type",
        "objects"
    ],
    "additionalProperties": True
}


CROSSDB_PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "source": {"type": "string", "minLength": 1},
        "source_name": {"type": "string", "minLength": 1},
        "sql": {"type": "string", "minLength": 1}
    },
    "required": [
        "source", 
        "source_name",
        "sql"
    ],
    "additionalProperties": True
}
