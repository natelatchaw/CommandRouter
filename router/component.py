import logging
import inspect
from inspect import Signature, BoundArguments
from types import MethodType
from typing import Any, Dict, List, Tuple, AnyStr
from router.command import Command
from router.error.component import ComponentAccessError, InvalidCommandError, InvalidInitializerError, ParameterMismatchError

class Component():
    """
    A container representation for a group of commands.
    """

    def __init__(self, name: str, obj: type):
        # get the signature of the type's initializer
        initializer_signature: Signature = inspect.signature(obj.__init__)
        # if the initializer requires parameters other than self
        if len(initializer_signature.parameters) > 1:
            # raise error
            raise InvalidInitializerError(name)

        # set component name
        self.name: str = name
        logging.debug('%s component: beginning initialization', self.name)
        # get the docstring for the class
        self.doc: str = obj.__doc__
        # instantiate obj and store
        self.instance: Any = obj()
        logging.debug('%s component: initialized instance with ID %s', self.name, id(self.instance))
        # populate commands dictionary
        self.commands: List[Command] = self.package()
        logging.debug('%s component: initialized command dictionary', self.name)
        
        # TODO: REMOVE self.commands: Dict[str, Signature] = dict()


    def package(self) -> List[Command]:
        """
        """

        logging.debug('%s component: beginning command search', self.name)
        # get each method member in the class instance
        members: List[Tuple[str, MethodType]] = [member for member in inspect.getmembers(self.instance, inspect.ismethod)]
        logging.debug('%s component: found %s available members', self.name, len(members))
        logging.debug('%s module: beginning command initialization process', self.name)
        # initialize command from each member
        commands: List[Command] = [Command(name, method_object) for name, method_object in members if not name.startswith('__')]
        logging.debug('%s component: found %s commands', self.name, len(commands))
        # return command list
        return commands


    def get_command(self, command_name: str) -> Command:
        """
        Retrieve a command's signature from the component.

        Parameters:
            command_name: str - the name of the command

        Throws:
            CommandAccessError - if the command list does not contain exactly one matching command
        """
        
        # find commands matching the provided command_name
        commands: List[Command] = [command for command in self.commands if command.name == command_name]
        
        # if exactly one command was found
        if len(commands) == 1:
            # return the command's signature
            return commands[0]

        # if zero or many commands were found
        else:
            # raise an error
            raise ComponentAccessError(self.name, command_name, f'{len(commands)} commands found for \'{command_name}\'')


        # try to get the command from the component instance
        try:
            return getattr(self.instance, command_name)
        # if the component doesn't contain a command named 'command_name'
        except AttributeError:
            raise InvalidCommandError(self.name, command_name)


    async def run_command(self, command_name: str, arguments: BoundArguments):
        """
        Run the command given the name and the arguments.

        Throws:
            - CommandAccessError: if the target command could not be determined.
            - ParameterMismatchError: if invalid parameters are provided to the target command.
        """
        
        # get the command
        command: Command = self.get_command(command_name)

        # if the provided arguments signature does not match
        if arguments.signature.parameters != command.signature.parameters:
            raise ParameterMismatchError(command.signature, arguments.signature)

        # if the called command is synchronous
        if Command.is_synchronous_method(command.method):
            # call command with parameters
            command.method(*arguments.args, **arguments.kwargs)

        # if the called command is synchronous
        if Command.is_asynchronous_method(command.method):
            # call command with parameters
            await command.method(*arguments.args, **arguments.kwargs)