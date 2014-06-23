"""API errors."""
from werkzeug.exceptions import HTTPException


class Error(Exception):
    status = 500
    error = "internal server error"

    def __init__(self, error=None, status=None):
        """Create an API error with the given error and status code."""
        self.status = status or self.__class__.status
        self.error = error or self.__class__.error

    @property
    def response(self):
        """Return the error as a repsonse tuple."""
        return {'status': self.status, 'error': self.error}, self.status


def get_error_response(error):
    """Return an error as a response tuple."""
    if isinstance(error, HTTPException):
        error = Error(error.name, error.code)
    if not isinstance(error, Error):
        error = Error()
    return error.response
