__version__ = "0.0.1"
from functools import update_wrapper


class LazyProperty(property):
    def __init__(self, method, fget=None, fset=None, fdel=None, doc=None):

        self.method = method
        self.cache_name = "_{}".format(self.method.__name__)

        doc = doc or method.__doc__
        super(LazyProperty, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

        update_wrapper(self, method)

    def __get__(self, instance, owner):

        if instance is None:
            return self

        if hasattr(instance, self.cache_name):
            result = getattr(instance, self.cache_name)
        else:
            if self.fget is not None:
                result = self.fget(instance)
            else:
                result = self.method(instance)

            setattr(instance, self.cache_name, result)

        return result


class LazyWritableProperty(LazyProperty):
    def __set__(self, instance, value):

        if instance is None:
            raise AttributeError

        if self.fset is None:
            setattr(instance, self.cache_name, value)
        else:
            self.fset(instance, value)
