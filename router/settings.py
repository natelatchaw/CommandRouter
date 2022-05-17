from router.error.configuration import ConfigurationError, EmptyConfigurationEntryError, MissingConfigurationEntryError
from router.configuration.tokenstore import TokenStore
from router.configuration.uxstore import UXStore

class Settings():
    def __init__(self, name: str):
        self.name = name
        self._tokenStore = TokenStore(name)
        self._uxStore = UXStore(name)

    @property
    def prefix(self) -> str:
        return self._uxStore.prefix
    @prefix.setter
    def prefix(self, prefix: str) -> None:
        self._uxStore.prefix = prefix

    @property
    def owner(self) -> int:
        entry_name: str = 'owner'
        try:
            return self._uxStore.owner
        except ValueError:
            raise EmptyConfigurationEntryError(entry_name)
    @owner.setter
    def owner(self, owner_id: int):
        self._uxStore.owner = owner_id

    @property
    def components(self) -> str:
        # define the configuration key
        entry_name: str = 'components'
        try:
            return self._uxStore.components
        # if the entry is missing in the configuration
        except MissingConfigurationEntryError:
            # generate an empty entry
            self._uxStore.components = str()
            raise ConfigurationError(' '.join([
                f'A \'{entry_name}\' entry could not be found in the configuration file; a key has been created for you.',
                f'This value is used to determine the path to use for component files.'
                f'Please provide a value.'
            ]))
        # if the entry is empty in the configuration
        except EmptyConfigurationEntryError:
            raise ConfigurationError(' '.join([
                f'The \'{entry_name}\' entry was empty in the configuration file.',
                f'This value is used to determine the path to use for component files.',
                f'Please provide a value.'
            ]))
    @components.setter
    def components(self, components: str) -> None:
        self._uxStore.components = components

    @property
    def mode(self) -> str:
        # define the configuration key
        entry_name: str = 'token'
        try:
            return self._tokenStore.mode
        # if the entry is missing in the configuration
        except MissingConfigurationEntryError:
            # generate an empty entry
            self._tokenStore.mode = str()
            raise ConfigurationError(' '.join([
                f'A \'{entry_name}\' entry in the configuration file could not be found; a key has been created for you.',
                f'This value is used to determine the token to use.',
                f'Please provide a value.'
            ]))
        # if the entry is empty in the configuration
        except EmptyConfigurationEntryError:
            raise ConfigurationError(' '.join([
                f'The \'{entry_name}\' entry was empty in the configuration file.',
                f'This value is used to determine the token to use.',
                f'Please provide a value.'
            ]))
    @mode.setter
    def mode(self, mode: str) -> None:
        self._tokenStore.mode = mode

    @property
    def token(self):
        try:
            return self._tokenStore.get_token(self.mode)
        except MissingConfigurationEntryError:
            self._tokenStore.add_token(self.mode, '')
            raise ConfigurationError(' '.join([
                f'A \'{self.mode}\' entry in the configuration file could not be found; a key has been created for you.',
                f'Please provide a value.'
            ]))
        except EmptyConfigurationEntryError:
            raise ConfigurationError(' '.join([
                f'The \'{self.mode}\' entry was empty in the configuration file.',
                f'Please provide a value.'
            ]))
    @token.setter
    def token(self, token):
        self._tokenStore.add_token(self.mode, token)

    @property
    def logging_channel(self) -> int:
        # define the configuration key
        entry_name: str = 'logging_channel'
        try:
            return self._uxStore.logging_channel
        # if the entry is missing in the configuration
        except MissingConfigurationEntryError:
            # generate an empty entry
            self._uxStore.logging_channel = str()
            raise EmptyConfigurationEntryError(entry_name)
        # if the entry is empty in the configuration
        except EmptyConfigurationEntryError:
            raise EmptyConfigurationEntryError(entry_name)
    @logging_channel.setter
    def logging_channel(self, channel_id: int) -> None:
        self._uxStore.logging_channel = channel_id