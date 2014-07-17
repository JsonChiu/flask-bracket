"""Classy API view."""
import inspect
from .decorators import view
from flask.ext.classy import FlaskView
from werkzeug.routing import parse_rule

suffixes = ('Endpoint', 'View')


def route(rule=None, **options):
    """
    A decorator that is used to define custom routes for methods in FlaskView subclasses. The
    format is exactly the same as Flask's `@app.route` decorator. If ule is absent the name of the
    decorated function will be used.
    """
    options = options.copy()
    options.update({'rule': rule})

    def decorator(f):
        # Put the rule cache on the method itself instead of globally
        rule = options.pop('rule', None)
        if not rule:
            rule = '/{}/'.format(f.__name__)
        if not hasattr(f, '_rule_cache') or f._rule_cache is None:
            f._rule_cache = {f.__name__: [(rule, options)]}
        elif f.__name__ not in f._rule_cache:
            f._rule_cache[f.__name__] = [(rule, options)]
        else:
            f._rule_cache[f.__name__].append((rule, options))
        return f

    return decorator


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
        attrs['_meta'] = EndpointMeta(cls, attrs)
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
            route_base = cls.__name__
            for suffix in suffixes:
                if route_base.endswith(suffix):
                    route_base = route_base[:-len(suffix)]
                    break
            route_base = route_base.lower()

        return route_base.strip("/")
