import inspect
from inspect import BoundArguments, Signature
from types import MethodType

from router.error.component import ParameterMismatchError


class Command():
    
    @property
    def name(self) -> str:
        return self._method.__name__

    @property
    def signature(self) -> Signature:
        return self._signature
    
    @property
    def doc(self) -> str:
        return self._method.__doc__

    def __init__(self, obj: MethodType) -> None:
        """Initialize a Command via its MethodType object."""

        # if the object is not a method
        if not inspect.ismethod(obj): raise TypeError(f'{obj.__name__} cannot be called as a method.')
        # set the MethodType object
        self._method: MethodType = obj
        # get the method's signature
        self._signature: Signature = inspect.signature(self._method)

    async def run(self, arguments: BoundArguments) -> None:
        """"""

        # if the provided arguments do not match the command arguments
        if self._signature.parameters != arguments.signature.parameters:
            raise ParameterMismatchError(self._signature, arguments.signature)
        
        if not inspect.iscoroutinefunction(self._method):
            self._method(*arguments.args, **arguments.kwargs)

        elif inspect.iscoroutinefunction(self._method):
            await self._method(*arguments.args, **arguments.kwargs)
















class CommandOld():
    
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
