import os
import configparser
from configparser import DuplicateSectionError
import pathlib

from router.error.configuration import ConfigurationError, ConfigurationWriteError, EmptyConfigurationEntryError, MissingConfigurationEntryError

class Configuration():
    def __init__(self, name: str):
        self._config = configparser.ConfigParser()
        self.name = name
        self.file = os.path.abspath(f'{name}.ini')

        if not os.path.exists(self.file):
            with open(self.file, 'w') as configFile:
                self._config.write(configFile)

        self._config.read(self.file)

    def get_config(self):
        return self._config

    def reload(self):
        self._config.read(self.file)

    def add_section(self, section):
        """
        Adds the given section to the config file.
        Raises:
            TypeError if the section parameter is not a string
            DuplicateSectionError if a section already exists with the name contained in the section parameter
        """
        try:
            self._config.add_section(section)
            self.write()
        # if the default section name is passed
        except ValueError:
            ##raise ConfigurationSectionError(section, Exception(f'Cannot add default section: default section already exists.'))
            return
        # if a section name that already exists is passed
        except DuplicateSectionError as duplicateSectionError:
            ##raise ConfigurationSectionError(section, Exception(f'Cannot add section {section}: {section} already exists.'))
            return

    def set_key_value(self, section, key, value):
        """
        Sets a value for the given key in the given section.
        """
        try:
            # set the section name to all caps
            section = section.upper()
            self.add_section(section)
        except (ValueError, DuplicateSectionError):
            # pass if the section already exists
            pass
        finally:
            self._config.set(section, key, value)
            self.write()

    def get_key_value(self, section, key):
        """
        Retrieves the value for the given key in the given section.

        Raises:
            `MissingConfigurationEntryError` if the provided section does not contain the provided key.
        """
        # reload the config file to get changes
        self.reload()
        # get the value for the provided key if it exists, or None if not
        value: str = self._config.get(section, key, fallback=None)
        # if the key does not exist in the config file
        if value is None: raise MissingConfigurationEntryError(key)
        # return value
        return value
            
    def write(self) -> None:
        with open(self.file, 'w') as configFile:
            self._config.write(configFile)

    def get_integer(self, section: str, key: str) -> int:
        # if the config is missing the given section
        if not self._config.has_section(section):
            # add the given section to the config
            self.add_section(section)
        try:
            # get the value from the config file
            value: str = self.get_key_value(section, key)
            # if the entry is an empty string
            if value == '': raise EmptyConfigurationEntryError(key)
            # parse the int and return
            return int(value)
        except MissingConfigurationEntryError:
            # create the key with an empty string value
            self.set_key_value(section, key, str())
            raise EmptyConfigurationEntryError(key)

    def set_integer(self, section: str, key: str, value: int) -> None:
        # if the value is not an integer
        if not isinstance(value, int): raise ConfigurationError(f'Cannot set {value} for key \'{key}\'; {int} was expected but a {type(value)} was received.')
        # add the given value to the given key in the given section
        self.set_key_value(section, key, str(value))

    def get_folder(self, section: str, key: str) -> pathlib.Path:
        # if the config is missing the given section
        if not self._config.has_section(section):
            # add the given section to the config
            self.add_section(section)
        try:
            # get the value from the config
            value: str = self.get_key_value(section, key)
            # if the entry is an empty string
            if value == '': raise EmptyConfigurationEntryError(key)
            # get a reference from the provided folder name
            path: pathlib.Path = pathlib.Path(value)
            # if the path doesn't exist, create it
            if not path.exists(): path.mkdir(parents=True, exist_ok=True)
            # return the path
            return path
        except MissingConfigurationEntryError:
            # create the key if it is missing
            self.set_key_value(section, key, str())
            raise EmptyConfigurationEntryError(key)

    def set_folder(self, section: str, key: str, value: str) -> None:
        # if the config is missing the given section
        if not self._config.has_section(section):
            # add the given section to the config
            self.add_section(section)
        try:
            # get a reference from the provided folder name
            path: pathlib.Path = pathlib.Path(value)
            # if the path doesn't exist, create it
            if not path.exists(): path.mkdir(parents=True, exist_ok=True)
            # add the given value to the given key in the given section
            self.set_key_value(section, key, value)
        except:
            raise

    def get_character(self, section: str, key: str) -> str:
        value = self.get_string(section, key)
        # if the given value is not a character
        if not (isinstance(value, str) and len(value) == 1): raise ConfigurationError(f'The value for {key} must be a single character.')
        return value

    def set_character(self, section: str, key: str, value: str) -> None:
        # if the given value is not a character
        if not (isinstance(value, str) and len(value) == 1): raise ConfigurationError(f'The value for {key} must be a single character.')
        # add the given value to the given key in the given section
        self.set_string(section, key, value)

    
    def get_string(self, section: str, key: str):
        # if the config is missing the given section
        if not self._config.has_section(section):
            # add the given section to the config
            self.add_section(section)
        try:
            # get the value from the config
            value = self.get_key_value(section, key)
            # if the key's value is missing
            if not value: raise EmptyConfigurationEntryError(key)
            # return the value
            return value
        except MissingConfigurationEntryError:
            # create the key if it is missing
            self.set_key_value(section, key, '')
            raise EmptyConfigurationEntryError(key)

    def set_string(self, section: str, key: str, value: str):
        # add the given value to the given key in the given section
        self.set_key_value(section, key, value)

