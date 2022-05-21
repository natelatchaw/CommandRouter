from configparser import ConfigParser, NoOptionError
from pathlib import Path
from typing import Dict, Iterator, MutableMapping


class Section(MutableMapping):

    def __setitem__(self, key: str, value: str) -> None:
        self._parser.set(self._name, key, value)
        self.__write__()

    def __getitem__(self, key: str) -> str | None:
        self.__read__()
        try:
            return self._parser.get(self._name, key)
        except NoOptionError:
            return None

    def __delitem__(self, key: str) -> None:
        key: str = self.__getitem__(key)
        self._parser.remove_option(self._name, key)
        self.__write__()

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
        self._name: str = name
        self._parser: ConfigParser = parser
        self._reference: Path = reference.resolve()
        if not self._parser.has_section(self._name):
            self._parser.add_section(self._name)

    @property
    def name(self) -> str:
        """The configuration section's name."""
        return self._name
