from __future__ import print_function, absolute_import


class BaseObject(object):

    _instance = None
    _subcls = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if cls._subcls is None:
            raise ValueError('BaseObject: subcls cannot be None!')

        if cls._instance is None:
            cls._instance = cls._subcls(*args, **kwargs)

        return cls._instance

    @classmethod
    def register(cls, subcls):
        if cls._subcls is not None:
            raise Exception('BaseObject: subcls has already been defined! %s' % str(cls._subcls))

        cls._subcls = subcls
        subcls.instance = cls.instance
        return subcls

    @classmethod
    def unregister(cls):
        cls._subcls = None
        cls._instance = None


class BaseObjectMultiple(object):

    _instance = {}
    _subcls = {}

    @classmethod
    def instance(cls, name, *args, **kwargs):
        if name not in cls._subcls:
            raise ValueError('BaseObjectMultiple: subcls not defined for %s!' % name)

        if name not in cls._instance:
            cls._instance[name] = cls._subcls[name](*args, **kwargs)

        return cls._instance[name]

    @classmethod
    def register(cls, subcls, name):
        cls._subcls[name] = subcls
        subcls.instance[name] = cls.instance
        return subcls

    @classmethod
    def unregister(cls, name):
        try:
            del cls._subcls[name]
        except KeyError:
            pass

        try:
            del cls._instance[name]
        except KeyError:
            pass


def baseobject(name=None):

    class _BaseObject(object):

        _instance = None
        _subcls = None

        @classmethod
        def instance(cls, *args, **kwargs):
            if cls._subcls is None:
                raise ValueError('BaseObject: subcls cannot be None!')

            if cls._instance is None:
                cls._instance = cls._subcls(*args, **kwargs)

            return cls._instance

        @classmethod
        def register(cls, subcls):
            if cls._subcls is not None:
                raise Exception('BaseObject: subcls has already been defined! %s' % str(cls._subcls))

            cls._subcls = subcls
            subcls.instance = cls.instance
            return subcls

        @classmethod
        def unregister(cls):
            cls._subcls = None
            cls._instance = None

    if isinstance(name, str):
        _BaseObject.__name__ = name

    return _BaseObject
