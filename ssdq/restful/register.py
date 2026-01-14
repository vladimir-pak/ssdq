from flask_restful import Api
from ..auth.utils import UserJWT
from ..logger.api import RestLog
from ..controls.validation import PostValidate, ValidationEmailsRest
from ..controls.detailjournal import DetailJournalREST
from ..controls.alerting import AlertingREST
from ..integration.jira import JiraREST


def register_rest_api(api:Api) -> None:
    api.add_resource(UserJWT, '/api/auth')
    api.add_resource(RestLog, '/api/logs')
    api.add_resource(PostValidate, '/api/validation')
    api.add_resource(ValidationEmailsRest, '/api/validation/emails')
    api.add_resource(DetailJournalREST, '/api/detailjournal')
    api.add_resource(AlertingREST, '/api/alerting/emails')
    api.add_resource(JiraREST, '/api/jira')
    return None
