"""Test the decorators module."""
import common
from flask import Flask, abort
from flask.ext import bracket
from flask.ext.bracket import errors
from werkzeug.exceptions import HTTPException


class TestView(common.ViewTestCase):
    """Test the view decorator."""

    def create_view(self, app, serializer, response):
        """Create the view to test. Return the path for the client to use."""
        route = '/'
        @app.route(route)
        @bracket.view(app=app, serializer=serializer)
        def view():
            if response is None:
                abort(500)
            if isinstance(response, int):
                abort(response)
            if isinstance(response, Exception):
                raise response
            return response
        return route


class TestViewDefault(common.TestCase):
    """Test the default view decorator."""

    def test_default(self):
        """View Defaults"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        client = app.test_client()
        response = {'status': 200, 'msg': 'success'}, 200
        want = self.serialize(response[0])

        @app.route('/')
        @bracket.view
        def view():
            return response

        client_res = client.get('/')
        self.assertEqual(client_res.status_code, 200)
        self.assertEqual(client_res.data, want)
