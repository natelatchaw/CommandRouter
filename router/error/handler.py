import pathlib

class HandlerError(Exception):
    """
    Base exception class for handler related errors.
    """
    
    def __init__(self, internal_error: Exception=None):
        self.internal_error: Exception = internal_error

    def __str__(self):
        return f'An unspecified exception occurred during message handling: {self.internal_error}'


class HandlerLoadError(HandlerError):
    """Raised when an exception occurs while loading handler inputs."""

    def __init__(self, item: pathlib.Path, internal_error: Exception=None):
        super().__init__(internal_error)
        self.item = item

    def __str__(self):
        if self.item.is_file():
            return f'An exception occurred while loading file \'{self.item.name}\': {self.internal_error}'
        elif self.item.is_dir():
            return f'An exception occurred while loading folder \'{self.item.name}\': {self.internal_error}'

class HandlerPrefixError(HandlerError):
    """Raised when the message to process does not begin with the expected prefix."""

    def __init__(self, prefix: str, internal_error: Exception=None):
        super().__init__(internal_error)
        self.prefix = prefix

    def __str__(self):
        return f'An execption occurred when parsing the input for prefix: {self.internal_error}'

class HandlerRunError(HandlerError):
    """Raised when an exception occurs during the running of a command."""

    def __init__(self, command_name: str, internal_error: Exception):
        super().__init__(internal_error)
        self.command_name = command_name
    
    def __str__(self):
        return f'An exception occurred while trying to run command \'{self.command_name}\': {self.internal_error}'

class ComponentAccessError(HandlerError):
    """Raised when a component cannot be accessed from the component registry."""

    def __init__(self, component_name: str, internal_error: Exception):
        super().__init__(internal_error)
        self.component_name = component_name

    def __str__(self):
        return f'An exception occurred while trying to access component \'{self.component_name}\': {self.internal_error}'

class ComponentLookupError(HandlerError):
    """Raised when a component cannot be looked up by a command name."""

    def __init__(self, command_name: str, internal_error: Exception):
        super().__init__(internal_error)
        self.command_name = command_name

    def __str__(self):
        return f'An exception occurred during component lookup for command \'{self.command_name}\': {self.internal_error}'