import inspect
import logging
from inspect import BoundArguments, Signature
from logging import Logger
from types import MethodType
from typing import Optional

from .component import Component

log: Logger = logging.getLogger(__name__)

class Command():
    
    @property
    def name(self) -> str:
        return self._method.__name__
    
    @property
    def doc(self) -> str:
        return self._method.__doc__

    @property
    def signature(self) -> Signature:
        return self._signature
        

    def __init__(self, obj: MethodType) -> None:
        """
        Initialize a command via its MethodType object.
        """

        # if the object is not a method
        if not inspect.ismethod(obj): raise TypeError(f'{obj.__name__} cannot be called as a method.')
        # set the MethodType object
        self._method: MethodType = obj
        # get the method's signature
        self._signature: Signature = inspect.signature(self._method)


    async def run(self, arguments: BoundArguments) -> None:
        """
        Run the command via provided BoundArguments.

        Raises:
        - SignatureMismatchException
            upon failure to provide matching command arguments
        """

        # if the provided arguments do not match the command arguments
        if arguments.signature.parameters != self._signature.parameters:
            raise SignatureMismatchException(arguments.signature, self._signature)
        if not inspect.iscoroutinefunction(self._method):
            self._method(*arguments.args, **arguments.kwargs)
        elif inspect.iscoroutinefunction(self._method):
            await self._method(*arguments.args, **arguments.kwargs)


class CommandError(Exception):
    """Base exception class for command related errors."""

    def __init__(self, message: str, exception: Optional[Exception] = None) -> None:
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message
        

class SignatureMismatchException(CommandError):
    """Raised when an exception occurs when binding command arguments."""

    def __init__(self, provided_signature: Signature, target_signature: Signature, exception: Optional[Exception] = None) -> None:
        message: str = f'Incompatible signature provided; received {provided_signature}, expected {target_signature}'
        super().__init__(message, exception)
