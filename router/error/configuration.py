class ConfigurationError(Exception):
    """
    Base exception class for configuration related errors.
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
        return f'An exception occurred during configuration manipulation: {self.message}'


class MissingConfigurationSectionError(ConfigurationError):
    """
    Raised when a specified section in the configuration cannot be found
    """

    def __init__(self, section: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'The \'{section}\' configuration section is missing.',
            f'Please create a section in the config file.'
        ])
        super().__init__(message, exception)


class MissingConfigurationEntryError(ConfigurationError):
    """
    Raised when a specified entry in the configuration cannot be found
    """

    def __init__(self, entry: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'The \'{entry}\' configuration entry is missing.',
            f'Please create an entry in the config file.'
        ])
        
        f'Configuration entry \'{entry}\' could not be found.'
        super().__init__(message, exception)


class EmptyConfigurationEntryError(ConfigurationError):
    """
    Raised when a specified entry in the configuration is empty, but a value is expected
    """

    def __init__(self, entry: str, exception: Exception | None = None):
        message: str = ' '.join([
            f'The \'{entry}\' configuration entry was empty, but a value was expected.',
            f'Please supply a valid value in the config file.'
        ])
        super().__init__(message, exception)


class ConfigurationReadError(ConfigurationError):
    """
    Raised when an attempt to read configuration data fails
    """

    def __init__(self, entry: str, exception: Exception | None = None):
        message: str = f'An error occurred while attempting to read data from configuration entry \'{entry}\''
        super().__init__(message, exception)


class ConfigurationWriteError(ConfigurationError):
    """
    Raised when an attempt to write configuration data fails
    """

    def __init__(self, entry: str, exception: Exception | None = None):
        message: str = f'An error occurred while attempting to write data to configuration entry \'{entry}\''
        super().__init__(exception)