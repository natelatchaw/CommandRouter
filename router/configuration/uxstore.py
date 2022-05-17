from configparser import DuplicateSectionError
from router.configuration.configuration import Configuration
from router.error.configuration import ConfigurationError, EmptyConfigurationEntryError, MissingConfigurationSectionError

class UXStore(Configuration):
    def __init__(self, name: str):
        super().__init__(name)
        # define section name
        self._section = 'UX'
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
        self._section = name.upper()

    @property
    def prefix(self):
        return self.get_character(self.section, 'prefix')
    @prefix.setter
    def prefix(self, prefix: str):
        self.set_character(self.section, 'prefix', prefix)

    @property
    def owner(self):
        return self.get_integer(self.section, 'owner')
    @owner.setter
    def owner(self, owner_id: int):
        self.set_integer(self.section, 'owner', owner_id)

    @property
    def components(self) -> str:
        return self.get_folder(self.section, 'components')
    @components.setter
    def components(self, components: str):
        self.set_folder(self.section, 'components', components)
        
    @property
    def logging_channel(self) -> int:
        return self.get_integer(self.section, 'logging_channel')
    @logging_channel.setter
    def logging_channel(self, channel_id: int):
        self.set_integer(self.section, 'logging_channel', channel_id)
