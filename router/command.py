import inspect
from inspect import Signature
from types import MethodType

class Command():
    
    @classmethod
    def is_synchronous_method(cls, obj):
        return inspect.ismethod(obj) and not inspect.iscoroutinefunction(obj)

    @classmethod
    def is_asynchronous_method(cls, obj):
        return inspect.ismethod(obj) and inspect.iscoroutinefunction(obj)

    @property
    def signature(self) -> Signature:
        return inspect.signature(self._method)

    @property
    def method(self) -> MethodType:
        return self._method

    def __init__(self, name: str, obj: MethodType):
        self.name = name
        self._method = obj
        # get the command's docstring
        self.doc = obj.__doc__
