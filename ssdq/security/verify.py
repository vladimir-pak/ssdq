from werkzeug.exceptions import BadRequest
import re


class InputValidator:
    environments = {
        'd': 'dev',
        't': 'test',
        'p': 'prod'
    }

    @staticmethod
    def get_validated_param(form, param_name, expected_type=str, required=True):
        """
        Validates and sanitizes input parameters from a form or query.
        
        Args:
            form: The form or query data from Flask request (e.g., request.form, request.args).
            param_name (str): The parameter name to validate.
            expected_type (type): The expected data type (default: str).
            required (bool): Whether the parameter is required (default: True).
        
        Returns:
            The validated and sanitized parameter value.
        
        Raises:
            BadRequest: If the parameter is missing or invalid.
        """
        value = form.get(param_name)
        if required and value is None:
            raise BadRequest(f"Missing required parameter: '{param_name}'")

        if value is not None:
            try:
                return expected_type(value)
            except ValueError:
                raise BadRequest(f"Invalid value for parameter '{param_name}'. Expected type: {expected_type.name}")

        return None
    
    @staticmethod
    def validate_vault_url(url:str, env:str, secret_type:str, path:str|None=None) -> bool:
        env = str(env)
        if env in list(InputValidator.environments.keys()):
            if secret_type == 'config':
                regex_pattern = re.compile(
                    r"^https://[a-zA-Z]*\S*:\d{2,5}/v1/secret_v2_" + env +
                    r"/data/sdq/" + (InputValidator.environments[env] if path is None else path) + r"/sdq"
                    r"/[a-zA-Z]*$", re.IGNORECASE
                )
            elif secret_type == 'secret':
                regex_pattern = re.compile(
                    r"^https://[a-zA-Z]*\S*:\d{2,5}/v1/secret_v2_" + env +
                    r"/data/sdq/" + (InputValidator.environments[env] if path is None else path) + r"/sdq"
                    r"/[a-zA-Z]*/(\w|/)*$", re.IGNORECASE
            )
            elif secret_type == 'login':
                regex_pattern = re.compile(
                    r"^https://[a-zA-Z]*\S*:\d{2,5}/v1/auth/approle_" + env +
                    r"_sdq/login$", re.IGNORECASE
                )
        else:
            return False
        return re.match(regex_pattern, url) is not None
    
    @staticmethod
    def validate_airflow_url(url:str) -> bool:
        regex_pattern = re.compile(
            r"^http(s|)://[a-zA-Z]*\S*(|:\d{2,5})/api/v1/sdq/\S*$", re.IGNORECASE
        )
        return re.match(regex_pattern, url) is not None

    @staticmethod
    def validate_jira_url(url:str) -> bool:
        regex_pattern = re.compile(
            r"^https://[a-zA-Z]*\S*/jira/rest/api/2/issue($|/\w*-\d*($|/?\S*$))", re.IGNORECASE
        )
        return re.match(regex_pattern, url) is not None
    
    @staticmethod
    def validate_jira_key(key:str) -> bool:
        regex_pattern = re.compile(
            r"^\w*-\d*$", re.IGNORECASE
        )
        return re.match(regex_pattern, key) is not None
    
    @staticmethod
    def validate_next_url(url:str, cur_host:str) -> bool:
        regex_pattern = re.compile(
            r"^http(s|)://" + cur_host, re.IGNORECASE
        )
        return re.match(regex_pattern, url) is not None
