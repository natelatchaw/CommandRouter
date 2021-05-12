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
