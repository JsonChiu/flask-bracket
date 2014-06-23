"""Test the endpoint module."""
import common
from flask import abort
from flask.ext import bracket
from flask.ext.bracket import errors


class TestEndpoint(common.ViewTestCase):
    """Test the Endpoint class."""

    def create_view(self, app, serializer, response):
        """Create the endpoint to test. Return the path for the client to use."""
        class Test(bracket.Endpoint):
            def index(self):
                if response is None:
                    abort(500)
                if isinstance(response, int):
                    abort(response)
                if isinstance(response, Exception):
                    raise response
                return response

        Test.register(app, serializer=serializer)
        return '/test/'
