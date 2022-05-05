import pathlib

class HandlerError(Exception):
    """
    Base exception class for handler related errors.
    """

    def __init___(self, message: str = None):
        self.message: str | None = message if message else "No information provided"

    def __init__(self, exception: Exception = None):
        self.message: str | None = str(exception) if exception else "No information provided"

    def __str__(self):
        return f'An exception occurred in the handler during message handling: {self.message}'


class HandlerLoadError(HandlerError):
    """
    Raised when an exception occurs while loading handler inputs.
    """

    def __init__(self, reference: pathlib.Path, message: str = None):
        self.reference: pathlib.Path = reference
        super().__init__(message)

    def __init__(self, reference: pathlib.Path, exception: Exception = None):
        self.reference: pathlib.Path = reference
        super().__init__(exception)

    def __str__(self):
        return f'An exception occurred in the handler while loading \'{self.reference.name}\': {self.message}'


class HandlerPrefixError(HandlerError):
    """
    Raised when the message to process does not begin with the expected prefix.
    """

    def __init__(self, prefix: str, exception: Exception = None):
        self.prefix = prefix
        super().__init__(exception)

    def __str__(self):
        return f'An exception occurred in the handler while parsing the input for prefix: {self.message}'


class HandlerExecutionError(HandlerError):
    """
    Raised when an exception occurs during command execution.
    """

    def __init__(self, command_name: str, internal_error: Exception):
        super().__init__(internal_error)
        self.command_name = command_name
    
    def __str__(self):
        return f'An exception occurred in the handler while trying to execute command \'{self.command_name}\': {self.message}'


class HandlerAccessError(HandlerError):
    """
    Raised when a component cannot be accessed from the component registry.
    """

    def __init__(self, component_name: str, message: str = None):
        self.component_name = component_name
        super().__init__(message)

    def __init__(self, component_name: str, exception: Exception = None):
        self.component_name = component_name
        super().__init__(exception)

    def __str__(self):
        return f'An exception occurred in the handler while trying to access component \'{self.component_name}\': {self.message}'


class HandlerLookupError(HandlerError):
    """Raised when a component cannot be looked up by a command name."""

    def __init__(self, command_name: str, exception: Exception = None):
        self.command_name = command_name
        super().__init__(exception)

    def __str__(self):
        return f'An exception occurred in the handler during lookup for command \'{self.command_name}\': {self.message}'