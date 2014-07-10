"""View decorators."""
from .errors import Error, get_error_response
from .serializers import JsonSerializer
from flask import current_app, request
from werkzeug.exceptions import HTTPException


def view(func=None, app=None, serializer=None, **kwargs):
    """
    Decorate a view with API functionality. By default Uses `flask.current_app` as the app instance
    and `JsonSerializer` as the serializer. These may be overridden with the `app` and `serializer`
    keyword parameters.
    """
    app = app or current_app
    serializer = serializer or JsonSerializer(app)

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                serializer.before_request(request)
                response = func(*args, **kwargs)
            except (Error, HTTPException) as e:
                response = get_error_response(e)
            except Exception as e:
                app.log_exception(e)
                response = get_error_response(e)
            return serializer.after_request(request, response)

        wrapper.__name__ = func.__name__
        if hasattr(func, '_rule_cache'):
            setattr(wrapper, '_rule_cache', func._rule_cache)
        return wrapper

    if func:
        return decorator(func)
    return decorator
