from inspect import Signature

class ComponentError(Exception):
    """
    Base exception class for component related errors.
    """
    
    def __init__(self, component_name: str, message: str = None):
        self.component_name: str = component_name
        self.message: str | None = message if message else "No information provided"

    def __init__(self, component_name: str, exception: Exception = None):
        self.component_name: str = component_name
        self.message: str | None = str(exception) if exception else "No information provided"
        self.inner_exception: Exception | None = exception

    def __str__(self):
        return f'An exception occurred in component {self.component_name}: {self.message}'


class ComponentLoadError(ComponentError):
    """
    Raised when an exception occurs while loading a component.
    """

    def __str__(self):
        return f'An exception occurred in component \'{self.component_name}\' while loading: {self.message}'


class ComponentAccessError(ComponentError):
    """
    Raised when an attempt to access a command in a component fails.
    """

    def __init__(self, component_name: str, command_name: str, message: str = None):
        self.command_name = command_name
        super().__init__(component_name, message)

    def __init__(self, component_name: str, command_name: str, exception: Exception = None):
        self.command_name = command_name
        super().__init__(component_name, exception)

    def __str__(self):
        return f'An exception occurred in component \'{self.component_name}\' while accessing command \'{self.command_name}\': {self.message}'


class InvalidCommandError(ComponentError):
    """
    Raised when an attempt to access a non-existent command is made.
    """
    
    def __init__(self, component_name, command_name):
        self.component_name = component_name
        self.command_name = command_name

    def __str__(self):
        return f'{self.command_name} command does not exist in {self.component_name} component.'


class InvalidInitializerError(ComponentError):
    """Raised when a component class is provided that requires initialization parameters."""

    def __init__(self, component_name: str):
        self.component_name = component_name

    def __str__(self):
        return f'{self.component_name} component requires initialization parameters, which are not supported.'

class ParameterMismatchError(ComponentError):
    """Raised when arguments provided to a command do not match its signature."""
    
    def __init__(self, command_signature: Signature, argument_signature: Signature):
        self.command_signature = command_signature
        self.argument_signature = argument_signature

    def __str__(self):
        return f'Invalid arguments provided to command. Expected {self.command_signature}; received {self.argument_signature}.'
