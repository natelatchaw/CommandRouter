class ConfigurationError(Exception):
    """
    Base exception class for configuration related errors.
    """
    
    def __init__(self, internal_error: Exception=None):
        self.internal_error: Exception = internal_error

    def __str__(self):
        return f'An unspecified exception occurred during configuration manipulation: {self.internal_error}'

class ConfigurationSectionError(ConfigurationError):
    """Raised when an exception occurs while getting data from as section the configuration file."""

    def __init__(self, section: str, internal_error: Exception=None):
        super().__init__(internal_error)
        self.section = section

    def __str__(self):
        return f'An exception occurred while looking up config section \'{self.section}\': {self.internal_error}'

class ConfigurationGetError(ConfigurationError):
    """Raised when an exception occurs while getting data from the configuration file."""

    def __init__(self, entry: str, internal_error: Exception=None):
        super().__init__(internal_error)
        self.entry = entry

    def __str__(self):
        return f'An exception occurred while looking up config entry \'{self.entry}\': {self.internal_error}'

class ConfigurationSetError(ConfigurationError):
    """Raised when an exception occurs while setting data to the configuration file."""

    def __init__(self, entry: str, internal_error: Exception):
        super().__init__(internal_error)
        self.entry = entry
    
    def __str__(self):
        return f'An exception occurred while setting config entry \'{self.entry}\': {self.internal_error}'

class ConfigurationTypeError(ConfigurationError):
    """Raised when a configuration value of an expected type cannot be casted to that type."""

    def __init__(self, entry: str, type: type, internal_error: Exception):
        super().__init__(internal_error)
        self.entry = entry
        self.type = type
        
    def __str__(self):
        return f'An exception occurred while converting config entry \'{self.entry}\' to type {self.type}: {self.internal_error}'

    