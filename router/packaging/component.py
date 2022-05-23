import inspect
from inspect import BoundArguments, Signature
from logging import Logger
import logging
from types import MethodType
from typing import Any, Dict, List, Optional, Tuple, Type

from .command import Command

log: Logger = logging.getLogger(__name__)

class Component():

    def __init__(self, obj: Type, *args, **kwargs):
        """
        Initialize a component via its type object.

        Raises:
        - ComponentInitializationError          upon failing to bind to the component's initializer
        """

        # set the Type object
        self._type: Type = obj
        # get the type's initializer signature
        self._signature: Signature = inspect.signature(self._type.__init__)
        # bind the provided parameters to the signature
        try:
            self._arguments: BoundArguments = self._signature.bind(self,*args, **kwargs)
        # if an error occurred during binding
        except TypeError as error:
            raise ComponentInitializationError(self._type.__name__, error)
        # initialize the class object
        self._instance: Any = self._type(self._arguments.args, self._arguments.kwargs)
        # load all commands
        self._commands: Dict[str, Command] = self.load()
    
    @property
    def name(self) -> str:
        return self._type.__name__

    @property
    def signature(self) -> Signature:
        return self._signature
    
    @property
    def doc(self) -> str:
        return self._type.__doc__

    @property
    def commands(self) -> Dict[str, Command]:
        return self._commands

    def load(self) -> Dict[str, Command]:
        # get all method members of the instance
        members: List[Tuple[str, MethodType]] = inspect.getmembers(self._instance, inspect.ismethod)
        # filter members that start with a double underscore
        members: List[Tuple[str, MethodType]] = [(method_name, method_object) for method_name, method_object, in members if not method_name.startswith('__')]
        # instantiate dictionary
        commands: Dict[str, Command] = dict()
        # for each member
        for method_name, method_object in members:
            try:
                # instantiate command
                command: Command = Command(method_object)
                # add command to dictionary
                commands[command.name] = command
            except Exception as error:
                log.error(error)
        # return dictionary
        return commands



class ComponentError(Exception):
    """Base exception class for component related errors."""

    def __init__(self, message: str, exception: Optional[Exception] = None) -> None:
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message
        

class ComponentInitializationError(ComponentError):
    """Raised when an exception occurs when intitializing a component."""

    def __init__(self, component_name: str, exception: Optional[Exception] = None) -> None:
        message: str = f'Failed to initialize component {component_name}: {exception}'
        super().__init__(message, exception)

