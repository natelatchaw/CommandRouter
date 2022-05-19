import importlib.util
from importlib.machinery import ModuleSpec
import inspect
import logging
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Tuple, Type

from router.component import Component


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
        """Initialize a Package via its Path reference."""

        # resolve the provided reference
        self._reference: Path = reference.resolve()
        # get the module spec located at the reference
        self._spec: ModuleSpec = importlib.util.spec_from_file_location(reference.stem, reference)
        # create the module from the module spec
        self._module: ModuleType = importlib.util.module_from_spec(self._spec)
        # execute the module via the spec loader
        try: self._spec.loader.exec_module(self._module)
        # if an error occurred during import
        except ImportError: raise
