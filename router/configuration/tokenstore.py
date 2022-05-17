from router.configuration.configuration import Configuration
from router.error.configuration import EmptyConfigurationEntryError, MissingConfigurationSectionError

class TokenStore(Configuration):
    
    def __init__(self, name: str):
        super().__init__(name)
        # define section name
        self._section = 'TOKENS'
        # try to initialize section in config file
        try:
            # add a section to the config file
            self.add_section(self.section)
        # if the section already exists
        except MissingConfigurationSectionError:
            # silent abort of section creation
            pass
        finally:
            print(f'Initialized {self._section} configuration store.')

    @property
    def section(self):
        return self._section
    @section.setter
    def section(self, name):
        # set to capitalized variant of provided name
        self._section = name.upper()    

    @property
    def mode(self):
        default_section: str = 'DEFAULT'
        entry_name: str = 'token'
        # if the config is missing the designated section
        if not self._config.has_section(default_section):
            # add the designated section to the config
            self.add_section(default_section)
        try:
            # get the mode value from the config file
            value: str = self.get_key_value(default_section, entry_name)
            # if the value is an empty string
            if value == '': raise EmptyConfigurationEntryError(entry_name)
            # return the value
            return value
        # if the designated section does not contain the mode key
        except ValueError:
            # set the config's key value to an empty string
            self.set_key_value(default_section, entry_name, str())
            raise EmptyConfigurationEntryError(entry_name)
    @mode.setter
    def mode(self, value) -> None:
        default_section = 'DEFAULT'
        entry_name = 'token'
        # set the config's key value to the provided value
        self.set_key_value(default_section, entry_name, value)


    def add_token(self, tag, token):
        # if the config is missing the token section
        if not self._config.has_section(self.section):
            # add the token section to the config
            self.add_section(self.section)
            # set the default mode to the token provided
            self.mode = tag
        # add the tag/token pair to the token section
        self.set_key_value(self.section, tag, token)

    def get_token(self, tag: str):
        # if the config is missing the token section
        if not self._config.has_section(self.section):
            # add the token section to the config
            self.add_section(self.section)

        try:    
            # get the value from the config file
            value: str = self.get_key_value(self.section, tag)
            # if the value is an empty string
            if value == '': raise EmptyConfigurationEntryError(tag)
            # return the value
            return value
        except ValueError:
            raise MissingConfigurationSectionError(tag)