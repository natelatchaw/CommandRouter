import configparser
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Iterator, List, MutableMapping

from router.configuration.section import Section


class Configuration(MutableMapping):

    def __setitem__(self, key: str, value: Section) -> None:
        self._sections.__setitem__(key, value)
        self.__write__()

    def __getitem__(self, key: str) -> Section:
        self.__read__()
        try:
            return self._sections.__getitem__(key)
        except KeyError:
            section: Section = Section(key, self._parser, self._reference)
            self.__setitem__(key, section)
            return self._sections.__getitem__(key)

    def __delitem__(self, key: str) -> None:
        section: Section = self.__getitem__(key)
        section.clear()
        self._parser.remove_section(section.name)
        self._sections.__delitem__(key)
        self.__write__()

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return self._sections.__iter__()

    def __len__(self) -> int:
        return self._sections.__len__()

    def __str__(self) -> str:
        return self._sections.__str__()

    def __write__(self) -> None:
        with open(self._reference, 'w') as file:
            self._parser.write(file)

    def __read__(self) -> None:
        self._parser.read(self._reference)

    def __init__(self, reference: Path):
        self._name: str = self._reference.stem
        self._parser: ConfigParser = configparser.ConfigParser()
        self._reference: Path = reference.resolve()
        if not self._reference.parent.exists():
            self._reference.parent.mkdir(parents=True, exist_ok=True)
        if not self._reference.is_file():
            self._reference.touch(exist_ok=True)
        self.__read__()
        sections: List[Section] = [Section(
            section, self._parser, self._reference) for section in self._parser.sections()]
        self._sections: Dict[str, Section] = {
            section.name: section for section in sections}

    @property
    def name(self) -> str:
        """The configuration file's name."""
        return self._name

    def add_section(self, name: str) -> None:
        section: Section = Section(name, self._parser, self._reference)
        self.__setitem__(name, section)
