"""Test functionality for the package."""
import json
import traceback
import unittest
from StringIO import StringIO
from flask import Flask, abort
from flask.ext import bracket
from flask.ext.bracket.errors import Error, get_error_response
from flask.ext.bracket.serializers import JsonSerializer


class MockApp(object):
    """Mock Flask app."""

    def log_exception(self, e):
        """Print current exception."""
        traceback.print_exc()


class MockRequest(object):
    """Mock Flask request."""

    def __init__(self, data='', method='GET'):
        self.stream = StringIO(data)
        self.data = ''
        self.method = method


class MockSerializer(JsonSerializer):
    """Mock JsonSerializer that logs method calls."""

    def __init__(self, app):
        super(MockSerializer, self).__init__(app)
        self.reset()

    def before_request(self, request):
        self.before = request.data
        return super(self.__class__, self).before_request(request)

    def after_request(self, request, response):
        self.after = (request.data, response)
        return super(self.__class__, self).after_request(request, response)

    def reset(self):
        self.before = None
        self.after = (None, None)


class TestCase(unittest.TestCase):
    """Base test case."""

    def serialize(self, data):
        """JSON serialize data in an expected way."""
        return json.dumps(data, indent=2)


class SerializerTestCase(TestCase):
    """Base test case for serializers."""

    def setUp(self):
        self.app = MockApp()

    def assertBefore(self, serializer, method, data=None, want=None):
        """Validate a before_request call."""
        request = MockRequest(method=method, data=data)
        if isinstance(want, type) and issubclass(want, Exception):
            self.assertRaises(want, serializer.before_request, request)
        else:
            serializer.before_request(request)
            self.assertEqual(request.data, want)

    def assertAfter(self, serializer, data, want=None, request=None):
        """Validate an after_request call."""
        request = request or MockRequest()

        if isinstance(want, type) and issubclass(want, Exception):
            self.assertRaises(want, serializer.after_request, request, data)
        else:
            if not want:
                if not isinstance(data, (list, tuple)):
                    want = (self.serialize(data), 200)
                elif len(data) == 1:
                    want = (self.serialize(data[0]), 200)
                else:
                    want = (self.serialize(data[0]), data[1])
            response = serializer.after_request(request, data)
            self.assertEqual(response.status_code, want[1])
            self.assertEqual(response.data, want[0])


class ViewTestCase(TestCase):
    """Base test case for views."""

    def create_view(self, app, serializer, response):
        raise NotImplementedError

    def assertRequest(self, method, request, response, want):
        """Execute a request and check the results."""
        error = isinstance(response, Exception)
        want_status = len(want) and want[1] or 200
        want_content = self.serialize(want[0])

        app = Flask(__name__)
        app.config['TESTING'] = True
        serializer = MockSerializer(app)

        route = self.create_view(app, serializer, response)
        client_method = getattr(app.test_client(), method.lower())
        client_res = client_method(route)

        view_req, view_res = serializer.after
        self.assertEqual(client_res.status_code, want_status)
        self.assertEqual(client_res.data, want_content)
        if method == 'GET':
            self.assertIsNone(view_req)
        else:
            self.assertEqual(view_req, request)
        if isinstance(response, int):
            self.assertEqual(view_res[1], response)
        else:
            if isinstance(response, Exception):
                response = get_error_response(response)
            self.assertEqual(view_res, response)

    def test_get(self):
        """View Request"""
        response = {'status': 200, 'msg': 'success'}, 200
        self.assertRequest('GET', None, response, response)

    def test_error(self):
        """View Error"""
        error = Error('test error', 400)
        want = {'error': 'test error'}, 400
        self.assertRequest('GET', None, error, want)

    def test_abort(self):
        """View Abort"""
        error = 404
        want = {'error': 'Not Found'}, 404
        self.assertRequest('GET', None, error, want)

    def test_unknown_error(self):
        """View Unknown Error"""
        error = Exception('unknown error occurred')
        want = {'error': 'internal server error'}, 500
        self.assertRequest('GET', None, error, want)
