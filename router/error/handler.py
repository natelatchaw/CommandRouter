import pathlib

class HandlerError(Exception):
    """
    Base exception class for handler related errors.
    """

    @property
    def message(self) -> str | None:
        """A message describing the exception at hand"""
        return self._message
    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @property
    def inner_exception(self) -> Exception | None:
        """The exception that caused the current exception (if available)"""
        return self._inner_exception
    @inner_exception.setter
    def inner_exception(self, exception: Exception) -> None:
        self._inner_exception = exception

    
    def __init__(self, message: str, exception: Exception | None = None):
        self.message = message
        self.inner_exception = exception

    def __str__(self):
        return f'An exception occurred in the handler during message handling: {self.message}'


class HandlerLoadError(HandlerError):
    """
    Raised when an exception occurs while loading handler inputs
    """

    def __init__(self, reference: pathlib.Path, details: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'Failed to load from \'{reference.name}\': {details}'
        ])
        super().__init__(message, exception)


class HandlerPrefixError(HandlerError):
    """
    Raised when the message to process does not begin with the expected prefix
    """

    def __init__(self, prefix: str, details: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'Message does not begin with prefix \'{prefix}\': {details}'
        ])
        super().__init__(message, exception)


class HandlerExecutionError(HandlerError):
    """
    Raised when an exception occurs during command execution
    """

    def __init__(self, command_name: str, details: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'Failed to execute command {command_name}: {details}'
        ])
        super().__init__(message, exception)
        

class HandlerAccessError(HandlerError):
    """
    Raised when a component cannot be accessed from the component registry
    """

    def __init__(self, component_name: str, details: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'Failed to access component {component_name}: {details}'
        ])
        super().__init__(message, exception)
        

class HandlerLookupError(HandlerError):
    """
    Raised when a component cannot be looked up by a command name
    """

    def __init__(self, command_name: str, details: str, exception: Exception = None):
        message: str = ' '.join([
            f'Failed to lookup command {command_name}: {details}'
        ])
        super().__init__(message, exception)