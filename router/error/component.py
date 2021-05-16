from inspect import Signature

class ComponentError(Exception):
    """
    Base exception class for component related errors.
    """
    
    def __init__(self, component_name: str=None, internal_error: Exception=None):
        self.component_name: str = component_name
        self.internal_error: Exception = internal_error

    def __str__(self):
        return f'An unspecified exception occurred in component {self.component_name}: {self.internal_error}'


class ComponentLoadError(ComponentError):
    """Raised when an exception occurs while loading a component."""

    def __str__(self):
        return f'An exception occurred while loading component \'{self.component_name}\': {self.internal_error}'

class CommandAccessError(ComponentError):
    """Raised when an attempt to access a command not contained in a component is made."""

    def __init__(self, component_name: str, command_name: str, internal_error: Exception=None):
        super().__init__(component_name, internal_error)
        self.command_name = command_name

    def __str__(self):
        return f'An exception occurred while trying to access command \'{self.command_name}\' in component \'{self.component_name}\': {self.internal_error}'

class InvalidCommandError(ComponentError):
    """Raised when an attempt to access a non-existent command is made."""
    
    def __init__(self, component_name, command_name):
        self.component_name = component_name
        self.command_name = command_name

    def __str__(self):
        return f'Command {self.command_name} does not exist in component {self.component_name}.'

class InvalidInitializerError(ComponentError):
    """Raised when a component class is provided that requires initialization parameters."""

    def __init__(self, component_name: str):
        self.component_name = component_name

    def __str__(self):
        return f'Component {self.component_name} requires initialization parameters, which are not supported.'

class ParameterMismatchError(ComponentError):
    """Raised when arguments provided to a command do not match its signature."""
    
    def __init__(self, command_signature: Signature, argument_signature: Signature):
        self.command_signature = command_signature
        self.argument_signature = argument_signature

    def __str__(self):
        return f'Invalid arguments provided to command. Expected {self.command_signature}; received {self.argument_signature}.'
