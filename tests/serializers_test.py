"""Test the serializers module."""
import common 
import unittest
from flask import Flask
from flask.ext.bracket import Error, serializers


class TestSerializer(common.SerializerTestCase):
    """Test Serializer class."""

    def test_init(self):
        """Serializer.__init__"""
        serializer = serializers.Serializer(self.app, nope=None)
        self.assertTrue(serializer.app, self.app)

    def test_before_request(self):
        """Serializer.before_request"""
        serializer = serializers.Serializer(self.app)
        self.assertRaises(NotImplementedError, serializer.before_request, None)

    def test_after_request(self):
        """Serializer.after_request"""
        serializer = serializers.Serializer(self.app)
        self.assertRaises(NotImplementedError, serializer.after_request, None, None)


class TestJsonSerializer(common.SerializerTestCase):
    """Test JsonSerializer class."""

    def test_init(self):
        """JsonSerializer.__init__"""
        default_content_type = 'application/json'
        serializer = serializers.JsonSerializer(self.app)
        self.assertTrue(serializer.content_type, default_content_type)

        content_type = 'test/plain'
        serializer = serializers.JsonSerializer(self.app, content_type=content_type)
        self.assertTrue(serializer.content_type, content_type)

    def test_before_request(self):
        """JsonSerializer.before_request"""
        serializer = serializers.JsonSerializer(self.app)
        want = {'query': 'i would like a cat'}
        data = self.serialize(want)
        self.assertBefore(serializer, 'POST', data, want)
        self.assertBefore(serializer, 'GET')

        data = 'invalid json'
        self.assertBefore(serializer, 'POST', data, Error)

    def test_after_request(self):
        """Serializer.after_request"""
        serializer = serializers.JsonSerializer(self.app)

        data = {'status': 200, 'msg': 'meow!'}
        self.assertAfter(serializer, data)

        data = {'status': 200, 'msg': 'meow!'},
        self.assertAfter(serializer, data)

        data = {'status': 200, 'msg': 'meow!'}, 200
        self.assertAfter(serializer, data)

        data = {'status': 404, 'error': 'we could not find a cat'}, 404
        self.assertAfter(serializer, data)

        data = 'not a valid response', 500
        self.assertAfter(serializer, data, Error)
