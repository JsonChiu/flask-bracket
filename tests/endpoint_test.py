"""Test the endpoint module."""
import common
from flask import abort
from flask.ext import bracket
from flask.ext.bracket import errors


def create_endpoint(response, name, route_base=None):
    """Create a endpoint view with the given name and optional `route_base`."""
    def index(self):
        if response is None:
            abort(500)
        if isinstance(response, int):
            abort(response)
        if isinstance(response, Exception):
            raise response
        return response

    attrs = {'index': index}
    if route_base:
        attrs['route_base'] = route_base

    return type(name, (bracket.Endpoint,), attrs)


class TestEndpointSuffix(common.ViewTestCase):
    """Test an Endpoint class with 'Endpoint' suffix."""

    def create_view(self, app, serializer, response):
        endpoint = create_endpoint(response, 'TestEndpoint')
        endpoint.register(app, serializer=serializer)
        return '/test/'

class TestViewSuffix(common.ViewTestCase):
    """Test an Endpoint class with 'View' suffix."""

    def create_view(self, app, serializer, response):
        endpoint = create_endpoint(response, 'TestView')
        endpoint.register(app, serializer=serializer)
        return '/test/'


class TestNoSuffix(common.ViewTestCase):
    """Test an Endpoint class with no suffix."""

    def create_view(self, app, serializer, response):
        endpoint = create_endpoint(response, 'Test')
        endpoint.register(app, serializer=serializer)
        return '/test/'


class TestRouteBase(common.ViewTestCase):
    """Test an Endpoint class with a route base."""

    def create_view(self, app, serializer, response):
        endpoint = create_endpoint(response, 'TestEndpoint', 'my_test_endpoint')
        endpoint.register(app, serializer=serializer)
        return '/my_test_endpoint/'
