"""Encoder functions."""
import json
import sys
from .errors import Error
from flask import Response


class Serializer(object):
    """Base class for all API request/response serializers."""

    def __init__(self, app=None, **kwargs):
        """Initialize the serializer for the given app."""
        self.app = app

    def before_request(self, request):
        """
        Deserialize a request. On POST and PUT methods this will decode the request contents into
        request.bracket. On other methods request.bracket will be set to None. This method requires
        that request.stream has not already been drained. Raises Error on decode error.
        """
        raise NotImplementedError

    def after_request(self, request, response):
        """
        Serialize a response tuple into an object. The response must be a tuple containing the
        dictionary to serialize and as content and the status code to send. Return a Response
        object containing the serialized contents.
        """
        raise NotImplementedError


class JsonSerializer(Serializer):
    """JSON serializer."""
    default_content_type = 'application/json'

    def __init__(self, app, content_type=None):
        """Initialize the serializer. Use the provided `content_type` in responses."""
        super(JsonSerializer, self).__init__(app)
        self.content_type = content_type or self.default_content_type

    def before_request(self, request):
        """Deserialize request data as JSON."""
        if request.method in {'POST', 'PUT'}:
            try:
                request.bracket = request.get_json(force=True)
            except (TypeError, ValueError):
                self.app.log_exception(sys.exc_info())
                raise Error("unable to deserialize request", 400)
        else:
            request.bracket = None
        return request

    def after_request(self, request, response):
        """Serialize response data as JSON."""
        if not isinstance(response, (list, tuple)):
            response = (response,)
        try:
            if not isinstance(response[0], (list, tuple, dict)):
                msg = "unable to serialize type {}"
                raise TypeError(msg.format(response[0].__class__.__name__))
            content = json.dumps(response[0], indent=2)
            status = len(response) == 1 and 200 or response[1]
            return Response(content, status=status, content_type=self.content_type)
        except (TypeError, ValueError):
            self.app.log_exception(sys.exc_info())
            raise Error("unable to serialize response", 500)
