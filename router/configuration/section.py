from configparser import ConfigParser, NoOptionError
from logging import Logger
import logging
from pathlib import Path
from typing import Dict, Iterator, List, MutableMapping

__all__: List[str] = [
    "Section"
]


class Section(MutableMapping):

    def __setitem__(self, key: str, value: str) -> None:
        self.__read__()
        self._parser.set(self._name, key, value)
        self.__write__()
        self._logger.debug('Set entry %s:%s:%s', self._reference.name, self._name, key)

    def __getitem__(self, key: str) -> str | None:
        self.__read__()
        try:
            entry: str = self._parser.get(self._name, key)
            self._logger.debug('Get entry %s:%s:%s', self._reference.name, self._name, key)
            return entry
        except NoOptionError:
            self._logger.debug('No entry %s:%s:%s', self._reference.name, self._name, key)
            return None

    def __delitem__(self, key: str) -> None:
        self.__read__()
        key: str = self.__getitem__(key)
        self._parser.remove_option(self._name, key)
        self.__write__()
        self._logger.debug('Delete entry %s:%s:%s', self._reference.name, self._name, key)

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return iter({key: value for key, value in self._parser.items(self._name)})

    def __len__(self) -> int:
        return len({key: value for key, value in self._parser.items(self._name)})

    def __str__(self) -> str:
        return str({key: value for key, value in self._parser.items(self._name)})

    def __write__(self) -> None:
        with open(self._reference, 'w') as file:
            self._parser.write(file)

    def __read__(self) -> None:
        self._parser.read(self._reference)

    def __init__(self, name: str, parser: ConfigParser, reference: Path) -> None:
        self._logger: Logger = logging.getLogger(__name__)
        self._parser: ConfigParser = parser
        self._reference: Path = reference.resolve()
        self._name: str = name
        if not self._parser.has_section(self._name):
            self._logger.debug('Missing target configuration section %s:%s', self._reference.name, self._name)
            self._parser.add_section(self._name)
            self._logger.debug('Missing target configuration section %s:%s', self._reference.name, self._name)

    @property
    def name(self) -> str:
        """The configuration section's name."""
        return self._name
