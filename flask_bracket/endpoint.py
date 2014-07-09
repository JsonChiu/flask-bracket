"""Classy API view."""
import inspect
from .decorators import view
from flask.ext.classy import FlaskView

suffixes = ('Endpoint', 'View')


class EndpointMeta(object):
    """Endpoint metadata class."""

    def __init__(self, cls, attrs):
        """Initialize the endpoint metadata."""
        self.views = [k for k, v in attrs.iteritems() if self.is_view(v)]

    def is_view(self, method):
        """Returns a list of methods that can be routed to"""
        return (inspect.isfunction(method) and
                not method.__name__.startswith("_") and
                not method.__name__.startswith("before_") and
                not method.__name__.startswith("after_"))

    def decorate(self, endpoint, app, serializer):
        """Decorate all view methods on an endpoint."""
        for name in self.views:
            decorator = view(app=app, serializer=serializer)
            method = getattr(endpoint, name)
            setattr(endpoint, name, decorator(method))


class EndpointBuilder(type):
    """Create an API class view."""

    def __new__(cls, name, bases, attrs):
        cls._meta = EndpointMeta(cls, attrs)
        return type.__new__(cls, name, bases, attrs)


class Endpoint(FlaskView):
    """Classy API view."""
    __metaclass__ = EndpointBuilder

    @classmethod
    def register(cls, app, serializer=None, **kwargs):
        """Register the view."""
        cls._meta.decorate(cls, app, serializer)
        super(Endpoint, cls).register(app, **kwargs)

    @classmethod
    def get_route_base(cls):
        """Returns the route base to use for the current class."""
        if cls.route_base is not None:
            route_base = cls.route_base
            base_rule = parse_rule(route_base)
            cls.base_args = [r[2] for r in base_rule]
        else:
            for suffix in suffixes:
                if cls.__name__.endswith(suffix):
                    route_base = cls.__name__[:-len(suffix)]
                    break
            route_base = route_base.lower()

        return route_base.strip("/")
