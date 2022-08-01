import inspect
import logging
from collections.abc import Mapping
from inspect import BoundArguments, Signature
from logging import Logger
from types import MethodType
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple, Type

from .command import Command

log: Logger = logging.getLogger(__name__)

class Component(Mapping[str, Command]):
    
    @property
    def name(self) -> str:
        return self._type.__name__

    @property
    def doc(self) -> str:
        if str.isspace(self._type.__doc__): return None
        return inspect.cleandoc(self._type.__doc__)

    @property
    def signature(self) -> Signature:
        return self._signature


    def __init__(self, obj: Type, *args, **kwargs):
        """
        Initialize a component via its type object.

        Raises:
        - ComponentInitializationError
            upon failing to bind to the component's initializer
        """

        # set the Type object
        self._type: Type = obj
        # get the type's initializer signature
        self._signature: Signature = inspect.signature(self._type.__init__)
        # bind the provided parameters to the signature
        try:
            self._arguments: BoundArguments = self._signature.bind(self, *args, **kwargs)
            # initialize the class object
            self._instance: Any = self._type(*self._arguments.args, **self._arguments.kwargs)
        # if an error occurred during binding
        except TypeError as error:
            raise ComponentInitializationError(self._type.__name__, error)
        # if the component raised an error during the __init__ call
        except Exception as error:
            raise ComponentInitializationError(self._type.__name__, error)
        # load all commands
        self._commands: Dict[str, Command] = dict()


    def load(self) -> None:
        """
        Initializes and stores instances of each method contained by the component
        as command instances
        """
        # get all method members of the instance
        members: List[Tuple[str, MethodType]] = inspect.getmembers(self._instance, inspect.ismethod)
        # filter members that start with a double underscore
        members: List[Tuple[str, MethodType]] = [(method_name, method_object) for method_name, method_object, in members if not method_name.startswith('__')]
        # for each member
        for method_name, method_object in members:
            # instantiate command
            command: Optional[Command] = self.__build_command__(method_object)
            # add command to dictionary
            if command: self._commands[command.name] = command


    def __build_command__(self, met: MethodType) -> Optional[Command]:
        try:
            # instantiate command
            command: Command = Command(met)
            # return the command
            return command
        except Exception as error:
            log.error(error)


    def __getitem__(self, key: str) -> Command:
        return self._commands.__getitem__(key)

    def __iter__(self) -> Iterator[str]:
        return self._commands.__iter__()

    def __len__(self) -> int:
        return self._commands.__len__()
        
        
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

