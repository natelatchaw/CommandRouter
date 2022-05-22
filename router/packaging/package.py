import importlib.util
import inspect
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Tuple, Type

from .component import Component


class Package():

    @property
    def name(self) -> str:
        # return the name from the spec
        return self._spec.name
    
    @property
    def doc(self) -> str:
        return self._module.__doc__

    @property
    def components(self) -> Dict[str, Component]:
        # get all class members of the module
        members: List[Tuple[str, Type]] = inspect.getmembers(self._module, inspect.isclass)
        # filter members without a matching module name
        members: List[Tuple[str, Type]] = [(class_name, class_object) for class_name, class_object in members if class_object.__module__ == self._module.__name__]
        # create component from each member
        components: List[Component] = [Component(class_object) for class_name, class_object in members]
        # return assembled dictionary
        return dict([(component.name, component) for component in components])

    
    def __init__(self, reference: Path) -> None:
        """
        Initialize a package via its path.

        Raises:
        - PackageInitializationError        upon failing to import module dependencies
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


class PackageError(Exception):
    """Base exception class for package related errors."""

    def __init__(self, message: str, exception: Exception | None = None) -> None:
        self._message = message
        self._inner_exception = exception

    def __str__(self) -> str:
        return self._message
        

class PackageInitializationError(PackageError):
    """Raised when an exception occurs when initializing a package."""

    def __init__(self, package_name: str, exception: Exception | None = None) -> None:
        message: str = f'Failed to initialize package {package_name}: {exception}'
        super().__init__(message, exception)


