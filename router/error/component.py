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
        return f'An exception occurred while loading component {self.component_name}: {self.internal_error}'