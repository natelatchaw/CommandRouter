from logging import Logger
import logging
import re
from inspect import BoundArguments
from pathlib import Path
from typing import Any, Callable, Dict, List, Match, Pattern

from router.packaging import Command, Component, Package, CommandError


class Handler():

    def __init__(self):
        self._logger: Logger = logging.getLogger(__name__)
        # initialize the registry
        self._registry: Dict[str, Entry] = dict()
        # initialize the package dictionary
        self._packages: Dict[str, Package] = dict()
        

    def load(self, directory: Path, extension: str = 'py'):
        """
        Load package files from a directory.
        Failed package assemblies are logged as warning messages.

        Raises:
        - HandlerLoadError          if the provided directory does not exist
        """

        # resolve the provided directory path
        directory: Path = directory.resolve()
        self._logger.debug('Resolved provided directory to %s', directory)

        # if the provided directory doesn't exist
        if not directory.exists(): raise HandlerLoadError(directory)

        # get all paths for files in the provided directory
        pattern: str = f'*.{extension}'
        references: List[Path] = [reference for reference in directory.glob(pattern) if reference.is_file()]
        self._logger.debug('Found %s %s files in %s', len(references), extension, str(directory))

        for reference in references:
            try:
                package: Package = Package(reference)
                for component in package.components.values():
                    for command in component.commands.values():
                        self._registry[command.name] = Entry(package.name, component.name, command.name)
            except ImportError as error:
                self._logger.warn('Package assembly failed for file %s: %s', reference.name, error)
            except Exception as error:
                self._logger.error(error)
            else:
                self._packages[package.name] = package

    async def process(self, prefix: str, message: str, *, optionals: Dict[str, Any] = dict(), filter: Callable[[List[str]], List[str]] = None) -> None:
        """
        Process a message, parsing it for:
        - a primary command name
        - delimited parameters key value pairs

        Raises:
            - TypeError                 upon invalid message type provided
            - HandlerExecutionError     upon failure to bind command arguments or a parameter mismatch
            - HandlerLookupError        upon failure to lookup command object from the registry
        """
        # filter non-string message parameters
        if not isinstance(message, str): raise TypeError(f'Expected type {type(str)}; received type {type(message)}')

        command_prefix: str = prefix
        # get command from message
        command_match: Match = re.match(rf'^{command_prefix}[\w]+', message)
        # if the prefixed command could not be found at the beginning of the message
        if not command_match: raise HandlerPrefixError(prefix)
        # get the prefixed command string from the match
        prefixed_command: str = command_match.group()
        # remove prefix from command
        command_name: str = re.sub(rf'^{command_prefix}', '', prefixed_command)

        parameter_prefix: str = '-'
        # compile regex for parameter/argument pairs
        parameter_argument_pair: Pattern = re.compile(rf'{parameter_prefix}[\w]+[\s]+(?:(?!\s\-).)*\b')
        # compile regex for the prefixed parameter
        prefixed_parameter: Pattern = re.compile(rf'^{parameter_prefix}')
        # find all substrings that start with the parameter prefix and have arguments
        parameter_matches: List[str] = re.findall(parameter_argument_pair, message)
        # strip the parameter prefix from each parameter/argument combo
        parameter_matches: List[str] = [re.sub(prefixed_parameter, '', parameter_match) for parameter_match in parameter_matches]
        
        # if a filter callback was provided, filter the parameter matches
        if filter: parameter_matches: List[str] = filter(parameter_matches)

        # split the argument/parameter combo into tuple(parameter, argument)
        parameter_pairs: List[List[str]] = [parameter_match.split(maxsplit=1) for parameter_match in parameter_matches]
        # convert list of tuples to dictionary
        kwargs: Dict[str, str] = {parameter_pair[0]: parameter_pair[-1] for parameter_pair in parameter_pairs}
        # create args list
        args: List[Any] = list()

        try:
            # run the command
            await self.run(command_name, args, kwargs, optionals)

        # if the message doesn't start with a prefix
        except HandlerPrefixError:
            return
        except HandlerError:
            raise

    async def run(self, command_name: str, args: List[Any], kwargs: Dict[str, str], optionals: Dict[str, Any] = dict()):
        """
        Run a command given its name, args and kwargs, as well as any optional objects the command requires.

        Raises:
            - HandlerExecutionError   upon failure to bind command arguments or a parameter mismatch
            - HandlerLookupError      upon failure to lookup command object from the registry
        """

        try:
            entry: Entry = self._registry[command_name]
            package: Package = self._packages[entry.package]
            component: Component = package.components[entry.component]
            command: Command = component.commands[entry.command]
        except KeyError as error:
            raise HandlerLookupError(command_name, error)
        
        # for each optional keyvalue pair passed in through contructor
        for optional_key, optional_value in optionals.items():
            # if the command's signature contains a parameter matching the optional key
            if optional_key in command.signature.parameters.keys():
                # add the correlated optional value to kwargs
                kwargs[optional_key] = optional_value

        try:
            # bind the processed arguments to the command signature
            bound_arguments: BoundArguments = command.signature.bind(*args, **kwargs)
            # run the command with the assembled signature
            await command.run(bound_arguments)
        except TypeError as error:
            raise HandlerExecutionError(command_name, error)
        except CommandError as error:
            raise HandlerExecutionError(command_name, error)

class Entry():

    @property
    def package(self) -> str:
        return self._package
    
    @property
    def component(self) -> str:
        return self._component
    
    @property
    def command(self) -> str:
        return self._command

    def __init__(self, package: str, component: str, command: str) -> None:
        self._package: str = package
        self._component: str = component
        self._command: str = command


class HandlerError(Exception):
    """Base exception class for handler related errors."""
    
    def __init__(self, message: str, exception: Exception | None = None):
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message


class HandlerLoadError(HandlerError):
    """Raised when an exception occurs while loading handler inputs."""

    def __init__(self, reference: Path, exception: Exception | None = None):
        message: str = f'Failed to load {reference}: {exception}'
        super().__init__(message, exception)


class HandlerPrefixError(HandlerError):
    """Raised when the message to process does not begin with the expected prefix."""

    def __init__(self, prefix: str, exception: Exception | None = None):
        message: str = f'Message does not begin with prefix \'{prefix}\''
        super().__init__(message, exception)


class HandlerExecutionError(HandlerError):
    """Raised when an exception occurs during command execution."""

    def __init__(self, command_name: str, exception: Exception | None = None):
        message: str = f'An exception occurred while executing command \'{command_name}\': {exception}'
        super().__init__(message, exception)
        

class HandlerLookupError(HandlerError):
    """Raised when a command cannot be looked up by command name."""

    def __init__(self, command_name: str, exception: Exception = None):
        message: str = f'Lookup for command \'{command_name}\' failed.'
        super().__init__(message, exception)
