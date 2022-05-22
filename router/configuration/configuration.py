import configparser
from configparser import ConfigParser
from logging import Logger
import logging
from pathlib import Path
from typing import Dict, Iterator, List, MutableMapping

from router.configuration import Section

__all__: List[str] = [
    "Configuration"
]


class Configuration(MutableMapping):

    def __setitem__(self, key: str, value: Section) -> None:
        try:
            self.__read__()
            self._sections.__setitem__(key, value)
            self.__write__()
            self._logger.debug('Set section %s:%s', self._name, key)
        except Exception:
            raise

    def __getitem__(self, key: str) -> Section:
        try:
            self.__read__()
            section: Section = self._sections.__getitem__(key)
            self._logger.debug('Get section %s:%s', self._reference.name, key)
            return section
        except KeyError:
            section: Section = Section(key, self._parser, self._reference)
            self._logger.debug('Created section %s:%s', self._reference.name, section.name)
            self.__setitem__(key, section)
            section: Section = self._sections.__getitem__(key)
            self._logger.debug('Get section %s:%s', self._reference.name, key)
            return section
        except Exception:
            raise

    def __delitem__(self, key: str) -> None:
        try:
            section: Section = self.__getitem__(key)
            section.clear()
            self._parser.remove_section(section.name)
            self._sections.__delitem__(key)
            self.__write__()
            self._logger.debug('Delete section %s:%s', self._reference.name, key)
        except Exception:
            raise

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return self._sections.__iter__()

    def __len__(self) -> int:
        return self._sections.__len__()

    def __str__(self) -> str:
        return self._sections.__str__()

    def __write__(self) -> None:
        with open(self._reference, 'w') as file:
            self._parser.write(file)
        self._logger.debug('Wrote configuration state to %s', self._reference.name)

    def __read__(self) -> None:
        self._parser.read(self._reference)
        self._logger.debug('Read configuration state from %s', self._reference.name)

    def __init__(self, reference: Path) -> None:
        self._logger: Logger = logging.getLogger(__name__)
        self._parser: ConfigParser = configparser.ConfigParser()
        self._reference: Path = reference.resolve()
        self._logger.debug('Determined target configuration file %s at %s', self._reference.name, self._reference.parent)
        self._name: str = self._reference.stem
        if not self._reference.parent.exists():
            self._logger.debug('Missing target configuration directory at %s', self._reference.parent)
            self._reference.parent.mkdir(parents=True, exist_ok=True)
            self._logger.debug('Created target configuration directory at %s', self._reference.parent)
        if not self._reference.is_file():
            self._logger.debug('Missing target configuration file %s at %s', self._reference.name, self._reference.parent)
            self._reference.touch(exist_ok=True)
            self._logger.debug('Created target configuration file %s at %s', self._reference.name, self._reference.parent)
        self.__read__()
        self._logger.debug('Completed initial configuration read for %s', self._reference.name)
        sections: List[Section] = [Section(section, self._parser, self._reference) for section in self._parser.sections()]
        self._sections: Dict[str, Section] = {section.name: section for section in sections}
        self._logger.debug('Loaded %s sections for configuration file %s', len(self._sections), self._reference.name)

    @property
    def name(self) -> str:
        """The configuration file's name."""
        return self._name
