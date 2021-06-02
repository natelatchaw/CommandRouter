from configparser import DuplicateSectionError
from router.error.configuration import ConfigurationEmptyEntryError, ConfigurationGetError, ConfigurationMissingEntryError, ConfigurationSectionError, ConfigurationSetError
from router.configuration.configuration import Configuration

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
        except ConfigurationSectionError:
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
    def prefix(self):
        try:
            return self.get_character(self.section, 'prefix')
        except ConfigurationEmptyEntryError:
            raise
    @prefix.setter
    def prefix(self, prefix: str):
        try:
            self.set_character(self.section, 'prefix', prefix)
        except ValueError as valueError:
            raise ConfigurationSetError('prefix', valueError)

    @property
    def owner(self):
        try:
            return self.get_integer(self.section, 'owner')
        except ConfigurationEmptyEntryError:
            raise
    @owner.setter
    def owner(self, owner_id: int):
        try:
            self.set_integer(self.section, 'owner', owner_id)
        except ValueError as valueError:
            raise ConfigurationSetError('owner', valueError)

    @property
    def components(self) -> str:
        try:
            return self.get_folder(self.section, 'components')
        except ConfigurationEmptyEntryError:
            raise
    @components.setter
    def components(self, components: str):
        try:
            self.set_folder(self.section, 'components', components)
        except ValueError as valueError:
            raise ConfigurationSetError('components', valueError)
        
    @property
    def logging_channel(self) -> int:
        try:
            return self.get_integer(self.section, 'logging_channel')
        except ConfigurationEmptyEntryError:
            raise
    @logging_channel.setter
    def logging_channel(self, channel_id: int):
        try:
            self.set_integer(self.section, 'logging_channel', channel_id)
        except ValueError as valueError:
            raise ConfigurationSetError('logging_channel', valueError)
