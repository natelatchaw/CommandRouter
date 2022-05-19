import inspect
from inspect import BoundArguments, Signature
from types import MethodType
from typing import Any, Dict, List, Tuple, Type

from router.command import Command
from router.error.component import InvalidInitializerError


class Component():
    
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
        # get all method members of the instance
        members: List[Tuple[str, MethodType]] = inspect.getmembers(self._instance, inspect.ismethod)
        # filter members that start with a double underscore
        members: List[Tuple[str, MethodType]] = [(method_name, method_object) for method_name, method_object, in members if not method_name.startswith('__')]
        # create command from each member
        commands: List[Command] = [Command(method_object) for method_name, method_object in members]
        # return assembled dictionary
        return dict([(command.name, command) for command in commands])


    def __init__(self, obj: Type, *args, **kwargs):
        """Initialize a Component via its Type object."""

        # set the Type object
        self._type: Type = obj
        # get the type's initializer signature
        self._signature: Signature = inspect.signature(self._type.__init__)
        # bind the provided parameters to the signature
        try: self._arguments: BoundArguments = self._signature.bind(self,*args, **kwargs)
        # if an error occurred during binding
        except TypeError: raise #InvalidInitializerError(self.name)
        # initialize the class object
        self._instance: Any = self._type(self._arguments.args, self._arguments.kwargs)
