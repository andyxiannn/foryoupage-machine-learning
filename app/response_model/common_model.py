from enum import Enum
import json
from fastapi.responses import JSONResponse
from loguru import logger
from exceptions.common_exception import InvalidInputError, NotFoundError, SendRequestError, IncorrectCredentialsError, JwtError, ExistedError, VSYSError
from datetime import datetime
from decimal import Decimal
from enum import Enum
def my_dict(obj):
    if not  hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(my_dict(item))
        elif isinstance(val, datetime):
            element = val.strftime("%m/%d/%Y, %H:%M:%S")
        elif isinstance(val, Decimal):
            element = str(val)
        elif isinstance(val, Enum):
            element = val
        else:
            element = my_dict(val)
        result[key] = element
    return result
def dict_response(message):
    resp = []
    if isinstance(message, list):
        for item in message:
            resp.append(my_dict(item))
    else:
        resp = my_dict(message)
    return resp
def message_success_response(message):
    resp = dict_response(message)
    return JSONResponse(
        status_code = 200,
        content = {
            "status": "Success",
            "message": resp
        }
    )
def base_success_response():
    return JSONResponse(
        status_code = 200,
        content = {
            "status": "Success",
            "message": "success"
        }
    )
def not_found_error_response(error):
    return JSONResponse(
        status_code = 404,
        content = {
            "status" : "Not Found Error",
            "message" : error
        }
    )
def send_request_error_response(error):
    return JSONResponse(
        status_code = 503,
        content = {
            "status" : "Request to 3rd Party Error",
            "message" : error
        }
    )
def invalid_input_error_response(error):
    return JSONResponse(
        status_code = 422,
        content = {
            "status" : "Invalid Input Error",
            "message" : error
        }
    )
def incorrect_credentials_error_response(error):
    return JSONResponse(
        status_code = 401,
        content = {
            "status" : "Incorrect Credentials Error",
            "message" : error
        }
    )
def jwt_error_response(error):
    return JSONResponse(
        status_code = 401,
        content = {
            "status" : "JWT Error",
            "message" : error
        }
    )
def existed_error_response(error):
    return JSONResponse(
        status_code = 419,
        content = {
            "status" : "Existed Error",
            "message" : error
        }
    )
def vsys_error_response(error):
    return JSONResponse(
        status_code = 419,
        content = {
            "status" : "Vsys Error",
            "message" : error
        }
    )
def base_error_response(error):
    return JSONResponse(
        status_code = 500,
        content = {
            "status" : "Internal Server Error",
            "message" : error
        }
    )
def errorHandler(error):
    logger.error(error.args[0])
    if type(error) is NotFoundError:
        return not_found_error_response(error.args[0])
    elif type(error) is SendRequestError:
        return send_request_error_response(error.args[0])
    elif type(error) is InvalidInputError:
        return invalid_input_error_response(error.args[0])
    elif type(error) is IncorrectCredentialsError:
        return incorrect_credentials_error_response(error.args[0])
    elif type(error) is JwtError:
        return jwt_error_response(error.args[0])
    elif type(error) is ExistedError:
        return existed_error_response(error.args[0])
    elif type(error) is VSYSError:
        return vsys_error_response(error.args[0])
    else:
        return base_error_response(error.args[0])

def successHandler(message = ""):
    if message != "":
        return message_success_response(message)
    else:
        return base_success_response()