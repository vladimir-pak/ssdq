from enum import Enum


class ControlStatus(Enum):
    DEVELOPMENT = 1 # Черновик
    EXPLOITATION = 2 # Эксплуатация
    ACTUALIZATION = 3 # Актуализация
    DISABLED = 4 # Отключен


class ControlStatusRu(Enum):
    DEVELOPMENT = "Черновик"
    EXPLOITATION = "Эксплуатация"
    ACTUALIZATION = "Актуализация"
    DISABLED = "Отключен"


class MonitoringFilter(Enum):
    ALL = "Все контроли"
    EXPLOITATION = "контроли в эксплуатации"
    ACTUALIZATION = "контроли на актуализации"
    DISABLED = "отключенные контроли"
    DEVELOPMENT = "черновик"
    USER = "Мои контроли"
    TEAM = "Контроли команды"
    EXPIRING = "Подходит срок актуализации"


class ValidationType(Enum):
    WARNING = 1 # Предупреждение о предстоящей актуализации
    DISABLED = 2 # Перевод в статус На актуализации
    EXPIRED = 3 # Истек срок актуализации


class critical_level(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


class AlertingType(Enum):
    ALWAYS = 1 # Всегда
    EXCEEDED = 2 # При превышении верхней границы
    NEVER = 3 # Никогда


class AlertingTypeRu(Enum):
    ALWAYS = "Всегда"
    EXCEEDED = "При превышении верхней границы"
    NEVER = "Никогда"


class JiraMode(Enum):
    SINGLE = 1 # Одиночный
    REGISTRY = 2 # Реестровый
    NEVER = 0 # Не создавать


class JiraModeRu(Enum):
    SINGLE = "Одиночный"
    REGISTRY = "Реестровый"
    NEVER = "Не создавать инцидент"


class DagType(Enum):
    SIMPLE = 1 # Простой
    CROSSDATABASE = 2 # Кросс-системный
    PATTERN = 3 # Шаблонизированный


class DagTypeRu(Enum):
    SIMPLE = "Простой"
    CROSSDATABASE = "Кросс-системный"
    PATTERN = "Шаблонизированный"


class DbType(Enum):
    POSTGRES = "POSTGRES"
    CLICKHOUSE = "CLICKHOUSE"
    IMPALA = "IMPALA"
    