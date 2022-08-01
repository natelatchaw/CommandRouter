import importlib.util
import inspect
import logging
from collections.abc import Mapping
from importlib.machinery import ModuleSpec
from logging import Logger
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type

from .component import Component

log: Logger = logging.getLogger(__name__)

class Package(Mapping[str, Component]):
    
    @property
    def name(self) -> str:
        return self._spec.name
    
    @property
    def doc(self) -> Optional[str]:
        if not self._module.__doc__:
            return None
        if str.isspace(self._module.__doc__):
            return None
        return inspect.cleandoc(self._module.__doc__)

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
        try: self._spec.loader.exec_module(self._module)
        # if an error occurred during import
        except ImportError as error: raise PackageInitializationError(self._spec.name, error)
        # initialize the components dictionary
        self._components: Dict[str, Component] = dict()


    def load(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes and stores instances of each class contained by the package
        as component instances

        Parameters:
        - args:
            arguments to be passed to the __init__ class method
        - kwargs:
            keyword arguments to be passed to the __init__ class method
        """
        # get all class members of the module
        members: List[Tuple[str, Type]] = inspect.getmembers(self._module, inspect.isclass)
        # filter members without a matching module name
        members: List[Tuple[str, Type]] = [(class_name, class_object) for class_name, class_object in members if class_object.__module__ == self._module.__name__]
        # for each member
        for class_name, class_object in members:
            # instantiate component
            component: Optional[Component] = self.__build_component__(class_object, *args, **kwargs)
            # add component to dictionary
            if component: self._components[component.name] = component


    def __build_component__(self, cls: Type, *args: Any, **kwargs: Any) -> Optional[Component]:
        try:
            # instantiate component
            component: Component = Component(cls, *args, **kwargs)
            # load the component
            component.load()
            # return the component
            return component
        except Exception as error:
            # log the error
            log.error(error)


    def __getitem__(self, key: str) -> Component:
        return self._components.__getitem__(key)

    def __iter__(self) -> Iterator[str]:
        return self._components.__iter__()

    def __len__(self) -> int:
        return self._components.__len__()
        

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


