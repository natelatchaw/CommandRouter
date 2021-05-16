import types
import inspect
from inspect import Signature, BoundArguments
from typing import Dict, List
from router.command import Command
from router.error.component import CommandAccessError, InvalidCommandError, InvalidInitializerError, ParameterMismatchError

class Component():

    def __init__(self, name: str, obj: object):
        # get the signature of the object's initializer
        initializer_signature: Signature = inspect.signature(obj.__init__)
        # if the initializer requires more parameters than self
        if len(initializer_signature.parameters) > 1:
            # raise error
            raise InvalidInitializerError(name)

        # set component name
        self.name = name
        # instantiate obj and store
        self.instance = obj()
        # instantiate commands dictionary
        self.commands: Dict[str, Signature] = dict()
        # get each method member in the class instance
        members = [member for member in inspect.getmembers(self.instance, inspect.ismethod)]
        # iterate over all methods in the class instance
        for name, member in members:
            # if method is a dunder method
            if name.startswith('__'):
                pass
            # otherwise
            else:
                # insert name, signature pair into commands dictionary
                self.commands[name] = Command(name, member)
        # get the docstring for the class
        self.doc = obj.__doc__

        print(f'Loaded {len(self.commands)} commands from {self.name} component.')

    def get_command_signature(self, command_name: str) -> Signature:
        """
        Retrieve a command signature from the component.

        Parameters:
            command_name: str - the command's name

        Throws:
            CommandAccessError - the component's commands dict doesn't contain an entry for command_name

        Note:
            Annotated types can be retreived from signatures, if available.
            for parameter in signature.parameters.values():
                print(parameter.annotation)
        """
        # try to get the signature from the commands dictionary
        try:
            command: Command = self.commands[command_name]
            return command.signature
        # if the component doesn't contain a command named 'command_name'
        except KeyError as keyError:
            raise CommandAccessError(self.name, command_name, keyError)

    def get_command_callable(self, command_name: str) -> types.MethodType:
        """
        Retrieve a command callable from the component.

        Parameters:
            command_name: str - the command's name
        """
        # try to get the command from the component instance
        try:
            return getattr(self.instance, command_name)
        # if the component doesn't contain a command named 'command_name'
        except AttributeError:
            raise InvalidCommandError(self.name, command_name)

    async def run_command(self, command_name: str, arguments: BoundArguments):
        """
        Run the command given the name and the arguments.
        """
        try:
            # get the command's callable
            command = self.get_command_callable(command_name)
            # the the command's signature
            signature = self.get_command_signature(command_name)
        # if the component doesn't contain a command named 'command_name'
        except InvalidCommandError:
            raise

        # if the provided arguments signature does not match
        if arguments.signature.parameters != signature.parameters:
            raise ParameterMismatchError(signature, arguments.signature)

        # if the called command is synchronous
        if Command.is_synchronous_method(command):
            # call command with parameters
            command(*arguments.args, **arguments.kwargs)

        # not supported yet
        if Command.is_asynchronous_method(command):
            await command(*arguments.args, **arguments.kwargs)