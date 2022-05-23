from logging import Logger
import logging
import re
from inspect import BoundArguments
from pathlib import Path
from typing import Any, Dict, List, Match, Optional, Pattern, Tuple

from router.packaging.package import PackageInitializationError

from .packaging import Command, Component, Package, CommandError

log: Logger = logging.getLogger(__name__)

class Handler():

    def __init__(self, parameter_prefix: str = '-'):
        # set the parameter prefix
        self._parameter_prefix: str = parameter_prefix
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
        log.debug('Resolved provided directory to %s', directory)

        # if the provided directory doesn't exist
        if not directory.exists(): raise HandlerLoadError(directory)

        # get all paths for files in the provided directory
        pattern: str = f'*.{extension}'
        references: List[Path] = [reference for reference in directory.glob(pattern) if reference.is_file()]
        log.debug('Found %s .%s files in %s', len(references), extension, str(directory))

        for reference in references:
            try:
                package: Package = Package(reference)

                for component in package.values():
                    for command in component.values():
                        self._registry[command.name] = Entry(package.name, component.name, command.name)
                        log.warn('Added command %s.%s.%s', package.name, component.name, command.name)

            except Exception as error:
                log.error(error)
            else:
                self._packages[package.name] = package

    async def process(self, message: str, *, args: List[Any] = list()) -> None:
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

        # compile regex pattern for the command name
        command_pattern: Pattern = re.compile(rf'^[\w]+')
        # find the command name in the message
        command_match: Match = re.match(command_pattern, message)
        # if the command could not be found in the message, raise exception
        if not command_match: raise MissingCommandError()
        # get the command name string from the match
        command_name: str = command_match.group(0)
        log.debug('Determined command name to be \'%s\'', command_name)

        # compile regex pattern for parameter name-value pairs
        parameter_pattern: Pattern = re.compile(rf'{self._parameter_prefix}([\w]+)[\s]+((?:(?!\s\-).)+\b)')
        # find all parameter name-value pairs in the message
        parameters: List[Tuple[str, str]] = re.findall(parameter_pattern, message)
        # convert parameter name-value pairs in kwargs dictionary
        kwargs: Dict[str, str] = {parameter_name: parameter_value for parameter_name, parameter_value in parameters}
        log.debug('Determined parameter list to be %s', kwargs)

        try:
            # run the command
            await self.run(command_name, args, kwargs)

        # if the message doesn't start with a prefix
        except MissingCommandError:
            return
        except HandlerError:
            raise

    async def run(self, command_name: str, args: List[Any], kwargs: Dict[str, str]):
        """
        Run a command given its name, args and kwargs, as well as any optional objects the command requires.

        Raises:
            - HandlerExecutionError   upon failure to bind command arguments or a parameter mismatch
            - HandlerLookupError      upon failure to lookup command object from the registry
        """

        try:
            entry: Entry = self._registry[command_name]
            command: Command = self._packages[entry.package][entry.component][entry.command]
        except KeyError as error:
            raise HandlerLookupError(command_name, error)

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
    
    def __init__(self, message: str, exception: Optional[Exception] = None):
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message


class HandlerLoadError(HandlerError):
    """Raised when an exception occurs while loading handler inputs."""

    def __init__(self, reference: Path, exception: Optional[Exception] = None):
        message: str = f'Failed to load {reference}: {exception}'
        super().__init__(message, exception)


class MissingCommandError(HandlerError):
    """Raised when a command name could not be determined from the message."""

    def __init__(self, exception: Optional[Exception] = None):
        message: str = f'Could not determine a command from the message.'
        super().__init__(message, exception)


class HandlerExecutionError(HandlerError):
    """Raised when an exception occurs during command execution."""

    def __init__(self, command_name: str, exception: Optional[Exception] = None):
        message: str = f'An exception occurred while executing command \'{command_name}\': {exception}'
        super().__init__(message, exception)
        

class HandlerLookupError(HandlerError):
    """Raised when a command cannot be looked up by command name."""

    def __init__(self, command_name: str, exception: Exception = None):
        message: str = f'Lookup for command \'{command_name}\' failed.'
        super().__init__(message, exception)
