class ModuleError(Exception):
    """
    Base exception class for module related errors.
    """
    
    def __init__(self, module_name: str=None, internal_error: Exception=None):
        self.module_name: str = module_name
        self.internal_error: Exception = internal_error

    def __str__(self):
        return f'An unspecified exception occurred in module {self.module_name}: {self.internal_error}'


class ModuleLoadError(ModuleError):
    """Raised when an exception occurs while loading a module."""

    def __str__(self):
        return f'An exception occurred while loading module {self.module_name}: {self.internal_error}'