from router.error.configuration import ConfigurationEmptyEntryError, ConfigurationError, ConfigurationGetError, ConfigurationMissingEntryError
from router.configuration.tokenstore import TokenStore
from router.configuration.uxstore import UXStore

class Settings():
    def __init__(self, name: str):
        self.name = name
        self._tokenStore = TokenStore(name)
        self._uxStore = UXStore(name)

    @property
    def prefix(self):
        return self._uxStore.prefix
    @prefix.setter
    def prefix(self, prefix):
        self._uxStore.prefix = prefix

    @property
    def owner(self):
        key = 'owner'
        try:
            return self._uxStore.owner
        except ValueError as valueError:
            invalidEntry = '\n'.join([
                str(valueError),
                f'Please insert a valid {key} id in the config file.'
            ])
            raise ConfigurationEmptyEntryError(key, ValueError(invalidEntry))
    @owner.setter
    def owner(self, owner_id: int):
        self._uxStore.owner = owner_id

    @property
    def components(self):
        entry_name = 'components'
        try:
            return self._uxStore.components
        except ConfigurationMissingEntryError as configurationMissingEntryError:
            self._uxStore.components = ''
            missing_entry = ' '.join([
                f'No {entry_name} selector was found in the config, a selector has been generated for you.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationMissingEntryError(entry_name, Exception(missing_entry))
        except ConfigurationEmptyEntryError:
            empty_entry = ' '.join([
                f'The {entry_name} selector in the config contained an empty string.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationEmptyEntryError(entry_name, Exception(empty_entry))
    @components.setter
    def components(self, components):
        self._uxStore.components = components

    @property
    def mode(self):
        entry_name = 'mode'
        try:
            return self._tokenStore.mode
        except ConfigurationMissingEntryError:
            self._tokenStore.mode = ''
            missing_entry = ' '.join([
                f'No {entry_name} selector was found in the config, a selector has been generated for you.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationMissingEntryError(entry_name, Exception(missing_entry))
        except ConfigurationEmptyEntryError:
            empty_entry = ' '.join([
                f'The {entry_name} selector in the config contained an empty string.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationEmptyEntryError(entry_name, Exception(empty_entry))
    @mode.setter
    def mode(self, mode):
        self._tokenStore.mode = mode

    @property
    def token(self):
        try:
            return self._tokenStore.get_token(self.mode)
        except ConfigurationMissingEntryError:
            self._tokenStore.add_token(self.mode, '')
            missingToken = ' '.join([
                f'No config entry found with tag \'{self.mode}\'.',
                'An entry has been created for you to insert your token.'
            ])
            raise ConfigurationMissingEntryError(self.mode, Exception(missingToken))
        except ConfigurationEmptyEntryError:
            emptyToken = ' '.join([
                f'Config entry with tag \'{self.mode}\' contained an empty string.',
                'Please insert a token for sign-in.'
            ])
            raise ConfigurationEmptyEntryError(self.mode, Exception(emptyToken))
    @token.setter
    def token(self, token):
        self._tokenStore.add_token(self.mode, token)

    @property
    def logging_channel(self):
        entry_name = 'logging_channel'
        try:
            return self._uxStore.logging_channel
        except ConfigurationEmptyEntryError:
            missing_entry = ' '.join([
                f'No {entry_name} selector was found in the config, a selector has been generated for you.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationMissingEntryError(entry_name, Exception(missing_entry))
        except ConfigurationEmptyEntryError:
            empty_entry = ' '.join([
                f'The {entry_name} selector in the config contained an empty string.',
                f'Please supply a valid value for the {entry_name} entry in the config file.'
            ])
            raise ConfigurationEmptyEntryError(entry_name, Exception(empty_entry))
    @logging_channel.setter
    def logging_channel(self, channel_id: int):
        self._uxStore.logging_channel = channel_id