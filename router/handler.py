import logging
import re
from inspect import BoundArguments
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Match, Optional, Pattern, Tuple

from .packaging import Command, CommandError, Component, Package

log: Logger = logging.getLogger(__name__)

class Handler():

    def __init__(self, parameter_prefix: str = '-'):
        # set the parameter prefix
        self._parameter_prefix: str = parameter_prefix
        # initialize the registry
        self._registry: Dict[str, Entry] = dict()
        # initialize the package dictionary
        self._packages: Dict[str, Package] = dict()
        # compile regex patterns
        self.__compile__()


    def __compile__(self) -> None:
        """
        Compile regex patterns used in message analyzation.
        """
        
        # compile the command pattern
        self._command_pattern: Pattern = re.compile(rf'^[\w]+')
        # compile the parameter pattern
        self._parameter_pattern: Pattern = re.compile(rf'{self._parameter_prefix}([\w]+)[\s]+((?:(?!\s\-).)+\b)')


    def __add_package__(self, package: Package) -> None:
        for component in package.values():
            for command in component.values():
                self._registry[command.name] = Entry(package.name, component.name, command.name)
                log.info('Added command %s.%s.%s', package.name, component.name, command.name)


    def __get_name__(self, message: str) -> Optional[str]:
        """
        Searches the message for the command name using the command pattern
        """
        # find command name matches in the message
        command_match: Match = re.match(self._command_pattern, message)
        # get the command name from the match
        command_name: Optional[str] = command_match.group(0) if command_match else None
        return command_name


    def __get_kwargs__(self, message: str) -> Dict[str, str]:
        """
        Searches the message for parameter key-value pairs using the parameter pattern
        """
        # find all parameter name-value pairs in the message
        parameters: List[Tuple[str, str]] = re.findall(self._parameter_pattern, message)
        # convert parameter name-value pairs into kwargs dictionary
        kwargs: Dict[str, str] = {parameter_name: parameter_value for parameter_name, parameter_value in parameters}
        return kwargs


    def load(self, directory: Path, extension: str = 'py', *args: Any, **kwargs: Any):
        """
        Load package files from a directory.
        Failed package assemblies are logged as warning messages.
        """

        # resolve the provided directory path
        directory: Path = directory.resolve()
        # if the provided directory doesn't exist, create it
        if not directory.exists(): directory.mkdir(parents=True, exist_ok=True)

        # define the filename pattern to search for
        pattern: str = f'*.{extension}'
        # get all paths for files with filenames matching the pattern in the provided directory
        references: List[Path] = [reference for reference in directory.glob(pattern) if reference.is_file()]
        # for each reference
        for reference in references:
            # instantiate package
            package: Optional[Package] = self.__build_package__(reference, *args, **kwargs)
            # if the package is None, continue to next reference
            if not package: continue
            # add package to dictionary
            self._packages[package.name] = package
            # register package
            self.__add_package__(package)

    
    def __build_package__(self, ref: Path, *args: Any, **kwargs: Any) -> Optional[Package]:
        try:
            # instantiate package
            package: Package = Package(ref)
            # load the package
            package.load(*args, **kwargs)
            # return the package
            return package
        except Exception as error:
            # log the error
            log.error(error)



    async def process(self, message: str, *, args: List[Any] = list()) -> None:
        """
        Process a message, parsing it for:
        - a primary command name
        - delimited parameter key-value pairs

        Raises:
        - TypeError
            upon invalid message type provided
        - HandlerExecutionError
            upon failure to bind command arguments or a parameter mismatch
        - HandlerLookupError
            upon failure to lookup command object from the registry
        """
        # filter non-string message parameters
        if not isinstance(message, str): raise TypeError(f'Expected type {type(str)}; received type {type(message)}')

        command_name: Optional[str] = self.__get_name__(message)
        if not command_name: raise MissingCommandError()
        log.debug('Determined command name to be \'%s\'', command_name)
        
        kwargs: Dict[str, str] = self.__get_kwargs__(message)
        log.debug('Determined parameter list to be %s', kwargs)
        
        # run the command
        await self.run(command_name, args, kwargs)


    async def run(self, command_name: str, args: List[Any], kwargs: Dict[str, str]):
        """
        Run a command given its name, args and kwargs, as well as any optional objects the command requires.

        Raises:
        - HandlerExecutionError
            upon failure to bind command arguments or a parameter mismatch
        - HandlerLookupError
            upon failure to lookup command object from the registry
        """

        try:
            # get the command entry from the registry
            entry: Entry = self._registry[command_name]
            # get the command from the package source
            command: Command = self._packages[entry.package][entry.component][entry.command]
            # bind the processed arguments to the command signature
            bound_arguments: BoundArguments = command.signature.bind(*args, **kwargs)
            # run the command with the assembled signature
            await command.run(bound_arguments)
        except KeyError as error:
            raise HandlerLookupError(command_name, error)
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
