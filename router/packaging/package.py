import importlib.util
import inspect
import logging
from collections.abc import Mapping
from importlib.machinery import ModuleSpec
from logging import Logger
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterator, List, Optional, Tuple, Type

from .component import Component

log: Logger = logging.getLogger(__name__)

class Package(Mapping[str, Component]):
    
    @property
    def name(self) -> str:
        return self._spec.name
    
    @property
    def doc(self) -> str:
        return self._module.__doc__

    @property
    def components(self) -> Dict[str, Component]:
        return self._components


    def __init__(self, reference: Path) -> None:
        """
        Initialize a package via its path.

        Raises:
        - PackageInitializationError
            upon failing to import module dependencies
        """

        # resolve the provided reference
        self._reference: Path = reference.resolve()
        # get the module spec located at the reference
        self._spec: ModuleSpec = importlib.util.spec_from_file_location(reference.stem, reference)
        # create the module from the module spec
        self._module: ModuleType = importlib.util.module_from_spec(self._spec)
        # execute the module via the spec loader
        try:
            self._spec.loader.exec_module(self._module)
        # if an error occurred during import
        except ImportError as error:
            raise PackageInitializationError(self._spec.name, error)
        # load all components
        self._components: Dict[str, Component] = self.__load__()


    def __getitem__(self, key: str) -> Component:
        return self._components.__getitem__(key)

    def __iter__(self) -> Iterator[str]:
        return self._components.__iter__()

    def __len__(self) -> int:
        return self._components.__len__()


    def __load__(self) -> Dict[str, Component]:
        # get all class members of the module
        members: List[Tuple[str, Type]] = inspect.getmembers(self._module, inspect.isclass)
        # filter members without a matching module name
        members: List[Tuple[str, Type]] = [(class_name, class_object) for class_name, class_object in members if class_object.__module__ == self._module.__name__]
        # instantiate dictionary
        components: Dict[str, Component] = dict()
        # for each member
        for class_name, class_object in members:
            try:
                # instantiate component
                component: Component = Component(class_object)
                # add component to dictionary
                components[component.name] = component
            except Exception as error:
                log.error(error)
        # return dictionary
        return components
        

class PackageError(Exception):
    """Base exception class for package related errors."""

    def __init__(self, message: str, exception: Optional[Exception] = None) -> None:
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message
        

class PackageInitializationError(PackageError):
    """Raised when an exception occurs when initializing a package."""

    def __init__(self, package_name: str, exception: Optional[Exception] = None) -> None:
        message: str = f'Failed to initialize package {package_name}: {exception}'
        super().__init__(message, exception)


