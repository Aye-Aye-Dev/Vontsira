'''
Created on 23 Dec 2020

@author: si
'''
from flask import current_app, jsonify, make_response


class JsonException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, system_message=None):
        """
        @param status_code: integer
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

        if self.status_code >= 500:
            current_app.logger.error(message)

        if self.status_code >= 400 and self.status_code != 404:
            if system_message:
                current_app.logger.warning("Client error: " + system_message)
            else:
                current_app.logger.warning("Client error: " + message)

    def to_dict(self):
        rv = {'error': {'message': self.message}}
        return rv


class UserException(JsonException):
    pass


def handle_json_exception(error):
    if hasattr(error, 'to_dict') and hasattr(error, 'status_code'):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    elif hasattr(error, 'message'):
        response = jsonify({'msg': error.message})
        return response, 500
    else:
        response = jsonify({'msg': 'Unknown error'})
        return response, 500


def handle_user_exception(error):
    assert isinstance(error, UserException)
    response = make_response(str(error.to_dict()))
    return response, error.status_code
