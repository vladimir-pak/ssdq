# import logging
import hashlib
from functools import wraps
from flask_login import current_user
from flask import request
import logging
# from ..app.extensions import logging.logger



class LogEvent:
    @staticmethod
    def log_checksum(filename:str, data:str) -> None:
        logging.info(f"eventName: checksum {filename}; message: {hashlib.md5(data.encode('utf-8')).hexdigest()}")

    @staticmethod
    def log_error(ex:Exception) -> None:
        tb = ex.__traceback__
        template = "An exception of type {0} occurred. Arguments: {1}. File: {2}. Row: {3}. Method: {4}"
        message = template.format(
            type(ex).__name__, 
            ex.args, 
            tb.tb_frame.f_code.co_filename,
            tb.tb_lineno,
            tb.tb_frame.f_code.co_name)
        logging.error(message)

    @staticmethod
    def log_warning(sUser:str=None, sUserId:int=None, route:str=None):
        logging.warning(
            f"eventName: permissionDenied; "\
            f"sUser: {current_user.login if sUser is None else sUser}; "\
            f"sUserId: {current_user.id if sUserId is None else sUserId}; "\
            f"route: {request.full_path if route is None else route}; message: permission denied; "\
            f"shost: {request.remote_addr}"
        )

    @staticmethod
    def log_event(**kwargs):
        try:
            constants = {
                "sUser": current_user.login,
                "sUserId": current_user.id,
                "sHost": request.remote_addr
            }
        except:
            constants = {"sHost": request.remote_addr}
        message = ""
        data = constants | kwargs
        for key, value in data.items():
            try:
                value = constants[key]
            except:
                pass
            message += f"{key}: {value}; "
        logging.info(message)


def log_route():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            LogEvent.log_event(
                eventName="logRoute",
                method=f"{request.method}",
                message=f"[{request.method}] {request.full_path}"
            )
            return f(*args, **kwargs)
        return decorated_function
    return decorator
